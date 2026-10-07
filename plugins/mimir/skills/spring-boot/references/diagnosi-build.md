# Errori di build e di avvio: cause tipiche

Metodo:
- Leggi tutto lo stack trace. La causa vera è quasi sempre l'ultimo `Caused by`, non la prima riga.
- Correggi una causa per volta e rilancia.
- Non cambiare versioni nel `pom.xml` o nel `build.gradle` senza ok.
- Per capire perché un'auto-configurazione è attiva o no, avvia con `--debug` (o `debug=true`): stampa il report delle condizioni.

| Sintomo | Cause tipiche | Cosa controllare |
|---|---|---|
| `required a bean of type ... that could not be found` / `NoSuchBeanDefinitionException` | Classe fuori dal component scan, annotazione mancante, condizione `@ConditionalOn…` o profilo non soddisfatti, auto-configurazione esclusa | Package rispetto alla classe `@SpringBootApplication`; profilo attivo; report delle condizioni |
| `NoUniqueBeanDefinitionException` | Più bean dello stesso tipo | `@Qualifier` o `@Primary`, oppure un bean di troppo |
| `The dependencies of some of the beans form a cycle` | Dipendenza circolare (dalla 2.6 vietata di default) | Correggi il design. `spring.main.allow-circular-references` solo come tampone dichiarato |
| `Failed to configure a DataSource: 'url' attribute is not specified` | Proprietà del datasource assenti per il profilo attivo, driver mancante | Profilo attivo, variabili d'ambiente, dipendenza del driver |
| `Could not resolve placeholder` | Proprietà mancante nell'ambiente o nel profilo | File di configurazione del profilo, variabili d'ambiente |
| `Schema-validation: missing table/column` | Con `ddl-auto=validate`, migrazione mancante o non applicata | Migrazioni presenti e applicate su quel database |
| `NoSuchMethodError`, `NoClassDefFoundError`, `ClassNotFoundException` a runtime | Conflitto di versioni tra librerie, versione forzata fuori dal BOM, `javax` e `jakarta` mescolati dopo un upgrade | `./mvnw -o dependency:tree -Dverbose -Dincludes=<groupId>:<artifactId>` |
| `cannot find symbol` su getter, builder o mapper | Annotation processor (Lombok, MapStruct) non configurato o nell'ordine sbagliato | `annotationProcessorPaths`: Lombok prima di MapStruct, con `lombok-mapstruct-binding` |
| `Failed to load ApplicationContext` nei test | Una delle cause sopra, nel contesto di test | L'ultimo `Caused by`; configurazione o profilo di test |
| `Port 8080 was already in use` | Un'altra istanza è avviata | Processo sulla porta, oppure `server.port` diverso in locale |
| Build offline: artefatto non trovato | Dipendenza non presente in `~/.m2` | Serve una build fuori dalla sandbox, con conferma dell'utente. Mai `-U` dentro la sandbox |
