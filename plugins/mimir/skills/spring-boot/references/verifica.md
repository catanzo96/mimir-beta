# Verifica prima di dichiarare finito

Ogni passo si chiude con il comando lanciato e l'esito letto, non con quello atteso. Un passo saltato si dichiara, con il motivo. Usa gli strumenti già configurati nel progetto: nessun plugin o dipendenza nuova senza ok.

Nella sandbox di Claude Code Maven e Gradle non hanno rete: usa `-o` / `--offline` (vedi la skill `java`, che indica anche le opzioni di Maven per le sessioni avviate con il launcher di Mímir).

## Passi
1. **Compilazione**: `./mvnw -o -q test-compile` (Gradle: `./gradlew --offline testClasses`). Compila anche i test: una firma cambiata li rompe prima che girino.
2. **Test**: `./mvnw -o test`, poi `verify` se il progetto ha test di integrazione e l'ambiente li permette (Testcontainers richiede Docker).
   - Leggi quanti test sono stati eseguiti, non solo "BUILD SUCCESS": zero test eseguiti, `skipTests` nel `pom.xml` o test esclusi da un profilo non sono una verifica.
   - Se la modifica corregge un bug, il test che lo riproduce deve fallire senza il fix e passare con il fix.
3. **Copertura**: se il progetto misura la copertura con JaCoCo, controlla il report (`target/site/jacoco/`) sulle classi toccate, non il totale.
4. **Analisi statica**: quella del progetto (SonarQube for IDE, SpotBugs, PMD, Checkstyle). Zero segnalazioni nuove sul codice scritto. L'analisi su server Sonar richiede rete e token: se serve, chiedi all'utente.
5. **Dipendenze**: se la modifica ne aggiunge o ne cambia la versione, controlla l'albero (`./mvnw -o dependency:tree`) per conflitti e versioni fuori dal BOM di Spring Boot. Una scansione delle vulnerabilità (es. OWASP dependency-check) solo se il progetto la usa già: scarica dati, quindi va fuori dalla sandbox con conferma.
6. **Avvio**: se cambiano configurazione, bean, profili o sicurezza, avvia l'applicazione (o un test di contesto) e controlla `health` e l'endpoint toccato.
7. **Rilettura del diff**: solo il perimetro richiesto. Niente codice di debug, segreti, log di dati personali, file di configurazione locali. Nessuna migrazione già rilasciata modificata.

## Resoconto
| Passo | Comando | Esito | Limiti o note |
|---|---|---|---|

Se un passo fallisce, riportalo così com'è: non riformularlo come successo parziale.
