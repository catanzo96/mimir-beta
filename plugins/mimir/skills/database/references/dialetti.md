# Differenze tra dialetti SQL

Le differenze che più spesso rompono una query o uno schema portati da un motore all'altro. Per le versioni specifiche controlla la documentazione ufficiale del motore in uso: le funzioni nuove arrivano nelle versioni recenti.

## Panoramica

| Tema | PostgreSQL | Oracle | MySQL / MariaDB | SQL Server |
|---|---|---|---|---|
| Chiave autogenerata | `GENERATED ... AS IDENTITY` (anche `serial`, legacy) | Sequenze; `IDENTITY` nelle versioni recenti; nelle vecchie sequenza + trigger | `AUTO_INCREMENT` | `IDENTITY(1,1)`, sequenze |
| Limite righe | `LIMIT n OFFSET m` | `FETCH FIRST n ROWS ONLY` e `OFFSET` nelle versioni recenti; prima `ROWNUM` | `LIMIT n OFFSET m` | `OFFSET m ROWS FETCH NEXT n ROWS ONLY` (richiede `ORDER BY`), oppure `TOP n` |
| Upsert | `INSERT ... ON CONFLICT DO UPDATE` | `MERGE` | `INSERT ... ON DUPLICATE KEY UPDATE` | `MERGE` (con insidie di concorrenza: usa `HOLDLOCK`) |
| Stringa vuota | Distinta da `NULL` | **Uguale a `NULL`** | Distinta da `NULL` | Distinta da `NULL` |
| Booleano | `BOOLEAN` | Fino alla 21c nessun tipo SQL: `NUMBER(1)` o `CHAR(1)`; `BOOLEAN` dalla 23ai | `BOOLEAN` è alias di `TINYINT(1)` | `BIT` |
| Concatenazione | `\|\|`, `concat()` | `\|\|` | `CONCAT()` (`\|\|` è OR, salvo modalità) | `+`, `CONCAT()` |
| Maiuscole nei confronti | Sensibile | Sensibile | Dipende dalla collation (spesso insensibile) | Dipende dalla collation (spesso insensibile) |
| Identificatori | Minuscolo se non tra virgolette | Maiuscolo se non tra virgolette | Dipende dal filesystem | Segue la collation |
| DDL transazionale | Sì | No (commit implicito) | No (commit implicito) | Sì |

## Tipi data e ora
- **PostgreSQL**: `timestamp` (senza fuso) e `timestamptz` (istante, normalizzato in UTC e mostrato nel fuso della sessione). Per gli istanti usa `timestamptz`.
- **Oracle**: `DATE` contiene anche l'ora (al secondo). `TIMESTAMP`, `TIMESTAMP WITH TIME ZONE`, `TIMESTAMP WITH LOCAL TIME ZONE`. `SYSDATE` è l'ora del server, `SYSTIMESTAMP` ha frazioni e fuso. La sottrazione di date dà giorni (frazionari). Il formato dipende da `NLS_DATE_FORMAT`: non fare affidamento sulle conversioni implicite, usa `TO_DATE` e `TO_TIMESTAMP` con formato, o i letterali `DATE '2026-03-01'`.
- **MySQL/MariaDB**: `DATETIME` non converte il fuso; `TIMESTAMP` sì (UTC internamente) e ha limiti di intervallo. Precisione frazionaria da dichiarare (`DATETIME(6)`). Date non valide come `0000-00-00` possono passare in modalità permissive: verifica `sql_mode`.
- **SQL Server**: preferisci `datetime2` a `datetime` (precisione e intervallo); `datetimeoffset` per istanti con offset. L'arrotondamento di `datetime` a 3 ms sorprende nei confronti di fine intervallo.

## Stringa vuota e NULL (Oracle)
In Oracle `''` è `NULL`. Conseguenze: `WHERE colonna = ''` non trova mai nulla, `colonna IS NULL` trova anche le "stringhe vuote", un `NOT NULL` rifiuta la stringa vuota, e la concatenazione con `NULL` si comporta come con la stringa vuota. Quando porti codice o dati da o verso Oracle, tratta i due valori in modo esplicito. Con JDBC o ORM: un campo vuoto letto torna `null`.

## Case sensitivity e collation
- PostgreSQL e Oracle confrontano in modo sensibile alle maiuscole: per l'insensibile usa `LOWER()` su entrambi i lati con indice su espressione (o `citext` / confronto linguistico in Oracle).
- MySQL e SQL Server con collation tipiche (`_ci`) sono insensibili anche su `UNIQUE`: `'Rossi'` e `'rossi'` collidono. Verifica la collation dello schema e delle colonne prima di migrare.
- Accenti e ordinamento cambiano con la collation: l'`ORDER BY` su testo non è lo stesso tra motori.

## Sequenze e identity
- Le sequenze non sono senza buchi: rollback e cache le lasciano. Non usarle come numerazione fiscale continua: per quella serve una tabella contatore con lock.
- PostgreSQL e Oracle: prelevare il valore con `RETURNING` (PostgreSQL) o `RETURNING INTO` (Oracle); MySQL: `LAST_INSERT_ID()`; SQL Server: `OUTPUT` o `SCOPE_IDENTITY()` (non `@@IDENTITY`, che può restituire un valore generato da un trigger).
- In Oracle una colonna `IDENTITY` o una sequenza di default non popola i dati già inseriti con valori espliciti: allinea la sequenza dopo gli import.
- InnoDB può lasciare buchi anche con `INSERT ... ON DUPLICATE KEY`.

## Upsert
- PostgreSQL `ON CONFLICT (colonne) DO UPDATE SET x = EXCLUDED.x`: richiede un vincolo o indice univoco sulle colonne indicate.
- MySQL `ON DUPLICATE KEY UPDATE`: scatta su qualunque chiave univoca, non solo sulla primaria.
- `MERGE` (Oracle, SQL Server): su SQL Server, in concorrenza, può dare violazioni di chiave; usa gli hint di lock o preferisci `UPDATE` poi `INSERT` in transazione.

## Paginazione e limiti
- Oracle: le versioni vecchie richiedono la query annidata con `ROWNUM`, e `ROWNUM` si applica prima dell'`ORDER BY` se non annidi.
- SQL Server: `OFFSET/FETCH` esige `ORDER BY`; `TOP` con `ORDER BY` è il vecchio stile.
- Oracle limita a 1000 elementi una lista `IN (...)` e storicamente identificatori a 30 caratteri (più lunghi nelle versioni recenti, ma verifica).

## Altro da ricordare
- **Booleani nei driver**: l'ORM mappa in modo diverso (`NUMBER(1)`, `CHAR`, `bit`): controlla il mapping quando cambi motore.
- **`GROUP BY`**: MySQL in modalità permissiva accetta colonne non aggregate; gli altri no. Non scrivere query che dipendono da questo.
- **Commit implicito**: in Oracle e MySQL il DDL chiude la transazione, quindi una migrazione con più DDL non è atomica. Pianificala di conseguenza.
- **Locking in lettura**: PostgreSQL e Oracle leggono senza bloccare gli scrittori (MVCC); SQL Server in `READ COMMITTED` di default può bloccare le letture, a meno di attivare lo snapshot per la lettura.
- Testa sul motore di destinazione: un dialetto "compatibile" (H2 in modalità Oracle o PostgreSQL) non garantisce gli stessi risultati.
