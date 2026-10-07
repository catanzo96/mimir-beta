---
name: java
description: Best practice Java. Usala quando scrivi, modifichi o rivedi codice Java, o in progetti con pom.xml o build.gradle.
---

# Java

Si applica insieme a `clean-code`. Le convenzioni del progetto e la versione di Java in uso (`pom.xml`, `build.gradle`) prevalgono: non usare feature non disponibili nella versione del progetto. **Su progetti Java 6-11, Spring Boot 1.x/2.x o senza test, vale `manutenzione-legacy`.**

## Java moderno (21+, 25 LTS)
- `record` per oggetti valore immutabili e contenitori di dati.
- **Pattern matching** con `instanceof` e `switch`: niente cast espliciti.
- **`sealed`** con `switch` esaustivo per gerarchie chiuse. È il modo idiomatico per trasformare dati per tipo; il polimorfismo resta per il comportamento.
- `var` per le variabili locali quando il tipo è evidente dal lato destro.
- `Optional`, `Stream` e `Collectors` per codice dichiarativo, senza sacrificare la leggibilità.
- Text block per stringhe multilinea (SQL, JSON nei test).
- Dalla 22: **variabili senza nome** `_` per parametri, catch e pattern non usati.
- Dalla 25 (LTS corrente): **costruttori con corpo flessibile**, per validare gli argomenti prima di `super(...)` o `this(...)`.

## Immutabilità
- Campi `final` di default.
- Per le variabili locali, `final var` quando vuoi rendere esplicita l'immutabilità. Non usare `val` di Lombok: dà problemi con IDE e tooling, e `final var` è nativo.
- Collezioni immutabili (`List.of`, `Collectors.toUnmodifiableList`, `stream.toList()`).

## Lombok
- Solo per il boilerplate strutturale: `@Getter`, `@Setter` (con parsimonia), `@ToString`, `@EqualsAndHashCode`, `@Builder`, `@RequiredArgsConstructor` (per l'injection da costruttore).
- **Niente `@Data`** su classi con logica o su entity JPA: genera `equals`, `hashCode` e `toString` impliciti (problemi con proxy, relazioni lazy e cicli).
- Se un `record` basta, preferiscilo a Lombok.

## Costanti
- `enum` per insiemi chiusi con significato (`StatoOrdine`, `TipoDocumento`).
- Classe `final` con costruttore privato per costanti tecniche: timeout, regex, header.
- ❌ Mai interfacce come contenitori di costanti: le costanti entrano nel contratto e si propagano a ogni implementazione.

## Optional e null
- `Optional` solo come **tipo di ritorno**, mai come campo, parametro o elemento di collezione.
- Mai `Optional.get()` senza controllo. Usa `orElseThrow()`, `orElse()`, `map()`.
- Collezioni vuote, mai `null`.
- Null-safety dichiarata con **JSpecify** (`@NullMarked` sul package, `@Nullable` dove serve), se il progetto la adotta. Con Spring Framework 7 è lo standard.
- Ai confini con codice legacy o librerie, `Optional.ofNullable()` per convertire subito i possibili `null`.

## Risorse
- **`try-with-resources`** per tutto ciò che è `AutoCloseable`: stream, connessioni, reader, client. Mai `close()` manuali nel `finally`.

## Eccezioni
- Eccezioni di dominio **unchecked** (`extends RuntimeException`).
- Le checked delle librerie si catturano e si rimappano in eccezioni di dominio, mantenendo la causa (`new XException(msg, e)`).
- Gestione centralizzata ai confini (es. `@RestControllerAdvice` in Spring).

## Lambda e stream
- Lambda brevi, con un solo livello di indentazione. Oltre, estrai in un metodo con un nome (anche come method reference).
- Parametri delle lambda con nomi espliciti (`ordine -> ...`, non `o -> ...`), salvo casi banali.
- Niente effetti collaterali dentro `map` e `filter`.

## Concorrenza
- Evita lo stato mutabile condiviso. Se serve, usa le classi concorrenti (`ConcurrentHashMap`, `AtomicLong`) e le loro operazioni atomiche (`computeIfAbsent`, `merge`), non un "controlla e poi scrivi" in due passi.
- Mai `new Thread` nel codice applicativo: executor dimensionati, con nome dei thread e chiusura gestita.
- `CompletableFuture` con un executor esplicito per l'I/O (non il common pool) e un timeout (`orTimeout`).
- `ThreadLocal` sempre ripulito in un `finally`: i thread dei pool vengono riusati.
- Virtual thread (21+): fino a Java 23 un `synchronized` attorno a I/O lento blocca il thread portante; lì meglio `ReentrantLock`.

## Idiomi e trappole
Denaro e `BigDecimal`, date e `Clock`, `equals`/`hashCode`, charset, collezioni immutabili e altre trappole frequenti: `references/idiomi.md`. Per i rischi di sicurezza (`ProcessBuilder`, deserializzazione, path) vedi `clean-code/references/sicurezza.md`.

## Dependency injection (Spring)
- Solo injection da costruttore, con `@RequiredArgsConstructor` e campi `private final`. Mai `@Autowired` su campi.

## Test
- JUnit 5 e Mockito, AssertJ per le asserzioni leggibili.
- `@DisplayName` con una descrizione discorsiva, oltre al nome del metodo parlante.
- Dati di test nelle mock factory (suffisso `*MockFactory`) o nei builder, nel package di test dedicato (es. `mocks`).
- Test di integrazione con suffisso `*IT`.
- Mapper MapStruct: vanno testati, perché contengono logica di conversione.

## Build nella sandbox di Claude Code
- Maven e Gradle non usano le variabili `HTTP(S)_PROXY` della sandbox: dentro la sandbox non hanno rete.
- Se le dipendenze sono già nella cache locale, lancia la build **offline** (`./mvnw -o …`, `./gradlew --offline …`).
- Se la variabile `MIMIR_MAVEN_SETTINGS` esiste (sessioni avviate con il launcher di Mímir), aggiungi sempre `-llr -s "$MIMIR_MAVEN_SETTINGS"` ai comandi Maven nella sandbox: `~/.m2/settings.xml` non è leggibile e senza `-s` Maven si ferma; senza `-llr` rifiuta gli artefatti in cache scaricati da repository definiti in quel file. Esempio: `mvn -llr -s "$MIMIR_MAVEN_SETTINGS" -q test-compile`. Nei progetti con `pom.xml` lo ricorda anche l'hook `maven-sandbox.py` all'avvio.
- Non configurare a mano il proxy della sandbox in un `settings.xml` e non leggere le sue credenziali dalle variabili d'ambiente: è un modo per scaricare dipendenze senza la conferma dell'utente.
- Se servono dipendenze nuove, se mancano nella cache o serve `-U`, fermati: la build va eseguita fuori dalla sandbox, con la conferma dell'utente.

## Qualità (Sonar)
- SonarQube for IDE (ex SonarLint) attivo nell'IDE. Prima della PR, zero segnalazioni nel codice del branch.
- Coverage tramite JaCoCo. Esclusioni tipiche in `sonar-project.properties`:
  ```properties
  sonar.coverage.exclusions=src/test/**,**/*Test.java,**/*Tests.java,**/*IT.java,**/mocks/**,**/*MockFactory.java
  ```
