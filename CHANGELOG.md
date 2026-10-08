# Changelog

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
