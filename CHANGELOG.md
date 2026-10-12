# Changelog

## 2026-10-10 (installer-2: rilievi di installer, launcher e CI)
- `install.py` su Linux e WSL2: con apt-get lancia prima `apt-get update` (3 tentativi, timeout HTTP di 30 s), perché con indici vecchi l'installazione non trova i pacchetti; se l'aggiornamento fallisce avvisa e installa con gli indici presenti. Il profilo AppArmor di `bwrap` si ricarica con `systemctl reload apparmor` e, se systemd manca o il comando fallisce, con `apparmor_parser -r`; la conferma mostra i comandi. La CI non prepara più apt da sé, così il percorso di `install.py` è provato; il timeout di 8 minuti passa allo step dell'installer. Review con `code-reviewer` e `security-reviewer`.
- `install.py` si ferma senza modifiche se il percorso di Mímir contiene `*`, `?`, `[`, `]` o `\`: secondo la doc le regole `Edit(…)` scritte a mano seguono gitignore senza escape e su Linux una voce di `denyWrite` con `*`, `?` o `[` viene saltata, quindi la protezione sarebbe sparita senza avviso; `]` e `\` per prudenza, e i caratteri di controllo, perché gitignore va a righe. Le parentesi sono letterali e restano ammesse (test con `mimir (copia)`).
- `install.py` si ferma senza modifiche se `settings.template.json` ha chiavi diverse da `attribution`, `skillListingBudgetFraction` e `permissions` con solo `ask` e `deny`: prima della prima installazione una sessione nella sandbox può modificare il template, che l'installer unisce fuori (`allow`, hook, sandbox allentata). Il controllo vale solo per il template, non per `~/.claude/settings.json` (test con un settings utente pieno di chiavi diverse). Il README chiede di lanciare l'installer subito dopo il clone, o di controllare prima con `git status` e `git diff HEAD`: il controllo copre solo il template, non installer, launcher, hook o regole modificati. Il messaggio d'errore mostra i nomi delle chiavi con `repr`, senza sequenze al terminale.
- `install.py` si ferma senza modifiche se il template o `~/.claude/settings.json` contengono, in una chiave o in un valore, un carattere non scrivibile in UTF-8 (un surrogato isolato come `"\ud800"`, che il JSON accetta): prima l'errore arrivava in scrittura, con un traceback e `CLAUDE.md` già scritto. Allo stesso modo si ferma se il percorso di Mímir non è UTF-8 valido (su Linux un byte come `\xff` nel nome: prima `profile.md` e `inbox.md` erano già creati) o contiene DEL o un carattere di controllo C1. Un errore di codifica in scrittura, come rete di sicurezza, ora si segnala come gli errori di I/O, con i file già scritti.
- `install.py` rifiuta `NaN`, `Infinity` e `-Infinity` nel template e in `~/.claude/settings.json`: `json` li accetta in lettura e li riscriverebbe tali e quali, lasciando un `settings.json` che non è JSON valido. Un template modificato dalla sandbox poteva farlo dentro `attribution`.
- `install.py` si ferma senza modifiche se `profile/` o `.git/info`, risolte con `realpath`, non sono esattamente le cartelle attese: `O_NOFOLLOW` copre solo l'ultimo componente, e una cartella sostituita con un symlink portava letture e creazioni fuori da Mímir o in una cartella protetta come `bin/`. In scrittura il controllo si ripete, perché la sandbox può cambiare le cartelle nel frattempo: il file si salta e l'installer esce con 1. Resta una finestra tra controllo e apertura (chiuderla richiederebbe `dir_fd` per ogni componente); il guadagno per chi la sfrutta è un `profile.md` o un `exclude` scritti altrove.
- `install.py` aggiunge `/.idea` a `.git/info/exclude`: la sandbox crea `.idea` come device a caratteri, non come cartella, e la voce `.idea/` del `.gitignore` vale solo per le cartelle, quindi `git status` lo mostrava come non tracciato.

## 2026-10-10 (git-guard: comandi git distruttivi)
- Regole `ask` in `settings.template.json` e `sandbox.settings.json` per reset, rebase, merge, cherry-pick, revert, pull, am, clean, restore, checkout, update-ref, filter-branch, prune e per le forme distruttive di branch, switch, stash e reflog (`git branch -D`, `git stash drop`…).
- Hook `git-guard.py`: `git commit` ammesso solo nelle forme note (`-m`/`--message` ripetuti, un solo `-F`/`--file`, `--amend`, `--amend --no-edit`); le righe con `#` contano nella lunghezza.
- Hook `git-guard.py`: la forma semplice vale per ogni comando con una regola `ask`, non più solo per commit, push e tag. Bloccati `git -C . reset --hard`, `cd x && git rebase`, una variabile in posizione di comando (`"$GIT" -C x push`), i sottocomandi espansi dalla shell (`git {reset,--hard}`, `git$IFS"push"`, `git @args` e `git ($b)` su PowerShell). Le letture (`git branch -a`, `git stash list`, `grep -rn git dir/`) passano. Tempo lineare anche su input lunghi e ripetuti; review con `code-reviewer`, 311 casi di test.
- Wrapper `run-python.sh --fail-closed`: senza Python blocca ogni sottocomando che git-guard tratta come scrittura (prima solo commit, push e tag), anche le letture di branch e stash; un test lo tiene allineato a `WRITE_SUBCOMMANDS`.
- Prova in sessione vera (`bin/claude-mimir`, Claude Code 2.1.296, repo usa e getta): `git commit -F <assoluto>`, `git branch -d` e `git reset --hard` chiedono conferma in modalità normale e auto; `git merge-base`, `git branch -a` e `git log` no; `git commit … && …` e `git -C . reset --hard` bloccati, e Claude li rilancia in forma semplice; la riga con `#` resta nel messaggio. Nel transcript un comando confermato a mano non ha la riga "Allowed by auto mode classifier".
- Skill `git-workflow`: branch nuovi con `git switch -c`, perché `git checkout` chiede sempre conferma. `scrivi-skill/references/hook.md`: posizione di comando e tempo lineare. README, `commit` e `sicurezza-claude-code` descrivono l'hook sui comandi git che scrivono.

## 2026-10-10 (git-workflow: commit da modifiche sovrapposte)
- Skill `git-workflow`, sezione "Più commit da modifiche sovrapposte": quando i temi toccano gli stessi file, lo stato di ogni tema si fotografa come tree con un indice temporaneo (`GIT_INDEX_FILE`) e dopo l'ok si committa in ordine con `git read-tree`. Usato per i commit dell'health-check e provato in un repo di prova (un file diviso tra due temi, confronto finale visto segnalare un albero diverso).

## 2026-10-10 (health-check: ripetizioni, nuova regola, confini)
- Regola in `rules/working-style.md`: nei repo dei progetti non si creano file di metodo (piani, analisi, stime, report, passaggi) se non richiesti. Prima era ripetuta in sei skill; `stime`, `stato-e-rischi`, `pianificazione` e `passaggio-consegne` ora la danno per scontata, `documentazione-tecnica` tiene la sua variante (anche il README si tocca solo con ok).
- Ripetizioni delle regole tolte dove non aggiungevano nulla dello stack: dipendenze nuove (`nodejs`, `cpp`, `python`, `php`, `refactoring`, `pianificazione`, `script-shell`), segreti nei log (`nodejs`, `quarkus`, `go`). Restano i passaggi che dicono dove si nasconde un segreto o come si inghiotte un'eccezione in quel linguaggio. `git-workflow` elenca solo le approvazioni che aggiunge alla regola (rebase e merge).
- Confini dichiarati nel corpo, description invariate: `analisi-tecnica` ("Quando non usarla") con `documentazione-tecnica`, `debugging` e `ticket`; SAL tra `stato-e-rischi` (contenuto), `riunioni` (riunione) e `presentazioni` (slide).

## 2026-10-10 (health-check: correzioni dall'audit)
- `plugin.json` di `mimir` e `brokkr` con `author`: `claude plugin validate --strict` falliva su entrambi (Claude Code 2.1.296), ora passa.
- Agent `code-reviewer`: ricava il branch base con `git symbolic-ref refs/remotes/origin/HEAD`, senza rete come gli altri agent di sola lettura, invece di `git remote show origin`.
- Skill `pianificazione`: la tabella dei modelli diventa un rimando a `rules/working-style.md`; la copia aveva perso "o inviare" nella condizione su `haiku`.
- Maven nella sandbox: `spring-boot/references/verifica.md`, `quarkus`, `design-api` e l'esempio di `delega/references/brief-esempi.md` dicono di aggiungere `-llr -s "$MIMIR_MAVEN_SETTINGS"` con il launcher, come `java`.
- `manutenzione-mimir/references/misure.md`: lo script dei riferimenti rotti cerca anche nelle skill dell'altro plugin (falso positivo su `decisioni` → `analisi-tecnica/templates/adr.md`).

## 2026-10-10 (retro del design delle interfacce)
- Skill `git-workflow`: si attiva anche per cambiare o unire un branch; pulizia dopo il merge in tre passi (l'utente cancella il remoto, la sessione il locale con `git branch -d`, un blocco di comandi per l'utente con `git config --remove-section`, `git fetch --prune` e `git branch -a`).
- Skill `commit`: nella richiesta di approvazione i file si elencano uno per uno, senza graffe né conteggi.
- Skill `animazioni-ui`: nelle prove headless si porta `currentTime` delle animazioni a mano, perché la timeline può restare ferma.
- Skill `python`: nei test che girano su Windows i percorsi assoluti si costruiscono, mai scritti come `/x/y` (`os.path.isabs` da Python 3.13).

## 2026-10-10 (design delle interfacce: correzioni dalla review)
- Provenienza: `THIRD_PARTY.md` elenca i file tradotti o adattati da skills di Emil Kowalski (MIT), taste-skill (MIT) e impeccable (Apache-2.0, testo in `LICENSES/`); la nota del 09/10 "riscritte da zero" è corretta. La riscrittura o l'eliminazione di quei file è prevista prima della pubblicazione.
- `animazioni-ui/references/ricette.md`: menu, modale, sfondo e drawer chiusi diventano `visibility: hidden` alla fine della chiusura, così escono dal focus e non catturano i clic (provato in Chromium headless); drawer laterali con `translateX` (destra di default), dal basso con `translateY`; l'altezza della fisarmonica è l'eccezione dichiarata al divieto di animare il layout.
- Agent `design-reviewer`: euristiche di Nielsen con la gravità del problema peggiore (0 nessun problema, 4 impedisce il compito, `n/a` se non si applica), senza totale e con la corrispondenza alle gravità delle segnalazioni; non precarica più `design-ui` ma ne carica i criteri di verifica, e carica `clean-code` per `a11y.md`; la description dice che non rivede il codice. `clean-code`, "Quale review": riga per `design-reviewer`.
- Minori: in `animazioni-ui` non si animano scorciatoie e azioni ripetute da tastiera, mentre aprire con Invio segue la regola del clic; `design-ui` controlla a 320px come `ui-casi-limite`; `anti-pattern.md` allineato a `mobile-web.md` (`svh` per il primo schermo, `dvh` per il guscio); `prototipi-ui` registra la route di prova solo in sviluppo; `react`, `vue` e `angular` rimandano a `ui-casi-limite`.

## 2026-10-10 (Ratatoskr: chiave del passaggio)
- Il passaggio è legato alla cartella di avvio della sessione (`CLAUDE_PROJECT_DIR`), con la `cwd` come ripiego. Prima la chiave veniva dalla `cwd` dell'evento, che segue i `cd` di Claude: nella prova del 09/10, dopo un `cd` nella cartella di Mímir l'avviso proponeva di scrivere il passaggio sotto la chiave di Mímir, e la ripresa nel progetto non l'avrebbe trovato.

## 2026-10-10 (retro di Ratatoskr)
- Regole: un ok condizionato o ambiguo non vale come approvazione; prima di terminare processi si propone il comando con il pattern o i PID; il controllo visto fallire vale anche per i test delle correzioni nate da una review.
- Skill `python`: FIFO e socket nei test vanno tolti con `os.remove` e la suite va lanciata con un timeout esterno; un errore di I/O su un file si simula sostituendo la funzione, non con i permessi.
- `scrivi-skill/references/hook.md`: il `systemMessage` di SessionStart dopo `/clear` non compare; una funzione che dipende da come Claude Code mostra o passa qualcosa si prova a mano in una sessione vera prima del merge.

## 2026-10-09 (Ratatoskr: correzioni dalla review)
- La ripresa non inietta più il passaggio: SessionStart lo archivia, mostra all'utente percorso, età e dimensione e dice a Claude di leggerlo solo se l'utente chiede di riprendere, come dati e con l'ok prima di azioni con effetti; oltre 9.000 byte Claude chiede prima di leggerlo. Prima il testo entrava in `additionalContext`, che l'utente non vede, e un contesto compromesso sopravviveva a `/clear`.
- Un passaggio di oltre 48 ore non si perde più in silenzio: avviso e ripresa lo archiviano con il suffisso `-scaduto` e lo dicono all'utente; l'avviso chiede un passaggio nuovo. `pending/` resta senza altre scadenze, documentato.
- Archivio con nomi univoci (prima un passaggio dello stesso secondo veniva sovrascritto) e i 7 giorni contati dall'archiviazione.
- `MIMIR_HANDOFF_DIR` relativa ignorata; una FIFO o un file non UTF-8 in `pending/` non bloccano più l'hook.
- Dopo la security review: un errore inatteso dà exit 0 e una riga su stderr invece di un traceback con exit 1; un consumato non cancellabile non ferma l'archiviazione; permessi e mtime si fissano prima dello spostamento. README: Write, a differenza della shell, può scrivere un passaggio.
- Dopo la prova manuale (modalità auto, Claude Code v2.1.296): il systemMessage di SessionStart dopo `/clear` non compare, quindi è Claude ad annunciare il passaggio (anche scaduto) nella prima risposta, senza leggerlo. README: esiti della prova e soglia minima di circa 50.000 token.
- Skill `passaggio-consegne`: description e testi per la ripresa su richiesta. README: uso, permessi di lettura fuori dalle cartelle di lavoro, indice degli hook. Test senza soglie di 1 s.

## 2026-10-09 (retro della fase 1)
- Skill `git-workflow`: merge sul branch base solo con la CI del branch verde; il lavoro di più sessioni o di un worktree passa da un branch, il commit diretto su main solo per modifiche piccole di una sessione. Prima di `switch` o `checkout` controllare se cambiano file protetti e, se sì, far lanciare il comando all'utente.
- Regola e skill `scrivi-skill`: i comandi da lanciare a mano vanno per il terminale dell'utente, senza `!`, in righe brevi con `S=` per i percorsi lunghi; `!` solo per un comando breve e autonomo, perché ogni `!` parte in una shell nuova.
- Skill `ci-cd` (`references/piattaforme.md`): sui runner Windows la 5.1 con un ambiente ridotto rianalizza i moduli a ogni avvio; passare `PSModuleAnalysisCachePath`.
- Skill `script-shell`: `GetFolderPath` della 5.1 può restituire una stringa vuota; leggere `$env:LOCALAPPDATA` e gestire il vuoto.
- Skill `debugging`: bisezione dell'ambiente con gruppi che coprono tutto, caso con tutti i gruppi, poi per aggiunta e per esclusione.

## 2026-10-09 (limatura, fase 1, passi 6 e 7: CI)
- CI GitHub Actions (`.github/workflows/ci.yml`) a ogni push e pull request, senza API key, `permissions: contents: read`, azioni fissate a SHA e `persist-credentials: false`.
  - Job `test`: tutte le suite (`.github/scripts/run_tests.py`) su Ubuntu, macOS e Windows, Python 3.8 e 3.14; su Windows con Windows PowerShell 5.1 (`MIMIR_TEST_PWSH=powershell`, perché sui runner `pwsh` viene prima) e con pwsh. I test girano con un utente locale non amministratore (`.github/scripts/run-as-user.ps1`), lo stop di `install.ps1` da amministratore.
  - Job `install`: installer due volte in una HOME pulita e controllo dei file prodotti (`.github/scripts/check_install.py`); su Ubuntu `bubblewrap` e `socat` installati davvero, `apt-get update` con timeout e tentativi.
  - Su Windows la classe `Installer` di `test_install.py` è saltata, dichiarato; i casi del launcher con argomenti vuoti o con `"` sono `expectedFailure`.
  - `.github` entra tra le cartelle protette da `install.py`.
  - Verde 12/12 (run 37952642178 su `cd3eebc`), vista fallire su un branch di prova (run 37907359520).
- Test su Windows: i job con PowerShell 5.1 passano da circa 17 a 2 minuti. Misurato su un branch di prova (run 37932870634 e 37939365792): l'avvio della 5.1 è veloce, l'autoload dei moduli costava 13-22 s a ogni avvio con l'ambiente ridotto dei test. I test passano `PSModuleAnalysisCachePath` del runner, che da sola basta (confermato dalla CI); il prodotto non cambia. Resta aperto perché `LOCALAPPDATA` riusata non bastava.
- `bin/claude-mimir.ps1` legge la cartella di Ratatoskr da `LOCALAPPDATA` invece che da `GetFolderPath`, che nella 5.1 restituiva una stringa vuota e fermava il launcher (CI rossa su `d2152cf`). Senza `LOCALAPPDATA` avvisa e parte senza passaggio tra sessioni.
- README: sezione CI, stato della prova su Windows, comando per tutte le suite.

## 2026-10-09 (Ratatoskr: passaggio tra sessioni)
- Hook `handoff.py` (Ratatoskr) su UserPromptSubmit, PostToolUse e SessionStart: oltre `MIMIR_HANDOFF_TOKENS` token di contesto (default 200000, il 20% di 1M) chiede a Claude di scrivere il passaggio di consegne e di proporre `/clear`; all'avvio e dopo `/clear` lo inietta nella nuova sessione come dati da verificare, con un messaggio per l'utente, e lo archivia in `consumati/`, cancellato dopo 7 giorni. Un passaggio di oltre 48 ore si archivia senza iniettarlo. Test in `test_handoff.py`, anche nella CI.
- Dopo la review di sicurezza: l'hook non segue i symlink, legge al massimo 9.001 caratteri, crea cartelle 0700 e archivia con 0600, e senza `CLAUDE_PLUGIN_DATA` non scrive stato in `/tmp`.
- I launcher esportano `MIMIR_HANDOFF_DIR` fuori da Mímir (`~/.local/state/mimir/handoff`, su Windows `%LOCALAPPDATA%\mimir\handoff`): la shell nella sandbox non ci scrive, quindi un passaggio si crea solo con Write.
- Skill `passaggio-consegne` (destinazione e limite di 9.000 caratteri su richiesta dell'hook) e `contesto-e-costi` (rimando a Ratatoskr); README: uso, indice hook, tema.

## 2026-10-09 (design delle interfacce)
- Skill `design-ui`: lettura della richiesta in una riga con tre assi (varietà, movimento, densità), superfici (lavorare, leggere, convincere), design system ufficiali e token, default da rifiutare, checklist sul risultato; in `references/` anti-pattern, pagine marketing, rifacimento, mobile web.
- Skill `animazioni-ui`: frequenza e scopo prima di animare, strumento più semplice, curve e durate, interruzione, movimento ridotto, revisione dal correttivo più forte; in `references/` ricette, gesti e spring, vocabolario.
- Skill `ui-casi-limite`: dati peggiori plausibili e limiti dello schema, stati vuoto/uno/tanti, firme dei guasti, resoconto prima delle correzioni; catalogo con dati italiani.
- Skill `prototipi-ui`, solo manuale: varianti divergenti dietro un selettore, poi promozione della scelta.
- Agent `design-reviewer` (sonnet, sola lettura): revisione dell'esperienza e della qualità visiva.
- `architettura-frontend`, `react`, `vue`, `angular` rimandano alle skill di design.
- Fonti: impeccable, skills di Emil Kowalski e taste-skill. Correzione del 10/10: la nota diceva "riscritte da zero", ma diversi file sono traduzioni o adattamenti stretti; l'elenco è in `THIRD_PARTY.md`.

## 2026-10-09 (retro della CI)
- Skill `ci-cd`: esito letto job per job (annullato o in timeout ≠ fallito), pipeline vista fallire su un branch di prova, misura prima di alzare un timeout; in `references/piattaforme.md` runner Windows da amministratore, `pwsh` prima di `powershell`, `persist-credentials: false`.
- Skill `script-shell`: tre trappole di PowerShell 5.1 (code page OEM, formato di `ConvertTo-Json`, variabili mancanti in un ambiente da zero).
- Skill `git-workflow`: file protetti che fermano `switch`, `checkout` e `stash`; la sezione `branch.<nome>` che `branch -D` non toglie nella sandbox; `gh` con il token nel keyring, che nella sandbox non si autentica.
- Skill `python`: `newline=` in `Path.write_text` dalla 3.10.

## 2026-10-08 (limatura, fase 1, passo 6)
- `git-guard.py` blocca un commit se non può leggere il file di `-F`/`--file`: file inesistente o non regolare, percorso con variabili, `~` o caratteri jolly (la shell li espande, l'hook leggerebbe un altro file), file oltre 100000 caratteri. Prima il messaggio non veniva controllato e restava solo la conferma `ask`.
- Skill `commit`: il file del messaggio si passa a `git commit -F` con il percorso assoluto restituito da Write, non con `$TMPDIR`.

## 2026-10-08 (limatura, fase 1, passo 5)
- `bin/claude-mimir.ps1`, launcher per Windows nativo, **non ancora provato su Windows**.
  - Stessi argomenti e sottocomando `agents` di `bin/claude-mimir`; in PowerShell 5.1 gli argomenti vuoti si perdono e i doppi apici interni non arrivano.
  - Non esporta `MIMIR_MAVEN_SETTINGS`: l'hook di Maven farebbe lanciare le build offline come nella sandbox.
  - Senza sandbox: a ogni avvio un avviso su stderr dice cosa si perde (rete e file liberi per la shell) e cosa resta attivo (regole ask/deny degli strumenti e hook).
  - Passa `sandbox\windows.settings.json` (ignorato da git, nella cartella protetta `sandbox`): `sandbox.settings.json` con `sandbox` = `{"enabled": false}`, così non vale nemmeno un blocco `sandbox` dei settings personali. Si confronta a ogni avvio con il contenuto calcolato e si riscrive se è diverso, anche se è stato manomesso.
  - Se `sandbox.settings.json` manca o non è valido, `claude` non parte.
  - Test in `test_claude_mimir.py`, con un `claude` finto; controllato con PSScriptAnalyzer sul profilo 5.1.
- `install.py`: su Windows nativo il messaggio finale indica `bin\claude-mimir.ps1`; `test_claude_mimir.py` entra tra i file protetti.

## 2026-10-08 (limatura, fase 1, passo 4)
- `install.ps1` per Windows nativo, **non ancora provato su Windows**: la prova è prevista nella CI (passo 6) e nella prova manuale.
  - Trova Python 3.8+ scartando lo stub dello Store e controlla Git for Windows; se mancano propone winget e rilegge il PATH.
  - Lancia `install.py` con `-I`.
  - Propone WSL2 solo con un sì o con `-InstallWsl`, ed eleva solo `wsl --install`.
  - Da amministratore si ferma e dice come rilanciarlo da utente normale.
  - Scritto per PowerShell 5.1: controllato con PSScriptAnalyzer (`PSUseCompatibleSyntax` e `PSUseCompatibleCommands` sul profilo 5.1) e provato con pwsh 7 su Linux, con comandi finti.
- `install.ps1` entra tra i file protetti.

## 2026-10-08 (limatura, fase 1)
- Installer in Python, solo libreria standard: `install.sh` cerca Python 3.8+ e lancia `install.py` con `-I`. Non serve più `jq`. L'installer legge e valida tutti i file prima di scrivere e scrive solo ciò che cambia, con un backup.
- `install.py` protegge i file di Mímir: `sandbox.filesystem.denyWrite` e `ask` su `Edit(//…)`, con le voci tolte se la cartella si sposta. Prima lo faceva uno script a mano.
- `install.py` aggiunge a `.git/info/exclude` i file vuoti creati dalla sandbox.
- Su Linux e WSL2, `install.py` installa con conferma `bubblewrap`, `socat` e il profilo AppArmor. Test in `test_install.py`, da lanciare con `python3 -I`.
- `install.py` non segue i symlink nella cartella di Mímir (`O_NOFOLLOW` e controllo del file regolare in lettura, `O_EXCL` in creazione). Un `settings.template.json` che punta alle credenziali le avrebbe unite in `settings.json`; un `inbox.md` pendente avrebbe fatto scrivere fuori dalla sandbox. I symlink in `~/.claude` si seguono.

## 2026-10-08 (retro)
- Regola: se una protezione blocca una modifica, non aggirarla; `scrivi-skill` descrive come prepararla nello scratchpad (controllo del testo atteso, prova su copia, comando `!` su una riga).
- `ricevere-review`: nella review di un controllo di sicurezza si correggono subito solo i passaggi in silenzio dimostrati; il resto si annota.
- `hook.md`: riconoscimento del comando con un tokenizer, fail-closed mirato, regole PowerShell, timeout che fa passare il comando, `ask` dell'hook non affidabile. `script-shell`: virgolette di PowerShell 5.1, PATH dopo winget, UTF-8 senza BOM. Plugin `mimir` 0.18.1.

## 2026-10-07 (limatura, fase 1)
- Hook multipiattaforma: gli hook passano da `run-python.sh`, che sceglie l'interprete (`python3`, `python`, `py -3`) invece di affidarsi allo shebang, e leggono e scrivono in UTF-8. Senza Python, o con un errore interno, i comandi git che scrivono vengono bloccati invece di passare senza controllo.
- `check-commit-message.py` diventa `git-guard.py`: riconosce git tra i token del comando (`git -C "cartella"`, `FOO=1 git`, `/usr/bin/git`, `git.exe`, `sh -c`, `eval`, corpi degli heredoc, tool PowerShell) invece che con regex, che su input costruiti andavano in timeout e lasciavano passare il comando. Blocca il force push e ogni commit, push o tag non in forma semplice: la conferma resta alle regole `ask` di settings, perché Claude Code ha ignorato un `ask` restituito dall'hook. Limiti dichiarati nel README.
- La skill `commit` scrive il messaggio in un file e usa `git commit -F <file>` come comando a sé. Regole `ask` su `git tag` anche in `settings.template.json`.
- Regole `ask` e `deny` anche per il tool PowerShell; `.gitattributes` fissa le fini riga degli script. Plugin `mimir` 0.18.0.

## 2026-10-07 (retro)
- Verifica della sandbox con il launcher: `/sandbox` non si apre quando la configurazione arriva da `--settings`; README e `sicurezza-claude-code` indicano la prova di rete (host ammesso risponde, host escluso bloccato). Plugin `mimir` 0.17.2.
- `git-workflow`: sezione "Nella sandbox" su `.git/config` protetto e push autenticati lanciati dall'utente. Plugin `mimir` 0.17.1.
- README, Confini: niente dati personali o aziendali nemmeno nella configurazione.

## 2026-10-07 (prima versione pubblica)
- Mímir pubblicato come pacchetto generico: nel repo solo il metodo, i dati personali in file locali ignorati da git.
  - `profile/profile.md` e `inbox.md` locali, creati da `install.sh` a partire da `profile/profile.example.md` e `inbox.example.md`.
  - In `sandbox.settings.json` restano solo i registri pubblici; gli host privati vanno in `~/.claude/settings.json`, le cui liste Claude Code unisce a quelle del launcher.
  - Licenza MIT.
  - README con installazione, personalizzazione e uso.
- Plugin `mimir` 0.17.0, `brokkr` 0.7.0.
