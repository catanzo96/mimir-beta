# Catalogo delle proposte (fase 3)

Chiavi verificate sulla documentazione ufficiale il 04/10/2026 con Claude Code 2.1.288 (`settings-reference`, `permissions`, `sandboxing`, `env-vars`, `devcontainer`). Prima di proporle, riverificale sulla versione installata. Ogni proposta va adattata: dove vive (`~/.claude/settings.json` per tutto, `sandbox.settings.json` di Mímir per le sessioni di lavoro), cosa rompe, come si prova.

## P1. Baseline dei permessi
- `permissions.disableBypassPermissionsMode: "disable"`: rifiuta `--dangerously-skip-permissions` e il `permissionMode: bypassPermissions` degli agent. Sulla macchina dell'utente sempre; il lavoro autonomo va nel dev container.
- `permissions.blockReadsOutsideWorkingDirectories: true`: `Read`, `Grep`, `Glob` e `LSP` rifiutano i percorsi fuori dalle cartelle di lavoro, in ogni modalità. Chiude in un colpo la lettura di `~/.m2/settings.xml`, `~/.docker/config.json` e simili da parte degli strumenti di Claude. Non vale per i comandi shell (lì serve la sandbox). Impatto: per leggere fuori serve `/add-dir`.
- In alternativa, o in più, `deny` puntuali sullo strumento `Read` per i file di credenziali presenti (`Read(~/.ssh/**)`, `Read(~/.m2/settings.xml)`, `Read(~/.docker/config.json)`, `Read(~/.gradle/gradle.properties)`, `Read(~/.gnupg/**)`, `Read(~/.claude.json)`, `Read(**/.env)`, `Read(**/.env.*)`, chiavi `*.pem` e `*.key`).
- `deny` su Bash come rete in più, non come confine: `Bash(sudo *)`, `Bash(git push --force *)`, `Bash(git push -f *)`. Evita `deny` che rompono il lavoro normale (`curl` serve per le API locali, `rm` per pulire `target/`): meglio `ask` mirati.
- `ask`: `Bash(git commit *)`, `Bash(git push *)`, `Bash(git tag *)` (già in Mímir), `Bash(dangerouslyDisableSandbox:true)` per vedere ogni richiesta di uscire dalla sandbox anche in modalità automatiche.
- `enableAllProjectMcpServers: false` (i server MCP di un repository si approvano uno per uno).
- `cleanupPeriodDays`: default 30. Ridurlo (es. 14) limita le trascrizioni in chiaro su disco, ma toglie la possibilità di riprendere sessioni vecchie. Da decidere con l'utente.

## P2. Sandbox (modalità assistita, `sandbox.settings.json`)
- `failIfUnavailable: true`: se la sandbox non parte, Claude Code non parte invece di lavorare senza.
- `network.strictAllowlist: true`: i domini fuori lista vengono negati invece di chiedere. Secondo `settings-reference` vale nelle impostazioni utente o managed; `sandboxing` cita anche `--settings`: **provalo** dal launcher prima di darlo per attivo.
- `network.deniedDomains`: domini mai ammessi anche se un'altra regola li coprirebbe (es. servizi di condivisione file e testo).
- `allowUnsandboxedCommands`: oggi `true` per i download di Maven (Maven non usa il proxy della sandbox). Metterlo a `false` blocca anche quei download: alternativa, una build online fuori dalla sessione quando servono dipendenze nuove.
- `autoAllowBashIfSandboxed`: `true` = comandi in sandbox senza conferma (flusso fluido, il confine è la sandbox); `false` = una conferma per ogni comando. In modalità assistita Mímir tiene `true`, con `ask` mirati.
- `credentials.files` in `deny` per i file di credenziali che i comandi non devono leggere. Attenzione: Maven legge `~/.m2/settings.xml` e Gradle `~/.gradle/gradle.properties`, quindi negarli ai comandi può rompere le build. Prima prova, poi decidi; per lo strumento `Read` vale P1.
- `credentials.envVars` in `deny` per i token in variabili d'ambiente (es. `GITHUB_TOKEN`, `NPM_TOKEN`), o `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` per toglierli a tutti i sottoprocessi (comandi, hook, MCP stdio).

## P3. Ambiente e telemetria (`env`)
Se la tua organizzazione vieta l'invio di feedback al fornitore: `DISABLE_FEEDBACK_COMMAND=1`, `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY=1`, `DISABLE_ERROR_REPORTING=1`, `DISABLE_TELEMETRY=1`. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` spegne anche funzioni (sincronizzazione delle skill, Remote Control e altre): proposta separata. Non disattivare l'aggiornamento automatico di Claude Code fuori da un container: servono le correzioni di sicurezza.

## P4. Hook di sicurezza
Solo se aggiungono qualcosa alla sandbox e ai permessi (es. negare `| sh`, `| bash`, scritture su `~/.claude/settings.json`, `.git/hooks`, `.mcp.json`). Scritti secondo `scrivi-skill/references/hook.md`: niente rete, falliscono in modo sicuro, testati con JSON finto, riconoscono il comando e non la stringa. Un audit log in `PostToolUse` solo con riassunti, mai contenuti di file o segreti.

## P5. Skill e agent
- Skill: niente `allowed-tools` con `Bash` generico; `disable-model-invocation: true` per quelle con effetti (deploy, commit, invio di dati); skill di terze parti da rimuovere o bloccare con `Skill(skill:<nome>)` in `deny`.
- Agent: `tools` sempre esplicito; i revisori con `disallowedTools: Edit, Write, NotebookEdit`; nessun `bypassPermissions`; `isolation: worktree` per gli agent che fanno modifiche estese.

## P6. MCP e plugin
Server da tenere o togliere, versioni fissate (niente `latest` o `npx -y` senza versione), token con scope minimo in variabili d'ambiente, OAuth dove c'è, `deniedMcpServers` per quelli da escludere. Plugin e marketplace di terze parti da rivedere o disinstallare. I connettori personali (posta, agenda) fuori dalle sessioni di lavoro: è la separazione delle modalità (Frigg, in arrivo in Mímir).

## P7. Dati locali
Permessi `700` su `~/.claude` e `600` su `~/.claude.json`. Trascrizioni vecchie che potrebbero contenere segreti: si elencano, non si leggono. Qualunque segreto esposto va ruotato.

## P8. Policy non allentabile (opzionale)
Le regole che nessun repository deve poter allentare vanno in `managed-settings.json` (Linux `/etc/claude-code/`). Richiede i permessi di amministratore: si danno i comandi all'utente, non si eseguono.
