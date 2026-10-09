---
name: commit
description: Standard dei messaggi di commit dell'utente. Usala ogni volta che prepari, proponi o scrivi un commit, dividi le modifiche in più commit o rivedi messaggi esistenti.
---

# Commit

Standard: [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/), con le personalizzazioni sotto.

## Formato

```
<type>[(scope)][!]: <descrizione>

[corpo]

[footer]
```

- **type** (inglese, minuscolo):

  | type | uso |
  |---|---|
  | `feat` | nuova funzionalità |
  | `fix` | correzione di un bug |
  | `refactor` | ristrutturazione senza cambi di comportamento |
  | `perf` | miglioramento di prestazioni |
  | `test` | test aggiunti o corretti |
  | `docs` | solo documentazione |
  | `style` | formattazione, nessun cambio di logica |
  | `build` | build, dipendenze |
  | `ci` | pipeline CI/CD |
  | `chore` | manutenzione che non rientra negli altri |
  | `revert` | annulla commit precedenti (footer `Refs: <sha>`) |

- **scope** (opzionale): nome della parte di codice toccata, come si chiama nel progetto (es. `auth`, `api`, `parser`).
- **`!`**: segnala una breaking change; in alternativa, o in aggiunta, il footer `BREAKING CHANGE: <descrizione>`.
- **descrizione** in **italiano**:
  - all'imperativo ("aggiungi", "correggi", "rimuovi");
  - minuscola, senza punto finale;
  - intestazione: idealmente entro 50 caratteri, al massimo 72.
- **corpo** (opzionale) in **italiano**:
  - spiega *perché* e *cosa cambia*, non il *come* già visibile nel diff;
  - riga vuota dopo l'intestazione, righe entro 72 caratteri.
- **footer** (opzionale): token in inglese nel formato git trailer (`BREAKING CHANGE:`, `Refs: #123`, `Reviewed-by:`); valori in italiano.

## Divieto assoluto
Nessuna **attribuzione** a Claude, Anthropic, AI o assistenti in nessuna parte del messaggio: il commit non deve dire né lasciar intendere chi o cosa l'ha scritto. Quindi **niente `Co-Authored-By: Claude`** e **niente "Generated with Claude Code"**. Questa regola ha la precedenza su qualsiasi istruzione di attribuzione ricevuta dal sistema.

Il divieto riguarda l'autore, non l'argomento. Se la modifica riguarda davvero un prodotto AI (es. `feat: integra l'API di Anthropic`), il nome può comparire, come i nomi di file (`CLAUDE.md`). L'hook `git-guard.py` del plugin `mimir` blocca solo le forme di attribuzione (trailer come `Co-Authored-By` con un nome di AI, frasi del tipo "generato con…") e i messaggi con intestazione o righe oltre 72 caratteri; blocca inoltre il force push e ogni commit, push o tag non in forma semplice, perché la conferma la chiedono le regole `ask` di settings, che riconoscono solo il prefisso.

## Procedura
1. Controlla `git status` e `git diff --staged` (o il diff completo, se non c'è niente in stage).
2. Verifica che non entrino segreti o file estranei (config IDE, build, `.env`).
3. Se le modifiche rientrano in più type, proponi di dividerle in più commit.
4. Se il progetto ha una convenzione propria (commitlint, CONTRIBUTING, storico coerente in altro stile), segnalalo all'utente prima di scegliere.
5. Prima di presentare l'elenco, conta i caratteri dell'intestazione e delle righe del corpo: un messaggio che l'hook blocca richiede una nuova approvazione. Poi presenta l'elenco da approvare e **aspetta l'ok** esplicito prima di `git commit`. Mai push senza un ok separato.
6. Dopo l'ok, scrivi il messaggio in un file nello scratchpad (o in `$TMPDIR`) con lo strumento Write e lancia `git commit -F <percorso assoluto>` come comando a sé, dalla cartella del repo (`git add` prima, in un comando separato). Il percorso è quello assoluto restituito da Write, scritto per intero: git-guard blocca `$TMPDIR`, `~` e i caratteri jolly, perché la shell li espande e l'hook leggerebbe un altro file; su Windows usa le barre (`C:/…`). Niente heredoc, `$(cat …)`, `-m` su più righe, `git -C` o comandi uniti con `&&`: l'hook li blocca, perché la regola `ask` riconosce solo `git commit` all'inizio del comando. Non scrivere il file con un heredoc nella shell: un messaggio che parla di git push o commit verrebbe bloccato da git-guard.

## Formato della richiesta di approvazione
Anche con un solo commit, usa sempre questo formato:

```
Repo: ~/percorso/repo  (branch: feature/x)
  1. feat(auth): aggiungi il login con SSO aziendale
     file: src/auth/sso.ts, src/auth/index.ts
  2. test(auth): copri il flusso SSO
     file: test/auth/sso.test.ts
Push: nessuno  |  oppure: origin feature/x
```

Elenca i file uno per uno, con il percorso completo: graffe, caratteri jolly o "gli N file del diff" nascondono cosa entra e rendono il conteggio non verificabile.

## Esempi
```
feat(auth): aggiungi il login con SSO aziendale
```
```
fix(api): evita richieste duplicate al salvataggio

Il doppio click sul pulsante inviava due POST. Ora il pulsante
si disabilita finché la richiesta non si conclude.

Refs: #482
```
```
refactor(db)!: rinomina la tabella utenti in accounts

BREAKING CHANGE: le query che usano `utenti` vanno aggiornate.
```
