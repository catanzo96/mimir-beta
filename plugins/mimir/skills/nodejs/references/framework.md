# Framework Node: Express, Fastify, NestJS

Usa il framework del progetto e le sue convenzioni. Versione e plugin si controllano nella documentazione ufficiale (Context7), non a memoria: Express 5, per esempio, gestisce le promise rifiutate nei handler, Express 4 no.

## Comune
- Tre strati: handler HTTP sottile (parsing, validazione, risposta) -> servizio (logica) -> accesso ai dati. Gli handler non contengono regole di business.
- Validazione di body, query, params e header con schema al confine; il tipo si ricava dallo schema.
- Errori: eccezioni di dominio tipizzate, mappate in un unico punto in risposte con codice e corpo coerenti (formato del progetto, ad esempio problem+json). Mai stack trace o messaggi interni al client.
- Autorizzazione per risorsa, non solo autenticazione. Per l'idea di fondo vedi `architettura-esagonale` se il progetto la adotta.
- Configurazione e dipendenze iniettate, non importate come singleton globali: il test sostituisce ciò che sta al confine.

## Express
- I middleware sono una catena ordinata: l'ordine è parte del comportamento (parser, sicurezza, autenticazione, route, 404, error handler per ultimo).
- L'error handler ha quattro argomenti `(err, req, res, next)`. In Express 4 le funzioni `async` non inoltrano gli errori: avvolgile con un wrapper o usa Express 5.
- `express.json({ limit })` con limite esplicito; `helmet`, CORS ristretto, `trust proxy` impostato solo se dietro un proxy noto.
- Mai due risposte per richiesta: dopo `res.send` usa `return`. Router per area, non un unico file di route.

## Fastify
- Encapsulation: i plugin (`fastify.register`) hanno scope proprio; decora (`decorate`) invece di variabili globali. Rispetta l'ordine di caricamento.
- Schema JSON (o type provider con Zod/TypeBox) su route: validazione in ingresso e serializzazione veloce in uscita; lo schema di risposta evita di far uscire campi non voluti.
- Hook (`onRequest`, `preHandler`, `onClose`) per autenticazione e risorse; `setErrorHandler` centralizzato.
- Logger (pino) integrato: usa `request.log`, che porta già l'id di richiesta. Test con `app.inject()` senza aprire porte.
- Handler `async` o callback, mai entrambi.

## NestJS
- Moduli per area funzionale; esporta solo ciò che serve agli altri. Provider iniettati da costruttore; dipendenze circolari (`forwardRef`) sono un segnale di confini sbagliati.
- Controller sottili, logica nei provider (service). I DTO sono classi con `class-validator` e `ValidationPipe` globale (`whitelist: true`, `forbidNonWhitelisted`, `transform`), oppure lo schema che il progetto ha scelto (Zod).
- Guard per autenticazione e autorizzazione, pipe per validazione e trasformazione, interceptor per logging e mappatura delle risposte, exception filter per gli errori. Non duplicare la stessa logica trasversale nei controller.
- `ConfigModule` con validazione dello schema all'avvio; `ConfigService` iniettato.
- Test: `Test.createTestingModule` con provider sostituiti (`overrideProvider`); unit test sui service, e2e con supertest sui controller.
- Chiusura ordinata: `app.enableShutdownHooks()` e i metodi `onModuleDestroy`/`onApplicationShutdown` per chiudere pool e client.

## Altri runtime
Bun e Deno esistono e hanno API proprie (Bun con test runner e bundler integrati, Deno con permessi e supporto TypeScript nativo). Se un progetto li usa, segui la loro documentazione; non assumere che un modulo Node funzioni identico e non proporre il cambio di runtime senza richiesta.
