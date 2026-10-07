---
name: database
description: "Modellare e ottimizzare database relazionali: schema, indici, transazioni, SQL. Usala quando scrivi SQL o migrazioni o rivedi query lente, o con Flyway e Liquibase."
---

# Database

Si applica insieme a `clean-code` (sicurezza compresa). Per JPA e Spring: `spring-boot/references/jpa.md`. Per far uscire le migrazioni nei rilasci: `rilascio` (se disponibile). Prevalgono motore, versione e convenzioni del progetto: prima di scrivere SQL capisci quale DBMS è in uso (differenze in `references/dialetti.md`).

## Modellazione
- Una **chiave primaria** per ogni tabella, stabile e senza significato di business. Le chiavi naturali (codice fiscale, codice prodotto) restano come vincolo `UNIQUE`: cambiano più spesso di quanto si pensi.
- **Vincoli nel database**, non solo nel codice: `NOT NULL`, `UNIQUE`, `CHECK`, chiavi esterne. Il codice dell'applicazione ha bug e ci sono altri scrittori (script, altre app, correzioni manuali); il DB è l'ultimo difensore.
- Una colonna `NULL` significa "sconosciuto o non applicabile". Se significa un terzo stato, usa un tipo esplicito.
- **Normalizza fino alla terza forma** come default: un fatto in un solo posto. **Denormalizza** solo con una misura (una query letta troppo spesso o troppo costosa), sapendo chi mantiene la copia allineata (trigger, job, applicazione) e cosa succede se diverge. Alternative prima di duplicare: vista, vista materializzata, indice coprente.
- Tipi giusti: date come tipo data, importi come `DECIMAL` con scala esplicita (mai `FLOAT`), booleani come tipo booleano o `CHAR(1)` con `CHECK`. Una stringa che contiene un elenco separato da virgole è quasi sempre una tabella mancante.
- Chiavi esterne con `ON DELETE` pensato: la cascata automatica su dati di business è raramente ciò che vuoi.
- Soft delete (`cancellato_il`) complica ogni query e ogni indice `UNIQUE`: usalo solo con un motivo (audit, ripristino) e valuta una tabella di storico.

## Indici
- Un indice rende più veloce la lettura e più lenta ogni scrittura: crealo per una query reale, non per precauzione.
- **Composti**: l'ordine conta. L'indice `(a, b, c)` serve filtri su `a`, su `a,b`, su `a,b,c`, non su `b` da solo. Prima le colonne con uguaglianza, poi quella con range o ordinamento. Se l'indice rispetta anche l'`ORDER BY`, il DB evita l'ordinamento.
- **Coprenti**: se tutte le colonne richieste stanno nell'indice (colonne incluse, `INCLUDE`), il DB non legge la tabella.
- **Chiavi esterne**: indicizzale (non sempre automatico) o i join e le cancellazioni dal padre scandiscono la tabella figlia.
- **Quando non servono o non vengono usati**:
  - tabelle piccole;
  - colonne a bassissima selettività (un booleano su metà delle righe);
  - funzione sulla colonna nel filtro (`WHERE UPPER(nome) = ...`, `WHERE DATE(creato) = ...`), salvo indice su espressione;
  - `LIKE '%testo'` con carattere jolly iniziale;
  - conversione implicita di tipo (colonna testo confrontata con un numero);
  - statistiche vecchie.
- Indici parziali o filtrati per i sottoinsiemi piccoli (solo le righe attive), dove il motore li offre.
- Gli indici inutilizzati e duplicati si trovano con le viste di statistiche del DBMS: rimuovili con prudenza, dopo un periodo di osservazione che includa i batch di fine mese.

## Leggere un piano di esecuzione
Usa il piano **reale** (`EXPLAIN ANALYZE`, piano effettivo in SQL Server, `DBMS_XPLAN` con statistiche in Oracle): il piano stimato mente quando le statistiche sono vecchie. Attenzione: `EXPLAIN ANALYZE` esegue la query, anche se modifica dati; mettila in una transazione che poi annulli, e non su produzione senza motivo.
- Confronta righe **stimate** e **reali**: scarti di ordini di grandezza spiegano quasi sempre il piano sbagliato (statistiche, correlazione tra colonne, parametri).
- Cerca i nodi dove va il tempo e le righe lette scartate dal filtro: sono il segnale di un indice mancante o inadatto.
- Scansione completa non è per forza un male (tabella piccola, o si legge buona parte dei dati). Lo è se legge milioni di righe per restituirne poche.
- Join: nested loop va bene con poche righe esterne e indice sull'interna; hash o merge con molte righe. Un nested loop su molte righe senza indice è il classico incidente.
- Ordinamenti e aggregazioni su disco (spill) indicano memoria insufficiente o una query da riscrivere.
- Confronta sempre prima e dopo, con dati di volume realistico: su una tabella di test da 100 righe ogni piano è buono.

## Transazioni e isolamento
- Transazione = unità di lavoro corta. Niente chiamate esterne o attese dell'utente mentre è aperta.
- Livelli e anomalie (il comportamento esatto varia col motore: verifica nella documentazione):

| Livello | Dirty read | Non-repeatable read | Phantom | Note |
|---|---|---|---|---|
| Read uncommitted | possibile | possibile | possibile | Quasi mai voluto |
| Read committed | no | possibile | possibile | Default di PostgreSQL, Oracle, SQL Server |
| Repeatable read | no | no | dipende | Default di MySQL/InnoDB; in PostgreSQL è snapshot |
| Serializable | no | no | no | Richiede di ritentare le transazioni abortite |

- **Aggiornamento perso** (leggi, calcola, scrivi): si evita con `UPDATE ... SET saldo = saldo - :x`, con lock pessimistico (`SELECT ... FOR UPDATE`), o con una colonna di versione e controllo `WHERE versione = :v` (ottimistico).
- Controllo "se non esiste, inserisci" non è sicuro senza un vincolo `UNIQUE`: usa il vincolo e gestisci la violazione, oppure l'upsert del dialetto.
- **Lock e deadlock**: acquisisci i lock sempre nello stesso ordine (per id crescente), tieni le transazioni brevi, gestisci l'errore di deadlock con un retry limitato. Per le code di lavori usa `FOR UPDATE SKIP LOCKED` dove esiste.
- Un aggiornamento in blocco lungo mantiene lock e riempie i log: spezzalo in lotti con commit intermedi, se la logica lo permette.
- Il default dell'ORM può non essere quello che pensi: leggi livello di isolamento e modalità di commit della connessione.

## Paginazione
- `LIMIT/OFFSET` legge e scarta le righe saltate: lento e instabile oltre le prime pagine.
- **Paginazione per chiave** (keyset): `WHERE (creato, id) > (:ultimo_creato, :ultimo_id) ORDER BY creato, id LIMIT :n`, con un indice su quelle colonne. Serve un ordinamento deterministico: aggiungi sempre un campo univoco. Il confronto tra tuple e `LIMIT` non esistono in tutti i dialetti (Oracle, SQL Server): lì si scrive `creato > :c OR (creato = :c AND id > :i)` con la sintassi di limite del database (`references/dialetti.md`).
- Mai `ORDER BY` assente con `LIMIT`: l'ordine non è definito.

## NULL e trappole SQL
- `x = NULL` non è mai vero: usa `IS NULL`. `NULL = NULL` è sconosciuto, non vero.
- **`NOT IN` con una sottoquery che contiene un `NULL` non restituisce righe**. Usa `NOT EXISTS`.
- Aggregati: `COUNT(colonna)` ignora i `NULL`, `COUNT(*)` no; `SUM` di soli `NULL` è `NULL`, non 0 (`COALESCE`).
- `LEFT JOIN` con il filtro sulla tabella di destra nel `WHERE` diventa un `INNER JOIN`: il filtro va nella `ON`.
- Join che moltiplicano le righe (uno-a-molti) falsano `SUM` e `COUNT`: aggrega prima, poi unisci.
- **Date e fusi**: intervalli semiaperti (`creato >= :da AND creato < :a`), mai `BETWEEN` su timestamp né `DATE(colonna) = ...` (spegne l'indice). Salva gli istanti in UTC, decidi il fuso a livello di presentazione. Attenzione al tipo: `timestamp` senza fuso e con fuso hanno semantiche diverse.
- Confronto tra stringhe: collation e maiuscole/minuscole dipendono dal motore (`dialetti.md`).

## Query sicure
- **Sempre parametri** (prepared statement): mai concatenare input nell'SQL. Per i nomi di colonna o l'ordinamento scelti dall'utente usa una lista bianca, perché i parametri non valgono per gli identificatori.
- `LIKE` con input utente: gestisci i caratteri jolly (`%`, `_`) con escape.
- Utente applicativo con i soli permessi necessari: niente DDL, niente accesso ad altri schemi. Dati sensibili cifrati o mascherati e mai nei log delle query.
- Un `UPDATE` o `DELETE` senza `WHERE` è l'errore più costoso: scrivilo prima con `SELECT`, controlla il numero di righe e fallo in transazione.

## Migrazioni dello schema
- Strumento del progetto (Flyway, Liquibase, altro). Una migrazione già applicata altrove non si modifica: se ne scrive una nuova.
- **Compatibilità tra versioni**: durante il rilascio convivono il codice vecchio e lo schema nuovo (o viceversa). Procedi per passi: aggiungi (colonna nullable o con default) → rilascia il codice che la usa → riempi i dati → imposta `NOT NULL` → rimuovi il vecchio in un rilascio successivo. Rinominare o cambiare tipo in un solo passo rompe uno dei due lati.
- Operazioni che bloccano la tabella (aggiungere un indice o una colonna con default su tabelle grandi, a seconda del motore): verifica la modalità non bloccante (`CONCURRENTLY`, `ONLINE`) e il tempo su un volume reale.
- Prevedi come tornare indietro; per i dati cancellati il rollback è un backup, non uno script.
- Dati di riferimento e backfill grandi: script separato, a lotti, riavviabile.

## Quando serve altro che SQL relazionale
Il relazionale è il default; scegli altro solo con un bisogno misurato. Quando e trappole di documentale, chiave-valore, colonnare e Redis: `references/nosql-redis.md`.

## Riferimenti
| File | Quando leggerlo |
|---|---|
| [references/dialetti.md](references/dialetti.md) | Scrivi SQL per PostgreSQL, Oracle, MySQL/MariaDB o SQL Server, o porti una query tra motori |
| [references/nosql-redis.md](references/nosql-redis.md) | Valuti o usi NoSQL, cache o Redis |

## Verifica
- Esegui le migrazioni su un database vuoto e su uno con dati realistici, con lo strumento del progetto (es. `./mvnw flyway:migrate`, con `-o` nella sandbox se le dipendenze sono già nella cache locale; `liquibase update`), su un ambiente locale o di test, mai su produzione senza ok.
- Lancia i test di integrazione sul DBMS vero (Testcontainers o ambiente del progetto) quando il dialetto conta: H2 non garantisce lo stesso comportamento.
- Per ogni query nuova o modificata su tabelle grandi, leggi il piano reale e riporta il confronto prima/dopo.
- Prima di consegnare, rileggi che nessuna migrazione già rilasciata sia stata modificata e che i comandi di sola lettura siano separati da quelli che scrivono.
