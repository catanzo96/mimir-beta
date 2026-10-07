---
name: python
description: Best practice Python moderno. Usala quando scrivi, modifichi o rivedi codice Python, o in progetti con pyproject.toml, requirements.txt, uv.lock o poetry.lock.
---

# Python

Si applica insieme a `clean-code`. Le convenzioni del progetto prevalgono: versione di Python, type checker, formatter, gestore delle dipendenze, librerie già adottate. Django e FastAPI: `references/django.md` e `references/fastapi.md`. Non cambiare strumenti o stile su codice che non tocchi.

## Prima di tutto: la versione
Cerca la versione minima in `pyproject.toml` (`requires-python`), `.python-version`, `tox.ini`, CI o Dockerfile. Non usare feature oltre quella versione. **Su progetti Python 2/3.6-3.9, EOL o senza test, vale `manutenzione-legacy` (se disponibile).**

Feature utili per versione (verificate su docs.python.org/3/whatsnew):
- **3.10**: `match`, `X | Y` nei tipi, `ParamSpec`, `zip(strict=True)`.
- **3.11**: `ExceptionGroup` e `except*`, `tomllib`, `Self`, `asyncio.TaskGroup`, `StrEnum`.
- **3.12**: sintassi generica `def f[T](x: T)` e `type Alias = ...`, `@override`, f-string senza limiti di quote, `itertools.batched`.
- **3.13**: `warnings.deprecated`, `TypeIs`, `ReadOnly`, default per i type parameter, `copy.replace`. Free-threading e JIT sono sperimentali.
- **3.14**: annotazioni valutate in modo differito (i riferimenti in avanti non richiedono più le virgolette), t-string (`t"..."`), `except A, B:` senza parentesi, `compression.zstd`, `concurrent.interpreters`; il free-threading è supportato ufficialmente.

## Tipi
- Annota parametri e ritorni delle API pubbliche; lascia inferire i locali. Il checker è quello del progetto (mypy o pyright) con la sua configurazione: non allentarla per far passare un errore.
- Sintassi moderna se la versione lo consente: `list[str]`, `str | None`, non `List`, `Optional`.
- Niente `Any` per comodità: `object`, `Protocol` o un tipo generico. `cast` e `# type: ignore` solo con motivo e codice dell'errore (`# type: ignore[arg-type]`).
- `Protocol` per i contratti definiti dal consumatore; `TypedDict` per dict con forma nota; `Literal` ed `Enum` per insiemi chiusi; `NewType` se confondere due ID è un rischio reale.
- `Optional` esplicito nei ritorni: l'assenza non si segnala con `""` o `-1`.

## Dati: dataclass, attrs, pydantic
Segui il progetto. In mancanza:
- `@dataclass(frozen=True, slots=True)` per oggetti valore interni; `kw_only=True` quando i campi sono molti.
- **Pydantic** ai confini (input HTTP, file, API esterne, configurazione): valida e converte. Dentro il dominio bastano dataclass: non propagare i modelli di validazione ovunque.
- Mai un default mutabile in una dataclass (`field(default_factory=list)`).
- `dict` come record ad hoc passato tra moduli: sostituiscilo con un tipo.

## Dipendenze e ambienti
- Dichiara tutto in `pyproject.toml` e usa **lo strumento già presente** (uv, poetry, pip-tools, pip + venv): riconoscilo da `uv.lock`, `poetry.lock`, `requirements*.in`.
- Un ambiente virtuale per progetto, mai installazioni nel Python di sistema.
- Il lockfile si aggiorna solo con lo strumento, mai a mano; dipendenze nuove solo con ok (regola generale).
- Separa runtime e sviluppo (`dependency-groups` o extra); non fissare con `==` nelle librerie, sì nelle applicazioni (via lockfile).

## Eccezioni e risorse
- Cattura eccezioni specifiche. `except Exception` solo ai confini (handler, worker) e con log; mai `except:` nudo, che inghiotte anche `KeyboardInterrupt`.
- Rilancia con la causa: `raise ErroreOrdine("...") from exc`. Un `raise` semplice mantiene il traceback.
- `with` per file, lock, connessioni, transazioni; `contextlib.contextmanager` con `try/finally` per le risorse proprie, `ExitStack` per un numero variabile.
- Le eccezioni di dominio ereditano da `Exception` (o da una base del progetto), non da `BaseException`.
- `assert` non è una validazione: con `-O` sparisce. Valida gli input con eccezioni.

## Iteratori e generatori
- Generatori e `yield` per sequenze grandi o infinite: elaborazione pigra, memoria costante.
- Un generatore si consuma una sola volta: se serve due volte, materializzalo (`list`) o rigeneralo.
- Comprehension per trasformazioni semplici; se servono due cicli annidati e una condizione, scrivi un ciclo o una funzione.
- `itertools`, `functools`, `collections` (`defaultdict`, `Counter`, `deque`) prima di reinventare. `zip(strict=True)` quando le lunghezze devono coincidere.
- `pathlib.Path` al posto di `os.path`; `enumerate` invece di indici a mano.

## Trappole
- **Default mutabili**: `def f(x=[])` condivide la lista tra le chiamate. Usa `None` e crea dentro, o `default_factory`.
- **Late binding nelle closure**: `[lambda: i for i in range(3)]` restituisce sempre l'ultimo `i`. Fissa il valore (`lambda i=i: i`, `functools.partial`).
- **`is` vs `==`**: `is` solo per `None`, `True`, `False` e sentinelle. Su interi e stringhe l'identità dipende dall'implementazione.
- **Float e denaro**: mai `float` per importi. `Decimal` costruito da stringa (`Decimal("0.10")`), non da float; imposta contesto e arrotondamento esplicitamente. Confronta i float con `math.isclose`.
- **Date**: oggetti `datetime` con fuso (`zoneinfo`); i naive solo se il progetto li usa ovunque. `datetime.utcnow()` è deprecato: `datetime.now(timezone.utc)`.
- **Mutare mentre si itera** su dict o liste: itera su una copia o costruisci una nuova collezione.
- **Import circolari**: si risolvono spostando la dipendenza o con un'interfaccia, non con import dentro le funzioni a tappeto.
- **Stringhe e SQL/shell**: mai f-string per query o comandi. Query parametrizzate; `subprocess.run([...], check=True)` con lista di argomenti, senza `shell=True` su input esterni. Niente `pickle` o `yaml.load` su dati non fidati (`yaml.safe_load`). Vedi `clean-code/references/sicurezza.md`.
- **Lettura/scrittura di testo**: `encoding="utf-8"` esplicito.

## Asyncio di base
- `async` solo se l'intero percorso è non bloccante: una chiamata sincrona lenta (requests, I/O su disco, CPU) dentro una coroutine blocca tutto il loop. Usa `await asyncio.to_thread(...)` o un client async.
- Concorrenza strutturata: `asyncio.TaskGroup` (3.11+) o `gather`; una `create_task` senza riferimento può essere raccolta dal garbage collector e gli errori si perdono.
- Timeout con `asyncio.timeout()` (3.11+) o `wait_for`; la cancellazione (`CancelledError`) non si inghiotte.
- `asyncio.run` una sola volta, al punto d'ingresso.

## Test con pytest
- Funzioni `test_*` semplici con `assert`; i test descrivono un comportamento, non un metodo.
- **Fixture** per preparare e ripulire (`yield`); scope ampio solo per risorse costose e immutabili. Condividi in `conftest.py`, senza logica nascosta.
- **`parametrize`** con `ids` leggibili per le tabelle di casi; `pytest.param(..., marks=...)` per i casi particolari.
- **`monkeypatch`** per variabili d'ambiente, attributi e dict; `tmp_path` per i file. Sostituisci il confine (rete, orologio, DB), non la logica interna. `unittest.mock.patch` va applicato dove il nome è *usato*, non dove è definito.
- `pytest.raises(Errore, match=...)` per le eccezioni attese; `pytest.approx` per i float.
- Niente `sleep` nei test: orologio iniettabile o `freezegun`/`time-machine` se già nel progetto.
- Per i principi generali (cosa testare, nomi, isolamento) vedi `clean-code/references/test.md`.

## Stile e strumenti
- Lint e formattazione con ciò che è configurato (`ruff`, `black`, `isort`, `flake8`, `pylint`): non introdurne altri. Se il formatter non è applicato al repo, non riformattare i file che non tocchi.
- Docstring e commenti solo per il perché, nella lingua del progetto. Naming PEP 8 (`snake_case`, `PascalCase`).
- Configurazione e segreti da variabili d'ambiente, validate all'avvio (Pydantic Settings o equivalente del progetto), mai nel repository.
- Logging con il modulo `logging` e argomenti pigri (`log.info("ordine %s", id)`), mai `print`; niente dati sensibili.

## Verifica
Lancia ciò che il progetto ha già configurato, tipicamente:
```bash
ruff check . && ruff format --check .   # oppure black --check, flake8
mypy .                                   # oppure pyright
pytest -q                                # con coverage se prevista: pytest --cov
```
Gli script esatti stanno in `pyproject.toml`, `Makefile`, `tox.ini`, `noxfile.py` o nella CI. Riporta i risultati reali, anche se falliscono.

## Riferimenti
- `references/django.md`: leggilo se il progetto ha `manage.py` o `django` nelle dipendenze (ORM, migrazioni, sicurezza, test).
- `references/fastapi.md`: leggilo se il progetto usa `fastapi` (dipendenze, Pydantic, async, test).
