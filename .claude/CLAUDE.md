# Sviluppo di Mímir

Vale per chi lavora sul repo di Mímir (main o un suo worktree). Il `CLAUDE.md` nella root è quello globale, caricato in ogni progetto: le istruzioni solo per Mímir stanno qui.

- Sessioni parallele: un worktree per lavoro, con il metodo di `git-workflow` (`references/sessioni-parallele.md`).
- `version` dei plugin: al merge su main, solo se il branch tocca `plugins/` (minor con `feat`, altrimenti patch), con un commit `chore(plugin)` che riporta "Versione X." nel corpo.
- I merge che toccano `sandbox.settings.json`, `plugins/`, `install.py` o `.github/` li lancia l'utente dal terminale: nella sandbox quei file sono in sola lettura e il merge si ferma a metà.
- Dopo un merge che cambia `settings.template.json` o l'installer, rilancia `install.sh`: la configurazione in `~/.claude` non si aggiorna da sola.
- `run_tests.py` nella sandbox fa fallire `test_run_python.py` (hook in sola lettura): rilancia quel test fuori dalla sandbox e controlla che non restino file `.tmp-test-*` in `plugins/mimir/hooks/scripts/`.
