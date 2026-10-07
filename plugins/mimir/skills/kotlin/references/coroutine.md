# Coroutine e Flow

Da leggere quando il codice usa `suspend`, `launch`, `async`, `Flow` o `Channel`. Presuppone `kotlinx.coroutines`: se il progetto usa un'altra libreria (Reactor, RxJava), restano le sue convenzioni.

## Structured concurrency
- Ogni coroutine vive in uno scope che ne controlla il ciclo di vita: se lo scope termina o fallisce, i figli vengono cancellati. Il lavoro asincrono si avvia dentro uno scope con un proprietario chiaro.
- **Niente `GlobalScope`**: nessun proprietario, nessuna cancellazione, errori persi. Lo scope è quello del framework (`viewModelScope`, scope della richiesta in Ktor/Spring) o uno creato e chiuso da te (`CoroutineScope(SupervisorJob() + dispatcher)` con `cancel()` allo shutdown).
- Parallelismo con `coroutineScope { val a = async { … }; val b = async { … }; a.await() to b.await() }`: se una fallisce, l'altra viene cancellata e l'eccezione arriva a chi chiama. `supervisorScope` quando i fallimenti sono indipendenti.
- Una funzione `suspend` non deve lanciare lavoro che sopravvive al suo ritorno: o attende, o riceve uno scope esplicito come parametro (o come ricevente).
- `launch` per effetti collaterali (le eccezioni non gestite arrivano al gestore dello scope), `async` solo se poi chiami `await`. Un `async` mai atteso nasconde l'errore fino a quel punto.

## Dispatcher
- `Dispatchers.Default` per CPU, `Dispatchers.IO` per I/O bloccante (JDBC, file, client sincroni), `Main` per la UI. Per codice già non bloccante (client HTTP async, driver R2DBC) non serve `IO`.
- Una funzione `suspend` pubblica deve essere **main-safe**: chi la chiama non deve sapere su quale thread girare. Lo spostamento si fa dentro (`withContext(Dispatchers.IO)`), non con regole per i chiamanti.
- Dispatcher iniettabile (parametro o classe) per i test; non scrivere `Dispatchers.IO` fisso nel cuore del codice.
- Bloccare un thread di `Default` con chiamate sincrone (`Thread.sleep`, `runBlocking`, JDBC) lo toglie agli altri: usa `IO` o un dispatcher dedicato (`limitedParallelism`).
- `runBlocking` solo ai confini sincroni (`main`, test semplici): mai dentro una coroutine.
- Con i virtual thread della JVM (21+) valuta se servono ancora coroutine: dipende dal progetto, non sostituire per moda.

## Cancellazione
- La cancellazione è cooperativa: il codice di calcolo lungo controlla `isActive`/`ensureActive()` o chiama funzioni `suspend` cancellabili. Un ciclo stretto senza punti di sospensione non si ferma.
- **Non inghiottire `CancellationException`**: un `catch (e: Exception)` o un `runCatching` dentro una coroutine la cattura e la coroutine continua a vivere da cancellata. Rilancia sempre `CancellationException` (`catch (e: CancellationException) { throw e }` prima del catch generico).
- Pulizia in `try { … } finally { … }`; se la pulizia stessa sospende, `withContext(NonCancellable) { … }` in quel blocco, e solo lì.
- Timeout con `withTimeout`/`withTimeoutOrNull` per le chiamate esterne.
- Lo stato condiviso tra coroutine segue le regole della concorrenza di sempre: `Mutex`, `AtomicReference`, strutture concorrenti, o meglio un solo proprietario dello stato (confinamento a un dispatcher o a un canale).

## Flow
- `Flow` per sequenze asincrone di valori; è *freddo*: ogni `collect` riavvia il produttore. `StateFlow` per uno stato osservabile (ha sempre un valore, confronta per uguaglianza), `SharedFlow` per eventi.
- Operatori nel produttore, `collect` solo nel consumatore finale. Il contesto si cambia con `flowOn` (a monte), mai con `withContext` dentro `flow { }` (viola la trasparenza del contesto e lancia un'eccezione).
- Gestione errori con `catch { }` (a monte) e `onCompletion`; `try/catch` attorno al `collect` cattura anche gli errori del consumatore.
- Backpressure: `buffer`, `conflate`, `collectLatest` in base a cosa può perdere il consumatore. Scegli consapevolmente, non lasciare il default per caso.
- `stateIn`/`shareIn` con `SharingStarted.WhileSubscribed(…)` per condividere un flusso freddo senza lasciarlo vivo senza ascoltatori.
- Non raccogliere un `Flow` infinito in un `launch` senza scope che lo cancelli.
- Non esporre `MutableStateFlow` dal tipo pubblico: espone `StateFlow` (`asStateFlow()`).

## Test
- `runTest` con `StandardTestDispatcher`/`UnconfinedTestDispatcher`: il tempo è virtuale, `delay` non attende davvero (`advanceTimeBy`, `advanceUntilIdle`). Passa il dispatcher di test al codice sotto test.
- Per i `Flow` verifica la sequenza completa degli elementi (`toList()` su un flusso finito, oppure la libreria Turbine se già nel progetto).
- Un test che passa solo con `Thread.sleep` o `delay` reali è fragile: rendi il tempo iniettabile.
- Cancellazione e timeout si testano: avvia, cancella, verifica che la pulizia sia avvenuta.
