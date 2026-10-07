# Django

Le convenzioni del progetto (struttura delle app, service layer, DRF o no) prevalgono. Controlla la versione in `pyproject.toml`/`requirements`: Django 5.2 è LTS (supporto esteso fino ad aprile 2028, da djangoproject.com/download, verificato il 03/10/2026); le versioni 6.x sono le più recenti. Gli aggiornamenti si leggono dalle release notes, non a memoria.

## Struttura
- Le view restano sottili: validazione e risposta. La logica di business va in funzioni o servizi testabili senza HTTP, nei modelli solo se riguarda il singolo oggetto.
- Una app per concetto di dominio; niente app "utils" o "core" che diventano cassetti.
- Impostazioni separate per ambiente (o variabili d'ambiente), segreti mai nel repository, `DEBUG=False` fuori dallo sviluppo.
- Modello utente personalizzato (`AUTH_USER_MODEL`) all'inizio del progetto: cambiarlo dopo è costoso.

## ORM e query
- **N+1**: un ciclo che accede a una relazione esegue una query per riga. `select_related` per FK e one-to-one (JOIN), `prefetch_related` per many-to-many e relazioni inverse; `Prefetch(...)` con queryset filtrato quando serve. Verifica con `assertNumQueries` o `django-debug-toolbar`, non a occhio.
- `only()`/`defer()`/`values()` quando servono pochi campi; `exists()` invece di `len(qs) > 0`; `count()` invece di `len(qs)`.
- Aggiornamenti in blocco con `update()`, `bulk_create`, `bulk_update` (non chiamano `save()` né i signal). Valori calcolati dal DB con `F()` per evitare race condition ("leggi, incrementa, scrivi").
- `transaction.atomic` attorno alle scritture che devono essere coerenti; `select_for_update()` solo dentro una transazione. Gli effetti esterni (mail, task) con `transaction.on_commit`.
- `get()` lancia `DoesNotExist` e `MultipleObjectsReturned`: gestiscili; `get_object_or_404` nelle view.
- Query SQL grezze solo con parametri (`raw(sql, params)`), mai f-string.

## Migrazioni
- Una migrazione per modifica, generata con `makemigrations` e **letta** prima del commit; vanno nel repository.
- Mai modificare una migrazione già applicata altrove: ne crei una nuova.
- Cambi distruttivi in più passi (aggiungi nullable, riempi, rendi obbligatorio; rimuovi l'uso, poi la colonna) per non rompere il deploy con vecchio e nuovo codice insieme.
- Le migrazioni dati con `RunPython` hanno sempre l'inversa (o `noop` dichiarato) e usano `apps.get_model`, non i modelli importati.
- Controlla la coerenza con `makemigrations --check --dry-run` in CI.

## Sicurezza
- Lascia attivi `CsrfViewMiddleware`, `SecurityMiddleware`, `XFrameOptionsMiddleware`. `@csrf_exempt` solo con un motivo (webhook con firma verificata).
- Output: i template fanno l'escape; `mark_safe` e `|safe` mai su dati dell'utente.
- `ALLOWED_HOSTS` valorizzato; in produzione `SECURE_SSL_REDIRECT`, cookie `Secure`/`HttpOnly`, HSTS. `python manage.py check --deploy` elenca cosa manca.
- Autorizzazione per oggetto, non solo per vista: filtra i queryset sull'utente (`get_queryset`) per evitare accessi ad ID altrui (IDOR). In DRF `permission_classes` esplicite.
- Upload: valida tipo e dimensione, salva fuori dalla root servita come codice, nomi generati.
- Password con gli hasher di Django; mai loggare `request.POST` intero.

## Test
- Il runner del progetto (`manage.py test` o pytest-django). `TestCase` annulla le modifiche con una transazione; `TransactionTestCase` solo se testi il commit.
- Dati con factory (factory_boy o funzioni del progetto) al posto di fixture JSON.
- `Client`/`APIClient` per le view, test diretti per i servizi. Verifica permessi (anonimo, altro utente) oltre al caso felice.
- Comandi: `python manage.py test` oppure `pytest`; `python manage.py makemigrations --check --dry-run`; `python manage.py check --deploy` per la configurazione di produzione.
