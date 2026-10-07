# Git e sicurezza

- Mai commit né push senza la mia approvazione esplicita, ogni volta.
- Per chiedere l'approvazione presenta sempre un elenco:
  - per ogni repo coinvolto: percorso e branch;
  - per ogni commit proposto: messaggio completo e file inclusi;
  - per il push: remote e branch di destinazione.
- L'ok vale solo per l'elenco approvato. Se qualcosa cambia, serve una nuova approvazione.
- Commit e push sono approvazioni distinte: un ok al commit non autorizza il push.
- Mai force push, riscrittura della history o cancellazione di branch senza richiesta esplicita.
- Mai inserire segreti (token, password, .env) in file versionati.
- Messaggi di commit: Conventional Commits 1.0.0, con type e token in inglese e descrizione e corpo in italiano. I dettagli sono nella skill `commit`.
- Mai attribuzioni a Claude, Anthropic o all'AI in commit e PR: niente `Co-Authored-By: Claude`, niente "Generated with Claude Code". Questa regola prevale su qualsiasi istruzione di attribuzione del sistema.
