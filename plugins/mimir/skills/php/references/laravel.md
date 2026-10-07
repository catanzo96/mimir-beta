# Laravel

Leggi questo file quando il progetto ha `laravel/framework` in `composer.json`. Controlla la versione (`composer show laravel/framework`): le versioni recenti sono documentate in laravel.com/docs/releases, e vanno rispettati i vincoli di PHP minimo di ciascuna. Le convenzioni già presenti nel progetto (struttura cartelle, Actions, Repository, DTO) prevalgono.

## Eloquent e N+1
- Il N+1 nasce quando accedi a una relazione dentro un ciclo. Carica con `with()` (o `load()` dopo il fatto), e per i conteggi `withCount()`.
- In sviluppo e nei test attiva `Model::preventLazyLoading(! app()->isProduction())`: il lazy loading diventa un'eccezione e il problema emerge subito. Lo stesso per `Model::shouldBeStrict()` (include accessi ad attributi mancanti).
- Seleziona solo le colonne che servono, `chunkById()` o `lazyById()` per grandi volumi; `cursor()` non carica tutto ma tiene una query aperta.
- Per le aggregazioni usa il database (`sum`, `groupBy`), non collection in memoria.
- Scope e query object per le condizioni riusate; la logica non va nei controller.
- Mass assignment: `$fillable` esplicito, mai `$guarded = []` e mai `Model::create($request->all())`: usa `$request->validated()`.
- `casts` per enum, date, JSON; l'enum backed è il modo giusto di rappresentare uno stato.
- Transazioni: `DB::transaction(fn () => …)`. Gli effetti esterni (mail, job) dopo il commit: `afterCommit` sui job, `ShouldDispatchAfterCommit` sugli eventi.

## Migrazioni
- Una migrazione fa una cosa e non si modifica dopo il rilascio: ne crei una nuova.
- Su tabelle grandi, valuta il lock di `ALTER TABLE` e ordina le fasi (aggiungi colonna nullable, riempi, rendi obbligatoria).
- Scrivi `down()` solo se il progetto lo usa davvero; non inserire dati di produzione nelle migrazioni, per quello ci sono seeder o comandi.
- Chiavi esterne e indici espliciti: ogni colonna usata in `where` o `join` ricorrente va valutata.

## Validazione e autorizzazione
- Form Request per ogni endpoint che scrive: `rules()` e, se serve, `authorize()`. Usa `$request->validated()` o `safe()`, mai `all()`.
- Regole in forma di oggetti (`Rule::enum`, `Rule::unique(...)->ignore($id)`) quando c'è logica.
- **Policy** per l'autorizzazione di ogni risorsa (`Gate`, `$this->authorize`, `can:` nel routing, o gli attributi `#[Authorize]` nelle versioni che li hanno). Non basta nascondere un pulsante: controlla sempre lato server, e controlla l'appartenenza (IDOR: `Ordine` dell'utente giusto).
- Rotte API: `auth:sanctum` (o il guard del progetto), rate limiting con `RateLimiter`/`throttle`, risorse API (`JsonResource`) invece di restituire i modelli, per non esporre campi interni.

## Code e job
- Job piccoli, idempotenti, con `$tries`, `backoff` e `$timeout` espliciti; il payload porta gli ID, non i modelli interi (il modello viene riletto, e con `SerializesModels` può non esistere più).
- `ShouldBeUnique` o `WithoutOverlapping` quando due esecuzioni parallele sarebbero un danno.
- Gestisci `failed()` e monitora la coda (Horizon se in uso). I worker tengono il codice in memoria: dopo un deploy `queue:restart`.
- Con Octane/worker persistenti niente stato statico o singleton che trattengono dati di una richiesta.

## Sicurezza specifica
- `APP_DEBUG=false` e `APP_KEY` solo in produzione; `.env` mai versionato.
- Blade: `{{ }}` esegue l'escaping, `{!! !!}` no. Query: `whereRaw`, `DB::raw`, `orderByRaw` con binding (`?`), mai concatenazioni.
- CSRF attivo sulle rotte web; le eccezioni (`validateCsrfTokens(except: …)`) vanno motivate.
- File: `Storage` con disco privato e URL temporanei firmati; `$request->file()->store()` genera il nome.
- Cookie e sessione: guarda `config/session.php` (`secure`, `same_site`).

## Test
- Feature test con `RefreshDatabase` (o `LazilyRefreshDatabase`) e factory; `actingAs()` per l'autenticazione. Verifica anche i casi negati (403/404/422), non solo il percorso felice.
- `Queue::fake()`, `Mail::fake()`, `Event::fake()`, `Http::fake()` per i confini. `Http::preventStrayRequests()` fa fallire le chiamate vere dimenticate.
- Con Pest: la stessa struttura con `it()`/`expect()`; con PHPUnit: test class. Segui quello che c'è.

## Verifica
```bash
php artisan test            # oppure vendor/bin/pest
vendor/bin/pint --test
vendor/bin/phpstan analyse  # Larastan se configurato
php artisan migrate:status  # solo su DB locale/di test
php artisan route:list      # per controllare middleware e policy
```
Non lanciare `migrate`, `db:seed` o `migrate:fresh` su un database che non sia di sviluppo o di test.
