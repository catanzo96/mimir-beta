---
name: php
description: Best practice PHP moderno (8.x). Usala quando scrivi, modifichi o rivedi codice PHP, Laravel o Symfony, o in progetti con composer.json o file .php.
---

# PHP

Si applica insieme a `clean-code`. Le convenzioni del progetto, il framework e la versione di PHP in uso (`composer.json`, sezione `require.php`) prevalgono: non usare feature non disponibili. **Su versioni di PHP fuori supporto (vedi php.net/supported-versions), framework non più supportati o senza test, vale `manutenzione-legacy` (se disponibile).**

## Prima di tutto: la versione
Leggi `require.php` e `config.platform.php` in `composer.json`, poi `php -v`: possono differire. Verifica le feature sulla versione minima supportata dal progetto, non su quella installata in locale.

| Versione | Feature utili |
|---|---|
| 8.0 | named arguments, attributi, `match`, union type, constructor promotion, nullsafe `?->`, `str_contains` |
| 8.1 | `enum`, proprietà `readonly`, first-class callable `f(...)`, tipi `never` e intersection, `new` negli inizializzatori, `array_is_list` |
| 8.2 | classi `readonly`, tipi `null`/`false`/`true` autonomi, DNF type, `#[\SensitiveParameter]` |
| 8.3 | costanti di classe tipizzate, `#[\Override]`, `json_validate`, `readonly` riscrivibile in `__clone` |
| 8.4 | property hooks, visibilità asimmetrica (`public private(set)`), `#[\Deprecated]`, `array_find`/`array_any`/`array_all`, lazy object, `new Foo()->metodo()` senza parentesi. Deprecato il tipo implicitamente nullable (`Foo $x = null`: scrivi `?Foo`) |
| 8.5 | operatore pipe `\|>`, `clone` con modifica di proprietà, `#[\NoDiscard]`, `array_first`/`array_last`, estensione URI |

Le versioni con supporto attivo cambiano ogni anno: controlla php.net/supported-versions.php prima di consigliare un salto di versione, e segnala (senza farla) una versione fuori supporto.

## Tipi e stile
- `declare(strict_types=1);` in ogni file nuovo: senza, `"5"` viene convertito silenziosamente in `5`. Il flag vale per le chiamate **fatte dal file**, quindi non protegge i valori che arrivano da fuori (request, DB, JSON): lì valida.
- Tipizza parametri, ritorni e proprietà. `mixed` solo dove è davvero il contratto; negli array descrivi la forma con i docblock per l'analisi statica (`list<Ordine>`, `array{id: int, nome: string}`).
- `enum` (backed) per insiemi chiusi, con `tryFrom()` ai confini; `match` invece di `switch`, perché è esaustivo e fa errore (`UnhandledMatchError`) senza ramo.
- `readonly` (proprietà o classe) per value object e DTO. Mutazione = nuovo oggetto.
- Costruttori con promotion per i servizi: le dipendenze sono `private readonly`.
- Confronti sempre con `===`. `==` ha regole di conversione che cambiano tra versioni, e `in_array`/`array_search` vanno chiamati con `strict: true`.
- `null` esplicito nel tipo (`?Utente`) e nullsafe solo dove l'assenza è un caso previsto, non per nascondere errori. Per le collezioni: array vuoto, mai `null`.
- Named arguments nel codice del progetto sì; verso librerie esterne no, se la libreria non garantisce i nomi dei parametri (Laravel, per esempio, li esclude dalla compatibilità).
- Niente `@` per sopprimere errori, niente `extract`, `eval`, variabili variabili.

## Composer e autoload
- Autoload **PSR-4** (`"autoload": {"psr-4": {"App\\": "src/"}}`): un file per classe, namespace uguale al percorso. Dopo modifiche all'autoload: `composer dump-autoload`.
- Versioni con `^`. Il `composer.lock` si versiona per le applicazioni, non per le librerie. In CI e in produzione `composer install --no-dev --optimize-autoloader`, mai `update`.
- Prima di proporre una dipendenza nuova: manutenzione, licenza, `composer audit`.
- Se usi estensioni (`ext-intl`, `ext-pdo_pgsql`) dichiarale in `require`.

## Standard PSR
- Stile: PSR-12 / PER-CS, applicato dallo strumento del progetto (PHP-CS-Fixer, Pint, PHPCS). Non riformattare file che non tocchi.
- Dipendi dalle interfacce: `Psr\Log\LoggerInterface` (PSR-3), `Psr\Http\Message` e `ClientInterface` (PSR-7/18), `Psr\Container\ContainerInterface` (PSR-11, solo nel codice di infrastruttura: nei servizi mai un container iniettato come service locator).
- Logging PSR-3 con segnaposto e contesto: `$log->warning('Ordine {id} rifiutato', ['id' => $id])`. Niente dati personali o token nel contesto.

## Eccezioni ed errori
- Eccezioni di dominio che estendono `\DomainException` o una base del progetto; `\Throwable` si cattura solo ai confini (handler globale, entry point di comandi e code).
- Mantieni la causa: `throw new PagamentoFallito('…', previous: $e)`.
- Non inghiottire: un `catch` vuoto o che fa solo `return null` nasconde il guasto.
- Errori e warning di PHP non sono eccezioni: in sviluppo e in test trasformali (il framework di solito lo fa; in script puri usa un error handler che lancia `ErrorException`).
- `display_errors=Off` in produzione, `log_errors=On`.

## Sicurezza
Il metodo generale è in `clean-code/references/sicurezza.md`. Trappole specifiche di PHP:
- **SQL**: PDO con prepared statement e `ATTR_EMULATE_PREPARES => false`, `ERRMODE_EXCEPTION`. Mai concatenare input, nemmeno in `ORDER BY` o nomi di colonna: lì whitelist. Nei query builder, attenzione ai metodi "raw".
- **XSS**: escaping in uscita, per contesto. Nei template del framework (Blade `{{ }}`, Twig) è automatico; `{!! !!}`, `|raw`, `echo` diretti no. Fuori dai template: `htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')`.
- **CSRF**: token su ogni richiesta che modifica stato in sessione/cookie; i framework lo fanno, verifica che non sia disattivato per comodità. Cookie di sessione `HttpOnly`, `Secure`, `SameSite`.
- **Password**: `password_hash()` (default o Argon2id) e `password_verify()`, `password_needs_rehash()` al login. Mai MD5/SHA1. Token casuali con `random_bytes()`/`random_int()`, mai `rand`/`mt_rand`. Confronti di segreti con `hash_equals()`.
- **Upload**: valida il tipo reale (`finfo`, non il nome o il `Content-Type` del client), dimensione, estensione da whitelist; salva fuori dalla document root con nome generato; mai `include` o esecuzione di file caricati.
- **Percorsi e inclusioni**: niente `include`/`require` con input; `realpath()` e controllo del prefisso per i file letti su richiesta.
- **Deserializzazione**: mai `unserialize()` su dati non fidati (gadget chain, `__destruct`, `__wakeup`); usa JSON, o `unserialize($s, ['allowed_classes' => false])` se obbligato.
- **Comandi e SSRF**: `escapeshellarg` non basta, preferisci librerie (Symfony Process con array di argomenti); valida gli URL richiesti dal server.
- **Mass assignment**: non passare `$request->all()` a un modello o a un hydrator; whitelist dei campi o DTO.
- `#[\SensitiveParameter]` (8.2) sui parametri con segreti, per tenerli fuori dagli stack trace.

## Test
- Usa il framework del progetto: PHPUnit (attributi `#[Test]`, `#[DataProvider]` dalla 10; le annotazioni docblock sono deprecate) oppure Pest. Non introdurre l'altro.
- Unit test sul dominio senza framework né DB; test di integrazione/feature su DB reale di test (transazione o refresh per test), non su un mock del DB.
- Mock solo ai confini (HTTP, mail, orologio). Orologio iniettabile (`Psr\Clock\ClockInterface`).
- Un bug = un test che lo riproduce, prima della correzione.

## Analisi statica e qualità
- PHPStan o Psalm, al livello già configurato nel progetto (baseline inclusa): il codice nuovo non aggiunge voci alla baseline. Non alzare il livello senza richiesta.
- Estensioni di framework (Larastan, phpstan-symfony) già presenti: non toglierle.
- Doctrine/Eloquent e array "magici" sono il punto dove i tipi si perdono: aggiungi docblock generici.

## Framework
Quando il progetto usa Laravel leggi `references/laravel.md` (Eloquent e N+1, migrazioni, validazione, code, policy). Per Symfony leggi `references/symfony.md` (servizi e autowiring, Doctrine, form, sicurezza). Se il codice è PHP puro o un altro framework, bastano le sezioni sopra.

## Verifica
Usa gli script già in `composer.json` (`composer run -l` per vederli). Tipicamente:
```bash
composer validate --strict
vendor/bin/phpunit            # oppure vendor/bin/pest, php artisan test, bin/phpunit
vendor/bin/phpstan analyse    # oppure vendor/bin/psalm
vendor/bin/pint --test        # oppure php-cs-fixer fix --dry-run --diff, phpcs
composer audit
```
Lancia solo gli strumenti configurati e limita il controllo di stile ai file toccati. Riporta quali comandi hai eseguito e con quale esito; se un servizio (DB, Redis) non è disponibile, dillo invece di dichiarare i test verdi.
