# Principi e struttura

## Principi di progettazione
- **KISS**: preferisci soluzioni semplici e lineari. Astrazione eccessiva, ottimizzazione prematura e generalizzazione si introducono solo per necessità concrete.
- **YAGNI**: non implementare ciò che non serve ora.
- **Riusa prima di scrivere**: cerca chi fa già il lavoro, in quest'ordine: il repo (helper, componenti, pattern esistenti), la libreria standard, una funzione nativa della piattaforma, una dipendenza già installata. Usa il primo che basta. Una dipendenza nuova è l'ultima scelta e va motivata.
- **DRY, con giudizio**: elimina la duplicazione di *conoscenza*, non ogni somiglianza. Due pezzi simili che cambiano per ragioni diverse non vanno unificati. Una duplicazione è meglio di un'astrazione sbagliata; astrai alla terza ripetizione.
- **Minima sorpresa**: il codice fa ciò che il nome promette, senza effetti collaterali inattesi.
- **Command Query Separation**: preferisci metodi che o modificano lo stato (command) o restituiscono un valore (query). Eccezioni idiomatiche ammesse:
  - operazioni atomiche (`incrementAndGet()`, `pop()`, `compareAndSet()`);
  - salvataggi che restituiscono l'oggetto persistito (`repository.save()`);
  - builder e interfacce fluenti.
- **Immutabilità di default**: variabili, campi e oggetti valore immutabili, salvo necessità.
- **Niente ottimizzazione prematura, ma niente inefficienze evidenti**: query in un ciclo (N+1), cicli annidati su collezioni grandi, I/O ripetuto evitabile. Queste vanno corrette subito.

## Metodi e funzioni
- **Una sola responsabilità.**
  - Il segnale principale è la **complessità cognitiva**: oltre 15, la soglia di default di Sonar, il metodo va semplificato.
  - Segnali secondari: più di circa 20 righe, oppure un nome che richiede "e" o "oppure".
- **Argomenti: al massimo circa 3.** Oltre, raggruppali in un oggetto con significato.
  ```java
  // Male
  void aggiorna(long id, String nome, String cognome, Ruolo ruolo) {}
  // Meglio
  void aggiorna(Utente utente) {}
  ```
- **Niente argomenti di output**: lo stato si modifica sull'oggetto a cui appartiene.
  ```java
  aggiornaEta(utente, eta);   // Male
  utente.aggiornaEta(eta);    // Meglio
  ```
- **Niente parametri flag** (`boolean isAdmin`, `int mode`) che selezionano percorsi diversi: dividi in metodi con nomi espliciti (`eseguiComeUtente()`, `eseguiComeAdmin()`).
- **Indentazione: al massimo 2 livelli.** Oltre, usa extract method.
  ```java
  void completaOrdine(Ordine ordine) {
      applicaSconto(ordine);
      gestisciSpedizione(ordine);
  }
  ```

## Flusso di controllo
- **Guard clause ed early return** invece di `else` annidati:
  ```java
  if (!utente.isOnline()) {
      return List.of();
  }
  return oggettiUtente();
  ```
  Un `else` simmetrico e breve resta accettabile.
- **Condizioni complesse**: incapsulale in un metodo o una variabile con un nome in forma positiva.
  ```java
  if (adminHaFattoAccessoOggi()) { ... }
  ```
- **`break` e `continue`**: evitali quando oscurano il flusso. Preferisci condizioni chiare, estrazione in metodi o operazioni dichiarative (stream, find, any).

## Valori e costanti
- **Niente magic number o stringhe magiche**: usa costanti con un nome (`MAX_TENTATIVI`).
- **Insiemi chiusi di valori con significato**: enum o tipo equivalente del linguaggio.
- **Assenza di valore**:
  - se è un caso valido, rappresentala in modo esplicito: Optional o Maybe. Nei linguaggi con null-safety nel type system (TypeScript strict, Kotlin) basta il tipo nullable controllato (`T | undefined`, `T?`);
  - se è un errore, lancia un'eccezione;
  - per le collezioni, restituisci una collezione vuota.
  - Mai `null` come segnale implicito, non dichiarato dal tipo.

## Organizzazione del file
- **Prossimità**: il codice che collabora sta vicino. Vale per metodi che si chiamano tra loro, metodi che condividono gli stessi campi e varianti dello stesso comportamento.
- **Stepdown**: il metodo di alto livello sta in alto, i dettagli che chiama subito sotto.
- Separa con righe vuote i blocchi logici diversi.

## Commenti
- Spiegano il *perché* (decisioni, vincoli, workaround), mai il *come*: quello lo dice il codice.
- Un commento non aggiornato è peggio di nessun commento. Se modifichi il codice, aggiorna i commenti.
- In review verifica che i commenti dicano ancora il vero: parametri e valori di ritorno descritti, riferimenti a comportamenti o ticket che non esistono più, "temporaneo" vecchio di anni.
- `TODO`, `FIXME`, `HACK` sono debito: nel codice che scrivi solo con un riferimento (ticket o motivo); quelli esistenti si segnalano, non si risolvono fuori perimetro.
- **Scorciatoie volute**: una soluzione semplificata con un limite noto porta il commento `shortcut: <limite>, <quando rivedere>` (es. `// shortcut: carica tutto in memoria, rivedere oltre 10k righe`). Se il progetto traccia il debito con un suo marcatore (TODO con ticket, convenzione del team), usa quello, con le stesse due informazioni.
- Niente codice commentato: c'è git.

## Manutenzione
- **Boy Scout Rule**: lascia il codice che tocchi un po' più pulito (un nome migliore, codice morto rimosso). Fuori dal perimetro del compito: segnala, non modificare.
- **Analisi statica**: usa gli strumenti del progetto (Sonar o SonarQube for IDE, linter, type checker). Prima della PR correggi le segnalazioni nel codice che hai scritto.
