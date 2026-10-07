---
name: quarkus
description: Best practice Quarkus, con confronti con Spring Boot. Usala quando scrivi o rivedi codice Quarkus, o in progetti con io.quarkus nel pom.xml o build.gradle.
---

# Quarkus

Si applica insieme a `java` e `clean-code`, e ad `architettura-esagonale` se il progetto la adotta. Prevalgono le convenzioni del progetto. Chi viene da Spring Boot (vedi `spring-boot`) ritrova quasi tutto, ma con tre differenze di fondo: la CDI è risolta **a build time**, la configurazione è MicroProfile Config, e il codice deve poter girare anche come eseguibile nativo.

## Prima di tutto: versione ed estensioni
- Leggi la versione della piattaforma in `pom.xml` (`quarkus.platform.version`, BOM `quarkus-bom`) o `gradle.properties`, e usa solo ciò che esiste lì. Prima di consigliare un aggiornamento controlla su `quarkus.io` le versioni supportate e le LTS; non migrare pattern esistenti senza richiesta.
- Il progetto Quarkus 3 usa `jakarta.*`. Se trovi `javax.*` o RESTEasy classico (`quarkus-resteasy`), è una versione datata: `manutenzione-legacy` (se disponibile).
- Le funzionalità arrivano da **estensioni**, non da librerie qualsiasi. Prima di aggiungere una libreria cerca l'estensione (`quarkus extension list --installable --search=<testo>`, o la pagina Extensions su quarkus.io): le estensioni sanno come comportarsi in build nativa. Una nuova estensione è una nuova dipendenza: chiedi l'ok. Le versioni delle estensioni vengono dal BOM: non fissarle a mano.
- Gli artefatti hanno rinominato di recente: `quarkus-rest` (ex `quarkus-resteasy-reactive`), `quarkus-rest-jackson`, `quarkus-rest-client` (+ `-jackson`). Non mescolare le due famiglie (`resteasy` e `rest`) nello stesso progetto.

## CDI (ArC) rispetto a Spring DI
- Annotazioni Jakarta: `@ApplicationScoped` (default sensato, un'istanza, proxy lazy), `@Singleton` (senza proxy), `@RequestScoped`, `@Dependent` (default se non indichi nulla), `@Inject`. Non c'è `@Component`/`@Service`: servono scope esplicito.
- **Rimozione dei bean non usati**: ArC elimina a build time i bean che non sono iniettati da nessuna parte. Se un bean è usato solo via `Instance<>`, `CDI.current()` o riflessione, marcalo `@Unremovable`. Primo sospetto davanti a un "bean non trovato" a runtime, tipicamente in prod e non in test.
- Iniezione: per campo o costruttore, ma la **costruttore** resta preferibile (come in Spring). Con `@Inject` su campi, Quarkus consente campi package-private (niente `private`: evita la riflessione) e un costruttore unico non richiede `@Inject`.
- Producer con `@Produces` (equivale a `@Bean`); `@Alternative` + priorità, o `@DefaultBean`, `@IfBuildProfile` e `@IfBuildProperty` per scegliere a build time.
- Qualificatori (`@Named`, qualificatori propri) al posto di `@Qualifier`; `@Priority` per l'ordine.
- Eventi: `Event<T>` e `@Observes` al posto degli `ApplicationEvent` di Spring. `@Startup` (o `@Observes StartupEvent`) per l'avvio.
- Interceptor con `@InterceptorBinding`: niente self-invocation, come i proxy Spring. Su metodi `private` non funzionano.
- Niente dipendenze circolari tra bean con scope normale mascherate dai proxy: è un segnale di design.
- Le estensioni `spring-di`, `spring-web`, `spring-data-jpa` esistono per **migrare** codice Spring. In un progetto Quarkus nuovo non usarle: scrivi CDI e JAX-RS. Se già presenti, vanno lasciate finché il progetto non decide altrimenti.

## Configurazione
- File `src/main/resources/application.properties` (anche YAML con l'estensione `quarkus-config-yaml`). Segui il formato del progetto.
- **Profili** con prefisso: `%dev.`, `%test.`, `%prod.`; profili personalizzati con `quarkus.profile`. Variabili d'ambiente per i segreti (`QUARKUS_DATASOURCE_PASSWORD`, `MY_APP_KEY`), mai valori reali nei file versionati.
- Valori **build time** (fissi dopo il build, per esempio estensioni e ottimizzazioni) e **runtime**: se una proprietà build time cambia in `prod` a runtime, viene ignorata. Le tabelle della guida "All configuration options" le distinguono con un lucchetto.
- Tipizza con `@ConfigMapping(prefix = "app")` su un'interfaccia (come le `@ConfigurationProperties` a record di Spring), con `@WithDefault` e `Optional`; `@ConfigProperty` per valori singoli. Validazione con Bean Validation (`quarkus-hibernate-validator`).
- Test e CI: `%test.` non deve puntare ai database reali.

## REST (Quarkus REST)
- JAX-RS: `@Path`, `@GET`/`@POST`, `@Consumes`/`@Produces`. Controller sottili che delegano a un servizio (come in Spring); DTO dedicati (`record`), mai entity esposte.
- Il metodo sul **event loop** non deve bloccare. Con `quarkus-rest` un metodo che ritorna tipi normali gira su un worker thread (blocking); uno che ritorna `Uni`/`Multi` gira sull'event loop (non-blocking). Cambia il default con `@Blocking` / `@NonBlocking`. Un'attività di I/O bloccante in un metodo non-blocking blocca l'event loop: Quarkus lo segnala nei log.
- Virtual thread: `@RunOnVirtualThread` su endpoint bloccanti (Java 21+). Verifica la compatibilità delle librerie JDBC e i casi di *pinning* prima di diffonderlo.
- Errori: `@ServerExceptionMapper` (o `ExceptionMapper`) centralizzati, risposte coerenti (Problem Details se il progetto le usa), mai stack trace al client.
- Validazione: `@Valid` sui DTO e sui parametri; `quarkus-hibernate-validator`.
- Client: `quarkus-rest-client` con interfaccia `@RegisterRestClient(configKey = "...")`; timeout configurati sempre (`quarkus.rest-client."chiave".read-timeout`) e resilienza con `quarkus-smallrye-fault-tolerance` se il progetto l'ha già.
- OpenAPI con `quarkus-smallrye-openapi` e sicurezza con `quarkus-oidc`/`quarkus-security`: rispetta ciò che il progetto già usa; autorizza con `@RolesAllowed`/`@Authenticated` e controlli di appartenenza, non solo a livello di route.

## Persistenza: Hibernate ORM e Panache
- Estensioni: `quarkus-hibernate-orm`, `quarkus-hibernate-orm-panache`, driver `quarkus-jdbc-postgresql` (o equivalente). Migrazioni con `quarkus-flyway` o `quarkus-liquibase`; la proprietà di generazione dello schema (`schema-management.strategy`, nelle versioni più vecchie `database.generation`: verifica il nome nella guida della versione in uso) su `none` o `validate` fuori da dev e test.
- **Panache, due stili** (scegli quello del progetto, non mischiarli):
  - *Active record*: l'entity estende `PanacheEntity` (o `PanacheEntityBase`) e ha i metodi statici (`Persona.find(...)`, `persist()`). Poco codice, ma accoppia dominio e persistenza e rende difficile testare con mock.
  - *Repository*: `@ApplicationScoped class PersonaRepository implements PanacheRepository<Persona>`. È lo stile più vicino a Spring Data e quello da preferire con architettura esagonale o dominio ricco.
- I campi pubblici delle entity in active record sono riscritti in getter/setter dall'enhancement a build time: non è magia di runtime, e non va "aggiustata" aggiungendo getter a mano senza capirlo.
- **Transazioni**: `@Transactional` (Jakarta) sul servizio, come in Spring; senza, Panache sulle scritture solleva `TransactionRequiredException`. Valgono le stesse trappole: query lazy fuori dalla transazione, N+1 (`JOIN FETCH`, proiezioni), niente I/O esterno dentro la transazione.
- Query: parametri con nome o posizionali, mai concatenazioni. Proiezioni con `.project(Dto.class)`; paginazione con `page(Page.of(n, size))`.
- Reattivo: `quarkus-hibernate-reactive-panache` con `Uni`; richiede driver reattivi (`quarkus-reactive-pg-client`) e **non si mescola con** Hibernate ORM bloccante sullo stesso datasource. Con Hibernate Reactive le transazioni si dichiarano con `@WithTransaction` (o `Panache.withTransaction`), non con `@Transactional`.

## Imperativo o reattivo (Mutiny)
- Default: **imperativo** (`quarkus-rest` con tipi normali), eventualmente su virtual thread. Il codice è più semplice e meglio debuggabile, e Quarkus lo esegue comunque con costi contenuti.
- **Reattivo** (`Uni<T>`, `Multi<T>`) quando serve davvero: streaming (SSE, WebSocket), molte connessioni concorrenti con I/O lento, messaggistica (Kafka con SmallRye Reactive Messaging), client non bloccanti. Tutto lo stack della richiesta deve essere non bloccante, altrimenti il vantaggio sparisce.
- Mutiny è *lazy*: un `Uni` che nessuno sottoscrive non fa nulla. Non chiamare `.await().indefinitely()` su un thread event loop; lo stato mutabile condiviso resta un rischio.
- Un servizio che fa sia I/O bloccante sia reattivo: confinalo con `@Blocking` o `Uni.createFrom().item(...).runSubscriptionOn(Infrastructure.getDefaultWorkerPool())`.

## Dev mode e Dev Services
- `./mvnw quarkus:dev` (o `quarkus dev`): live reload, Dev UI su `/q/dev`, test continui con `r` o `quarkus.test.continuous-testing`. Le modifiche ai valori build time richiedono un riavvio automatico.
- **Dev Services** avviano container (database, Kafka, Keycloak, Redis…) in dev e in test se **non** configuri URL espliciti per quel servizio. Richiedono Docker/Podman: nella sandbox di Claude Code probabilmente non sono disponibili, e senza container i test falliscono per motivi che non riguardano il codice. Segnalalo, non aggirarlo disattivando i servizi (`quarkus.devservices.enabled=false`) senza ok.
- La configurazione di `%dev.` e `%test.` non deve diventare l'unica verificata: prova anche con il profilo `prod` (almeno un `@QuarkusIntegrationTest`).

## Test
- `@QuarkusTest` avvia l'applicazione una volta per suite: per questo i test non devono dipendere dall'ordine né dallo stato lasciato. Iniezione con `@Inject`; mock di bean CDI con `@InjectMock` (estensione `quarkus-junit-mockito`).
- `@QuarkusComponentTest` per testare un solo bean con dipendenze mockate, senza avviare tutto: più veloce per la logica di dominio. La logica pura va testata senza Quarkus.
- REST: REST Assured (`given().when().get(...).then().statusCode(200)`). `@TestHTTPEndpoint` evita di ripetere i percorsi. `@TestProfile` per cambiare configurazione in una classe (costa un riavvio).
- Database: i test girano su Dev Services (container reali): niente H2 al posto di Postgres se in produzione c'è Postgres.
- `@QuarkusIntegrationTest` esegue i test contro il **pacchetto** costruito (JAR, container, o eseguibile nativo): niente `@Inject` né mock, solo chiamate dall'esterno. Per questo di solito classi `*IT` che estendono il test (`class XIT extends XTest`). Il CI deve girare almeno una volta il profilo nativo, se il progetto rilascia in nativo.

## Build nativa (GraalVM / Mandrel)
- `./mvnw package -Dnative` (con `-Dquarkus.native.container-build=true` per compilare in container senza GraalVM locale). Mandrel è la distribuzione di GraalVM per Quarkus; la versione richiesta è nella guida della versione in uso.
- La build nativa è una **analisi statica a chiusura del mondo**: tutto ciò che si raggiunge solo via **riflessione**, risorse, proxy dinamici o serializzazione va registrato. Le estensioni lo fanno per le librerie supportate; per il codice proprio:
  - `@RegisterForReflection` sulle classi (DTO serializzati a mano, ad esempio con Jackson su tipi non rilevati);
  - `quarkus.native.resources.includes` per file in `resources`;
  - per le librerie senza estensione servono la configurazione GraalVM o un `ReflectiveClassBuildItem` in un'estensione.
- Sintomi tipici in nativo e non in JVM: `ClassNotFoundException` o campi null nei JSON, risorse non trovate, inizializzazione di classi a runtime. Prova presto la build nativa su un caso reale, non alla fine.
- Evita: caricamento dinamico di classi, `Class.forName` con nomi calcolati, agent Java, librerie con molta riflessione senza estensione. Tempi e memoria di build alti: la nativa si costruisce in CI o alla bisogna, non a ogni modifica.
- Costo e beneficio vanno dichiarati: avvio e memoria minori, throughput di picco spesso inferiore alla JVM con JIT, build lenta e debug più difficile. Non proporre il nativo senza un obiettivo di avvio o di densità.

## Osservabilità
- Health: `quarkus-smallrye-health` (`/q/health/live`, `/ready`, `/started`); readiness che dipende da risorse esterne, liveness no.
- Metriche: `quarkus-micrometer` (con registry, es. Prometheus) sono il percorso collaudato; OpenTelemetry in `quarkus-opentelemetry` per tracce e log. Esiste `quarkus-micrometer-opentelemetry` per usare Micrometer e OpenTelemetry insieme con output OTLP unificato. Verifica nella guida della versione quale combinazione è supportata.
- Log: JSON con `quarkus-logging-json` negli ambienti aggregati; mai segreti o dati personali nei log, MDC per correlazione.
- Gli endpoint `/q/*` (health, metrics, openapi) vanno protetti o esposti su un'interfaccia di gestione separata (`quarkus.management.enabled=true`), non lasciati aperti.

## Verifica
Usa il wrapper del progetto (`./mvnw` o `./gradlew`), offline nella sandbox se le dipendenze sono in cache (vedi `java`):
```bash
./mvnw -o verify               # test e *IT sul JAR
./mvnw -o verify -Dnative      # solo se il progetto rilascia in nativo
./mvnw quarkus:dev             # prova manuale, con Dev UI
```
Per ogni test fallito per mancanza di Docker o rete, riportalo come "non verificato" e non come passato. Zero segnalazioni Sonar sul codice scritto, come per `java`.
