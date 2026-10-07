# Messaggistica: idempotenza, outbox, inbox

Leggi questo file quando scrivi un produttore o un consumatore di messaggi, o rendi affidabile un'operazione ritentabile.

## Idempotenza
Un'operazione è idempotente se eseguirla due volte equivale a eseguirla una. Come ottenerla, dal più semplice:
1. **Naturale**: "imposta lo stato a X", "inserisci o aggiorna per chiave", invece di "incrementa", "aggiungi alla lista".
2. **Con chiave di idempotenza**: il chiamante genera un id univoco per l'intenzione (non per il tentativo) e lo invia a ogni ritentativo. Il servizio registra id ed esito: se lo rivede, restituisce l'esito già calcolato senza rieseguire. Il vincolo di unicità sul database è la difesa che regge anche con richieste concorrenti.
3. **Inbox**: il consumatore salva l'id del messaggio in una tabella nella stessa transazione dell'effetto. Un duplicato viola il vincolo e viene scartato. Mantieni gli id per un tempo almeno pari alla finestra massima di ridelivery e poi ripulisci.

Controlla che l'id identifichi l'intenzione di business: se cambia a ogni ritentativo, non deduplica nulla.

## Ordine
Non contare sull'ordine di arrivo se non garantito: nemmeno dentro una partizione quando i retry rimettono in coda. Se serve, porta nel messaggio un numero di versione dell'aggregato e scarta o rimanda quello più vecchio dello stato già applicato. Le chiavi di partizione per aggregato garantiscono l'ordine per aggregato, non globale.

## Outbox
Problema: aggiornare il database e pubblicare sul broker sono due operazioni senza transazione comune. Se una riesce e l'altra no, dato e messaggio divergono.
- Nella stessa transazione del cambio di stato inserisci il messaggio in una tabella `outbox` (id, tipo, payload, istante, stato).
- Un relay legge i messaggi non pubblicati, li invia e li marca. Può essere un job periodico o lettura del log del database (CDC), a seconda dell'infrastruttura del progetto.
- Il relay può inviare lo stesso messaggio due volte: i consumatori sono idempotenti.
- Operativamente: ripulisci i messaggi pubblicati, monitora il ritardo (messaggi non pubblicati da troppo), proteggi il relay dalla concorrenza se ne hai più istanze.
- Non pubblicare sul broker dentro la transazione del database né subito dopo il commit "sperando": è il difetto che l'outbox risolve.

## Consumatori
- Conferma (ack) del messaggio solo dopo aver completato l'effetto e il suo salvataggio.
- Distingui errori **transitori** (rete, timeout: ritenta con backoff) da **permanenti** (messaggio non valido, regola violata: dead letter subito, non ritentare).
- Messaggio avvelenato: limite di tentativi, dead letter con causa e id di correlazione, allarme, procedura per rilanciarlo dopo la correzione.
- Valida lo schema in ingresso: il messaggio è input esterno come una richiesta HTTP.
- Una singola elaborazione non tiene transazioni aperte durante chiamate remote.

## Esempio di schema inbox
```sql
CREATE TABLE messaggio_elaborato (
  id_messaggio  VARCHAR(64) PRIMARY KEY,
  elaborato_il  TIMESTAMP NOT NULL
);
```
Nel consumatore, in un'unica transazione: inserisci l'id (se viola la chiave primaria, il messaggio è un duplicato: ack e fine), applica l'effetto, commit.
