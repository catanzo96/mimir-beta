---
name: rust
description: Best practice Rust idiomatico. Usala quando scrivi, modifichi o rivedi codice Rust (.rs), o in progetti con Cargo.toml, rust-toolchain.toml o clippy.toml.
---

# Rust

Si applica insieme a `clean-code`. Prevalgono le convenzioni del progetto: edizione e `rust-version` in `Cargo.toml`, `rust-toolchain.toml`, `rustfmt.toml`, lint di `clippy`. Non usare feature più recenti della versione minima dichiarata. Async, `unsafe`, workspace e feature di Cargo: `references/async-unsafe-cargo.md`.

## Prima di tutto: la versione
Leggi `edition` e `rust-version` in `Cargo.toml` (e il `rust-toolchain.toml`).
- Edizioni: 2018, 2021, **2024** (stabile dalla 1.85, febbraio 2025). Il compilatore è retrocompatibile: un progetto resta sulla sua edizione finché non migra (`cargo fix --edition`, da fare in un commit separato).
- Dalla 1.65: `let … else`. Dalla 1.75: `async fn` e `impl Trait` nei trait. Dalla 1.80: `LazyLock` e `LazyCell` nella std (al posto di `once_cell`/`lazy_static` per il codice nuovo).
- Dalla 1.85: closure async (`async || …`, trait `AsyncFn*`). Con l'edizione 2024 e dalla 1.88: **let chain** (`if let Some(x) = a && x > 0 && let Ok(y) = b`).
- Edizione 2024: `unsafe extern` per i blocchi FFI, `unsafe_op_in_unsafe_fn` in warning, `gen` parola riservata, nuove regole sui temporanei nelle espressioni finali e sulla cattura dei lifetime in `impl Trait` di ritorno.
- Su codice con edizione 2015 o senza test vale `manutenzione-legacy` (se disponibile).

## Ownership e borrowing
- Parti dai riferimenti: le funzioni prendono `&str`, `&[T]`, `&Path` e non `String`, `Vec<T>`, `PathBuf`, salvo che debbano possedere il valore. Prendi `T` per valore quando lo consumi o lo memorizzi; `impl Into<String>` solo per API dove il chiamante spesso ha già una `String`.
- **Clonare** è lecito quando semplifica e il costo è irrilevante (dati piccoli, percorso non caldo): un `.clone()` per placare il borrow checker, però, spesso nasconde un problema di struttura. Prova prima a restringere lo scope del prestito, a dividere la struct o a restituire un valore invece di un riferimento. Non clonare dentro un ciclo caldo senza averlo misurato.
- `Cow<'a, str>` quando una funzione di solito restituisce l'input invariato e solo a volte ne alloca uno nuovo (escape, normalizzazione). Non come ottimizzazione generale.
- **Lifetime espliciti solo quando il compilatore li chiede.** Una struct che contiene un riferimento (`struct Parser<'a>`) è un segnale: valuta se possedere i dati (`String`, `Arc<str>`) renda l'API più semplice. Se una firma ha tre lifetime, riprogetta.
- Preferisci l'ownership alla condivisione: passa i dati, restituisci i risultati. Lo stato condiviso mutabile è l'ultima scelta.
- Indici e `unwrap` su slice: usa `get`, iteratori, `split_at`, `chunks`, pattern slice (`[primo, resto @ ..]`) invece di indicizzare a mano.

## Errori
- Funzioni fallibili restituiscono `Result<T, E>`; l'operatore `?` propaga. Assenza di valore: `Option`. Mai codici magici (`-1`, stringa vuota).
- **Niente `unwrap()` e `expect()` nel codice di produzione**, salvo un invariante che il codice vicino garantisce: in quel caso `expect("motivo per cui non può fallire")`, che dice *perché*. Nei test e negli esempi sono ammessi. `panic!` per bug e stati impossibili, non per input o I/O.
- **Librerie**: tipo di errore proprio, un `enum` con le varianti che il chiamante può distinguere; `thiserror` per derivare `Display`/`Error` e `#[from]`/`#[source]` per la causa, se il progetto lo usa. **Applicazioni**: `anyhow` (`anyhow::Result`, `.context("cosa stavi facendo")`) per propagare con contesto, se il progetto lo usa. Non introdurre nessuna delle due senza ok.
- Il contesto dice cosa si stava facendo (`.context("lettura del file di configurazione")`), non ripete il messaggio dell'errore. Non loggare e rilanciare lo stesso errore: lo gestisce chi sta al confine (`main`, il gestore della richiesta).
- Non convertire un errore in `String` per perderne la causa: tieni il `source`.
- `Box<dyn Error + Send + Sync>` va bene per codice breve e prototipi, non per l'API di una libreria.

## Trait, generics e `dyn`
- Generics (`fn f<T: Trait>(t: T)`, `impl Trait` in argomento) per dispatch statico: più veloce, ma una copia del codice per tipo e tempi di compilazione maggiori. `dyn Trait` per collezioni eterogenee, plugin, per ridurre il codice generato o ai confini di un'architettura (`Box<dyn Trait>`, `&dyn Trait`).
- Non usare `dyn` per abitudine da Java: parti dagli enum quando le varianti sono note e chiuse (`match` esaustivo, come `sealed` in Java), dai trait quando l'insieme è aperto.
- Bound minimi e sul punto dove servono (`where`). Non esporre generics che nessuno varia.
- Implementa i trait standard dove hanno senso: `Debug` quasi sempre, `Clone`, `PartialEq`, `Default`, `Display`, `From`/`TryFrom` per le conversioni. `Default` con `..Default::default()` per le struct di configurazione. Con `derive`, ricorda che `PartialEq` e `Hash` devono essere coerenti.
- **Newtype** (`struct IdOrdine(u64)`) per distinguere ID e unità; costruttori che validano gli invarianti e campi privati: così lo stato invalido non è rappresentabile. Pattern builder solo per struct con molti parametri opzionali.
- Una funzione che restituisce un iteratore: `impl Iterator<Item = T> + '_`, non un `Vec` intermedio.

## Iteratori
- Catene di iteratori (`map`, `filter`, `filter_map`, `flat_map`, `fold`, `zip`) al posto di cicli con indici e `push`. Un `for` va benissimo quando c'è un effetto collaterale o la logica è lunga: non forzare una catena illeggibile.
- `collect::<Result<Vec<_>, _>>()` per fermarsi al primo errore; `collect::<Vec<_>>()` solo quando serve davvero una collezione. Annota il tipo (`::<Vec<_>>`) invece di affidarti all'inferenza a distanza.
- `iter()` prende in prestito, `into_iter()` consuma, `iter_mut()` modifica: scegli apposta. Gli iteratori sono pigri: senza un consumatore non fanno nulla.
- `HashMap` ha ordine di iterazione non deterministico: se l'ordine conta (output, test, serializzazione) usa `BTreeMap` o ordina.

## Smart pointer e mutabilità interna
- `Box<T>` per allocare sullo heap un valore (tipi ricorsivi, `dyn Trait`, valori grandi da spostare). Non serve per "rendere tutto un riferimento".
- `Rc<T>` (un thread) e `Arc<T>` (più thread) per la proprietà condivisa; `Arc::clone(&x)` è economico e dice che stai condividendo. Prima di condividere, chiediti se basta passare un riferimento o spostare il valore.
- `RefCell<T>` e `Cell<T>` (un thread) spostano i controlli di prestito a runtime: un doppio prestito diventa un `panic`. `Mutex<T>`/`RwLock<T>` (thread): il lock si tiene per il minor tempo possibile, mai attraverso un `.await` con il `Mutex` della std, e l'ordine dei lock deve essere uniforme (deadlock). Un lock "avvelenato" (`PoisonError`) si gestisce, non si ignora con `unwrap` per principio.
- `Arc<Mutex<T>>` ovunque segnala una struttura da ripensare: canali (`mpsc`), un solo task proprietario dello stato, o dati immutabili condivisi.
- `Rc<RefCell<…>>` con cicli perde memoria: `Weak` per i riferimenti all'indietro.

## Concorrenza
- `Send` e `Sync` guidano il compilatore: se un tipo non è `Send`, non attraversa thread né `.await` su un runtime multi-thread. Non aggirare con `unsafe impl Send` senza una prova.
- Thread con `std::thread::scope` per prestare dati locali; `rayon` per il parallelismo sui dati, se già nel progetto.

## Stile e strumenti
- `rustfmt` e `clippy` sono la norma: il codice passa `cargo fmt --check` e `cargo clippy` senza warning. Un `#[allow(clippy::…)]` ha un commento col motivo ed è il più stretto possibile (sull'elemento, non sul crate).
- Visibilità minima: `pub(crate)` e privato di default; ciò che è `pub` in una libreria è un impegno di compatibilità.
- Documentazione `///` con una sezione `# Errors` e `# Panics` dove serve, ed esempio che gira come doctest.
- Nomi: `snake_case` per funzioni e variabili, `UpperCamelCase` per i tipi, `SCREAMING_SNAKE_CASE` per le costanti. Conversioni: `as_` (prestito, economico), `to_` (costoso), `into_` (consuma), `from_`.
- `#[must_use]` su funzioni il cui risultato non va ignorato. `#[non_exhaustive]` su enum e struct pubblici di una libreria che potranno crescere.
- Overflow: in debug panica, in release avvolge; per aritmetica con valori esterni `checked_*`, `saturating_*` o `wrapping_*` scelti consapevolmente; mai `as` per restringere (`u64 as u32` tronca in silenzio): `try_from`.

## Test
- Unit test in un modulo `#[cfg(test)] mod tests` nello stesso file; test di integrazione in `tests/`, che usano solo l'API pubblica; esempi nei doctest (`cargo test` li esegue). Test async con `#[tokio::test]` se il progetto usa tokio.
- Funzioni che restituiscono `Result` nei test: `-> Result<(), Box<dyn Error>>` con `?`, più leggibile di `unwrap` a catena.
- Un test che verifica un errore controlla la variante (`assert!(matches!(…))`), non il testo del messaggio.
- Proprietà e casi limite con `proptest`/`quickcheck`, snapshot con `insta`, mock con `mockall`: solo se già nel progetto. Per i doppi di test spesso basta un trait con un'implementazione finta.
- `cargo test` non esegue i benchmark; per le prestazioni `criterion` o `cargo bench`, e solo con una misura prima di ottimizzare.

## Verifica
Prima di dichiarare finito, con la toolchain del progetto:
- `cargo check --all-targets`, poi `cargo test` (nel workspace `--workspace`; `--all-features` se le feature sono parte del contratto; i doctest sono inclusi).
- `cargo clippy --all-targets -- -D warnings` (o la configurazione di CI del progetto) e `cargo fmt --check`: non riformattare file che non hai toccato.
- `cargo doc --no-deps` se hai modificato la documentazione pubblica.
- Se aggiungi una dipendenza (serve ok): `cargo audit` o `cargo deny` se il progetto li usa, e una `Cargo.lock` coerente nel commit.
- In sandbox senza rete: `cargo --offline` con le dipendenze già in cache.
