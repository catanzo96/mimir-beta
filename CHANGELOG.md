# Changelog

## 2026-10-09 (Ratatoskr: correzioni dalla review)
- La ripresa non inietta più il passaggio: SessionStart lo archivia, mostra all'utente percorso, età e dimensione e dice a Claude di leggerlo solo se l'utente chiede di riprendere, come dati e con l'ok prima di azioni con effetti; oltre 9.000 byte Claude chiede prima di leggerlo. Prima il testo entrava in `additionalContext`, che l'utente non vede, e un contesto compromesso sopravviveva a `/clear`.
- Un passaggio di oltre 48 ore non si perde più in silenzio: avviso e ripresa lo archiviano con il suffisso `-scaduto` e lo dicono all'utente; l'avviso chiede un passaggio nuovo. `pending/` resta senza altre scadenze, documentato.
- Archivio con nomi univoci (prima un passaggio dello stesso secondo veniva sovrascritto) e i 7 giorni contati dall'archiviazione.
- `MIMIR_HANDOFF_DIR` relativa ignorata; una FIFO o un file non UTF-8 in `pending/` non bloccano più l'hook.
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
- Idee da impeccable, skills di Emil Kowalski e taste-skill, riscritte da zero.

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
