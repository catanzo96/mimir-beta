---
name: cpp
description: Best practice C++ moderno (17/20/23). Usala quando scrivi, modifichi o rivedi codice C++ (anche una nota sul C), o in progetti con CMakeLists.txt, .cpp o .hpp.
---

# C++

Si applica insieme a `clean-code`. Le convenzioni del progetto (standard del linguaggio, compilatore, stile, librerie, eccezioni sì o no) prevalgono. Su codebase pre-C++11 o con gestione manuale della memoria vale `manutenzione-legacy` (se disponibile): migra solo ciò che tocchi.

## Prima di tutto: la versione e il compilatore
Leggi `CMAKE_CXX_STANDARD` o `target_compile_features` in `CMakeLists.txt`, i flag di build e il compilatore in CI. Il supporto reale dipende anche dalla libreria standard (libstdc++, libc++, MSVC STL): una feature dichiarata dallo standard può mancare. Verifica compilando, non per memoria.

| Standard | Feature utili |
|---|---|
| C++11/14 | `auto`, lambda, `unique_ptr`/`shared_ptr`, move, `constexpr`, `make_unique` (14) |
| C++17 | `std::string_view`, `std::optional`, `std::variant`, structured binding, `if` con inizializzatore, `[[nodiscard]]`, `std::filesystem`, `if constexpr`, CTAD |
| C++20 | concept e `requires`, `std::span`, `std::jthread` e `stop_token`, ranges, `<=>`, `consteval`, `std::format`, moduli (supporto di toolchain ancora disomogeneo) |
| C++23 | `std::expected`, `std::print`, `std::optional` monadico (`and_then`), `std::flat_map`, `deducing this`, `std::unreachable` |

Se la libreria del progetto non ha `std::expected`, esistono implementazioni di terze parti con la stessa interfaccia: non aggiungerle senza ok.

## Proprietà e risorse (RAII)
- Ogni risorsa (memoria, file, socket, lock, handle) ha un proprietario: un oggetto il cui distruttore la rilascia. Niente `new`/`delete`, `fopen`/`fclose` o `lock()`/`unlock()` a mano nel codice applicativo.
- **Valori prima dei puntatori**: un membro o una variabile locale per valore è più semplice e più veloce di qualsiasi puntatore. Il contenitore standard (`std::vector`, `std::string`) prima di un array a mano.
- `std::unique_ptr` è il default per la proprietà singola; si crea con `std::make_unique`. `std::shared_ptr` solo con proprietà davvero condivisa e di durata non determinabile: costa (contatore atomico) e nasconde il design. I cicli di `shared_ptr` perdono memoria: rompili con `weak_ptr`.
- Parametri: una funzione che usa un oggetto senza possederlo prende `T&` o `const T&`, non uno smart pointer. `unique_ptr<T>` per valore dice "ti cedo la proprietà"; `shared_ptr` per valore solo se la funzione deve condividerla.
- Puntatore grezzo o riferimento = non proprietario, mai da liberare. Per le API C con handle usa un `unique_ptr` con deleter personalizzato.
- Costruttori che acquisiscono tutto o falliscono (eccezione o factory): niente oggetti a metà inizializzati con un `init()` da chiamare dopo.
- `noexcept` su move e `swap`: se un move può lanciare, `std::vector` ricade sulla copia.

## Regola dello zero e dei cinque
- **Zero**: se i membri gestiscono già le proprie risorse, non dichiarare distruttore, copia né move. È il caso normale.
- **Cinque**: se dichiari uno tra distruttore, copy/move constructor, copy/move assignment, definisci o `= delete` / `= default` tutti e cinque.
- Un distruttore `virtual` in ogni classe base polimorfica (o protetto e non virtuale se non si cancella tramite la base). Le gerarchie con `override` esplicito e `final` quando non si ereditano.
- Evita lo slicing: le classi polimorfiche non si copiano per valore.

## Move e passaggio di parametri
- Funzioni: tipi piccoli e banali per valore (`int`, `string_view`, `span`); oggetti costosi per `const&`; sink (che li conserva) per valore con `std::move` nel corpo.
- `std::move` è un cast: dopo, l'oggetto è valido ma con valore non specificato; non usarlo. `std::move` su un valore di ritorno locale è un errore (impedisce la copy elision): scrivi `return x;`.
- `std::forward` solo nei template con forwarding reference (`T&&` deducendo `T`); altrove `T&&` è un rvalue reference.
- Un `const` su un oggetto che poi viene spostato lo copia in silenzio.

## const e interfacce
- `const` di default: variabili, riferimenti, metodi che non modificano lo stato, `constexpr` per ciò che si calcola a compile time.
- `[[nodiscard]]` su funzioni che restituiscono errori, risorse o valori puri. `explicit` sui costruttori a un argomento e sugli operatori di conversione.
- `enum class`, mai `enum` non scoped. `using` invece di `typedef`. Niente `using namespace` negli header.
- Gli header si bastano da soli (include ciò che usano), con `#pragma once` o include guard secondo il progetto. Dichiarazioni anticipate dove bastano.
- Niente macro per costanti o funzioni: `constexpr`, `inline`, template.

## string_view e span: rischi di lifetime
Non possiedono i dati: sono comodi come **parametri**, pericolosi come valori conservati.
- Mai restituire o salvare una `string_view`/`span` che punta a un temporaneo o a un locale: `std::string_view v = std::string("ciao");` punta a memoria già liberata.
- Non salvarli come membri o in contenitori se l'origine può morire o riallocarsi (`vector` dopo `push_back` invalida riferimenti, puntatori, iteratori e span).
- `string_view` non è terminata da `\0`: passarla a un'API C con `.data()` è un bug. Costruisci una `std::string`.
- Lo stesso vale per i range: una view da un temporaneo (`views::filter` su un rvalue) è un dangling reference.
- Anche lambda con cattura per riferimento portate fuori scope (thread, callback, `std::async`) sono dangling.

## Comportamento indefinito frequente
- Accesso fuori limite (`operator[]`, `front()` su vuoto): usa `.at()` dove l'indice non è già garantito, o `span`/range.
- Overflow di interi con segno; confronti e conversioni signed/unsigned (`size_t` meno qualcosa); shift oltre la larghezza.
- Uso dopo `free`/`delete`, doppia liberazione, iteratore invalidato, lettura di variabile non inizializzata, `nullptr` dereferenziato.
- Data race; ordine di valutazione degli argomenti non specificato; modifica di un oggetto `const` tramite `const_cast`.
- Distruzione di un oggetto derivato tramite puntatore a base senza distruttore virtuale.
- `reinterpret_cast` e type punning: per i byte usa `std::memcpy` o `std::bit_cast` (C++20).
- C-style cast: usa `static_cast`; gli altri cast sono un segnale da motivare.

## Concorrenza
- Il default è non condividere. Se serve, un mutex per ogni dato condiviso, preso con `std::scoped_lock` (più mutex senza deadlock) o `std::lock_guard`/`unique_lock`; mai `lock()` a mano.
- Un dato è **protetto da un solo mutex**, e questo si scrive in un commento. Non chiamare codice sconosciuto (callback) tenendo un lock.
- `std::jthread` (C++20) si unisce nel distruttore e supporta `stop_token`; `std::thread` non unito alla distruzione chiama `std::terminate`. Quasi sempre `jthread`.
- `std::atomic` per contatori e flag semplici; l'ordine di memoria di default (`seq_cst`) va bene finché non c'è una misura e una prova che serva altro. Non è un sostituto di un mutex per invarianti su più variabili.
- `condition_variable`: sempre con un predicato (risvegli spuri). Per i task asincroni, attenzione al distruttore di `std::future` da `std::async`, che blocca.
- Per l'I/O e il parallelismo di dati valuta la libreria già in uso nel progetto prima di scrivere thread a mano.

## Errori
- Rispetta la scelta del progetto: eccezioni, codici di ritorno o `std::expected`. Non mischiarle nello stesso strato.
- **Eccezioni** per errori non locali e raramente attesi, con costruttori che falliscono; lancia per valore e cattura per `const&`. Le funzioni di cleanup (distruttori, `swap`, move) non lanciano.
- **`std::expected<T, E>`** (C++23) o codici + `[[nodiscard]]` per errori attesi e frequenti (parsing, validazione, I/O) e per codice senza eccezioni (embedded, hot path).
- `std::optional` per l'assenza di un valore, non per un errore di cui serve la causa. Mai un valore sentinella (`-1`, `nullptr`).
- Le asserzioni (`assert`) verificano bug del programmatore, non input esterno: gli input si validano sempre ai confini.

## CMake moderno
- Un target per libreria o eseguibile: `add_library`, `add_executable`, poi `target_link_libraries`, `target_include_directories`, `target_compile_features(… cxx_std_20)`, ciascuno con `PRIVATE`/`PUBLIC`/`INTERFACE` motivato.
- Niente comandi globali (`include_directories`, `add_definitions`, `link_libraries`, `set(CMAKE_CXX_FLAGS …)`) e niente impostazioni a livello di directory: le proprietà viaggiano con il target (`target_include_directories`, `target_compile_definitions`, `target_link_libraries`).
- Dipendenze con `find_package` (config package) o `FetchContent` con versione e hash fissati; una dipendenza nuova va concordata.
- `CMAKE_EXPORT_COMPILE_COMMANDS=ON` per analizzatori e IDE; `CMakePresets.json` se il progetto lo usa per configurazioni riproducibili. Build out-of-source.
- Non cambiare standard, compilatore o flag di tutto il progetto per ottenere una compilazione.

## Warning, sanitizer e analisi
- Warning attivi sui target del progetto: GCC/Clang `-Wall -Wextra -Wpedantic` (più `-Wshadow -Wconversion` se il progetto è già pulito), MSVC `/W4`. Warning come errori (`-Werror`, `/WX`) in CI e per il codice nuovo; non sulle dipendenze di terzi (`SYSTEM` negli include) e non attivarli su un progetto che oggi ne ha centinaia.
- **Sanitizer** nei test: `-fsanitize=address,undefined` (ASan + UBSan) con `-fno-omit-frame-pointer`, ottimizzazioni basse; **TSan** (`-fsanitize=thread`) in una build separata, perché non si combina con ASan. Valgono in debug e in CI, non in release.
- `clang-tidy` (`bugprone-*`, `cppcoreguidelines-*`, `modernize-*`, `performance-*` nelle parti che il progetto abilita) e `cppcheck` se già configurati. Un check non va disattivato per far passare il codice: o si corregge, o si motiva con un `NOLINT` mirato.
- Formattazione: `.clang-format` del progetto, solo sui file toccati.

## Test
- Usa il framework del progetto: GoogleTest (`TEST`, `TEST_F`, `EXPECT_*`, `gmock` per i confini) o Catch2 (`TEST_CASE`, `SECTION`, `REQUIRE`). Registra i test con CTest (`enable_testing`, `gtest_discover_tests` o `catch_discover_tests`).
- Test piccoli e deterministici, senza sleep: nella concorrenza usa sincronizzazione esplicita. Il codice con bug di memoria e race va eseguito sotto sanitizer.
- Ogni bug corretto ha un test che lo riproduce. Per parser e protocolli, valuta un fuzzer (`libFuzzer`) se il progetto ne ha già uno.

## Una nota sul C
In un file C (`.c`, o `extern "C"`) valgono le regole del C, non quelle del C++: niente RAII, quindi un solo punto di uscita o un `goto cleanup` ordinato, controllo di ogni `malloc` e valore di ritorno, `size_t` e `snprintf` con limite, niente `strcpy`/`gets`/`sprintf`. Nei header condivisi con C++: `extern "C"` dentro `#ifdef __cplusplus`, e nessun tipo C++ nell'interfaccia. Non convertire C in C++ se non richiesto.

## Verifica
Usa i preset e gli script già nel progetto:
```bash
cmake --preset <nome>      # oppure cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j
ctest --test-dir build --output-on-failure
```
Poi, se configurati: build con sanitizer (`-fsanitize=address,undefined`, e TSan se c'è codice concorrente), `clang-tidy` sui file modificati, `clang-format --dry-run -Werror` sui soli file toccati. Riporta compilatore, standard e flag usati; se non hai potuto compilare con il toolchain del progetto, dillo.
