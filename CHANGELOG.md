# Changelog

## 2026-10-07 (retro)
- `git-workflow`: sezione "Nella sandbox" su `.git/config` protetto e push autenticati lanciati dall'utente. Plugin `mimir` 0.17.1.
- README, Confini: niente dati personali o aziendali nemmeno nella configurazione.

## 2026-10-07 (prima versione pubblica)
- Mímir pubblicato come pacchetto generico: nel repo solo il metodo, i dati personali in file locali ignorati da git.
  - `profile/profile.md` e `inbox.md` locali, creati da `install.sh` a partire da `profile/profile.example.md` e `inbox.example.md`.
  - In `sandbox.settings.json` restano solo i registri pubblici; gli host privati vanno in `~/.claude/settings.json`, le cui liste Claude Code unisce a quelle del launcher.
  - Licenza MIT.
  - README con installazione, personalizzazione e uso.
- Plugin `mimir` 0.17.0, `brokkr` 0.7.0.
