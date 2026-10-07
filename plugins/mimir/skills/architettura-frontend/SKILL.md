---
name: architettura-frontend
description: Architettura frontend indipendente dal framework. Usala quando strutturi o rivedi un'app web (feature, stato, routing, chiamate al backend).
---

# Architettura frontend

Si applica insieme a `clean-code`, a `typescript` e alla skill del framework: `angular`, `react` o `vue`. Qui ci sono i principi che valgono ovunque; l'implementazione nel framework sta nella sua skill. Prevalgono struttura, librerie (es. NgRx, TanStack Query, Pinia) e convenzioni del progetto: non cambiare approccio a metà.

## Organizzazione per feature
- Struttura per **feature** (dominio: `ordini`, `fatture`), non per tipo tecnico globale (`components/`, `services/`). Dentro una feature trovi tutto ciò che la riguarda: schermate, componenti, stato, accesso ai dati, test.
- Ogni feature ha un **punto d'ingresso** (file `index`, modulo o route) che espone solo ciò che serve fuori; il resto è privato. Gli import "profondi" nei file interni di un'altra feature sono vietati.
- Le dipendenze vanno in una direzione: l'applicazione conosce le feature, le feature usano `shared`/`core`, `shared` non conosce le feature. Le feature non si importano tra loro: se due ne hanno bisogno, il pezzo comune sale in `shared`, oppure comunicano tramite route, eventi o un servizio di livello superiore.
- `shared` non diventa una discarica: contiene solo ciò che è davvero trasversale e privo di logica di una feature.
- Fai rispettare i confini con gli strumenti del progetto (regole di lint sugli import, es. ESLint con vincoli di dipendenza, Nx, dependency-cruiser) se già presenti.
- Come i contesti di un backend (`ddd`): una feature ha il suo linguaggio. Stesso concetto con forme diverse tra feature è lecito; un modello unico gigante condiviso no.

## Componenti
- **Container** (smart): sa dove stanno i dati, legge lo stato, chiama i servizi, gestisce gli eventi di alto livello. **Presentazionale** (dumb): riceve dati e callback, mostra e notifica, senza conoscere servizi, router o store.
- I presentazionali sono prevedibili e testabili con soli input; la maggior parte della UI dovrebbe essere così.
- Componenti piccoli con una responsabilità; se serve un commento per spiegare le sezioni di un template, sono componenti da estrarre.
- La logica di dominio e le regole non vivono nei componenti: in funzioni pure, servizi o nel modello di feature, testabili senza UI.
- Composizione prima di configurazione: slot/contenuto proiettato al posto di liste di flag booleani.

## Stato
Scegli il livello più basso che basta:
1. **Locale** al componente (apertura di un menu, valore di un campo): resta lì.
2. **Condiviso** tra componenti vicini: sale al genitore comune o a un servizio/store della feature.
3. **Globale** (utente, tema, permessi): pochi elementi, in `core`.
4. **Server state** (dati che vivono sul backend): non copiarlo a mano nello store globale. Trattalo con cache, invalidazione, deduplicazione delle richieste e rinfresco, con lo strumento che il progetto usa (strato di query del framework o libreria dedicata). Lo store globale tiene lo stato dell'interfaccia, non una seconda copia del database.

Altre regole:
- Una sola fonte di verità per ogni dato; lo stato derivato si calcola, non si memorizza.
- Stato immutabile e aggiornamenti espliciti: rendono i cambi tracciabili.
- Lo stato dell'URL (filtri, pagina, tab) sta nell'URL: la pagina diventa condivisibile e il pulsante indietro funziona.
- Niente store globale "per sicurezza": ogni elemento globale è una dipendenza da tutto.

## Comunicazione col backend
- Uno **strato di accesso ai dati** per feature (servizio o client): i componenti non costruiscono URL né parlano di HTTP. Il client ha tipi di richiesta e risposta, meglio se generati dal contratto (OpenAPI) quando il progetto lo prevede (vedi `sistemi-distribuiti`, contratti).
- **Modello di trasporto separato dal modello di vista**: mappa all'ingresso, così un cambio di API tocca un punto solo (stesso principio dell'anticorruption layer in `ddd`).
- Ogni chiamata ha **tre stati** gestiti: caricamento, errore, vuoto, oltre al successo. Tutti e quattro sono visibili e testati.
- **Errori** gestiti in modo centralizzato (intercettore o middleware) per i casi comuni (sessione scaduta, rete assente, errore generico), e localmente quando la schermata può fare qualcosa di utile (ritenta, correggi il campo). Messaggi comprensibili all'utente, senza dettagli tecnici; il dettaglio va nei log insieme all'id di correlazione.
- Retry automatico solo per letture o operazioni idempotenti. Un doppio clic non deve duplicare un'azione: disabilita il comando durante l'invio.
- Se il backend è eventualmente consistente, mostra lo stato intermedio e non l'esito finale prima del tempo.
- Segreti e token: mai nel codice o nel bundle; i token sono gestiti secondo la politica del progetto (preferisci cookie `HttpOnly` quando possibile, vedi `clean-code`, sicurezza).

## Routing e caricamento
- Le route rispecchiano le feature; ogni feature si carica **a richiesta** (lazy loading) dal proprio punto d'ingresso, tranne la parte iniziale necessaria.
- I controlli di accesso nel router (guardie, redirect) migliorano l'esperienza ma non sono sicurezza: l'autorizzazione vera sta nel backend.
- Gestisci le route sconosciute, gli errori di caricamento di un pezzo e le transizioni.

## Design system e componenti condivisi
- I componenti di base (bottoni, campi, tabelle, dialog) vivono in un unico posto e usano **token di design** (colori, spaziature, tipografia) invece di valori scritti nei singoli stili. Il tema o la modalità scura diventano un cambio di token.
- Prima di creare un componente, controlla se esiste già in `shared` o nella libreria di UI adottata. Non aggiungere una libreria di componenti senza ok.
- Un componente condiviso ha API piccola e documentata, stati (disabilitato, errore, caricamento) e test. Non accetta logica di una feature.
- Più applicazioni che condividono la UI: libreria separata e versionata, con changelog.

## Micro-frontend: solo se servono
Hanno senso quando più **team indipendenti** devono rilasciare parti diverse della stessa interfaccia senza coordinarsi. Costi: framework e dipendenze duplicati, bundle più pesanti, UX incoerente, stato e routing condivisi più difficili, ambienti da integrare. Un'app a feature ben confinata, con un monorepo se serve, risolve la maggior parte dei casi. Mai per "modernità".

## Prestazioni e accessibilità
- Misura prima di ottimizzare (strumenti del browser, analisi del bundle): vedi `clean-code`, principi. Controlli di base: lazy loading, niente librerie intere per una funzione, immagini dimensionate, liste lunghe virtualizzate o paginate, rendering che non si ripete senza cambiamenti. Indicazioni specifiche del framework nella sua skill.
- **Accessibilità come requisito**, non rifinitura: elementi semantici, controlli raggiungibili e usabili da tastiera, focus visibile e gestito alla navigazione e nei dialog, etichette per i campi, alternative testuali, contrasto, messaggi di errore e stati dinamici annunciati. Si progetta dall'inizio: rimediare dopo costa molto di più.

## Verifica
Con gli script già configurati nel progetto (controlla `package.json`): type check, lint (comprese le regole sui confini), test unitari e dei componenti, build di produzione; se ci sono, test end-to-end e controlli di accessibilità automatici. Riporta cosa hai lanciato e l'esito. Per le modifiche visibili alla UI, un controllo a mano nel browser (percorso principale, stati di caricamento/errore/vuoto, tastiera): se non puoi farlo, dichiaralo.
