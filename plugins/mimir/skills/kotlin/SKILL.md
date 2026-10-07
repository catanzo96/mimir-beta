---
name: kotlin
description: Best practice Kotlin e coroutine. Usala quando scrivi, modifichi o rivedi codice Kotlin (.kt, .kts), anche con Spring, o in progetti con build.gradle.kts.
---

# Kotlin

Si applica insieme a `clean-code`. Per ciò che vale uguale in Java (JPA, Spring, sicurezza, test di integrazione) rimanda a `java` e `spring-boot`: qui c'è solo ciò che cambia con Kotlin. Prevalgono le convenzioni del progetto (`detekt`, `ktlint`, `.editorconfig`, versione di Kotlin e della JVM). Coroutine e Flow: `references/coroutine.md`. Kotlin con Spring e JPA, Gradle: `references/spring-gradle.md`.

## Prima di tutto: la versione
Leggi la versione del plugin Kotlin in `build.gradle.kts` o `libs.versions.toml`, e il `jvmTarget`/`jvmToolchain`.
- Dalla 2.0 il compilatore K2 è quello predefinito. Nella 2.4 il vecchio K1 non è più supportato (`languageVersion` 1.9 eliminata).
- 2.2: stabili le **guard condition** nel `when` (`is Stringa if x.isNotEmpty() -> …`), `break`/`continue` non locali nelle lambda inline e l'interpolazione multi-dollaro.
- 2.3: stabili i type alias annidati e i controlli di esaustività del `when` basati sul flusso dei dati.
- 2.4: stabili **context parameters** e **explicit backing fields**. Prima erano preview o sperimentali con flag: se la versione è più vecchia, non usarli.
- Per un progetto su Kotlin 1.x o 2.0 con codice datato vale `manutenzione-legacy` (se disponibile).

## Null safety
- Il tipo dice se un valore può mancare (`Cliente?`). Niente `!!`: è un `NullPointerException` rimandato e nascosto. Se un invariante lo garantisce, esprimilo (`requireNotNull`, `checkNotNull`, con un messaggio).
- Per il nullable usa `?.`, `?:` (anche con `return` o `throw` a destra), `let` solo se rende il codice più chiaro di un `if`.
- `lateinit` solo per ciò che un framework inietta dopo la costruzione (test, DI su campo); mai come scorciatoia per evitare il costruttore.
- Collezioni vuote, non `null`. Un `List<T?>` e un `List<T>?` sono cose diverse: scegli consapevolmente.
- **Tipi piattaforma** (`String!`): ciò che arriva da codice Java senza annotazioni non è controllato. Ai confini dichiara il tipo (`val nome: String? = oggettoJava.nome`) e gestisci il caso: con `String` il crash arriva più tardi, lontano dalla causa.

## Dati e tipi
- `data class` per valori: `val` e non `var`, copia con `copy()`. Non per entity JPA (vedi `references/spring-gradle.md`) né per classi con identità e stato mutabile.
- `value class` per ID e unità di misura (`@JvmInline value class IdOrdine(val valore: Long)`): tipi distinti senza costo a runtime. Con Java, JPA e serializzazione verifica come vengono trattati.
- **`sealed interface`/`sealed class` + `when` esaustivo come espressione** per stati e risultati: un caso nuovo non gestito è un errore di compilazione. Niente `else` che lo nasconde.
- `enum` per insiemi chiusi senza dati propri per variante; `object` per i singleton veri (non per contenere funzioni statiche: usa funzioni a livello di file o `companion object`).
- Parametri con nome e valori di default al posto di overload multipli e builder. Con troppi booleani, un tipo (enum o classe) vale più di `crea(true, false)`.
- `val` di default, `var` solo se il valore cambia davvero. Collezioni di sola lettura (`List`) nell'API pubblica; `MutableList` resta locale (attenzione: `List` è una vista, non è immutabile, se qualcuno mantiene la `MutableList`).

## Funzioni ed estensioni
- Espressioni al posto di istruzioni: `if`, `when` e `try` restituiscono un valore. Corpo a espressione per funzioni brevi.
- **Funzioni di estensione** per aggiungere comportamento a tipi che non controlli, nello stesso package o file del chiamante principale. Non per nascondere logica di dominio che appartiene a una classe tua. Sono risolte staticamente: non sono polimorfiche.
- **Scope function con misura**: `let` per trasformare un nullable, `apply` per configurare un oggetto appena creato, `also` per un effetto collaterale (log), `run`/`with` raramente. Niente catene annidate e niente due scope function una dentro l'altra: dopo la seconda non si capisce più cosa sia `it` o `this`.
- Lambda e funzioni inline: `inline` solo per funzioni di ordine superiore corte e dove serve (`reified`, return non locale). Non è un'ottimizzazione generica.
- `Sequence` solo con collezioni grandi o pipeline lunghe: per poche decine di elementi le operazioni su `List` sono più semplici e spesso più veloci.
- `require` per validare gli argomenti, `check` per lo stato, `error()` per gli stati impossibili.

## Errori
- Le eccezioni in Kotlin sono tutte unchecked: documenta quali lancia una funzione pubblica. Eccezioni di dominio con la causa (`cause`).
- Per errori attesi, un risultato esplicito: `sealed interface` (Successo/Errore) o il tipo `Result` del progetto. `runCatching` cattura anche `CancellationException`, rompendo le coroutine: nelle funzioni `suspend` evitalo o rilancia quella eccezione.
- `catch (e: Exception)` che inghiotte è vietato come in Java; vedi `clean-code/references/errori-logging.md`.

## Interoperabilità con Java
- Da Java, il codice Kotlin ha forme particolari: `@JvmStatic` e `@JvmField` per esporre membri statici e campi, `@JvmOverloads` per i default, `@JvmName` per risolvere i conflitti di firma, `@Throws` se un chiamante Java deve catturare un'eccezione checked.
- Le funzioni a livello di file finiscono in una classe `NomeFileKt`: `@file:JvmName` per un nome stabile.
- Le proprietà `val`/`var` diventano getter/setter; un `Boolean` `isAttivo` diventa `isAttivo()`.
- Le annotazioni Java vanno applicate al target giusto (`@field:`, `@get:`, `@param:`): con le validazioni Bean (`@field:NotBlank`) dimenticare il prefisso è il motivo tipico per cui la validazione non scatta.
- Le lambda SAM e i tipi generici con varianza (`out`, `in`) possono sorprendere nella firma vista da Java (`? extends`): se l'API è pubblica per codice Java, prova a chiamarla da un test Java.

## Test
- Il framework del progetto: JUnit 5 con MockK, oppure Kotest. MockK se già presente: gestisce funzioni `suspend`, estensioni e oggetti. Se il progetto usa Mockito, resta quello.
- Nomi dei test con backtick solo se il progetto lo fa (`` fun `rifiuta un ordine vuoto`() ``). Dati di test con parametri di default e `copy()` invece di builder.
- Coroutine: `runTest` (kotlinx-coroutines-test), mai `runBlocking` con `delay` reali. Dettagli in `references/coroutine.md`.
- Spring Boot: `@MockkBean` (SpringMockK) al posto di `@MockBean` se il progetto lo adotta.

## Verifica
Prima di dichiarare finito, con gli strumenti del progetto:
- Compilazione e test: `./gradlew build` (o `./gradlew test` mirato mentre lavori); in sandbox senza rete `--offline`, come in `java`.
- Lint e analisi statica già configurati: `./gradlew ktlintCheck`, `detekt`, Sonar. Non lanciare `ktlintFormat` su file che non hai toccato.
- Warning del compilatore nuovi trattati come errori da risolvere (`allWarningsAsErrors` se attivo), non soppressi con `@Suppress` senza motivo scritto.
- Nessuna nuova dipendenza (nemmeno `kotlinx-*`) senza ok.
