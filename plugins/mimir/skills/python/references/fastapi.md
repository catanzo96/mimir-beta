# FastAPI

Le convenzioni del progetto prevalgono. Controlla la versione di FastAPI e se Pydantic è v1 o v2: l'API dei modelli è diversa (`model_validate`, `model_dump`, `field_validator` in v2; `parse_obj`, `dict`, `validator` in v1). La documentazione aggiornata si consulta (Context7 o fastapi.tiangolo.com) prima di fare affermazioni su feature recenti.

## Struttura
- `APIRouter` per area funzionale, montati in un solo punto. Logica di business in servizi/funzioni senza dipendenza da FastAPI; gli endpoint orchestrano.
- Schemi diversi per input, output e persistenza (`OrdineCrea`, `OrdineLeggi`, il modello ORM): non esporre mai il modello del database come risposta.
- `response_model` esplicito sugli endpoint: filtra i campi in uscita (niente hash di password per distrazione) e documenta l'API.
- Codici di stato corretti (`201` in creazione, `204` senza corpo, `404`, `409`, `422` per la validazione).

## Dipendenze
- `Depends` per ciò che è condiviso: sessione DB, utente corrente, permessi, paginazione. Una dipendenza con `yield` libera la risorsa a fine richiesta (sessione, connessione).
- Le dipendenze sono il punto di sostituzione nei test: `app.dependency_overrides[get_db] = ...`.
- Le impostazioni si leggono una volta (`pydantic-settings`, `lru_cache` sulla funzione di accesso), non a ogni richiesta.
- Autenticazione e autorizzazione come dipendenze riusabili; verifica sempre che l'oggetto richiesto appartenga all'utente.

## Pydantic
- Validazione dichiarativa nei tipi (`Field(ge=0, max_length=...)`, `Annotated`, enum, `Literal`); validator solo per regole che i tipi non esprimono.
- `model_config = ConfigDict(from_attributes=True)` per leggere dagli oggetti ORM; `extra="forbid"` sugli input se un campo sconosciuto è un errore.
- `Decimal` per il denaro, datetime con fuso. Non fidarti dei dati solo perché "tipizzati": i limiti (lunghezze, intervalli) vanno dichiarati.
- Gli errori di validazione tornano come `422`: non catturarli per trasformarli in `500`.

## Async
- `async def` solo se dentro usi chiamate awaitable. Un endpoint `async` che chiama codice bloccante (driver sincrono, `requests`, calcoli lunghi) ferma l'intero event loop. Con codice bloccante usa `def` (FastAPI lo esegue in un threadpool) o `run_in_threadpool`.
- Driver e ORM coerenti: sessione async (`AsyncSession`) con driver async; non mescolare sincrono e asincrono nella stessa sessione.
- Lavoro lungo o da ritentare: coda di task (Celery, ARQ, il sistema del progetto), non `BackgroundTasks` per cose critiche: non sopravvivono a un riavvio del processo.
- Client HTTP: un `httpx.AsyncClient` condiviso con timeout, creato nel lifespan, non uno per richiesta.
- Avvio e chiusura (pool, client) nel `lifespan`, non nei vecchi `on_event`.

## Errori e sicurezza
- `HTTPException` per gli errori attesi nel confine HTTP; eccezioni di dominio mappate con `exception_handler` centralizzati, senza trapelare stack trace o messaggi interni.
- CORS con elenco esplicito di origini, mai `*` con credenziali. Limiti sulle dimensioni di body e upload.
- Query SQL parametrizzate (ORM del progetto o `text()` con parametri legati); nessun segreto nei log.

## Test
- `TestClient` (sincrono) o `httpx.AsyncClient` con `ASGITransport` per i test async con pytest-asyncio/anyio, secondo il progetto.
- Sostituisci le dipendenze con `dependency_overrides` e ripulisci dopo ogni test.
- Verifica anche autorizzazione e validazione (`422`), non solo il caso felice.
- Comandi tipici: `pytest -q`, `ruff check .`, `mypy .` come in `SKILL.md`.
