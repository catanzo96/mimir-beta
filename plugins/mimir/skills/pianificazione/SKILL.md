---
name: pianificazione
description: Dalla richiesta alla specifica al piano per compiti medi e grandi. Usala quando il compito tocca più file o ha requisiti poco chiari, prima di scrivere codice.
when_to_use: 'Es.: "come lo implementeresti?", "facciamo un piano", "devo aggiungere la funzione X", "mettimi alla prova il piano", "facciamo uno spike", richieste vaghe che toccano più moduli.'
---

# Pianificazione

Si applica insieme a `clean-code` e alla skill del linguaggio o del framework. Se disponibili, `analisi-funzionale` e `analisi-tecnica` coprono documenti formali per il cliente. Prevalgono le convenzioni del progetto e le regole di `rules/working-style.md`.

Scopo: capire cosa serve davvero, fissare il perimetro e arrivare a passi piccoli, verificabili, approvati dall'utente prima di partire.

## Quando non usarla
- Compito piccolo e chiaro (una funzione, un fix noto): procedi direttamente.
- Domanda di design con più opzioni e nessuna implementazione da pianificare: usa l'agent `architetto` (uso 1).
- Un difetto da capire: `debugging`.

## 1. Obiettivo e perimetro
- Riformula in una frase cosa deve ottenere il compito e per chi. Se non riesci, mancano informazioni.
- Esplora il repo prima di chiedere: CLAUDE.md, struttura, codice vicino, test esistenti. Non chiedere ciò che il codice dice già.
- Scrivi cosa resta fuori. Il fuori perimetro evita che il compito si allarghi e va confermato dall'utente.
- Segnala senza fare ciò che trovi di fuori perimetro (casi non coperti, dati pregressi, debito).

## 2. Domande
- Solo quelle che cambiano il piano: scelte di comportamento, dati esistenti, vincoli di compatibilità, casi limite, priorità.
- Poche alla volta, in ordine di impatto. Per ciascuna proponi la risposta che consigli e il motivo: all'utente basta confermare o correggere.
- Se una risposta manca ma non blocca, scrivila come assunzione esplicita nel piano.

### Interrogatorio a round
Per compiti grandi o rischiosi (dati, migrazioni, sicurezza, pagamenti, contratti con altri sistemi), o quando l'utente chiede di mettere alla prova il piano:
1. Ordina le decisioni aperte per dipendenza: alcune si possono prendere solo dopo altre.
2. Ogni round raccoglie, in un messaggio numerato, le decisioni che hanno già tutte le premesse chiuse e che cambiano il piano, ognuna con la risposta consigliata; se sono più di sette, solo le più impattanti. Chiedere ora ciò che dipende da una risposta mancante produce risposte da rifare.
3. Dopo le risposte, guarda quali decisioni si sono sbloccate e prepara il round successivo.
4. Copri: obiettivo e confini; perché questa soluzione e non l'alternativa ovvia; cosa succede se fallisce a metà e come si torna indietro; casi limite (volumi molto maggiori, dati sporchi, accessi concorrenti, permessi).
5. "Non so" non chiude un ramo: diventa un'assunzione esplicita, una domanda a qualcun altro o uno spike.
6. Nessun codice durante l'interrogatorio. Alla fine riassumi decisioni, assunzioni e fuori perimetro e chiedi conferma prima del piano.

### Spike
Quando una domanda si chiude solo provando (una libreria fa davvero X? due approcci, quale regge?), proponi uno spike prima del piano e aspetta l'ok su domande, tempo e posto:
- **Domande osservabili**, da 1 a 4, nella forma "dato…, quando…, allora si vede…". Prima la più rischiosa: se cade quella, le altre non servono.
- **Tempo massimo** e **posto usa e getta**: di default lo scratchpad. Un branch nel repo del progetto e ogni dipendenza nuova richiedono l'ok dell'utente. Niente dati reali né scritture su sistemi condivisi.
- Il codice dello spike non entra nel prodotto: se serve pulirlo per tenerlo, lo spike è cresciuto oltre il suo scopo.
- La prova si deve poter vedere o rilanciare (un test, uno script, una pagina): un messaggio di successo stampato non dimostra niente. Oltre al caso che deve funzionare, prova quello che dovrebbe fallire.
- **Esito** per domanda: confermata, confermata con vincoli (quali), smentita. Anche la smentita è un risultato utile: costa uno spike invece di una funzione intera.
- Se si confrontano approcci, stessa domanda per ciascuno e tabella finale di confronto.
- Prima di chiudere, guarda i punti di contatto: due spike riusciti separatamente non provano che funzionino insieme.

Se la risposta sta nella documentazione o nel codice, non serve uno spike: basta `ricerca`.

## 3. Specifica breve
Per compiti medi e grandi scrivi (in chat, non in un file, salvo richiesta) una specifica di mezza pagina:
- **Obiettivo** e **fuori perimetro**;
- **Comportamento atteso**, con esempi concreti di input e output;
- **Criteri di accettazione**: frasi verificabili ("dato X, quando Y, allora Z"), ciascuna con il modo di controllarla (test, comando, scenario);
- **Vincoli**: versioni, contratti, compatibilità, sicurezza, prestazioni;
- **Assunzioni e domande aperte**.

Per compiti con più opzioni di design chiedi prima la raccomandazione all'architetto e riporta la scelta.

## 4. Piano a passi
Ogni passo:
- cambia una cosa sola e lascia il sistema funzionante (build e test verdi);
- ha il suo modo di verifica, scritto prima;
- indica i file toccati e, se non banale, come si annulla.

Ordine di dipendenza: contratti e dati prima, logica poi, interfaccia e integrazioni alla fine. Se un passo richiede "e poi sistemiamo", va spezzato. Fai emergere nel piano i rischi (dati, migrazioni, contratti con altri sistemi) e come tornare indietro se ci si ferma a metà.

Per un refactor: prima i test che bloccano il comportamento attuale, poi i passi di struttura, tenendo separato ogni commit `refactor` da quelli funzionali.

Forma del piano: elenco numerato con, per passo, "cosa", "file", "verifica". Breve: un piano più lungo del codice che descrive non viene letto.

## 5. Approvazioni
- **Il piano**: per procedure grandi aspetta l'ok dell'utente prima di toccare il codice (`rules/working-style.md`). Un ok vale per il piano presentato: se cambia in modo sostanziale, ripresentalo.
- **Commit e push**: mai senza approvazione esplicita, con l'elenco previsto da `rules/git-and-safety.md`. Proponi dove un passo chiude un commit sensato.
- Durante l'esecuzione, se un passo fa emergere qualcosa che cambia il piano, fermati e riporta invece di adattare in silenzio.

## 6. Delegare
Delega solo quando serve davvero: molta lettura da non tenere nella conversazione, lavori indipendenti da fare in parallelo, un modello diverso. Ogni delega ha un compito chiuso, il perimetro e il formato del resoconto, e il suo esito si verifica prima di usarlo.

| Lavoro | Dove e con quale modello |
|---|---|
| Ricerca, lettura di molti file, riassunti | subagent su `haiku` |
| Implementazione di un passo ben definito, review | subagent su `sonnet` |
| Architettura, scelte difficili, piano di un compito grande | agent `architetto` (`opus`, sola lettura) |

Non delegare a `haiku` contenuti esterni non fidati se l'agent può scrivere. Passi che toccano gli stessi file non vanno in parallelo.

## 7. Dove salvare il piano
- Nella cartella che il progetto indica (docs, specifiche, ADR) o, se non c'è, nello scratchpad della sessione.
- Mai file di piano o di metodo nei repo dei clienti senza l'ok dell'utente.
- Il piano non duplica ciò che esiste altrove (ticket, specifiche, ADR): rimanda per percorso o link.

## 8. Eseguire
Un passo alla volta: modifica, verifica del passo, segna come fatto. Se la verifica fallisce, `debugging` prima di proseguire. Non anticipare passi successivi e non allargare il perimetro. A fine piano ripassa i criteri di accettazione uno per uno.

## Verifica
Prima di dichiarare finito: per ogni criterio di accettazione indica come l'hai controllato e l'esito; lancia build, test e linter del progetto già configurati (`mvn verify`, `./gradlew check`, `npm test`, `ng lint`, `pytest`). Riporta ciò che non hai verificato e ciò che è rimasto fuori perimetro.
