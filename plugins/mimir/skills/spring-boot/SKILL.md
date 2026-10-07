---
name: spring-boot
description: Best practice Spring Boot 3.x/4.x. Usala quando scrivi, modifichi o rivedi codice Spring o Spring Boot, o in progetti con spring-boot-starter in pom.xml o build.gradle.
---

# Spring Boot

Si applica insieme a `java` e `clean-code`, e ad `architettura-esagonale` se il progetto la adotta. Prevalgono le convenzioni del progetto: struttura, librerie, stile di configurazione e versione.

## Prima di tutto: la versione
Leggi la versione di Spring Boot nel `pom.xml` o nel `build.gradle` (parent o BOM) e usa solo le API disponibili lì. Non migrare pattern esistenti se non è richiesto: segnala l'opportunità.

| Versione | Da sapere |
|---|---|
| 2.x | Java 8+, `javax.*`, Spring Framework 5. Sicurezza con `WebSecurityConfigurerAdapter` (deprecato dalla 2.7), test con `@MockBean`, a volte ancora JUnit 4 (vintage). Per il resto vale `manutenzione-legacy` |
| 3.x | Java 17+, `jakarta.*`, Spring Framework 6. Da 3.1 `@ServiceConnection` per Testcontainers; da 3.2 `RestClient` e virtual thread; da 3.4 `@MockitoBean` (sostituisce `@MockBean`), `MockMvcTester` e log strutturati |
| 4.x | Spring Framework 7, Jackson 3 (package `tools.jackson`, Jackson 2 deprecato), starter modulari, Undertow rimosso. Novità: client HTTP dichiarativi auto-configurati (`@ImportHttpServices`), versioning delle API (`spring.mvc.apiversion.*`), `RestTestClient`, null safety con JSpecify, `@Retryable` e `@ConcurrencyLimit` nel core |

Dalla 4 molti package di auto-configuration e test sono cambiati: segui gli import già presenti nel progetto e la documentazione della versione in uso.

## Configurazione
- **`@ConfigurationProperties`** tipizzate, meglio se `record`, con `@Validated`, invece di `@Value` sparsi nel codice.
- **Profili** per le differenze tra ambienti. Niente logica condizionale sul nome del profilo nel codice.
- **Mai segreti** in `application.yml` o `application.properties` versionati: usa variabili d'ambiente, un vault o un secret manager.
- `spring.jpa.open-in-view=false`: evita query lazy inattese durante il rendering della risposta.
- Le librerie di terze parti si configurano con `@Bean` in classi `@Configuration` dedicate, piccole e per argomento.

## Dependency injection
- Solo **injection da costruttore**: campi `private final` con `@RequiredArgsConstructor` o un costruttore esplicito. Mai `@Autowired` su campi o setter.
- Niente dipendenze circolari: sono un segnale di design da correggere, non da aggirare con `@Lazy`.
- Niente `ApplicationContext.getBean()` nel codice applicativo.

## REST
Le regole di design valide per ogni stack (risorse, status code, errori, paginazione, versioning, idempotenza) sono in `design-api`. Qui come si applicano in Spring.
- **Controller sottili**: validano l'input, mappano i DTO e delegano a un service o caso d'uso. Nessuna logica di business.
- **DTO dedicati**, meglio se `record`, per request e response. Mai esporre entity JPA.
- **Validazione ai confini** con Bean Validation (`@Valid`, `@NotNull`, `@Size`…) sui DTO in ingresso.
- **Errori**:
  - gestione centralizzata in `@RestControllerAdvice`;
  - risposte `ProblemDetail` (RFC 9457);
  - eccezioni di dominio mappate su status HTTP coerenti.
  - Mai stack trace nella risposta.
- **Status code** con `ResponseEntity` o `@ResponseStatus`: `201` con `Location` (`ServletUriComponentsBuilder`), `404` per una risorsa non trovata, mai un `200` con body vuoto o `null`.
- **Paginazione** con `Pageable` o cursori.
- **Versioning**: il meccanismo del progetto. Dalla 4 c'è il supporto nativo (`spring.mvc.apiversion.*`).

## Persistenza e transazioni
- **`@Transactional` sul layer service o application**, non su controller o repository custom.
  - `readOnly = true` per le operazioni di sola lettura.
- **Attenzione ai proxy**: `@Transactional`, `@Async`, `@Cacheable` e `@Retryable` non funzionano su metodi `private` né su chiamate interne alla stessa classe (self-invocation).
- **Fetch lazy di default.** Evita il problema N+1 con `JOIN FETCH`, `@EntityGraph` o proiezioni.
- **Proiezioni** (interfacce o record DTO) per le letture che non richiedono l'entity completa.
- **Entity**:
  - niente `@Data`;
  - `equals` e `hashCode` basati sull'identificativo e sicuri con i proxy, oppure non ridefiniti;
  - costruttore protetto per JPA.
- **Schema gestito con migrazioni** (Flyway o Liquibase). `ddl-auto` a `validate` o `none` fuori dallo sviluppo locale.
- **Niente I/O esterno dentro una transazione**: chiamate HTTP, messaggi, email. Tengono occupata la connessione al DB e, se la transazione poi fallisce, l'effetto esterno è già avvenuto.
  - Per gli effetti successivi usa `@TransactionalEventListener(phase = AFTER_COMMIT)`.
  - Se serve garantire l'invio, usa il pattern outbox.
- Transazioni brevi: niente elaborazioni lunghe mentre la connessione è aperta.
- **Segnali da cercare in review**:
  - `@Query` che modifica dati senza `@Modifying` (e senza `clearAutomatically` se dopo si rilegge l'entity);
  - `CascadeType.ALL` o `REMOVE` su relazioni verso entity condivise, e `orphanRemoval` messo senza volerlo;
  - `FetchType.EAGER` sulle collection;
  - `findAll()` o liste senza paginazione su tabelle che crescono;
  - stato mutabile in campi di un bean singleton.
- Pool di connessioni, indici, batch e migrazioni: `references/jpa.md`.

## Client HTTP
- `RestClient` per le chiamate sincrone, `WebClient` solo in contesti reattivi. `RestTemplate` è legacy: non usarlo nel codice nuovo.
- **Client dichiarativi** (`@HttpExchange`, `@GetExchange`…) per le integrazioni strutturate. Dalla 4 si importano con `@ImportHttpServices` e si configurano via `spring.http.serviceclient.<gruppo>.*`.
- **Timeout sempre configurati** (connessione e lettura).
- Retry solo su operazioni idempotenti, con backoff.
- Errori delle chiamate esterne tradotti in eccezioni di dominio, dentro l'adapter.

## Concorrenza
- Con Java 21+ valuta i virtual thread (`spring.threads.virtual.enabled=true`) per i carichi I/O-bound, se il progetto li adotta.
- `@Async` e `@Scheduled` con executor configurati esplicitamente, non quelli di default.

## Sicurezza
- Configurazione di Spring Security con un bean `SecurityFilterChain`. `WebSecurityConfigurerAdapter` non esiste più.
- Autorizzazione a livello di metodo (`@PreAuthorize`) per le regole di dominio. Negare di default, aprire in modo esplicito.
- CSRF: disabilitalo solo per API stateless con token, mai per applicazioni con sessione e cookie.
- Esponi solo gli endpoint Actuator necessari (`health`, `info`, `prometheus`…), protetti.
- **CORS** configurato nella filter chain con origini esplicite: mai `*` insieme alle credenziali, mai `*` in produzione.
- **Cookie di sessione** `HttpOnly`, `Secure` e con `SameSite` adeguato.
- **Upload**: limiti di dimensione (`spring.servlet.multipart.*`), tipo verificato sul contenuto e non solo sull'estensione, nome del file mai usato così com'è per scrivere su disco.

## Osservabilità
- Actuator e Micrometer per metriche e health. Tracing con Micrometer Tracing oppure OpenTelemetry (dalla 4 c'è `spring-boot-starter-opentelemetry`).
- Log strutturati (`logging.structured.format.console`) quando c'è un aggregatore di log.
- Trace ID nei log, per correlare le richieste.

## Test
- **Unit test senza Spring** per service e logica di dominio: istanzia la classe e mocka le dipendenze con Mockito. Sono i più veloci.
- **Test slice** per un singolo layer, invece di `@SpringBootTest` ovunque:
  - `@WebMvcTest` (con `MockMvcTester` o `RestTestClient`);
  - `@DataJpaTest`;
  - `@JsonTest`;
  - `@RestClientTest`.
- **`@SpringBootTest`** solo per i test di integrazione end-to-end (`*IT`).
- **`@MockitoBean`** e `@MockitoSpyBean` per sostituire bean nel contesto. `@MockBean` è deprecato.
- **Database e servizi reali** con Testcontainers e `@ServiceConnection`, invece di H2 quando il dialetto conta.
- `@DataJpaTest` è transazionale e fa rollback a fine test: tienine conto quando verifichi flush, lazy loading o vincoli.
- Riusa il contesto di Spring tra i test: evita configurazioni diverse per ogni classe e `@DirtiesContext` superflui.

## Verifica
Prima di dichiarare finito, segui `references/verifica.md`: build, test, analisi statica e rilettura del diff, con i comandi lanciati e l'esito riportati nel resoconto. Se l'avvio o la build falliscono, `references/diagnosi-build.md` raccoglie le cause tipiche.

## Struttura
- **Package per feature o per layer esagonale**, non per tipo tecnico globale (niente `controllers/`, `services/` a livello radice), salvo convenzione del progetto.
- Classe `@SpringBootApplication` nel package radice.
