# Qualità del codice

Le convenzioni del progetto (CLAUDE.md, linter, `.editorconfig`, codice esistente) prevalgono. Queste regole sono il default.

- Semplicità prima di tutto (KISS, YAGNI): niente astrazioni, generalizzazioni o ottimizzazioni senza un bisogno concreto.
- Codice prevedibile: nomi che dicono cosa fa una cosa, nessun effetto collaterale nascosto.
- Scrivi codice che si legga come quello circostante: stessi idiomi, naming e densità di commenti.
- Commenti solo per il *perché* (decisioni, vincoli). Se cambi il codice, aggiorna i commenti.
- Assenza di valore sempre esplicita: Optional, collezione vuota, eccezione. Mai `null` come segnale implicito. Nei linguaggi con null-safety nel type system (TypeScript strict, Kotlin) il tipo nullable controllato è l'alternativa esplicita.
- Gestisci gli errori ai confini del sistema. Mai inghiottire un'eccezione.
- Mai loggare dati sensibili (password, token, dati personali).
- Sicurezza di base sempre: input esterni validati, query parametrizzate, output codificato, minimo privilegio.
- Nessuna nuova dipendenza senza motivarla e chiedere il mio ok. Prima verifica se il progetto o la libreria standard coprono già il bisogno.
- La logica critica deve essere coperta da test.
- Prima di dichiarare finito: test, linter e analisi statica del progetto (es. Sonar) puliti sul codice che hai scritto.
- Boy Scout Rule solo sul codice che stai già toccando. I miglioramenti più ampi li segnali o li proponi come commit `refactor` separato.
- Per scrivere, modificare o rivedere codice usa la skill `clean-code`, più quelle del linguaggio, del framework e dell'architettura, se esistono.
