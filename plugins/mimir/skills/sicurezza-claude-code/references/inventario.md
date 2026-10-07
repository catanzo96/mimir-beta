# Inventario (fase 1)

Solo lettura. Dei segreti si verificano esistenza, percorso e permessi, mai il contenuto.

## a) Impostazioni
- `~/.claude/settings.json`, `~/.claude/settings.local.json` (se esiste).
- Per ogni progetto indicato dall'utente (o la cartella corrente): `.claude/settings.json`, `.claude/settings.local.json`.
- Mímir: `sandbox.settings.json` (passato dal launcher con `--settings`) e `settings.template.json` (unito a `~/.claude/settings.json` da `install.sh`).
- Managed settings, se presenti: Linux `/etc/claude-code/managed-settings.json` e `managed-settings.d/`; macOS `/Library/Application Support/ClaudeCode/managed-settings.json`; Windows `C:\Program Files\ClaudeCode\managed-settings.json`; `managed-mcp.json`.

## b) Permessi
`defaultMode`, `allow`, `ask`, `deny`, `additionalDirectories`, `disableBypassPermissionsMode`, `disableAutoMode`, `blockReadsOutsideWorkingDirectories`. Cerca:
- regole troppo larghe in `allow`: `Bash`, `Bash(*)`, `Bash(git *)`, `Bash(npm *)`, `Bash(docker *)`, `WebFetch`, `mcp__*`;
- regole accumulate con "Yes, don't ask again" in `.claude/settings.local.json`;
- file di credenziali leggibili dallo strumento `Read`.

## c) Sandbox
`enabled`, `failIfUnavailable`, `allowUnsandboxedCommands`, `autoAllowBashIfSandboxed`, `excludedCommands`, `filesystem.*`, `credentials.*`, `network.allowedDomains`, `network.deniedDomains`, `network.strictAllowlist`, `enableWeakerNestedSandbox`. Su Linux e WSL2: `bwrap` e `socat` installati, profilo AppArmor per `bwrap` dove serve.

Elenca i file di credenziali presenti in home (solo `ls`): `~/.ssh`, `~/.git-credentials`, `~/.aws`, `~/.m2/settings.xml`, `~/.gradle/gradle.properties`, `~/.docker/config.json`, `~/.npmrc`, `~/.pypirc`, `~/.netrc`, `~/.kube/config`, `~/.gnupg`, `~/.config/gh`, `~/.config/gcloud`, `~/.azure`, e quali sono protetti dalla sandbox e da `Read`.

## d) Hook
Tutti gli hook in ogni scope e nei plugin (`hooks/hooks.json`). Per ciascuno: comando, se fa rete, se scarica codice, se legge segreti, se il file è scrivibile da un repository. Gli hook girano fuori dalla sandbox con i privilegi dell'utente.

## e) MCP
`~/.claude.json` (solo nomi dei server, comando o URL e scope, non i token), `.mcp.json` dei progetti, `enableAllProjectMcpServers`, `enabledMcpjsonServers`, `disabledMcpjsonServers`, `allowedMcpServers`, `deniedMcpServers`, connettori di claude.ai. Per ogni server: locale o remoto, versione fissata o `latest`/`npx -y`, autenticazione (OAuth, token in env, token in chiaro), cosa concede, provenienza. I server MCP locali girano fuori dalla sandbox.

## f) Skill
`~/.claude/skills/`, `.claude/skills/`, `~/.claude/skills/synced/`, `.claude/commands/`, skill dei plugin. Per ognuna: `allowed-tools`, `disallowed-tools`, `disable-model-invocation`, iniezione dinamica `` !`comando` ``, script inclusi (leggili e riassumi), accessi di rete, scritture fuori dal progetto.

## g) Agent
`~/.claude/agents/`, `.claude/agents/`, agent dei plugin. Per ognuno: `tools` (se manca eredita tutto: segnalalo), `disallowedTools`, `permissionMode`, `mcpServers`, `hooks`, `model`, `isolation`. Negli agent di plugin `permissionMode`, `hooks` e `mcpServers` sono ignorati.

## h) Plugin e marketplace
`claude plugin list`, `claude plugin marketplace list`, `claude plugin details <nome>`. Leggi `hooks/hooks.json`, `.mcp.json` e `bin/` di ogni plugin. Stato dell'auto-update per marketplace, marketplace di terze parti, plugin caricati con `--plugin-dir` (Mímir).

## i) CLAUDE.md e memoria
`~/.claude/CLAUDE.md`, `CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/` dei progetti, memoria automatica: segreti, URL interni, istruzioni che allargano i permessi, testi che sembrano prompt injection.

## j) Dati locali
Dimensione e periodo di conservazione di `~/.claude/projects/` (trascrizioni in chiaro), `cleanupPeriodDays`, permessi di `~/.claude` e `~/.claude.json` (solo l'utente).

## k) Ambiente e telemetria
`DISABLE_TELEMETRY`, `DISABLE_ERROR_REPORTING`, `DISABLE_FEEDBACK_COMMAND`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`. Override di `ANTHROPIC_BASE_URL` o di `env` nei file di progetto. Variabili con segreti esportate nella shell da cui parte Claude Code (solo i nomi).

## l) Segnali di attacchi noti nei progetti
Hook che eseguono `curl`, `wget` o `bash` scaricati; `enableAllProjectMcpServers: true` insieme a un `.mcp.json`; override di `env` o `ANTHROPIC_BASE_URL` in `.claude/settings.json` di un repository.
