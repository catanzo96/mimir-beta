# Progettare e rivedere i tipi

Un buon tipo fa lavorare il compilatore al posto dei test: rende impossibili gli stati non validi e rende evidenti quelli validi. Si applica soprattutto ai tipi di dominio e alle API pubbliche di un modulo, non ai DTO di passaggio.

## Quattro domande per ogni tipo
1. **Incapsulamento**: dall'esterno si può portare il valore in uno stato non valido? Proprietà scrivibili, array interni restituiti e modificabili, costruttori che accettano qualsiasi cosa.
2. **Invarianti espresse**: le regole ("almeno un elemento", "data fine dopo data inizio", "importo positivo") sono nel tipo o nel costruttore, o sono solo nei commenti e nei chiamanti?
3. **Utilità**: il tipo distingue davvero i casi che il codice tratta in modo diverso? Un tipo troppo largo (`string`, `object`, molti campi opzionali) sposta i controlli ovunque.
4. **Applicazione**: le invarianti valgono anche per i dati che entrano dai confini (HTTP, storage)? Se un dato non validato può diventare quel tipo con un `as`, il tipo promette più di quanto garantisce.

## Tecniche
- **Union discriminate** al posto di campi opzionali che dipendono l'uno dall'altro: `{ stato: 'pagato'; dataPagamento: Date } | { stato: 'aperto' }` invece di `{ stato: string; dataPagamento?: Date }`.
- **Costruttori intelligenti**: una funzione `crea…` che valida e restituisce il tipo (o un errore), e nessun altro modo di ottenerlo. Con i branded type il "marchio" lo applica solo quella funzione.
- **Tipi non vuoti** quando serve: `[T, ...T[]]` per "almeno un elemento".
- **`readonly`** sulle proprietà che non devono cambiare dopo la creazione, e copie difensive delle collezioni ricevute o restituite.
- **Niente "booleani gemelli"** (`isLoading` e `isError` insieme): sono quattro combinazioni, alcune impossibili. Una union di stati ne ha esattamente tante quante sono gli stati reali.

## Segnali in review
- Molti campi opzionali nello stesso tipo, usati insieme solo in certe combinazioni.
- `as` o `!` per convincere il compilatore che un valore è del tipo giusto.
- Lo stesso controllo di validità ripetuto in più chiamanti.
- Un tipo esportato che espone dettagli interni (campi tecnici, strutture di supporto) che i chiamanti non dovrebbero usare.

Nel codice esistente, questi sono segnali da riportare: non si riprogettano i tipi dentro un fix.
