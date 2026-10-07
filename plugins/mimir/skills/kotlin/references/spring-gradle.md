# Kotlin con Spring Boot e Gradle

Da leggere quando il progetto è Kotlin con Spring Boot o JPA, o quando tocchi `build.gradle.kts`. Per Spring in sé vedi `spring-boot`; per JPA e le sue regole `java` e `spring-boot`.

## Plugin del compilatore
- Le classi Kotlin sono `final`, ma Spring ha bisogno di sottoclassi (proxy per `@Transactional`, `@Configuration`, `@Cacheable`…). Il plugin **`kotlin("plugin.spring")`** (basato su `allopen`) apre le classi annotate con le annotazioni di Spring.
- **`kotlin("plugin.jpa")`** (basato su `no-arg`) genera il costruttore senza argomenti richiesto da JPA per `@Entity`, `@Embeddable`, `@MappedSuperclass`. È sintetico: non lo vedi dal codice Kotlin.
- Se serve `open` su altre annotazioni (es. entity per i proxy lazy), `allOpen { annotation("jakarta.persistence.Entity") }`. Verifica che la classe sia davvero `open` se usi il lazy loading.
- Le versioni dei plugin seguono la versione del plugin Kotlin: allineale (`kotlin("jvm")`, `kotlin("plugin.spring")`, `kotlin("plugin.jpa")` con lo stesso numero).

## Nullabilità e Spring
- Spring legge la nullabilità dai tipi Kotlin: un parametro `String?` di un endpoint o di un `@RequestParam` è opzionale, `String` è obbligatorio. Non dichiarare nullable "per sicurezza": cambia il contratto.
- Con Spring Boot 3.x: le annotazioni di nullabilità Java dei progetti Spring sono trattate come tipi Kotlin; per i vecchi progetti serve l'opzione `-Xjsr305=strict` del compilatore, che i progetti generati da start.spring.io impostano nel build. Controlla la configurazione di `kotlin { compilerOptions { … } }`. Con Spring Boot 4 la nullabilità passa a JSpecify e Jackson alla 3 (gruppo `tools.jackson`): segui la documentazione della versione in uso.
- Jackson: serve il modulo Kotlin (`jackson-module-kotlin`) per costruttori primari e `data class` senza `@JsonCreator`. Spring Boot lo registra se è sul classpath, ma la dipendenza va dichiarata (con ok dell'utente se è nuova).
- Le annotazioni di validazione vanno sul target giusto: `@field:NotBlank`, `@field:Size`, non `@NotBlank` sul parametro del costruttore.

## Entity JPA in Kotlin
- **Non `data class` per le entity**: `equals`, `hashCode` e `toString` generati sui campi rompono proxy, relazioni lazy e cicli, come `@Data` di Lombok in Java.
- Classe normale (aperta dal plugin), `var` per i campi mutati da JPA, `id` nullabile (`Long? = null`) finché non è persistita. Un `id` non nullable con valore finto (`0`) fa trattare un'entity nuova come esistente.
- `equals`/`hashCode` basati sull'identità di business o sull'id solo con una strategia consapevole; non lasciare quelli generati.
- Relazioni: `MutableList` o `MutableSet` inizializzate vuote, mai `null`. Collezioni lazy fuori dalla transazione sollevano `LazyInitializationException` come in Java.
- Nei repository, il tipo di ritorno nullable (`findByEmail(email: String): Cliente?`) è l'alternativa a `Optional`: Spring Data lo capisce.
- Proiezioni con `data class` o interfacce; una `data class` come DTO di lettura è corretta.

## Costruttori e iniezione
- Constructor injection con il costruttore primario: `class OrdineService(private val repo: OrdineRepository)`. Niente `@Autowired` e niente `lateinit` per le dipendenze.
- `@ConfigurationProperties` con una `data class` immutabile e costruttore (binding per costruttore) invece di `lateinit var`. Valori di default Kotlin per le proprietà opzionali.

## Coroutine in Spring
- Spring MVC e WebFlux supportano funzioni `suspend` e `Flow` negli handler. Con MVC il thread della richiesta è di Tomcat: l'I/O bloccante dentro una coroutine finisce comunque su `Dispatchers.IO`, non c'è magia.
- `@Transactional` con `suspend` funziona solo con transazioni reattive (R2DBC) o con le versioni di Spring che lo supportano: se il repository è JDBC/JPA, i metodi restano bloccanti e non vanno trattati come `suspend` per sembrare moderni.
- Per `@Async`, `@Scheduled` e simili controlla cosa supporta la versione in uso prima di combinarli con `suspend`.

## Gradle Kotlin DSL
- Catalogo versioni (`gradle/libs.versions.toml`) e `plugins { alias(libs.plugins.…) }` se il progetto lo usa; non mischiare versioni scritte a mano.
- Toolchain: `kotlin { jvmToolchain(21) }` fa coincidere compilazione Kotlin e Java; senza, `jvmTarget` e `sourceCompatibility` possono divergere e produrre errori sibillini.
- Sorgenti: `src/main/kotlin` e `src/test/kotlin`; Java e Kotlin possono convivere nello stesso modulo. Gli annotation processor che generano codice Java (MapStruct, metamodel di Hibernate) vanno configurati per Kotlin con `kapt` o `ksp`: se il codice generato non compare, parti da lì.
- Annotation processor: `kapt` è in manutenzione, `ksp` dove il processore lo supporta. Non cambiare strumento in una modifica non correlata. Lombok con Kotlin ha limiti pesanti: in un progetto Kotlin non si usa.
- Build in sandbox: Gradle non usa il proxy della sandbox, quindi `--offline` con dipendenze già in cache, come descritto in `java`.
- `allWarningsAsErrors`, `explicitApi()` (per le librerie) e `-Xjsr305=strict` si decidono col progetto, non si attivano di propria iniziativa.
