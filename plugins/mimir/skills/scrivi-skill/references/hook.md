# Scrivere un hook

Un hook è un comando (o una chiamata HTTP, un prompt, un agent) che l'harness esegue a un evento della sessione. Vale al 100% perché non dipende da ciò che Claude decide. Per le regole di comportamento, che Claude può interpretare, usa una regola o una skill. Dettagli e nomi sulla pagina `hooks` della documentazione di Claude Code, da controllare quando cambia la versione.

## Eventi che servono di più
| Evento | Quando scatta | Può bloccare? |
|---|---|---|
| `PreToolUse` | prima che un tool venga eseguito | sì |
| `PostToolUse` | dopo un tool riuscito | no (il tool è già girato); lo stderr arriva a Claude |
| `UserPromptSubmit` | quando l'utente invia un prompt | sì |
| `SessionStart` | all'avvio, alla ripresa, dopo `/clear` o `/compact` | no; lo stdout entra nel contesto |
| `Stop` | quando Claude sta per concludere il turno | sì (lo obbliga a continuare) |
| `SubagentStart`, `SubagentStop` | avvio e fine di un subagent | `SubagentStop` sì |
| `PreCompact` | prima della compattazione | sì |
| `PermissionRequest` | quando sta per comparire una richiesta di permesso | decide lui |

Ne esistono molti altri (`PostToolUseFailure`, `Notification`, `SessionEnd`, `PreModelSwitch`, `FileChanged`, ...): l'elenco completo e quali bloccano sono nella pagina `hooks`. Un evento che non blocca non può fermare l'azione: se serve un divieto, usa `PreToolUse`.

## Input
Lo script riceve un oggetto JSON su stdin. Campi comuni: `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`; per gli eventi sui tool anche `tool_name` e `tool_input` (per Bash, `tool_input.command`). Leggi con un parser JSON, non con grep sul testo. In Python decodifica i byte in UTF-8 (`json.loads(sys.stdin.buffer.read().decode("utf-8"))`) e scrivi stdout e stderr in UTF-8 (`sys.stdout.reconfigure(encoding="utf-8")`): su Windows la codifica di default della console non lo è.

## Uscita
- **Exit 0**: via libera. Lo stdout è letto come JSON se è un oggetto; altrimenti è solo log, salvo `UserPromptSubmit`, `SessionStart` e pochi altri, dove entra nel contesto di Claude.
- **Exit 2**: blocca (dove l'evento lo consente) e lo stderr viene mostrato a Claude come motivo. Scrivi un messaggio che dica cosa correggere: Claude lo legge e riprova.
- **Qualsiasi altro codice (anche 1)**: errore non bloccante, l'azione prosegue. Un controllo che deve bloccare ma esce con 1 non blocca: è l'errore più comune.
- **JSON in stdout con exit 0**, dove l'evento supporta una decisione:
  - `PreToolUse`: `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow|deny|ask|defer", "permissionDecisionReason": "...", "updatedInput": {...}}}`; `updatedInput` riscrive i parametri del tool. Non affidarti a `ask` per un controllo di sicurezza: l'08/10, con Claude Code 2.1.293 in sandbox e modalità auto, un `ask` dell'hook è stato ignorato e il comando è partito. Per chiedere conferma usa una regola `ask` di settings e fai bloccare all'hook le forme che la regola non riconosce;
  - `UserPromptSubmit`, `PostToolUse`, `Stop` e altri: `{"decision": "block", "reason": "..."}`;
  - `PostToolUse` e `SessionStart`: `additionalContext` per aggiungere testo al contesto di Claude;
  - campi universali: `continue: false` con `stopReason`, `systemMessage`.
- Il `systemMessage` di `SessionStart` dopo `/clear` non compare all'utente (prova con Claude Code v2.1.296): se l'utente deve saperlo, chiedi a Claude nell'`additionalContext` di dirlo nella prima risposta.
- Una funzione che dipende da come Claude Code mostra o passa qualcosa (messaggi, contesto, permessi) va provata a mano in una sessione vera prima del merge: la documentazione non basta.
  Non mischiare i due stili: con exit 2 il JSON è ignorato.

## Matcher e filtri
- `matcher` è una stringa unica sul nome del tool (`PreToolUse`, `PostToolUse`): `Bash`, oppure `Edit|Write` per più tool. Usa una stringa, non un array. Con caratteri diversi da lettere, cifre, `_`, `-`, spazi, `|`, `,` è una regex (non ancorata): `^Bash$`, `mcp__.*`.
- Il nome del tool è sensibile alle maiuscole: `Bash`, non `bash`.
- Su Windows senza Git Bash i comandi passano dal tool `PowerShell`: le regole `Bash(...)` non lo coprono. Servono regole `PowerShell(...)` e il matcher `Bash|PowerShell`.
- Altri eventi filtrano su altro (per `SessionStart` la sorgente: `startup`, `resume`, `clear`, `compact`); `UserPromptSubmit` e `Stop` non hanno matcher.
- Il campo `if` (permission rule syntax, per esempio `Bash(git *)`) restringe ancora, ma solo sugli eventi dei tool. Non sostituisce il controllo nello script: i pattern complessi girano comunque.

## Timeout
Il campo `timeout` è in secondi: default 600 per i comandi, 30 per `UserPromptSubmit`. Imposta un valore breve (5-10 s per un controllo, come `git-guard.py`): un hook lento rallenta ogni azione. Niente rete negli hook di controllo, e nessun dato sensibile nei log.

## Dove si definisce
- **Plugin**: `hooks/hooks.json` del plugin, con la chiave `hooks` (come in `plugins/mimir/hooks/hooks.json`). Vale per chi installa il plugin. Script in `hooks/scripts/`.
- **Settings**: `hooks` in `settings.json` (utente, progetto, locale, gestito). Non esiste un file di hook separato per progetto o utente.
- Anche nel frontmatter di skill e agent: valgono finché la skill o l'agent sono attivi.
- Verifica con `/hooks` che l'hook compaia; con `claude --debug-file <file>` leggi quali matcher sono stati valutati, il codice di uscita e l'output. Le modifiche a `settings.json` si applicano in sessione senza riavvio.

## Percorsi e variabili
Dentro `command` Claude Code sostituisce `${CLAUDE_PLUGIN_ROOT}` (cartella di installazione del plugin), `${CLAUDE_PROJECT_DIR}` (radice del progetto) e `${CLAUDE_PLUGIN_DATA}` (dati persistenti del plugin). Il percorso può contenere spazi: nella forma shell mettilo tra virgolette (`"\"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/x.py\""` in JSON). Nella forma exec (`command` con `args`) non passa dalla shell e il problema non c'è. Gli script Python di Mímir non si affidano allo shebang, che su Windows non è affidabile (python.org e winget creano `python.exe` e `py.exe`, non `python3.exe`, e lo stub dello Store nel PATH esce con 9009): passano da `hooks/scripts/run-python.sh` con `"shell": "bash"`, che prova `python3`, `python` e `py -3`. Con `--fail-closed`, se Python manca, il wrapper blocca i comandi che lo script doveva controllare.

## Scrivere lo script di controllo
- **Riconosci il comando, non la stringa.** Una ricerca della parola scatta su `echo "git commit"`, su un messaggio o su un percorso. Dividi il comando in token con un vero tokenizer (`shlex` con `punctuation_chars`, a capo come separatore, commenti disattivati), separa i comandi semplici su `; & | ( )` e cerca il programma tra i token: anche dopo `FOO=1`, `env`, `sudo`, come percorso, dentro `sh -c` ed `eval`. Controlla il contenuto dove conta (il messaggio, non l'intero comando). Blocca la forma dell'abuso (un trailer, una frase), non la parola.
- **Gestisci le forme alternative**: `-m` ripetuto, `--message=`, `-F file`, `-F -` con heredoc, `--trailer`. Se non riesci a ricostruire l'input, scegli esplicitamente se lasciar passare o bloccare, e dichiaralo nel commento in testa allo script.
- **Fallisci in modo esplicito**: input non JSON o campo mancante non devono produrre un blocco involontario né un crash silenzioso.
- **Fail-closed mirato**: un controllo di sicurezza che non riesce a decidere (errore interno, Python assente) blocca, ma solo il caso che protegge (per esempio un comando che contiene git e commit), perché l'hook gira su ogni comando.
- Il messaggio su stderr dice cosa non va e come correggere.
- Uno script che modifica il comando (`updatedInput`) o decide permessi richiede ancora più prudenza: provalo con casi ostili.

## Provare l'hook
Prima di affidarti a un hook provalo su casi che devono bloccare e casi che devono passare, e guarda il test fallire contro una versione sbagliata.
- Il modello è `plugins/mimir/hooks/scripts/test_git_guard.py`: dizionari di comandi per esito (`CONTENT_BLOCK`, `FORM_BLOCK`, `ALLOW`…), lo script lanciato con il JSON su stdin in byte UTF-8 e con un timeout pari a quello di `hooks.json`, e il controllo del codice di uscita (2 per i blocchi, 0 per i passaggi), del motivo su stderr e dell'assenza di output su stdout. Lancio: `python3 plugins/mimir/hooks/scripts/test_git_guard.py [percorso script]`; esce con 1 se un caso sbaglia e stampa quale.
- Includi: il caso base che deve bloccare; le varianti di forma (altro modo di passare lo stesso messaggio); i falsi positivi già visti (parole nel comando, percorsi, nomi di file); il limite esatto (72 caratteri esatti passano, 73 bloccano).
- Quando correggi un falso positivo, aggiungi prima il caso al test, guardalo fallire, poi correggi.
- Dopo il test sullo script, prova una volta l'hook vero in una sessione (`/hooks` per vederlo, poi un'azione che deve bloccare): il test sullo script non prova il matcher né il percorso nel `hooks.json`.

## Trappole
- Exit 1 al posto di 2: non blocca.
- Matcher in minuscolo, o array, o tool scritto male: l'hook non scatta e non dà errori.
- Stdout con testo aggiuntivo (un `echo` dimenticato, l'output del profilo della shell) rompe il JSON.
- Script non eseguibile o percorso senza virgolette con spazi: l'hook fallisce in modo non bloccante.
- Hook di `PostToolUse` usato per vietare: il tool è già stato eseguito.
- Controlli lenti o con rete: il timeout predefinito è lungo e ogni azione ne paga il costo.
- Hook in timeout: è un errore non bloccante, il comando passa. Niente regex con quantificatori sovrapposti sull'input (backtracking esponenziale), niente scansioni ripetute per ogni token; nei test, un caso di tempo per ogni input costruito, con il timeout di `hooks.json`.
- Un `ask` restituito dall'hook può essere ignorato (vedi sopra): per un controllo che deve valere, blocca.
