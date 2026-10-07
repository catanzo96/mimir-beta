# Symfony

Leggi questo file quando il progetto ha `symfony/framework-bundle`. Controlla la versione in `composer.lock` (le versioni e le LTS sono su symfony.com/releases) e leggi la documentazione di quella: le feature si spostano tra minori. Le convenzioni del progetto prevalgono.

## Servizi e autowiring
- Dipendenze dal costruttore, tipizzate sull'interfaccia: l'autowiring risolve da solo se esiste un solo servizio per quel tipo. Con più implementazioni: alias esplicito in `services.yaml`, `#[Autowire(service: '…')]` o `#[AsAlias]`.
- Servizi `private` (default): non si prendono dal container con `$container->get()`. Nei test usa il container di test (`static::getContainer()`).
- Parametri e segreti: `#[Autowire('%env(API_KEY)%')]` o `#[Autowire(param: '…')]`; i segreti in produzione nel Secrets vault o nelle variabili d'ambiente, mai in `.env` versionato con valori reali.
- Più implementazioni selezionabili a runtime: `#[AutowireIterator]`, `#[AutowireLocator]` con tag, invece di iniettare il container.
- Event listener e subscriber con `#[AsEventListener]`; handler dei messaggi con `#[AsMessageHandler]`.
- Controller sottili, `AbstractController` solo se servono i suoi helper; i ruoli degli argomenti con `#[MapRequestPayload]`, `#[MapQueryString]`, `#[MapEntity]` per DTO e validazione già al confine.
- Dopo modifiche alla configurazione: `bin/console debug:container <servizio>`, `debug:autowiring`, `lint:container`.

## Doctrine
- Entity senza logica di infrastruttura; mapping con attributi (`#[ORM\Entity]`). Repository per le query: niente DQL nei controller.
- N+1: `JOIN` con `addSelect()` o `fetch: 'EAGER'` solo dove serve; per le liste di sola lettura proietta in DTO (`SELECT NEW …`).
- `flush()` una volta, al confine dell'operazione (handler, controller), non in ogni metodo di servizio. Per più scritture atomiche `wrapInTransaction()`.
- Migrazioni con `doctrine/doctrine-migrations-bundle` (`make:migration`, poi **leggi** il SQL generato: a volte include modifiche non volute). `doctrine:schema:update --force` mai in ambienti condivisi.
- `EntityManager` chiuso dopo un errore: in worker di lunga durata (Messenger) la gestione è del bundle, non riaprirlo a mano.
- Query: parametri con `setParameter()`, mai interpolati.

## Form e validazione
- Form type per l'input HTML; per le API preferisci DTO con `#[Assert\…]` e `MapRequestPayload`. Mai legare il form direttamente a un'entity con campi sensibili (`roles`, `isAdmin`): usa un DTO.
- Vincoli con `symfony/validator`, anche su classi non-entity. I gruppi di validazione solo se servono davvero.
- CSRF dei form è automatico; per le azioni fuori da form (`DELETE` via link) `isCsrfTokenValid()`.

## Sicurezza
- Firewall e `access_control` in `security.yaml`: l'ordine conta (vince la prima regola che corrisponde). Poi autorizza anche nel codice con `#[IsGranted]` o i voter: `access_control` da solo non basta per i controlli per-risorsa.
- **Voter** per le regole sulla singola risorsa (`ORDER_EDIT`), non `if` sui ruoli sparsi.
- Password: `PasswordHasherInterface` con `auto` e `migrate_from` per i cambi di algoritmo. Mai un hasher scritto a mano.
- Login: `form_login`/`json_login`, `login_throttling` attivo; per i token, `access_token` o lo strumento già in uso.
- Twig fa l'escaping di default: attenzione a `|raw` e a `{% autoescape false %}`.
- Debug: `APP_ENV=prod`, `APP_DEBUG=0`; la web profiler toolbar mai in produzione.
- Upload: `File` con constraint `#[Assert\File(mimeTypes: …)]`, nome generato, salvataggio fuori da `public/`.

## Messenger e cache
- Messaggi con dati semplici (ID, scalari); handler idempotenti; configura retry e transport di fallimento (`failed`). Dopo un deploy `messenger:stop-workers`.
- Cache con `CacheInterface::get($chiave, callback)`: la chiave non contiene caratteri riservati e la scadenza è esplicita.

## Test
- `KernelTestCase` per servizi, `WebTestCase` per i flussi HTTP, `PHPUnit` come runner. Per i DB, `dama/doctrine-test-bundle` o ricreazione dello schema, se già usati.
- Verifica anche accessi negati e validazione fallita, non solo il caso felice.

## Verifica
```bash
bin/console lint:container
bin/console lint:yaml config && bin/console lint:twig templates
bin/console doctrine:schema:validate    # su DB locale
bin/phpunit
vendor/bin/phpstan analyse              # con phpstan-symfony/doctrine se presenti
```
