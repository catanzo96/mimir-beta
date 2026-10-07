---
name: sistemi-distribuiti
description: Linee guida per sistemi distribuiti e a messaggi. Usala quando progetti o rivedi comunicazione tra servizi, code, eventi, saga, retry, o scegli tra monolite e microservizi.
---

# Sistemi distribuiti

Si applica insieme a `clean-code`, a `ddd` per i confini e ad `architettura-esagonale` per la struttura interna dei servizi. Prevalgono le convenzioni e l'infrastruttura del progetto (broker, librerie di resilienza, formato dei messaggi): usa quelli, non introdurne di nuovi senza ok.

## Prima di distribuire
La rete rompe tre assunzioni: la chiamata può fallire, può essere lenta, può essere eseguita senza che tu lo sappia. Ogni punto di questa skill discende da qui.

**Monolite modulare o microservizi.** Parti dal monolite modulare (moduli con interfacce esplicite, dati separati per modulo) e distribuisci solo con una ragione concreta:
- team che devono rilasciare in modo indipendente;
- requisiti di scala o di isolamento dei guasti molto diversi tra parti;
- tecnologie incompatibili per necessità.

Costi reali dei microservizi: transazioni che non esistono più, consistenza eventuale, debug su più processi, versionamento dei contratti, pipeline e ambienti moltiplicati, latenza, costi operativi. Se il team è piccolo o i confini del dominio non sono chiari, si peggiora e basta. Se i confini sono sbagliati, un servizio diventa "monolite distribuito": cambia sempre insieme agli altri.

**Confini dei servizi**: seguono i bounded context (`ddd`), non le entità né i layer tecnici. Ogni servizio possiede i suoi dati: nessun database condiviso tra servizi, nessuna lettura diretta delle tabelle altrui.

## Sincrono o a messaggi
- **Sincrono** (REST, gRPC) quando il chiamante ha bisogno della risposta per proseguire. Accoppia i tempi: se l'altro è giù, tu sei giù. Più catene sincrone, più bassa la disponibilità complessiva.
- **Messaggi** (comandi ed eventi) quando basta che il lavoro avvenga, a tempo debito. Disaccoppia nel tempo, ma introduce consistenza eventuale e richiede idempotenza.
- Comando: chiede di fare qualcosa a un destinatario preciso. Evento: annuncia un fatto, senza sapere chi ascolta. Non travestire comandi da eventi.
- Non usare le code per simulare chiamate sincrone (richiesta e attesa della risposta): ottieni la complessità di entrambi.

## Consegna e idempotenza
- I broker garantiscono in pratica consegna **almeno una volta**: i duplicati arrivano, e anche l'ordine può saltare. "Esattamente una volta" a livello di business si ottiene con idempotenza, non con il broker.
- Ogni consumatore e ogni operazione che può essere ritentata deve essere **idempotente**: ripeterla produce lo stesso effetto. Tecniche in `references/messaggistica.md`: chiave di idempotenza, deduplicazione con inbox, operazioni naturalmente idempotenti (imposta lo stato, non "incrementa").
- **Outbox**: per cambiare il database e pubblicare un messaggio in modo affidabile, scrivi il messaggio nella stessa transazione del dato e pubblicalo poi da un relay. Evita la scrittura doppia (DB e broker), che prima o poi si disallinea. Dettagli in `references/messaggistica.md`.
- Messaggi che falliscono sempre: coda degli scarti (dead letter) con allarme e procedura di ripresa, non perdita silenziosa né retry infinito.

## Saga e consistenza eventuale
- Un processo che attraversa più servizi è una **saga**: sequenza di transazioni locali, ciascuna con la sua **compensazione** (annullamento di business, non rollback).
  - *Orchestrata*: un coordinatore dice cosa fare e tiene lo stato. Più chiara da seguire e testare; il coordinatore è un punto da presidiare.
  - *Coreografata*: ogni servizio reagisce agli eventi. Poco accoppiata, ma il flusso complessivo non sta scritto in nessun posto: usala per flussi corti.
- Le compensazioni sono operazioni di business e possono fallire a loro volta: devono essere idempotenti e ritentabili. Alcuni passi non sono compensabili (email inviata): mettili per ultimi.
- La saga ha stati espliciti (in corso, completata, compensata, fallita) e timeout.
- **Mostrare la consistenza eventuale all'utente**: non fingere che sia immediato. Stato intermedio visibile ("in elaborazione"), risposta `202` con un riferimento per seguire l'esito, aggiornamento per notifica o polling, nessun "operazione riuscita" prima che lo sia. Per la UI vedi `architettura-frontend`.

## Resilienza
Ogni chiamata remota ha:
- **Timeout** esplicito, più corto di quello di chi ti chiama. Senza timeout, un servizio lento esaurisce i thread di tutti.
- **Retry** solo su errori transitori e su operazioni idempotenti, con backoff esponenziale e **jitter**, con numero massimo di tentativi. I retry si moltiplicano lungo la catena: ritenta a un solo livello.
- **Circuit breaker** per smettere di chiamare chi sta fallendo e riprovare con cautela dopo una pausa.
- **Bulkhead**: pool o limiti di concorrenza separati per dipendenza, perché un servizio lento non consumi le risorse destinate agli altri.
- **Degrado controllato**: decidi prima cosa fa il servizio se una dipendenza non c'è (cache, valore di default, funzione disattivata, errore chiaro).
- Preferisci le funzioni di resilienza già presenti nel framework o nelle librerie del progetto (es. Resilience4j, `@Retryable` di Spring) a codice scritto a mano.

## Contratti ed evoluzione
- Il contratto (API, schema degli eventi) si definisce prima e si versiona: `references/contratti-osservabilita.md`.
- Cambi compatibili: aggiungi campi opzionali. Cambi incompatibili: nuova versione, convivenza, poi ritiro. Il consumatore ignora i campi che non conosce.

## CQRS ed event sourcing: solo se servono
- **CQRS** (modelli separati per scrittura e lettura): conviene se le letture hanno forma o carico molto diversi dalle scritture, o servono viste che attraversano più servizi. Per un semplice elenco bastano query dedicate sullo stesso database. Costo: dati replicati e in ritardo.
- **Event sourcing** (lo stato è la sequenza degli eventi): conviene se lo storico completo e il "cosa è successo" sono un requisito (audit forte, ricostruzione nel tempo). Costi alti: versionamento degli eventi per sempre, proiezioni, interrogazioni difficili. Mai di default.

## Osservabilità distribuita
Senza correlazione, un errore su cinque servizi è indecifrabile: trace id propagato in ogni chiamata e messaggio, loggato in ogni riga, più metriche e health. Dettagli in `references/contratti-osservabilita.md`.

## Verifica
- Ogni chiamata remota ha timeout; i retry sono solo su operazioni idempotenti.
- Ogni consumatore di messaggi è provato con lo stesso messaggio consegnato due volte e fuori ordine.
- Le compensazioni e il percorso di fallimento di ogni saga hanno un test.
- Test di contratto tra produttore e consumatore, se il progetto li ha.
- Build, test e lint del progetto puliti (comandi già configurati, es. `mvn verify`, `npm test`); per i test su broker e database reali usa gli strumenti del progetto (es. Testcontainers). Se non riesci a provare un flusso distribuito, dichiaralo come non verificato.
