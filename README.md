# Mímir

Un assistente personale per Claude Code, in italiano: regole di lavoro, skill, agent e hook per lavorare con Claude con standard alti, su qualsiasi progetto e tecnologia.
Parte dalla sfera lavorativa (sviluppo, analisi, manutenzione, gestione); più avanti si aggiungerà quella privata.

Il repo contiene solo il metodo. Ciò che riguarda te (chi sei, le tue note, gli host della tua azienda) sta in file locali che git ignora o nelle tue impostazioni utente di Claude Code.

## Installazione
Prerequisiti: Claude Code e Python 3.8+. Su Linux e WSL2 l'installer installa i requisiti della sandbox, dopo una conferma (vedi [Sandbox](#sandbox)).

```bash
git clone <url del repo> <cartella> && <cartella>/install.sh
```
Su Windows nativo, da PowerShell:
```powershell
git clone <url del repo> <cartella>
powershell -ExecutionPolicy Bypass -File <cartella>\install.ps1
```
`-ExecutionPolicy Bypass` vale solo per questo lancio e non cambia la policy di sistema. `install.ps1` cerca Python 3.8+ (`py -3`, poi `python`, scartando lo stub dello Store) e Git for Windows, il cui bash fa girare gli hook. Se mancano, propone di installarli con winget, dopo una conferma. Poi lancia `install.py`.

Su Windows nativo la sandbox non esiste: alla fine `install.ps1` propone WSL2 e stampa i passi per installare Mímir dentro WSL. Lo fa solo con una risposta sì o con `-InstallWsl`, mai con `-Yes`. Serve un riavvio.

Lancia `install.ps1` da utente normale: da amministratore si ferma, perché `install.py` e i programmi del PATH girerebbero elevati. Su Windows nativo, senza sandbox, una sessione di Claude può modificare quei file. Per WSL lo script eleva solo `wsl --install`, con la richiesta UAC.

**Non ancora provato su Windows vero**: la prova è prevista nella CI (passo 6) e nella prova manuale.

Lancia sempre `install.sh` o `install.ps1`. Le opzioni sono le stesse, scritte in modo diverso:
- `--yes` e `-Yes` rispondono sì alle conferme (con `install.ps1`, non a WSL);
- `--skip-system` e `-SkipSystem` saltano i passi di sistema: sudo su Linux, winget e WSL su Windows. Lo script avvia `install.py` con `python -I`: la cartella di Mímir è scrivibile dalla sandbox e l'installer gira fuori, quindi non deve importare moduli piantati accanto a sé.

Si può rilanciare senza danni. Prima legge e valida i file; se uno non è valido si ferma senza modificare nulla. Poi scrive, con un backup, solo ciò che cambia:
- crea `profile/profile.md` e `inbox.md` dagli esempi, se mancano;
- importa le regole di Mímir in `~/.claude/CLAUDE.md`;
- unisce `settings.template.json` a `~/.claude/settings.json`;
- protegge i file di Mímir che girano fuori dalla sandbox o entrano in ogni sessione (`plugins`, `bin`, `rules`, `profile`, `CLAUDE.md`, gli installer…):
  - con `sandbox.filesystem.denyWrite`, la shell nella sandbox non li scrive;
  - con le regole `ask` su `Edit(//…)`, Edit e Write chiedono conferma;
  - se Mímir si sposta, toglie le voci del percorso vecchio;
- aggiunge a `.git/info/exclude` i file vuoti che la sandbox crea nel repo;
- registra il marketplace `mimir`;
- su Linux e WSL2 installa `bubblewrap` e `socat` (apt-get, dnf, pacman o zypper) e, se AppArmor lo richiede, il profilo per `bwrap`. Lo fa con sudo e dopo una conferma. Se qualcosa non riesce, continua con il resto ma esce con un errore.

Dalla cartella di Mímir l'installer non segue i symlink: rifiuta esempi, template ed `exclude` che sono symlink e non crea un file personale al posto di un symlink. La cartella è scrivibile dalla sandbox, e un symlink porterebbe un segreto in un file leggibile o una scrittura fuori. In `~/.claude`, che la sandbox non scrive, i symlink (per esempio verso un repo di dotfiles) si seguono.

Test: `python3 -I test_install.py`, che usa copie di Mímir in una cartella temporanea e non tocca `~/.claude`. I test di `install.ps1`, e quelli di `bin/claude-mimir.ps1` in `test_claude_mimir.py`, girano se trovano PowerShell (`MIMIR_TEST_PWSH`, `pwsh` o `powershell`); altrimenti vengono saltati.

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
- `bin\claude-mimir.ps1` (Windows nativo): `powershell -NoProfile -ExecutionPolicy Bypass -File <cartella>\bin\claude-mimir.ps1`, con gli argomenti di `claude`. Gira **senza sandbox** e lo ricorda a ogni avvio: rete e file, credenziali comprese, sono liberi per la shell; restano attivi le regole ask/deny degli strumenti di Claude e gli hook. Per la protezione completa usa WSL2.
  - Passa a Claude Code `sandbox\windows.settings.json`: una copia di `sandbox.settings.json` con la sandbox spenta, ignorata da git, rigenerata a ogni avvio se è diversa.
  - Rispetto a `bin/claude-mimir` non esporta `MIMIR_MAVEN_SETTINGS`: senza sandbox Maven usa i settings personali e la rete.
  - Limite di Windows PowerShell 5.1: gli argomenti vuoti si perdono e i doppi apici dentro un argomento non arrivano a `claude`.
  - Non ancora provato su Windows vero.
- **Passaggio tra sessioni (Ratatoskr)**: con le sessioni avviate dal launcher, quando il contesto supera i 200.000 token (il 20% di una finestra da 1M) Claude chiude il passo in corso, scrive il passaggio di consegne e ti chiede `/clear`. La sessione che parte dopo `/clear`, o una nuova avviata nella stessa cartella, lo riceve nel contesto (lo vedi in un messaggio) e riprende da lì.
  - I passaggi stanno fuori da Mímir, in `~/.local/state/mimir/handoff/` (`$XDG_STATE_HOME` se c'è; su Windows nativo `%LOCALAPPDATA%\mimir\handoff\`): `pending/` per quelli da riprendere, `consumati/` per quelli ripresi, cancellati dopo 7 giorni. Un passaggio non ripreso entro 48 ore si archivia senza iniettarlo.
  - Fuori da Mímir perché la shell nella sandbox non ci può scrivere: un passaggio si crea solo con Write, che segue i permessi della sessione (in modalità auto lo approva il classificatore, come nella prova del 09/10). Così un comando della shell non può preparare un passaggio per un altro progetto né piazzare symlink, che l'hook comunque non segue.
  - Soglia: `MIMIR_HANDOFF_TOKENS=<token>` nell'ambiente prima di lanciare il launcher. È in token perché la dimensione della finestra non arriva agli hook: con un modello da 200k abbassala (per esempio a 40000). Tienila ben sopra il contesto con cui parte una sessione (misuralo con `/context`; il 09/10 una sessione su Mímir era a 53.000 token dopo il primo comando): sotto, anche la sessione ripresa riceve subito l'avviso e il giro ricomincia. Per provare l'hook con una soglia bassa, dopo la ripresa esci invece di continuare.
  - Il passaggio è legato alla cartella di lavoro: due sessioni parallele nella stessa cartella se lo contendono (con i worktree non succede).
  - Non serve se vuoi solo alleggerire la sessione: per quello c'è `/compact` (skill `contesto-e-costi`).
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
| **Ratatoskr** | lo scoiattolo che porta i messaggi lungo Yggdrasill | l'orchestrazione tra le parti | primo pezzo: l'hook `handoff.py` in `mimir`, che passa il lavoro da una sessione alla successiva |

## Sicurezza: due livelli
- **Modalità assistita** (oggi): sessioni avviate con `bin/claude-mimir`, con la sandbox qui sotto, i plugin di Mímir e l'hook su commit, push e tag. L'utente approva le azioni.
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

Prerequisiti su Linux e WSL2: `bubblewrap`, `socat` e, su Ubuntu 24.04+, il profilo AppArmor per `bwrap`. Li installa `install.sh` (vedi la [documentazione](https://code.claude.com/docs/en/sandboxing#set-up-linux-and-wsl2)).

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
| `passaggio-consegne` | mimir | generica | Documento per riprendere il lavoro in un'altra sessione o passarlo a un collega. Solo manuale: `/passaggio-consegne`; la fa seguire anche l'hook `handoff.py` |
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
| `design-ui` | mimir | design | Qualità visiva delle UI web: lettura della richiesta con tre assi, superfici (lavorare, leggere, convincere), design system e token, default da rifiutare, checklist finale; pagine marketing, rifacimento, mobile web |
| `animazioni-ui` | mimir | design | Se animare (frequenza e scopo), strumento più semplice, proprietà, curve e durate, interruzione, movimento ridotto; revisione; ricette, gesti e spring, vocabolario |
| `ui-casi-limite` | mimir | design | Dati peggiori plausibili dai limiti di schema e DB, stati vuoto/uno/tanti, firme dei guasti, scelta tra a capo e troncamento; resoconto prima delle correzioni |
| `prototipi-ui` | mimir | design | Varianti divergenti su un asse dichiarato dietro un selettore, promozione della scelta. Solo manuale: `/prototipi-ui` |
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
| `design-reviewer` | mimir | sonnet | Review in sola lettura dell'esperienza e della qualità visiva di una UI: aderenza, bloccanti d'uso, euristiche di Nielsen con punteggio, carico cognitivo, due utenti, checklist di `design-ui`; separa il visto dal dedotto |
| `Explore` | `.claude/agents/` | haiku | Sostituisce l'Explore integrato di Claude Code (che userebbe il modello della sessione) per le ricerche nel codice. Attivo nelle sessioni avviate con `bin/claude-mimir` |

## Indice hook
| Hook | Plugin | Evento | Scopo |
|---|---|---|---|
| `git-guard.py` | mimir | PreToolUse (Bash, PowerShell) | Sui comandi git lanciati da Claude blocca i commit con attribuzioni all'AI o righe del messaggio oltre 72 caratteri, il force push e ogni commit, push o tag non in forma semplice (l'intero comando `git commit …`, `git push …` o `git tag …`, senza `git -C`, opzioni globali, variabili, `&&`, `;`, `|`, heredoc, `$( )` o a capo); `commit-tree` e `send-pack` sempre. In forma semplice non interviene: la conferma la chiede la regola `ask` di settings, perché un `ask` restituito dall'hook è stato ignorato da Claude Code (2.1.293, sandbox e modalità auto, 08/10). Riconosce git tra i token del comando: anche `git -C "cartella"`, `FOO=1 git`, `/usr/bin/git`, `git.exe`, `sh -c`, `eval`, `iex`, e nei corpi degli heredoc. Limiti: è una rete contro errori e injection banali, non contro un avversario determinato; non vede alias di git, alias e variabili di PowerShell, funzioni shell, script, `make`, hook git, comandi passati a `ssh`, `update-ref` e `fast-import`, e `merge`, `revert`, `cherry-pick` e `pull` creano commit senza passare dall'hook. Gira tramite `run-python.sh`, che sceglie l'interprete (python3, python, py -3) e senza Python blocca commit, push e tag. Test: `python3 plugins/mimir/hooks/scripts/test_git_guard.py` e `test_run_python.py` |
| `retro-nudge.py` | mimir | UserPromptSubmit | Ogni 25 prompt della stessa sessione aggiunge al contesto un promemoria: se sono emerse correzioni, proporre `/retro` a fine compito. Non scrive e non blocca mai. Contatori in `${CLAUDE_PLUGIN_DATA}/retro-nudge/`, tolti dopo 7 giorni. Test: `python3 plugins/mimir/hooks/scripts/test_retro_nudge.py` |
| `maven-sandbox.py` | mimir | SessionStart | Nei progetti con `pom.xml` avviati dal launcher (variabile `MIMIR_MAVEN_SETTINGS`) mette in contesto come lanciare Maven nella sandbox e il divieto di configurare a mano il proxy. Test: `python3 plugins/mimir/hooks/scripts/test_maven_sandbox.py` |
| `handoff.py` (Ratatoskr) | mimir | UserPromptSubmit, PostToolUse, SessionStart (startup, clear) | Legge dal transcript i token di contesto dell'ultima risposta (input e cache, come la statusline). Oltre `MIMIR_HANDOFF_TOKENS` (default 200000) chiede a Claude di scrivere il passaggio di consegne con la procedura di `passaggio-consegne` in `$MIMIR_HANDOFF_DIR/pending/<cartella>.md` e di proporre `/clear`: a ogni prompt, e una sola volta per sessione dopo un tool (stato in `${CLAUDE_PLUGIN_DATA}/handoff/`; senza quella cartella, solo a ogni prompt). All'avvio e dopo `/clear` inietta il passaggio della cartella come dati da verificare, con un messaggio per l'utente, lo sposta in `consumati/` (0600) e cancella quelli oltre 7 giorni; un passaggio di oltre 48 ore si archivia senza iniettarlo. Non segue i symlink e legge al massimo 9.001 caratteri. Attivo solo con `MIMIR_HANDOFF_DIR`, esportata dai launcher fuori da Mímir; ignora i subagent; non blocca mai. Il transcript può essere indietro di un turno. Test: `python3 plugins/mimir/hooks/scripts/test_handoff.py` |
