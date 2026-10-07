# Migrazioni del database nei rilasci

Da leggere quando un rilascio cambia lo schema o i dati esistenti. Vale con Flyway, Liquibase o script manuali.

## Regole
- **Una migrazione già applicata in un ambiente non si modifica**: ogni correzione è una migrazione nuova.
- **Ogni migrazione ha un rollback scritto**: uno script inverso oppure, più spesso per lo schema, una migrazione correttiva in avanti. Se è irreversibile, va dichiarato, con la procedura alternativa (ripristino da backup).
- Una migrazione per cambiamento logico, con un nome che dice cosa fa.
- **Provala su dati con volumi realistici** prima della produzione: una modifica istantanea su 100 righe può bloccare una tabella per minuti su 10 milioni. Annota i tempi misurati nel piano.
- **Schema e dati separati**: le modifiche di struttura in una migrazione, il popolamento o la correzione dei dati in un'altra (o in uno script a parte), così si verificano e si annullano separatamente.

## Cambiare senza rompere il codice in esercizio
Durante il deploy, e in caso di rollback del codice, la versione vecchia dell'applicazione gira sullo schema nuovo. Lo schema deve quindi andare bene a entrambe le versioni.

Per i cambiamenti che rompono la compatibilità si procede in più rilasci:
1. **Espandi**: aggiungi senza togliere. Colonne nuove nullable o con un default, tabelle nuove, il codice scrive in entrambe le forme.
2. **Migra i dati**: backfill a lotti, ripetibile (se si interrompe, si riprende), con conteggi prima e dopo.
3. **Contrai**: in un rilascio successivo, quando nessuna versione in esercizio usa più la forma vecchia, togli colonne o vincoli vecchi.

Esempi:
- rinominare una colonna = aggiungere la nuova, copiare, far leggere il codice dalla nuova, poi togliere la vecchia;
- rendere obbligatoria una colonna = prima popolarla, poi aggiungere il vincolo.

## Lock e tabelle grandi
- Creazione di indici, aggiunta di vincoli e alcune `ALTER TABLE` bloccano la tabella. Il comportamento dipende dal database e dalla versione: verifica sulla documentazione del DB in uso le opzioni non bloccanti (creazione di indici online o concorrente, vincoli validati in un secondo momento).
- Backfill a lotti con commit intermedi, non un unico `UPDATE` su tutta la tabella: transazioni enormi bloccano righe e riempiono i log del database.
- Fuori dalla finestra di picco, se il progetto non ha una finestra concordata.

## Verifica
- Prima: conteggi delle tabelle toccate e stato della tabella di storico delle migrazioni.
- Dopo: migrazioni applicate tutte e nell'ordine atteso, conteggi coerenti con quanto previsto, applicazione avviata senza errori di validazione dello schema.
