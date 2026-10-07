# Entity Framework Core

Da leggere quando scrivi o rivedi query, mapping, migrazioni o salvataggi. EF Core 10 richiede .NET 10; EF Core 8 e 9 su .NET 8/9. Controlla la versione del pacchetto e quella del provider.

## DbContext
- Un `DbContext` per richiesta (scoped), mai singleton né condiviso tra thread: non è thread-safe. Nei servizi singleton o nei `BackgroundService` usa `IDbContextFactory<T>` e un contesto per unità di lavoro.
- Non c'è bisogno di un "repository" sopra EF per forza: il `DbContext` è già unit of work e `DbSet` un repository. Un'astrazione serve se l'architettura la richiede (vedi `architettura-esagonale`), non per abitudine.
- Metodi `...Async` con il `CancellationToken` della richiesta.

## Tracking
- Il tracking è attivo di default: ogni entity letta è seguita e confrontata al `SaveChanges`. Nelle query di sola lettura `AsNoTracking()` (o `AsNoTrackingWithIdentityResolution()` se il grafo ha duplicati), oppure proiezione su DTO.
- **Proietta con `Select`** quello che serve invece di caricare entity intere: meno colonne, niente tracking, nessun rischio di esporre campi interni.
- Non tenere il contesto vivo a lungo: le entity tracciate si accumulano e le letture diventano stantie.

## N+1 e caricamento dei dati correlati
- N+1 nasce dal caricamento lazy o da una query dentro un ciclo. Il lazy loading (proxy) è disattivo di default: lasciarlo così.
- `Include`/`ThenInclude` per i casi veri; più `Include` di collezioni producono un prodotto cartesiano (esplosione di righe): valuta `AsSplitQuery()` (più query, ma coerenti dalla 10 per l'ordinamento) o, meglio, una proiezione.
- Verifica le query generate: log SQL in sviluppo (`LogTo`, `EnableSensitiveDataLogging` solo in locale) o `ToQueryString()`. Una query "plausibile" non è una query verificata.
- Paginazione sempre con un `OrderBy` deterministico (con tie-break sulla chiave) prima di `Skip`/`Take`.

## Traduzione LINQ
- Se EF non riesce a tradurre un'espressione lancia un'eccezione: non "risolvere" con `AsEnumerable()` o `ToList()` prima del filtro, che porta in memoria l'intera tabella. Riscrivi l'espressione o usa SQL.
- `Contains` su una collezione locale è tradotto in `IN`; da EF 10 ogni valore è un parametro separato (prima, JSON o costanti): occhio ai piani e alla dimensione delle liste.
- Da .NET 10 esistono `LeftJoin` e `RightJoin` in LINQ, riconosciuti da EF 10: sostituiscono il giro con `GroupJoin` e `DefaultIfEmpty`.
- Aggiornamenti e cancellazioni di massa con `ExecuteUpdateAsync`/`ExecuteDeleteAsync` (7+): non passano dal tracking né dai valori della `SaveChanges` (audit, concorrenza, eventi). Da EF 10 il lambda di `ExecuteUpdate` è un normale lambda, utile per aggiornamenti condizionali.
- Filtri globali (soft delete, multi-tenant): `IgnoreQueryFilters()` è un buco da tenere d'occhio in review. Da EF 10 i filtri hanno un nome e si disattivano singolarmente.

## SQL raw: sempre parametrizzato
- `FromSql($"...{valore}")`, `SqlQuery<T>($"...")` e `ExecuteSql($"...")` (EF 7+; `SqlQuery` su tipi non mappati dalla 8) trasformano l'interpolazione in parametri: sono sicuri.
- `FromSqlRaw`, `SqlQueryRaw` e `ExecuteSqlRaw` con stringhe concatenate o interpolate con `$` **non** parametrizzano: SQL injection. Si usano solo per parti dinamiche non parametrizzabili (nomi di colonna) provenienti da una lista bianca, con i valori passati come `DbParameter`. Da EF 10 un analyzer segnala la concatenazione.
- Mai costruire a mano con `string.Format` o `+` un SQL con input esterno. `FromSql` si compone con LINQ solo se il SQL è una `SELECT` componibile (niente `;` finale, niente stored procedure con ulteriori operatori).

## Migrazioni
- Una migrazione per modifica, nel repository, riletta prima del commit: l'SQL generato (`dotnet ef migrations script`) va guardato, soprattutto per rename (EF può generare drop+create e perdere dati), colonne non nullable su tabelle piene, indici su tabelle grandi.
- Mai modificare una migrazione già applicata in altri ambienti: se ne aggiunge una nuova.
- In produzione: script SQL idempotenti (`--idempotent`) o un bundle (`dotnet ef migrations bundle`) eseguiti dalla pipeline, non `Database.Migrate()` all'avvio dell'app con più istanze.
- Con più sviluppatori, i conflitti sullo snapshot del modello si risolvono rigenerando, non fondendo a mano.
- Cambi distruttivi in due fasi (aggiungi e riempi, poi rimuovi) per non rompere le versioni in esecuzione durante il rilascio.

## Concorrenza
- Concorrenza ottimistica con un token: `[Timestamp]`/`rowversion` (SQL Server) o una colonna di versione/`xmin` (PostgreSQL). Un `DbUpdateConcurrencyException` va gestito: rileggere e riprovare o restituire 409, mai ignorarlo.
- Transazioni: un `SaveChanges` è già atomico. Per più unità di lavoro `BeginTransactionAsync`, con `await using`; con una `ExecutionStrategy` di retry le transazioni manuali vanno racchiuse in `strategy.ExecuteAsync`.
- Operazioni "leggi, decidi, scrivi" fuori da una transazione o da un token di concorrenza sono una race: l'unicità si garantisce con un indice univoco, non con un controllo prima dell'insert.

## Modello
- Configurazione con `IEntityTypeConfiguration<T>` per entity, non attributi e `OnModelCreating` enormi, salvo convenzione diversa del progetto.
- Lunghezze, precisione dei `decimal` (denaro: tipo con precisione e scala esplicite) e nullabilità dichiarate: i default (`nvarchar(max)`) raramente sono quelli voluti.
- Value object e tipi con sotto-struttura: complex type (dalla 8, JSON e opzionali dalla 10) invece delle owned entity, che hanno ancora identità e semantica per riferimento.
- Enum salvati come stringa se il database è letto da altri; come intero solo con valori stabili e documentati.
- Dati sensibili: i valori dei parametri non vanno nei log (`EnableSensitiveDataLogging` spento fuori da sviluppo).
