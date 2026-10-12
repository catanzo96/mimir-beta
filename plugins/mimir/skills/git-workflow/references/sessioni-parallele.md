# Sessioni parallele in worktree

Da leggere quando più sessioni lavorano ognuna nel proprio worktree e una sessione su main le coordina.

## Apertura
- Un worktree sorella per sessione (`<repo>-<nome>`, branch `<nome>` da main), con un file di perimetro non versionato: obiettivo, fuori perimetro, stato.
- Pochi worktree aperti insieme, uno solo se la CI è ferma: ogni merge cambia la base degli altri.

## Coordinamento
- Chi coordina non scrive nei worktree: verifica sul worktree (log, status, diff, stato del perimetro) ciò che le sessioni dichiarano.
- L'ok a commit e merge l'utente lo scrive nella sessione che li esegue; chi coordina suggerisce la frase.

## Chiusura
1. L'utente unisce main nel branch con `--no-commit`; la sessione del worktree risolve e committa con ok.
2. Suite completa e review del branch intero, poi la sessione dichiara il branch pronto.
3. Merge su main.
4. Se il merge cambia ciò che un installer o uno script di setup copia o genera, rilancialo subito: la configurazione installata resta indietro senza dare segni.
5. Archivia il perimetro fuori dal worktree e controlla la copia con `diff` prima della rimozione: `git worktree remove` cancella anche i file ignorati.
6. `git worktree remove` lo lancia l'utente dal terminale: nella sandbox può fallire a metà.
