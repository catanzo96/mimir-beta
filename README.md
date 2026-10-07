# Mímir

Un assistente personale per Claude Code, in italiano: regole di lavoro, skill, agent e hook per lavorare con Claude con standard alti, su qualsiasi progetto e tecnologia.
Parte dalla sfera lavorativa (sviluppo, analisi, manutenzione, gestione); più avanti si aggiungerà quella privata.

Il repo contiene solo il metodo. Ciò che riguarda te (chi sei, le tue note, gli host della tua azienda) sta in file locali che git ignora o nelle tue impostazioni utente di Claude Code.

## Installazione
Prerequisiti: Claude Code, `jq` (per unire le impostazioni), su Linux i requisiti della sandbox (vedi [Sandbox](#sandbox)).

```bash
git clone <url del repo> <cartella> && <cartella>/install.sh
```
`install.sh` si può rilanciare senza danni:
- crea `profile/profile.md` e `inbox.md` dagli esempi, se mancano;
- importa le regole di Mímir in `~/.claude/CLAUDE.md`;
- unisce `settings.template.json` a `~/.claude/settings.json`, con un backup;
- registra il marketplace `mimir`.

La cartella può stare ovunque: launcher e script ricavano il percorso dalla propria posizione. Fuori dal repo Claude Code vuole percorsi assoluti (marketplace, import in `~/.claude/CLAUDE.md`): se sposti la cartella, rilancia `install.sh` e li riallinea.

## Personalizzazione
| File | Cosa contiene | In git |
|---|---|---|
| `profile/profile.md` | chi sei: ruolo, livello, cosa stai sviluppando. Sempre in contesto | no (esempio: `profile/profile.example.md`) |
| `inbox.md` | le tue annotazioni da smaltire con `/retro` | no (esempio: `inbox.example.md`) |
| `~/.claude/settings.json` | host privati della sandbox (azienda, clienti) in `sandbox.network.allowedDomains`, altre cache in `sandbox.filesystem.allowWrite`. Claude Code unisce le liste di questo file a quelle di `sandbox.settings.json` | fuori dal repo |

Le regole in `rules/` e le skill sono il metodo condiviso: se vuoi cambiarle, fallo con `/retro` o con la skill `scrivi-skill`.

## Uso
- `bin/claude-mimir`: avvia Claude Code con Mímir attivo (regole, plugin caricati dalla cartella, sandbox). Accetta gli argomenti di `claude`, per esempio `--add-dir <cartella>`.
- In alternativa, nelle sessioni normali: `/plugin install mimir@mimir` e, dove si lavora, `/plugin install brokkr@mimir`.

## Il tema: la mitologia norrena
I nomi vengono dalla mitologia norrena; nei nomi tecnici (cartelle, plugin, variabili) si scrivono senza accento e in minuscolo.

| Nome | Nel mito | In questo progetto | Oggi |
|---|---|---|---|
| **Mímir** | il custode del pozzo della saggezza, consultato da Odino | il sistema nel suo insieme e la conoscenza condivisa: regole, profilo, metodo, linguaggi, agent di review e di design, hook | plugin `mimir` |
| **Brokkr** | il fabbro che forgiò Mjöllnir | il lavoro: analisi, ticket, manutenzione, rilasci, interventi, persone, stato e rischi | plugin `brokkr` |
| **Skuld** | la norna di ciò che sarà | la pianificazione | ruolo; oggi le skill `pianificazione`, `stime` e `decisioni` stanno in `mimir` |
| **Frigg** | la regina di Asgard, custode della casa | la vita privata | da costruire |
| **Heimdall** | il guardiano che vede e sente tutto | promemoria e notifiche | futuro |
| **Ratatoskr** | lo scoiattolo che porta i messaggi lungo Yggdrasill | l'orchestrazione tra le parti | futuro |

## Sicurezza: due livelli
- **Modalità assistita** (oggi): sessioni avviate con `bin/claude-mimir`, con la sandbox qui sotto, i plugin di Mímir e l'hook dei commit. L'utente approva le azioni.
- **Via libera a Claude** (lavoro autonomo, senza conferme): solo dentro un dev container con firewall in uscita e nessuna credenziale dell'host. Requisiti in `plugins/mimir/skills/sicurezza-claude-code/references/devcontainer.md`.
- Audit e hardening della configurazione: `/sicurezza-claude-code` (solo lettura finché non approvi le proposte).
- La sandbox copre solo i comandi shell: `Read`, `WebFetch`, MCP e hook restano fuori e si proteggono con i permessi.

## Sandbox
`sandbox.settings.json`: la sandbox dei comandi shell.
- **Filesystem**: scrittura limitata al progetto e alle cache di build, indicate una per una (`~/.npm/_cacache`, `~/.gradle/caches`, `~/.m2/repository`…). Niente `~/.cache`, `~/.npm` o `~/.gradle` interi: da lì partono gli MCP fuori dalla sandbox (`uvx`, `npx`) o codice alla build successiva (`~/.gradle/init.d`).
- **Credenziali**: `~/.ssh`, `~/.git-credentials`, `~/.aws/credentials`, `~/.docker/config.json`, `~/.gnupg`, `~/.m2/settings.xml`, `~/.gradle/gradle.properties`, `~/.claude.json` e i `.env` non si leggono né con lo strumento Read né dai comandi: le `deny` su `Read` valgono anche per la sandbox (provato il 05/10 con e senza le regole).
- **Sandbox obbligatoria**: `failIfUnavailable: true`, se la sandbox non parte Claude Code non parte.
- **Niente wildcard sulla home in `denyRead`**: su Linux vengono espanse percorrendo tutta la home (cestino e `node_modules` compresi) e l'avvio si blocca.
- **Rete**: solo i domini ammessi. Nel repo ci sono solo registri pubblici (GitHub, Maven Central, npm); gli host privati vanno in `~/.claude/settings.json`: Claude Code unisce le liste dei diversi file di impostazioni invece di sostituirle. Per controllare il risultato, fai eseguire a Claude nella sandbox un `curl` verso un host ammesso (deve rispondere) e uno escluso (deve essere bloccato): con il launcher `/sandbox` non si apre, perché la configurazione arriva da `--settings`, che ha la precedenza.
- **Uscita dalla sandbox**: ogni nuovo tentativo di un comando fuori dalla sandbox chiede conferma (`ask` su `Bash(dangerouslyDisableSandbox:true)`), anche in modalità auto, dove altrimenti lo approverebbe il classificatore (visto nel test del 05/10).
- Disattiva anche il sondaggio di feedback.
- **Lista delle skill**: `skillListingBudgetFraction` al 3% (anche in `settings.template.json`). Con il default dell'1%, su un modello da 200k token Claude Code scartava 33 descrizioni su 38; al 3% le vede tutte (provato in headless il 03/10).

Prerequisiti su Ubuntu 24.04: `socat` e il profilo AppArmor per `bwrap` (vedi la [documentazione](https://code.claude.com/docs/en/sandboxing#set-up-linux-and-wsl2)).

- **Java/Maven**: non usa il proxy della sandbox, quindi dentro la sandbox non ha rete. Le build si lanciano offline; per scaricare dipendenze si esce dalla sandbox, con conferma.
  - `~/.m2/settings.xml` non è leggibile (credenziali) e Maven si ferma se non può leggerlo. Il launcher esporta `MIMIR_MAVEN_SETTINGS`, che punta a `sandbox/maven-settings.xml` (offline, senza credenziali); la skill `java` e l'hook `maven-sandbox.py` fanno usare `mvn -llr -s "$MIMIR_MAVEN_SETTINGS"`. `-llr` serve perché gli artefatti in cache sono stati scaricati da repository definiti nel settings personale. Provato il 07/10 su un progetto Spring Boot 3.4 con Maven 3.8.7: senza le opzioni la build fallisce, con le opzioni `compile` e `package` riescono.
  - Gradle con `~/.gradle/gradle.properties` non leggibile: non ancora provato.

Provata il 29/09 su un repo Maven: blocco delle credenziali e build in auto-allow funzionanti.

Per provarla in un repo senza toccare la configurazione globale:
```bash
cd ~/workspace/<repo> && claude --settings <cartella di Mímir>/sandbox.settings.json
```
Anche qui `/sandbox` non si apre, per lo stesso motivo: verifica con la prova di rete descritta sopra.

## Livelli

| Livello | Dove | Quando si attiva |
|---|---|---|
| 0. Profilo: chi sono | `profile/profile.md` (locale), importato da `CLAUDE.md` | Sempre, in ogni sessione |
| 1. Regole: come si lavora | `rules/*.md`, importate da `CLAUDE.md` | Sempre, in ogni sessione |
| 2. Vincoli automatici | `plugins/mimir/hooks/`, `settings.template.json` | Sempre, li applica l'harness |
| 3. Skill generiche | `plugins/<plugin>/skills/` | Su richiesta, per tipo di compito |
| 4. Skill e agent di dettaglio | `plugins/<plugin>/skills/`, `plugins/<plugin>/agents/` | Su richiesta, per tecnologia o dominio |

## Dove va una cosa
- Vale per ogni compito → **regola** (breve: sta sempre in contesto)
- Deve valere al 100% → **hook o permesso**
- Vale per un tipo di compito → **skill generica** (il metodo qui, i dati concreti nel CLAUDE.md del progetto)
- Vale per una tecnologia o un dominio → **skill di dettaglio**
- Serve un contesto isolato, tool ristretti o un modello diverso dalla sessione → **agent**
- Riguarda un solo progetto → CLAUDE.md di quel progetto, non qui

Come si scrivono skill, agent, regole e hook: skill `scrivi-skill`.

## Confini
- **Lavoro e privato separati**: il plugin `mimir` vale in ogni ambito, `brokkr` solo per il lavoro; più avanti arriverà `frigg` per la vita privata.
- **Qui il metodo, non i dati**: il repo è pubblico, quindi niente codice, credenziali, informazioni di azienda e clienti né dati personali, nemmeno nella configurazione (host della sandbox, percorsi, email). Quelli stanno nei progetti, in file locali ignorati da git (`profile/profile.md`, `inbox.md`) o nelle impostazioni utente di Claude Code.

## Ciclo di miglioramento
1. Mentre lavori, annota in `inbox.md` (locale).
2. A fine sessione lancia `/retro`: propone le modifiche, tu approvi. Nelle sessioni lunghe, ogni 25 prompt, un hook ricorda a Claude di proportelo.
3. Le modifiche finiscono in `CHANGELOG.md`, poi fai il commit quando lo decidi tu.

## Indice skill
| Skill | Plugin | Strato | Scopo |
|---|---|---|---|
| `retro` | mimir | generica | Trasforma correzioni e preferenze in miglioramenti di Mímir. Solo manuale: `/retro` |
| `scrivi-skill` | mimir | generica | Standard per scrivere skill, agent, regole e hook: description, modelli, struttura, prova |
| `commit` | mimir | generica | Messaggi di commit: Conventional Commits in italiano, senza riferimenti a Claude |
| `git-workflow` | mimir | generica | Branching, MR/PR, catene di MR dipendenti, tag SemVer |
| `clean-code` | mimir | generica | Best practice trasversali: principi, OOP, naming, errori e fallimenti silenziosi, logging, test, smell, accessibilità web, come ricevere una review; quale review usare (`code-reviewer`, `/simplify`, `/code-review`) |
| `java` | mimir | linguaggio | Java 21+, Lombok, Optional, eccezioni, concorrenza, idiomi e trappole (denaro, date, charset), JUnit/Mockito, Sonar |
| `typescript` | mimir | linguaggio | Tipi e strictness, union discriminate, async, moduli, validazione ai confini, sicurezza JS/Node, progettazione dei tipi |
| `angular` | mimir | framework | Angular moderno: standalone, signals, control flow, OnPush/zoneless, resource, RxJS per intento, SSR e sicurezza, accessibilità, test ed e2e |
| `spring-boot` | mimir | framework | Spring Boot 2.x/3.x/4.x: configurazione, REST, JPA e transazioni, client HTTP, sicurezza, test, ciclo di verifica, diagnosi degli errori di build e avvio |
| `architettura-esagonale` | mimir | architettura | Ports & adapters, dominio ricco, test per layer |
| `debugging` | mimir | generica | Metodo per trovare la causa: ciclo di riproduzione, bisezione, un'ipotesi per volta, intermittenti, causa non trovata |
| `pianificazione` | mimir | generica | Dalla richiesta alla specifica al piano a passi verificabili, con approvazioni e deleghe; interrogatorio a round sul piano e spike usa e getta |
| `passaggio-consegne` | mimir | generica | Documento per riprendere il lavoro in un'altra sessione o passarlo a un collega. Solo manuale: `/passaggio-consegne` |
| `refactoring` | mimir | generica | Refactoring sicuro: rete di test, passi piccoli, mosse principali, commit `refactor` separati |
| `tdd` | mimir | generica | Ciclo rosso-verde-refactor come strumento, quando conviene e quando no |
| `script-shell` | mimir | generica | Script Bash e sh robusti e portabili: intestazione, quoting, pulizia, GNU/BSD, quando passare a Python |
| `design-api` | mimir | generica | API HTTP: risorse, status, errori RFC 9457, paginazione, versioning, idempotenza, OpenAPI |
| `database` | mimir | generica | Modellazione, indici, piani di esecuzione, transazioni e lock; dialetti PostgreSQL, Oracle, MySQL, SQL Server; NoSQL e Redis |
| `container` | mimir | generica | Docker e Compose; Kubernetes di base (probe, risorse, configurazione, diagnosi in sola lettura) |
| `ci-cd` | mimir | generica | Pipeline: fasi, stesso artefatto, segreti, approvazioni; Azure DevOps, GitLab CI, GitHub Actions, Jenkins |
| `ddd` | mimir | architettura | Domain-Driven Design pragmatico: linguaggio comune, bounded context, aggregati, eventi |
| `sistemi-distribuiti` | mimir | architettura | Monolite modulare o microservizi, messaggi, idempotenza, outbox, saga, resilienza, contratti |
| `architettura-frontend` | mimir | architettura | Organizzazione per feature, stato, confini dei moduli, comunicazione con il backend, per ogni framework |
| `python` | mimir | linguaggio | Python moderno, typing, packaging, pytest; Django e FastAPI |
| `nodejs` | mimir | linguaggio | Backend Node.js: versioni LTS, ESM, errori asincroni, event loop, shutdown; Express, Fastify, NestJS |
| `go` | mimir | linguaggio | Go idiomatico: errori, interfacce, concorrenza e context, test table-driven |
| `csharp-dotnet` | mimir | linguaggio | C# e .NET: async, DI, LINQ; ASP.NET Core ed EF Core |
| `kotlin` | mimir | linguaggio | Kotlin idiomatico, coroutine, interoperabilità con Java, Spring e Gradle |
| `rust` | mimir | linguaggio | Rust idiomatico: ownership, errori, trait, async, unsafe, cargo |
| `php` | mimir | linguaggio | PHP 8.x, Composer, sicurezza, PHPStan; Laravel e Symfony |
| `cpp` | mimir | linguaggio | C++ moderno: RAII, smart pointer, UB frequenti, concorrenza, CMake, sanitizer |
| `quarkus` | mimir | framework | Quarkus per chi viene da Spring: CDI, REST, Panache, Dev Services, build nativa |
| `react` | mimir | framework | React moderno: hook, quando non usare useEffect, stato, Actions, Server Components, Testing Library |
| `vue` | mimir | framework | Vue 3: Composition API, reattività, defineModel, Pinia, Router, test |
| `decisioni` | mimir | management | Decisioni non solo tecniche: domanda, reversibilità, criteri, opzioni, raccomandazione, registro; brief 1-3-1 da inoltrare e questionario per chi ha le informazioni |
| `stime` | mimir | management | Stime a intervallo o a tre punti, assunzioni, costi nascosti, dati storici, come comunicarle |
| `riunioni` | mimir | management | Agenda, verbale con decisioni e azioni (anche da appunti e trascrizioni, senza inventare responsabili o date), follow-up; riunioni ricorrenti (standup, retrospettiva, SAL) |
| `gestione-persone` | brokkr | management | 1:1, feedback, assegnazione di compiti ai colleghi, onboarding, conflitti, crescita. Claude prepara, non decide sulle persone |
| `stato-e-rischi` | brokkr | management | Report di stato con semaforo motivato, registro dei rischi, escalation; obblighi, scadenze e rischi estratti da documenti con la fonte |
| `scrittura-professionale` | mimir | documenti | Mail e documenti di lavoro: essenziale in testa, tono, cattive notizie, varianti tipiche. Propone il testo, non invia |
| `presentazioni` | mimir | documenti | Messaggio, struttura e una idea per slide; il file con gli strumenti disponibili |
| `ricerca` | mimir | documenti | Ricerca con fonti primarie, date e versioni, verifica incrociata, fatti separati da ipotesi; registro numerato delle fonti e citazioni verificate |
| `documentazione-tecnica` | mimir | documenti | README, guide, riferimenti, spiegazioni: quale tipo serve e come non farli invecchiare; mappa del codice di un repo con diagrammi Mermaid |
| `contesto-e-costi` | mimir | Claude | Cosa entra nel contesto, come misurarlo, cosa costa, le leve (delega, compact, clear, rewind, branch, btw, subtask, cache) |
| `delega` | mimir | Claude | Brief per subagent e workflow: compito chiuso, contesto, modello, resoconto, verifica dell'esito; `/goal`, `/loop`, `/batch`, `/background` e routine con i paletti di sicurezza |
| `manutenzione-mimir` | mimir | Claude | Audit periodico di skill e regole. Solo manuale: `/manutenzione-mimir` |
| `sicurezza-claude-code` | mimir | Claude | Audit e hardening di Claude Code (permessi, sandbox, hook, MCP, skill, agent, plugin), proposte verificate, dev container per il lavoro autonomo. Solo manuale: `/sicurezza-claude-code` |
| `analisi-funzionale` | brokkr | analisi | Business logic e AS-IS (le sei cose, requisiti e invarianti con test), MEV con criteri di accettazione, collaudo, round di chiarimento, domande al cliente |
| `analisi-tecnica` | brokkr | analisi | Diagnosi, impatto su più repo e contratti toccati, delta, pacchetti di query, registro del debito, ADR, audit delle dipendenze e di prontezza al rilascio, checklist di design. Contiene il metodo delle evidenze |
| `ticket` | brokkr | manutenzione | Dal ticket al rilascio: triage, riproduzione, causa radice un'ipotesi per volta, fix minimo o intervento sui dati, verifica PRIMA/DOPO, documento del ticket |
| `manutenzione-legacy` | brokkr | manutenzione | Modifiche sicure su versioni datate e senza test: niente sintassi moderna, diff minimo, stile degli esemplari, encoding, rimozione sicura, verifica senza test |
| `runbook` | brokkr | manutenzione | Runbook riutilizzabili e resoconti di interventi: stato prima/dopo, backup → modifica → prova end-to-end, rollback scritto prima, comandi distruttivi riconfermati, "Se hai fretta" |
| `rilascio` | brokkr | manutenzione | Piano rilasci a lotti, checklist con esito atteso, baseline prima/dopo, criteri di rollback, migrazioni del database, Go/No-Go, note di rilascio |

## Indice agent
| Agent | Plugin | Modello | Scopo |
|---|---|---|---|
| `code-reviewer` | mimir | sonnet | Review in sola lettura di un diff con le skill di codice: aderenza alla richiesta, correttezza (anche fallimenti silenziosi), sicurezza, design, test, perimetro del diff. Segnalazioni verificate, ordinate per gravità, con il costo di lasciarle; passate separate sui diff grandi, cautela sul codice da togliere |
| `security-reviewer` | mimir | sonnet | Review di sicurezza in sola lettura: autorizzazione sulla risorsa, injection, sessioni, segreti, file, SSRF, parsing, configurazione. Scenario, evidenza e correzione per ogni segnalazione |
| `architetto` | mimir | opus | Decisioni di design con opzioni e raccomandazione, piani a passi verificabili per i compiti grandi. Sola lettura |
| `Explore` | `.claude/agents/` | haiku | Sostituisce l'Explore integrato di Claude Code (che userebbe il modello della sessione) per le ricerche nel codice. Attivo nelle sessioni avviate con `bin/claude-mimir` |

## Indice hook
| Hook | Plugin | Evento | Scopo |
|---|---|---|---|
| `check-commit-message.py` | mimir | PreToolUse (Bash) | Sui commit creati da Claude blocca le attribuzioni all'AI e le righe del messaggio oltre 72 caratteri. Test: `python3 plugins/mimir/hooks/scripts/test_check_commit_message.py` |
| `retro-nudge.py` | mimir | UserPromptSubmit | Ogni 25 prompt della stessa sessione aggiunge al contesto un promemoria: se sono emerse correzioni, proporre `/retro` a fine compito. Non scrive e non blocca mai. Contatori in `${CLAUDE_PLUGIN_DATA}/retro-nudge/`, tolti dopo 7 giorni. Test: `python3 plugins/mimir/hooks/scripts/test_retro_nudge.py` |
| `maven-sandbox.py` | mimir | SessionStart | Nei progetti con `pom.xml` avviati dal launcher (variabile `MIMIR_MAVEN_SETTINGS`) mette in contesto come lanciare Maven nella sandbox e il divieto di configurare a mano il proxy. Test: `python3 plugins/mimir/hooks/scripts/test_maven_sandbox.py` |
