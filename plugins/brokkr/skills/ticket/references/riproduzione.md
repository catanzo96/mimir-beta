# Riprodurre il problema di un ticket

Il metodo generale (ciclo di riproduzione, cosa è cambiato, confronto con un caso che funziona, bisezione, restringere, problemi intermittenti, causa non trovata) è nella skill `debugging`. Qui c'è solo ciò che è specifico di un difetto segnalato dal cliente o da un utente.

## Cosa ricavare dalla segnalazione
- **Quando**: data e ora esatte dell'evento, con il fuso. Servono per trovare i log e per sapere quale versione era in esercizio.
- **Chi e con quale ruolo**: profilo, ente, permessi. Molti difetti dipendono dal ruolo o dai dati di un solo ente.
- **Su quale dato**: codice pratica, identificativo del record, file caricato. Mai dati personali nel documento del ticket.
- **Dove**: ambiente (produzione, collaudo) e versione in esercizio in quel momento (tag o commit del rilascio). Le evidenze `file:riga` si prendono su quella versione, non sul branch di sviluppo.
- Se manca qualcosa di questo, è la prima domanda da fare (template `domande` di `analisi-funzionale`).

## Riprodurre senza accesso diretto
- **Log dell'evento**: si chiedono all'utente o a chi ha accesso, con l'intervallo di tempo preciso e l'eventuale id di correlazione.
- **Query in sola lettura** preparate da te e lanciate dall'utente, con ambiente e data nel documento del ticket (sezione "Query di riferimento"). Prima quella che conferma il dato anomalo, poi quelle che cercano altri casi uguali.
- **Replay** del payload o del file reale: prima di salvarlo o incollarlo, togli dati personali e segreti.
- **Dati del cliente in locale**: solo anonimizzati e con l'ok dell'utente. Altrimenti un caso sintetico costruito con le stesse caratteristiche (stato, ruolo, valori limite).

## Quanti casi
- Conta quanti record o utenti sono colpiti: cambia la priorità e decide se serve un intervento sui dati.
- Cerca da quando succede: la data del primo caso indica spesso il rilascio o la modifica che l'ha introdotto.
