# Revisione di design: punti da passare in rassegna

Per ADR, analisi d'impatto e progettazione di un servizio o di un'integrazione. Non tutti i punti valgono sempre: si riportano solo quelli pertinenti, con la risposta e l'evidenza. Un punto senza risposta diventa una domanda aperta.

## Requisiti
- Cosa deve fare, per chi, e cosa è esplicitamente fuori.
- Requisiti non funzionali con numeri: utenti contemporanei, volumi di dati, tempi di risposta accettabili, disponibilità richiesta, finestre di manutenzione.
- Vincoli: normativa (dati personali, conservazione, accessibilità), piattaforme imposte, competenze del team, budget.

## Stime di massima
- Richieste al secondo nei momenti di picco, non in media.
- Crescita dei dati in un anno e in cinque.
- Dimensione dei messaggi e dei file scambiati.
- Le stime servono a capire l'ordine di grandezza: decidono se un problema esiste, non come risolverlo.

## Dati
- Dove sta la fonte di verità di ogni dato, e chi può scriverlo.
- Consistenza richiesta: serve leggere subito ciò che si è scritto, o un ritardo è accettabile? Cosa succede se due utenti modificano lo stesso dato?
- Relazionale o altro: la scelta segue i modelli di accesso, non la moda.
- Crescita: indici, archiviazione dei dati vecchi, partizionamento solo se i volumi lo richiedono.

## Prestazioni
- Cache: cosa si mette, per quanto tempo, come si invalida, cosa succede se è vuota o vecchia.
- Lavori lunghi fuori dalla richiesta dell'utente: code, job, elaborazioni a lotti.
- Paginazione e limiti su tutto ciò che può crescere.

## Affidabilità
- Punti singoli di guasto: cosa si ferma se cade quel componente.
- Chiamate esterne: timeout, tentativi solo su operazioni idempotenti, comportamento quando il sistema esterno è giù.
- Idempotenza: un messaggio o una richiesta ripetuti non devono produrre effetti doppi.
- Sovraccarico: limiti di frequenza, code con dimensione massima, cosa si rifiuta quando si è al limite.
- Ripristino: backup, tempo massimo di fermo e di dati persi accettati.

## Sicurezza
- Autenticazione e autorizzazione: chi può fare cosa, controllato lato server sulla risorsa.
- Dati sensibili: dove passano, dove restano, chi li vede nei log.
- Superficie esposta: endpoint pubblici, porte, integrazioni.

## Esercizio
- Osservabilità: log, metriche e allarmi che dicono se funziona, prima che lo dica un utente.
- Rilascio: si può rilasciare senza fermo? Lo schema regge la versione vecchia e quella nuova insieme?
- Rollback: come si torna indietro e cosa non si può annullare.
- Costi di esercizio e di manutenzione nel tempo.

## Evoluzione
- Contratti verso altri sistemi: versionamento, compatibilità, chi va avvisato dei cambiamenti.
- Cosa diventa difficile cambiare dopo questa scelta.
