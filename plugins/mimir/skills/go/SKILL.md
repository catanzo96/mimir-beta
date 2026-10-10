---
name: go
description: Best practice Go idiomatico. Usala quando scrivi, modifichi o rivedi codice Go, o in progetti con go.mod, go.work o .golangci.yml.
---

# Go

Si applica insieme a `clean-code`, che qui si legge con l'occhio di Go: semplicità, pochi livelli, niente gerarchie. Le convenzioni del progetto prevalgono: versione nella direttiva `go` di `go.mod`, linter configurato, struttura dei package, librerie già in uso. `gofmt` è l'unico stile ammesso, ma non riformattare file che non tocchi.

## Prima di tutto: la versione
Leggi `go` (e `toolchain`) in `go.mod`: non usare feature oltre quella versione. Verificato su go.dev il 03/10/2026: ultime major 1.27 (agosto 2026), 1.26, 1.25; ogni major è supportata finché non escono due successive. **Su progetti con Go precedente alla 1.21, senza moduli o senza test, vale `manutenzione-legacy` (se disponibile).**

Feature utili per versione:
- **1.21**: `log/slog`, built-in `min`, `max`, `clear`, pacchetti `slices` e `maps`.
- **1.22**: `for i := range 10`; la variabile del ciclo è nuova a ogni iterazione (niente più copia `i := i` prima di una goroutine o closure; conta la versione in `go.mod`).
- **1.23**: range su funzioni (iteratori, pacchetto `iter`), `slices.Collect`, `maps.Keys`.
- **1.24**: alias generici, direttiva `tool` in `go.mod` (sostituisce `tools.go`), `os.Root`, `omitzero` in `encoding/json`, `testing.B.Loop`.
- **1.25**: `sync.WaitGroup.Go`, `testing/synctest` per testare codice concorrente con tempo virtuale, `GOMAXPROCS` che rispetta i limiti cgroup.
- **1.26**: `new(expr)` (puntatore a un valore calcolato, utile per campi opzionali), `errors.AsType` generico, `go fix` rinnovato con i modernizer.
- **1.27**: metodi generici con parametri di tipo proprio, `encoding/json/v2`, profilo `goroutineleak`. Leggi le release notes prima di adottare queste novità in un progetto.

## Errori
- Gli errori sono valori: ritornali, non lanciare `panic`. `panic` solo per bug di programmazione e stati impossibili; mai per input o I/O.
- Controlla subito `if err != nil` e ritorna: il percorso felice resta a sinistra, senza `else`.
- Aggiungi contesto con `fmt.Errorf("carico ordine %d: %w", id, err)`: `%w` mantiene la catena. Il messaggio dice cosa stavi facendo, non "errore".
- `errors.Is` per confrontare con un errore sentinella, `errors.As` (o `errors.AsType`, 1.26+) per estrarre un tipo. Mai confronto per stringa né `==` su errori avvolti.
- Sentinelle (`var ErrNonTrovato = errors.New(...)`) o tipi di errore per ciò che il chiamante deve distinguere; il resto resta opaco. Un errore si gestisce **o** si logga, non entrambi: log una sola volta al confine.
- Mai `_ = f()` su un errore che conta. Su `defer f.Close()` in scrittura, controlla l'errore di `Close`.
- `errors.Join` per aggregare errori; `recover` solo ai confini (server, worker) per non far cadere il processo.

## Interfacce e tipi
- Interfacce **piccole** e **definite dal consumatore**, nel package che le usa, non accanto all'implementazione. "Accetta interfacce, restituisci tipi concreti."
- Nessuna interfaccia "per il mock" finché serve una sola implementazione: introducila quando il test o un secondo uso la richiede.
- **Zero value utile**: un `var b bytes.Buffer` o un `sync.Mutex` funzionano senza costruttore; progetta i tuoi tipi allo stesso modo, ed evita costruttori `New` che servono solo a inizializzare campi.
- Opzioni di configurazione: struct di config o functional options se il progetto le usa; non decine di parametri posizionali.
- Embedding per composizione, non per simulare l'ereditarietà; ricorda che espone i metodi del tipo incorporato.
- Slice e map: una slice `nil` è valida (`len`, `append`, `range`); distingui `nil` da vuota solo dove ha senso (JSON: `omitempty`/`omitzero`). Scrivere su una map `nil` va in panic. Una sotto-slice condivide l'array: `slices.Clone` prima di mutare. Le map non sono sicure per accessi concorrenti, e l'ordine di iterazione è casuale.
- Il receiver è un puntatore se il metodo muta o il tipo è grande, e **coerente** per tutti i metodi del tipo.
- `any` solo ai confini; con i generics, vincoli (`comparable`, `cmp.Ordered`, interfacce) e solo quando evitano duplicazione reale.

## Concorrenza
- Ogni goroutine ha un **ciclo di vita chiaro**: sai chi la avvia, quando finisce e chi la attende. Una goroutine senza un modo di fermarsi è una perdita.
- `context.Context` primo parametro (`ctx`) di ciò che fa I/O o può durare; non nelle struct. Propaga cancellazione e timeout (`context.WithTimeout`, sempre `defer cancel()`); controlla `ctx.Done()` nei cicli lunghi.
- **`errgroup`** (`golang.org/x/sync/errgroup`, già nel progetto o da proporre) per lanciare gruppi di lavoro con errore e cancellazione condivisi, con `SetLimit` per limitare la concorrenza. `sync.WaitGroup` (con `.Go` dalla 1.25) quando non servono errori.
- **Canali per passare dati o segnali, mutex per proteggere stato.** Se hai un campo condiviso e due metodi, un `sync.Mutex` è più semplice di un canale. Chi **invia** chiude il canale; mai chiudere da più parti. Un canale senza lettore blocca il mittente per sempre: canali con buffer o `select` con `ctx.Done()`.
- Data race: `go test -race` in CI sul codice concorrente; un contatore condiviso si protegge o usa `sync/atomic`. Una race non è un errore "raro": è comportamento indefinito.
- Non avviare goroutine in una libreria in modo nascosto; offri `Close`/`Shutdown` e fai attendere chi chiude.
- `time.After` in un ciclo crea timer che vivono fino alla scadenza (dalla 1.23 sono recuperabili, ma `time.NewTimer` e `Stop` restano più chiari dove contano). Niente `time.Sleep` per sincronizzare.
- Server HTTP: `http.Server` con timeout (`ReadHeaderTimeout` almeno) e `Shutdown(ctx)` su `SIGTERM`; il client `http.Client` con timeout, e il body della risposta si chiude sempre.

## Struttura dei package
- Un package è un concetto con un nome corto e minuscolo, senza underscore né plurali ridondanti; il nome si legge nel punto d'uso (`ordini.Servizio`, non `ordini.OrdiniServizio`).
- **Niente `util`, `common`, `helpers`, `base`**: sono cassetti. Se una funzione serve a un solo package, vive lì.
- `internal/` per ciò che non deve essere importato da fuori il modulo; `cmd/<app>/main.go` per i binari, con `main` sottile (configurazione, wiring, avvio).
- Evita i cicli di import ripensando le dipendenze, non creando package di tipi condivisi.
- Struttura piatta finché regge: non copiare gerarchie da altri linguaggi. Per i confini architetturali vedi `architettura-esagonale` se il progetto la adotta.
- Esporta il minimo (iniziale maiuscola) e documenta ogni identificatore esportato con un commento che inizia con il suo nome.
- `init()` e variabili globali mutabili: evitali; il wiring sta in `main`.

## Test
- **Table-driven** con `t.Run(nome, ...)` per i casi; ogni caso con un nome parlante. Struct con `want`/`wantErr`, confronto con `cmp.Diff` se il progetto usa `go-cmp`, altrimenti confronti espliciti.
- `t.Helper()` negli helper, `t.Cleanup` per la pulizia, `t.TempDir()`, `t.Setenv`; `t.Parallel()` solo se i test sono davvero indipendenti.
- Test nel package `x_test` per verificare l'API pubblica; nel package stesso per l'interno.
- Fake scritti a mano per le interfacce piccole prima di librerie di mock. Test di integrazione dietro build tag o `testing.Short()`, secondo il progetto.
- **Benchmark**: `func BenchmarkX(b *testing.B)` con `for b.Loop()` (1.24+) o `for range b.N`; misura con `-benchmem` e confronta con `benchstat`, prima di ottimizzare.
- Fuzzing (`testing.F`) per parser e input non fidati. `go test -cover` come indicazione, non come obiettivo.
- Per i principi generali vedi `clean-code/references/test.md`.

## Sicurezza e log
- `log/slog` (1.21+) con campi strutturati se il progetto lo usa. Query con parametri (`db.QueryContext(ctx, sql, args...)`), mai `fmt.Sprintf` in SQL. `os/exec` con argomenti separati, mai `sh -c` con input esterni. Percorsi da input confinati con `os.Root` (1.24+) o controlli espliciti. Altre indicazioni: `clean-code/references/sicurezza.md`.
- Segreti e configurazione da ambiente, validati all'avvio.
- `crypto/rand` per valori di sicurezza, mai `math/rand`.

## Verifica
Usa gli strumenti già configurati (`Makefile`, CI, `.golangci.yml`):
```bash
gofmt -l .            # elenca i file non formattati, non li riscrive
go vet ./...
golangci-lint run     # oppure staticcheck ./..., secondo il progetto
go test -race ./...   # con -cover se richiesto
go build ./...
```
Se `go.mod` cambia (`go mod tidy`), controlla il diff: dipendenze nuove solo con ok. Riporta gli esiti reali.
