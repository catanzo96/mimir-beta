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

Provato nella CI su `windows-latest`, con Windows PowerShell 5.1 e PowerShell 7, da utente non amministratore (vedi [CI](#ci)). Manca ancora la prova manuale su un Windows vero.

Lancia sempre `install.sh` o `install.ps1`. Le opzioni sono le stesse, scritte in modo diverso:
- `--yes` e `-Yes` rispondono sì alle conferme (con `install.ps1`, non a WSL);
- `--skip-system` e `-SkipSystem` saltano i passi di sistema: sudo su Linux, winget e WSL su Windows. Lo script avvia `install.py` con `python -I`: la cartella di Mímir è scrivibile dalla sandbox e l'installer gira fuori, quindi non deve importare moduli piantati accanto a sé.

Lancia l'installer subito dopo il clone: prima della prima installazione la protezione non c'è, e una sessione di Claude nella cartella può modificare i file che l'installer usa fuori dalla sandbox. Se hai già aperto sessioni, controlla prima con `git status` e `git diff HEAD`. L'installer rifiuta un `settings.template.json` con chiavi diverse da `attribution`, `skillListingBudgetFraction` e `permissions` (solo `ask` e `deny`); il tuo `~/.claude/settings.json` può avere qualsiasi chiave. Il controllo copre solo il template: non protegge da installer, launcher, hook o regole modificati.

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
- su Linux e WSL2 installa `bubblewrap` e `socat` (apt-get, dnf, pacman o zypper) e, se AppArmor lo richiede, il profilo per `bwrap`. Lo fa con sudo e dopo una conferma che mostra i comandi. Se qualcosa non riesce, continua con il resto ma esce con un errore.
  - con apt-get aggiorna prima gli indici; se `apt-get update` fallisce, installa con quelli presenti;
  - il profilo si carica con `systemctl reload apparmor` o, senza systemd o se non riesce, con `apparmor_parser -r`;
  - se non si carica, l'installer toglie il profilo appena scritto, così al lancio successivo riprova. Un `/etc/apparmor.d/bwrap` che c'era già, anche come symlink, non si tocca.

Dalla cartella di Mímir l'installer non segue i symlink: rifiuta esempi, template ed `exclude` che sono symlink e non crea un file personale al posto di un symlink. Lo stesso vale per le cartelle intermedie: se `profile/` o `.git/info`, risolte, non sono esattamente quelle attese (un symlink verso fuori o verso un'altra cartella di Mímir), si ferma senza modifiche. Se cambiano durante l'installazione, salta quei file ed esce con un errore. La cartella è scrivibile dalla sandbox, e un symlink porterebbe un segreto in un file leggibile o una scrittura fuori. In `~/.claude`, che la sandbox non scrive, i symlink (per esempio verso un repo di dotfiles) si seguono.

Test: `python3 -I test_install.py`, che usa copie di Mímir in una cartella temporanea e non tocca `~/.claude`. I test di `install.ps1`, e quelli di `bin/claude-mimir.ps1` in `test_claude_mimir.py`, girano se trovano PowerShell (`MIMIR_TEST_PWSH`, `pwsh` o `powershell`); altrimenti vengono saltati. Tutte le suite insieme, compresi i test degli hook: `python3 -I .github/scripts/run_tests.py`.

La cartella può stare ovunque: launcher e script ricavano il percorso dalla propria posizione. Il percorso però non deve contenere `*`, `?`, `[` o, per prudenza, `]`, `\` e caratteri di controllo (a capo, tab, DEL, C1), e deve essere UTF-8 valido: l'installer si ferma senza modifiche, perché Claude Code leggerebbe il percorso come un pattern nelle regole `Edit(…)` e, su Linux e WSL2, salterebbe le voci di `denyWrite` con `*`, `?` o `[`. Le parentesi tonde vanno bene. Fuori dal repo Claude Code vuole percorsi assoluti (marketplace, import in `~/.claude/CLAUDE.md`): se sposti la cartella, rilancia `install.sh` e li riallinea.

### CI
`.github/workflows/ci.yml` gira a ogni push e pull request, senza API key, con permessi in sola lettura e azioni fissate a uno SHA:
- job `test`: tutte le suite su Ubuntu, macOS e Windows, con Python 3.8 (il minimo) e 3.14; su Windows sia con Windows PowerShell 5.1 sia con PowerShell 7, da utente non amministratore. Lo stop da amministratore di `install.ps1` si prova come amministratore;
- job `install`: l'installer due volte in una HOME pulita, poi `.github/scripts/check_install.py` controlla i file prodotti e che il secondo lancio non cambi nulla. Su Ubuntu installa davvero `bubblewrap` e `socat`; su Windows passa da `install.ps1`.

Su Windows la classe `Installer` di `test_install.py` è saltata: lì `install.py` lo provano i test di `install.ps1` e il job `install`.

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
  - Se `LOCALAPPDATA` non è impostata, avvisa e parte senza il passaggio tra sessioni (Ratatoskr).
  - Provato nella CI (5.1 e 7) con un `claude` finto; non ancora con Claude Code su un Windows vero.
- **Passaggio tra sessioni (Ratatoskr)**: con le sessioni avviate dal launcher, quando il contesto supera i 200.000 token (il 20% di una finestra da 1M) Claude chiude il passo in corso, scrive il passaggio di consegne e ti chiede `/clear`. Nella sessione che parte dopo `/clear`, o in una nuova nella stessa cartella, Claude ti dice nella prima risposta percorso, età e dimensione del passaggio, senza leggerlo: il messaggio che l'hook manda su SessionStart dopo `/clear` non compare (prova del 09/10, Claude Code v2.1.296). Per riprendere chiedilo a Claude ("riprendi dal passaggio"): lo legge e riparte da lì. Il testo non entra nel contesto da solo, così un passaggio scritto da un contesto compromesso non arriva alla sessione nuova senza una tua richiesta, e puoi aprirlo prima.
  - I passaggi stanno fuori da Mímir, in `~/.local/state/mimir/handoff/` (`$XDG_STATE_HOME` se c'è; su Windows nativo `%LOCALAPPDATA%\mimir\handoff\`): `pending/` per quelli da riprendere, `consumati/` per quelli ripresi, cancellati dopo 7 giorni. Un passaggio di oltre 48 ore, probabilmente di un altro lavoro, va in `consumati/` con il suffisso `-scaduto`: Claude te lo dice nella prima risposta, con il percorso, senza proporre di riprenderlo. `pending/` non ha altre scadenze.
  - Il passaggio sta fuori dalle cartelle di lavoro. In modalità auto, nella prova del 09/10, né la scrittura (approvata dal classificatore) né la lettura alla ripresa hanno chiesto conferma. La doc (pagina permission-modes) dice che la prima lettura di un percorso esterno chiede il permesso una volta ("Yes, and keep allowing…") e che dopo il primo sì le letture esterne non chiedono più conferma. Con `permissions.blockReadsOutsideWorkingDirectories` la lettura è bloccata: apri il file a mano. In modalità default la lettura fuori dalle cartelle di lavoro probabilmente chiede conferma (dedotto dalla doc, da provare). Un passaggio oltre i 9.000 caratteri: Claude te ne dice la dimensione e chiede prima di leggerlo.
  - Soglia: il contesto di partenza di una sessione è già circa 49.000 token (prova del 09/10), quindi con `MIMIR_HANDOFF_TOKENS` sotto i 50.000 l'avviso scatta subito.
  - Fuori da Mímir perché la shell nella sandbox non ci può scrivere: un passaggio si crea solo con Write, che segue i permessi della sessione (in modalità auto lo approva il classificatore, come nella prova del 09/10). Così un comando della shell non può preparare un passaggio per un altro progetto né piazzare symlink, che l'hook comunque non segue. Write invece può: un contesto compromesso può scrivere un passaggio, anche per un'altra cartella, e alla ripresa lo vedi come uno vero. Per questo il testo non entra da solo nel contesto: se un passaggio non te lo aspetti, aprilo prima di chiedere di riprendere.
  - Soglia: `MIMIR_HANDOFF_TOKENS=<token>` nell'ambiente prima di lanciare il launcher. È in token perché la dimensione della finestra non arriva agli hook: con un modello da 200k abbassala (per esempio a 40000). Tienila ben sopra il contesto con cui parte una sessione (misuralo con `/context`; il 09/10 una sessione su Mímir era a 53.000 token dopo il primo comando): sotto, anche la sessione ripresa riceve subito l'avviso e il giro ricomincia. Per provare l'hook con una soglia bassa, dopo la ripresa esci invece di continuare.
  - Il passaggio è legato alla cartella in cui è partita la sessione (`CLAUDE_PROJECT_DIR`), anche se Claude poi fa `cd` altrove: due sessioni parallele partite nella stessa cartella se lo contendono (con i worktree non succede).
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
- **Modalità assistita** (oggi): sessioni avviate con `bin/claude-mimir`, con la sandbox qui sotto, i plugin di Mímir e l'hook sui comandi git che scrivono. L'utente approva le azioni.
- **Via libera a Claude** (lavoro autonomo, senza conferme): solo dentro un dev container con firewall in uscita e nessuna credenziale dell'host. Requisiti in `plugins/mimir/skills/sicurezza-claude-code/references/devcontainer.md`.
- Audit e hardening della configurazione: `/sicurezza-claude-code` (solo lettura finché non approvi le proposte).
- La sandbox copre solo i comandi shell: `Read`, `WebFetch`, MCP e hook restano fuori e si proteggono con i permessi.

## Sandbox
`sandbox.settings.json`: la sandbox dei comandi shell.
- **Filesystem**: scrittura limitata al progetto e alle cache di build, indicate una per una (`~/.npm/_cacache`, `~/.gradle/caches`, `~/.m2/repository`…). Niente `~/.cache`, `~/.npm` o `~/.gradle` interi: da lì partono gli MCP fuori dalla sandbox (`uvx`, `npx`) o codice alla build successiva (`~/.gradle/init.d`).
- **Credenziali**: `~/.ssh`, `~/.git-credentials`, `~/.aws/credentials`, `~/.docker/config.json`, `~/.gnupg`, `~/.m2/settings.xml`, `~/.gradle/gradle.properties`, `~/.claude.json`, i `.env`, `~/.config/gh/hosts.yml` e `~/.config/hub` (dove gh e hub possono tenere il token in chiaro; di gh solo `hosts.yml`, perché `config.yml` serve anche senza autenticazione) non si leggono né con lo strumento Read né dai comandi: le `deny` su `Read` valgono anche per la sandbox (provato il 05/10 con e senza le regole; per gh e hub l'11/10 con Claude Code 2.1.296: la sessione parte anche senza `~/.config/hub`, Read su `hosts.yml` è negato e nella sandbox `cat` di `hosts.yml` esce con Permission denied mentre `config.yml` si legge; in modalità auto il classificatore ferma i `cat` su `~/.config/gh` già prima della sandbox).
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
| `design-reviewer` | mimir | sonnet | Review in sola lettura dell'esperienza e della qualità visiva di una UI: compito principale, stati, accessibilità, gerarchia, testi, carattere, dati veri e scostamenti dalla richiesta, con i criteri di `design-ui`; dichiara ciò che non ha visto e separa l'accertato dal dedotto |
| `Explore` | `.claude/agents/` | haiku | Sostituisce l'Explore integrato di Claude Code (che userebbe il modello della sessione) per le ricerche nel codice. Attivo nelle sessioni avviate con `bin/claude-mimir` |

## Indice hook
| Hook | Plugin | Evento | Scopo |
|---|---|---|---|
| `git-guard.py` | mimir | PreToolUse (Bash, PowerShell) | Sui comandi git lanciati da Claude blocca i commit con attribuzioni all'AI o righe del messaggio oltre 72 caratteri, i commit con argomenti fuori da un elenco chiuso, il force push e ogni comando git con una regola `ask` non in forma semplice: commit, push, tag, reset, rebase, merge, checkout, restore, clean e gli altri, più le forme distruttive di branch, switch, stash, reflog, rm, checkout-index e worktree (`git branch -D`, `git stash drop`, `git rm -f`, `git checkout-index -f`, `git worktree remove`, anche senza `--force` perché cancella i file ignorati). Forma semplice: l'intero comando inizia con il prefisso esatto di una regola `ask` (`git reset …`, `git branch -D …`), senza `git -C`, opzioni globali, variabili, `&&`, `;`, `|`, heredoc, `$( )` o a capo; per branch, switch, stash, reflog, rm, checkout-index e worktree l'opzione distruttiva (o la parola: `drop`, `remove`) va subito dopo il sottocomando, da sola (`git rm -rf x` diventa `git rm -f -r x`). Le letture e le forme che non distruggono (`git branch -a`, `git stash list`, `git rm --cached`, `git worktree list`) passano anche nei comandi composti. `commit-tree` e `send-pack` sempre bloccati. In forma semplice non interviene: la conferma la chiede la regola `ask` di settings, perché un `ask` restituito dall'hook è stato ignorato da Claude Code (2.1.293, sandbox e modalità auto, 08/10). Riconosce git tra i token del comando: anche `git -C "cartella"`, `FOO=1 git`, `/usr/bin/git`, `git.exe`, `sh -c`, `eval`, `iex`, con un redirect attaccato a un argomento (`git push -f>/dev/null`), e nei corpi degli heredoc, anche quando `cat` o `tee` li scrivono in un file (il motivo indica di usare Write o Edit). Limiti: è una rete contro errori e injection banali, non contro un avversario determinato; un'analisi che supera 6 s (input costruiti come `git -c` ripetuto o molti `<<` sulla stessa riga) blocca qualsiasi comando, anche innocuo, prima del timeout di 10 s oltre il quale il comando passerebbe (misure nel CHANGELOG); non vede alias di git, alias e variabili di PowerShell, funzioni shell, script, `make`, hook git, comandi passati a `ssh`, `update-ref` e `fast-import`, un redirect prima del sottocomando, git ricavato da una sostituzione (`$(which git) push`), il comando tra virgolette di `git submodule foreach '…'` e `git bisect run '…'`, un'attribuzione scritta con caratteri a larghezza zero o omoglifi; le forme distruttive senza regola `ask` passano: `git branch -C` e `fetch +ref` (recuperabili dalla reflog), `stash pop`, `remote prune`, `symbolic-ref`, `submodule deinit -f`, `mv -f`, `read-tree --reset` (senza `-u` perde solo lo stage) e `gc --prune=now` (distrugge solo ciò che la reflog non tiene più); un argomento tra virgolette che contiene `<` o `>` viene tagliato lì e il comando può essere bloccato, e `git push -o -f` è bloccato anche se per git `-f` è il valore di `-o` (entrambi fail-closed); non è verificato che la regola `ask` riconosca il prefisso con un redirect attaccato all'opzione (`git branch -D>y x`), che l'hook lascia alla regola; un heredoc che cita soltanto un comando git che scrive è bloccato anche quando `cat` o `tee` lo scrivono in un file (un'esenzione è stata provata e ritirata dopo tre falle: CHANGELOG); `merge`, `revert`, `cherry-pick` e `pull` chiedono conferma ma creano commit senza il controllo del messaggio. `gh` e `hub` non passano dall'hook: hanno solo la regola `ask` sul prefisso (`gh …`, `hub …`), quindi `FOO=1 gh …`, `command gh`, `/usr/bin/gh`, `gh.exe`, `sh -c "gh …"`, `eval` e `$(which gh)` partono senza conferma, e con il solo `settings.template.json` (senza sandbox) quel prefisso è l'unico cancello; nella sandbox gh non ha il token (il keyring è irraggiungibile: niente socket Unix, verificato il 10/10) e `~/.config/gh/hosts.yml` e `~/.config/hub` sono tra le credenziali negate, ma `GH_TOKEN` o `GITHUB_TOKEN` nell'ambiente arriverebbero ai comandi. Fuori dalla sandbox `git credential fill` restituisce il token dell'helper di gh senza conferma. Gira tramite `run-python.sh`, che sceglie l'interprete (python3, python, py -3, ogni voce del PATH) e lo lancia con `-I` (niente `PYTHONPATH`, variabili `PYTHON*` e user site; restano `sitecustomize` e `.pth` dell'interprete, `BASH_ENV`, `LD_PRELOAD` e gli shim di versione, `py -3 -I` su Windows non è provato: elenco nel CHANGELOG) dalla cartella reale, scartando quelli nelle cartelle note che la sandbox può scrivere, sia dove il PATH li trova sia dove porta un link di cartella: il progetto (`CLAUDE_PROJECT_DIR`, altrimenti la cwd: un `.venv/bin` attivato o `node_modules/.bin`), le cartelle di `allowWrite` di `sandbox.settings.json` (un test le tiene allineate) e le temporanee della sandbox (`/tmp/claude`, `/tmp/claude-<uid>`, `TMPDIR`), più ogni voce relativa del PATH (`.`, `bin`, vuota). Limiti: con il progetto uguale alla home o a un suo antenato (`/home`, `/`) il progetto non si scarta, quindi un `python3` piantato nel PATH sotto la home verrebbe usato: non avviare Claude dalla home; le cartelle aggiunte ad `allowWrite` nel proprio `settings.json` non sono coperte; un link al file dell'interprete (non alla cartella) che porta in una di queste cartelle non viene seguito, quindi quell'interprete viene usato (il link va creato fuori dalla sandbox); i comandi degli hook li lancia `sh -c` e `bash` viene cercato nel PATH della sessione, quindi un `bash` piantato prima di quello di sistema viene usato (prova del 10/10, Claude Code 2.1.296 su Linux, e documentazione hooks); nelle sessioni di sviluppo di Mímir gli script degli hook stanno nel progetto, scrivibile dalla sandbox. Senza Python blocca i comandi git che scrivono (anche le letture di branch e stash, che senza Python non si distinguono). Test: `python3 plugins/mimir/hooks/scripts/test_git_guard.py` e `test_run_python.py` |
| `retro-nudge.py` | mimir | UserPromptSubmit | Ogni 25 prompt della stessa sessione aggiunge al contesto un promemoria: se sono emerse correzioni, proporre `/retro` a fine compito. Non scrive e non blocca mai. Contatori in `${CLAUDE_PLUGIN_DATA}/retro-nudge/`, tolti dopo 7 giorni. Test: `python3 plugins/mimir/hooks/scripts/test_retro_nudge.py` |
| `maven-sandbox.py` | mimir | SessionStart | Nei progetti con `pom.xml` avviati dal launcher (variabile `MIMIR_MAVEN_SETTINGS`) mette in contesto come lanciare Maven nella sandbox e il divieto di configurare a mano il proxy. Test: `python3 plugins/mimir/hooks/scripts/test_maven_sandbox.py` |
| `handoff.py` (Ratatoskr) | mimir | UserPromptSubmit, PostToolUse, SessionStart (startup, clear) | Legge dal transcript i token di contesto dell'ultima risposta (input e cache, come la statusline). Oltre `MIMIR_HANDOFF_TOKENS` (default 200000) chiede a Claude di scrivere il passaggio di consegne con la procedura di `passaggio-consegne` in `$MIMIR_HANDOFF_DIR/pending/<cartella>.md` (la cartella di avvio, `CLAUDE_PROJECT_DIR`; senza, la `cwd` dell'evento, che segue i `cd` di Claude) e di proporre `/clear`: a ogni prompt, e una sola volta per sessione dopo un tool (stato in `${CLAUDE_PLUGIN_DATA}/handoff/`; senza quella cartella, solo a ogni prompt). All'avvio e dopo `/clear`, se c'è un passaggio della cartella, lo sposta in `consumati/` (0600) e lo segnala: un messaggio per te (dopo `/clear` non compare) e a Claude l'istruzione di dirti nella prima risposta percorso, età e dimensione e di leggerlo solo se chiedi di riprendere, come dati. Non ne inietta il testo. Cancella i consumati oltre 7 giorni; un passaggio di oltre 48 ore lo archiviano sia la ripresa sia l'avviso, con il suffisso `-scaduto`, e Claude te lo dice senza proporre di riprenderlo. Non segue i symlink. Attivo solo con `MIMIR_HANDOFF_DIR`, esportata dai launcher fuori da Mímir; ignora i subagent; non blocca mai. Il transcript può essere indietro di un turno. Test: `python3 plugins/mimir/hooks/scripts/test_handoff.py` |
