# Async, unsafe e Cargo

Da leggere quando il codice usa `async`/`.await`, blocchi `unsafe` o FFI, o quando tocchi `Cargo.toml` (workspace, feature, dipendenze).

## Async
- Rust non ha un runtime: ne serve uno. **Tokio** è il più diffuso; usa quello del progetto (async-std, smol) e non mescolare. `#[tokio::main]` e `#[tokio::test]` solo se tokio è già presente.
- **Non bloccare il runtime.** Dentro una funzione `async`, `std::thread::sleep`, I/O sincrono su file o rete, calcoli lunghi e `Mutex::lock` contesi bloccano il thread del worker e fermano gli altri task. Usa le versioni async (`tokio::time::sleep`, `tokio::fs`) o sposta il lavoro in `tokio::task::spawn_blocking` (bloccante/CPU).
- Un `Future` non fa nulla finché non lo attendi o lo spawni: `foo();` senza `.await` compila (con un warning `unused_must_use`) e non esegue niente. Tratta quel warning come un errore.
- **`Send`**: `tokio::spawn` richiede un future `Send`. Un tipo non `Send` (come `Rc`, un `MutexGuard` della std) tenuto attraverso un `.await` rende il future non `Send`, con un errore lungo. Chiudi lo scope prima dell'`.await` (blocco `{ … }` attorno al guard) o usa il mutex di tokio se il lock deve attraversare un `.await`.
- Mutex: il `std::sync::Mutex` va bene se il lock è breve e non attraversa `.await`; `tokio::sync::Mutex` solo se serve tenerlo attraverso un `.await`. Per lo stato condiviso spesso un canale (`mpsc`, `watch`, `oneshot`) è più chiaro.
- **Cancellazione**: un future viene cancellato quando lo si droppa (timeout, `select!`); ciò che non è cancel-safe può lasciare lavoro a metà. Controlla la documentazione di ogni operazione dentro `tokio::select!`. Le risorse si liberano con `Drop`, non con codice dopo l'`.await`.
- Concorrenza strutturata: `JoinSet`/`join!`/`try_join!` per più operazioni insieme; un `tokio::spawn` il cui `JoinHandle` viene ignorato perde panic ed errori. Usa un `CancellationToken` (tokio-util, se presente) per lo shutdown ordinato.
- Timeout (`tokio::time::timeout`) su ogni chiamata di rete. Canali limitati (`mpsc::channel(n)`) e non illimitati: la backpressure evita la memoria che cresce.
- `async fn` nei trait è stabile (1.75), ma il future restituito non ha il bound `Send`: per l'uso con tokio, `trait_variant` o la crate `async-trait` se già nel progetto.

## unsafe
- `unsafe` solo quando non c'è alternativa sicura misurata e necessaria: FFI, strutture dati a basso livello, ottimizzazioni dimostrate. Prima cerca nella std o in una crate verificata.
- **Ogni blocco `unsafe` ha un commento `// SAFETY:`** che dice quali invarianti garantiscono la correttezza (puntatore valido, allineato, non aliasato, lifetime). Ogni `unsafe fn` o `unsafe trait` ha una sezione `# Safety` nella documentazione, che dice cosa deve garantire il chiamante.
- Blocchi piccoli, con una sola operazione non sicura; incapsulali in un'API sicura che mantiene l'invariante. Con l'edizione 2024 `unsafe_op_in_unsafe_fn` richiede il blocco anche dentro una `unsafe fn`: segui il progetto.
- Indefinito è indefinito: puntatori nulli o dangling, data race, riferimenti aliasati mutabili, valori non validi (`bool` ≠ 0/1, enum con discriminante assente). Provalo con **Miri** (`cargo +nightly miri test`) dove possibile, e con sanitizer.
- `unsafe impl Send/Sync` e `mem::transmute` sono quasi sempre un errore: motivali per iscritto.
- FFI: tipi `#[repr(C)]`, stringhe con `CString`/`CStr`, nessuno `panic` che attraversa il confine (`catch_unwind` o `extern "C-unwind"`), proprietà della memoria dichiarata (chi alloca, libera).

## Cargo
- **Workspace** (`[workspace]` con `members`) per più crate che si evolvono insieme: `Cargo.lock` unico, `target/` condiviso, dipendenze e versione comuni in `[workspace.dependencies]` e `[workspace.package]`, riferite con `dep.workspace = true`. Non creare crate per ogni cartella: una crate si separa per confini di compilazione, riuso o dipendenze diverse.
- `Cargo.lock` nel repo per binari e applicazioni; per le librerie la scelta è del progetto.
- **Feature**: devono essere *additive*: attivarne una non toglie funzioni né rompe il codice, perché le feature si uniscono tra tutte le crate che dipendono dalla stessa. Niente feature che si escludono a vicenda. Un `default` minimo; le dipendenze opzionali con `optional = true`. Testa la build senza le feature di default (`--no-default-features`) e con tutte.
- Versioni delle dipendenze con intervalli compatibili (`"1.2"`, caret), non `*` né versioni git senza revisione; per le librerie, `rust-version` dichiarata.
- Dipendenze: ogni crate in più è codice di terzi nella tua supply chain e tempo di compilazione. Ne servono motivo e ok dell'utente; controlla manutenzione, licenza, `cargo audit`/`cargo deny` se usati. Le `features` delle dipendenze si abilitano solo se necessarie (`default-features = false`).
- Profili: `[profile.release]` con `lto`, `codegen-units`, `panic = "abort"` sono scelte di progetto, da misurare, non da aggiungere "per velocità".
- `build.rs` e macro procedurali allungano la compilazione e vanno motivati. `cargo tree -d` per i duplicati, `cargo tree -i <crate>` per capire chi tira dentro una dipendenza.
- `cargo clippy` e `cargo fmt` si configurano in `clippy.toml`/`rustfmt.toml` e, per i lint di crate, nella tabella `[lints]` di `Cargo.toml` (anche `[workspace.lints]`).
