---
name: csharp-dotnet
description: Best practice C# e .NET. Usala quando scrivi, modifichi o rivedi codice C# (.cs), o in progetti con .csproj, .sln, global.json o Directory.Build.props.
---

# C# e .NET

Si applica insieme a `clean-code`. Le convenzioni del progetto (`.editorconfig`, analyzer, `LangVersion`, `TargetFramework`) prevalgono: non usare feature non disponibili nella versione in uso. Per ASP.NET Core vedi `references/aspnet-core.md`, per Entity Framework `references/ef-core.md`.

## Prima di tutto: la versione
Leggi `TargetFramework` e `LangVersion` nel `.csproj` (o in `Directory.Build.props`) e `global.json`. Ogni versione di C# esce con una versione di .NET e ne è il default.
- **.NET 10** (C# 14) è l'LTS corrente, supportato fino a novembre 2028. **.NET 8** (C# 12) è LTS e **.NET 9** (C# 13) è STS: entrambi finiscono il supporto il 10 novembre 2026. Su un progetto più vecchio, o su .NET Framework, vale `manutenzione-legacy` (se disponibile).
- C# 8: nullable reference types, `await foreach`, `IAsyncDisposable`, indici e range. C# 9: `record`, `init`, pattern relazionali e logici (`is not null`). C# 10: file-scoped namespace, `record struct`. C# 11: `required`, raw string literal, list pattern.
- C# 12 (.NET 8): costruttori primari su ogni classe e struct, **collection expression** (`[1, 2, ..altri]`).
- C# 13 (.NET 9): `params` su collezioni e `Span`, tipo `System.Threading.Lock` per `lock`.
- C# 14 (.NET 10): parola chiave `field` nelle proprietà, extension member, assegnazione null-conditional (`a?.B = x`).

## Nullabilità
- `<Nullable>enable</Nullable>` sempre nel codice nuovo. Un warning di nullabilità si risolve nel tipo o nel flusso, non con `!`: il suppressor è una promessa non verificata.
- `required` per le proprietà obbligatorie degli oggetti inizializzati, invece di un costruttore con dieci parametri.
- Assenza di valore esplicita nel tipo (`Cliente?`), mai un `null` che il tipo non dichiara. Collezioni vuote, mai `null`.
- Ai confini (JSON, DB, librerie non annotate) valida subito: un DTO deserializzato può avere `null` anche dove il tipo dice di no.

## Tipi e sintassi moderna
- `record` per valori immutabili e DTO (uguaglianza per valore, `with`). Non per le entity con identità o stato mutabile: l'uguaglianza per valore sorprende con EF e con le collezioni.
- `record struct` o `readonly struct` solo per tipi piccoli e misurati. Altrimenti classe.
- Costruttore primario: i parametri sono catturati, non sono campi `readonly`. Se li modifichi per errore, nessun avviso. Per i servizi con DI è comodo; se un parametro serve in più punti, valuta un campo esplicito.
- Pattern matching e `switch` expression per trasformare per tipo o per forma. Il compilatore avvisa dei casi mancanti su enum, `bool` e tuple, ma non sulle gerarchie di classi (anche `sealed`): lì aggiungi un ramo `_` che lancia un'eccezione.
- `sealed` di default sulle classi non pensate per l'ereditarietà.
- Collection expression al posto di `new List<T> { }` e `Array.Empty<T>()` quando la versione lo permette.
- Enum: valida l'input esterno con `Enum.IsDefined`, perché `(StatoOrdine)99` compila e vive.

## Async
- `async`/`await` fino in fondo. **Mai `.Result`, `.Wait()` o `.GetAwaiter().GetResult()`** su codice async: deadlock con un contesto di sincronizzazione e thread del pool bloccati sotto carico.
- Nomi con suffisso `Async`; ritorna `Task`/`ValueTask`, mai `async void` (solo per gli event handler).
- `CancellationToken` come ultimo parametro, propagato fino all'I/O. In ASP.NET Core arriva dalla richiesta.
- `ConfigureAwait(false)`: nelle **librerie** sì; nel codice applicativo ASP.NET Core non serve (non c'è contesto di sincronizzazione), in UI (WPF, WinForms, MAUI) serve il contesto, quindi no.
- Parallelismo con `Task.WhenAll` su operazioni indipendenti. `Task.Run` non rende async un I/O: serve solo per spostare lavoro CPU fuori da un thread da non bloccare.
- Fire and forget: mai una `Task` ignorata (le eccezioni si perdono). Usa un `BackgroundService` o una coda, con log degli errori.
- Il tempo da `TimeProvider` iniettato (.NET 8+), non da `DateTime.UtcNow` sparsi: i test lo controllano.

## Risorse
- `using` declaration per `IDisposable`, `await using` per `IAsyncDisposable`. Una classe che implementa solo `IAsyncDisposable` non può essere smaltita da un consumatore sincrono (`using` senza `await`): implementa anche `IDisposable` quando può servire.
- `HttpClient` mai creato per chiamata né singleton nudo: `IHttpClientFactory` o client tipizzato.
- Gli oggetti creati dal container DI li smaltisce il container: non chiamare `Dispose` su un servizio iniettato.

## LINQ
- L'esecuzione è differita: una query enumerata due volte gira due volte (e su EF fa due query). Materializza con `ToList()` quando serve un risultato stabile.
- Mai `Count() > 0` su `IEnumerable`: `Any()`. Mai `First()` dove l'assenza è un caso reale: `FirstOrDefault()` e gestisci il caso, o `Single()` se l'unicità è un invariante.
- Su `IQueryable` (EF) ciò che scrivi diventa SQL: niente metodi propri nel `Where`, e la query resta `IQueryable` fino alla fine. Dettagli in `references/ef-core.md`.
- Una `foreach` con effetti collaterali non diventa un `Select`: LINQ per trasformare, non per eseguire.

## Dependency injection
- Lifetime: `Transient`, `Scoped` (una per richiesta), `Singleton`. **Un singleton non deve dipendere da uno scoped** (lo cattura: stato condiviso, `DbContext` usato da più thread). Se serve, il singleton riceve `IServiceScopeFactory` e crea uno scope. Attiva `ValidateScopes` e `ValidateOnBuild` anche fuori da Development se il progetto lo consente.
- Solo injection da costruttore. Niente service locator (`IServiceProvider` iniettato per risolvere a mano) fuori da factory o composition root.
- Registrazioni raggruppate in metodi di estensione per feature (`AddOrdini()`), non un unico `Program.cs` di 300 righe.

## Configurazione, logging, errori
- **Options pattern**: classe tipizzata + `AddOptions<T>().BindConfiguration("Sezione").ValidateDataAnnotations().ValidateOnStart()`, così un valore mancante ferma l'avvio. `IOptions<T>` per valori fissi, `IOptionsSnapshot<T>` (scoped) o `IOptionsMonitor<T>` se devono cambiare a runtime.
- Segreti mai in `appsettings.json` versionato: user secrets in sviluppo, variabili d'ambiente o secret manager in produzione.
- Logging con `ILogger<T>` e template con segnaposto (`_logger.LogInformation("Ordine {Id}", id)`), mai interpolazione di stringhe. Per i percorsi caldi `LoggerMessage`/`[LoggerMessage]`. Non loggare dati sensibili.
- Eccezioni: `throw;` e non `throw ex;` (perde lo stack). Cattura tipi specifici, mai `catch (Exception)` che inghiotte. Gestione centralizzata ai confini (vedi ASP.NET Core).
- `ArgumentNullException.ThrowIfNull` e simili per i guard clause.

## Test
- Il framework del progetto (xUnit, NUnit o MSTest): non mescolarli. Nomi che descrivono il comportamento; un solo motivo di fallimento per test.
- Asserzioni con la libreria già in uso (FluentAssertions, Shouldly, quelle native): non aggiungerne una nuova senza ok. Doppi con NSubstitute o Moq, secondo il progetto.
- Integrazione ASP.NET Core con `WebApplicationFactory<Program>`; con database reali, Testcontainers se già presente, non l'in-memory di EF (non ha vincoli, transazioni né SQL reale).
- Test async: `async Task`, mai `async void`; niente `Thread.Sleep`.

## Verifica
Prima di dichiarare finito, sul codice che hai scritto:
- `dotnet build` senza warning nuovi (se `TreatWarningsAsErrors` è attivo, passa per forza).
- `dotnet test` (un progetto o un filtro mirato mentre lavori, la suite intera alla fine).
- `dotnet format --verify-no-changes` solo se il progetto lo usa, e senza riformattare file che non hai toccato. Analyzer (Roslyn, Sonar) puliti.
- Nuovi pacchetti NuGet solo con l'ok dell'utente; `dotnet list package --vulnerable` se aggiorni dipendenze.
