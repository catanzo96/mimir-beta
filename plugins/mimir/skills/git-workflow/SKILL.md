---
name: git-workflow
description: Flusso di lavoro con git. Usala quando crei o riallinei un branch, prepari o descrivi una MR/PR, gestisci feature dipendenti o crei un tag di rilascio.
---

# Git workflow

Si applica insieme alla skill `commit` e alle regole in `git-and-safety`. Il modello di branching del progetto (branch permanenti, default branch, protezioni) prevale: prima ricavalo dal repo (`git branch -r`, CONTRIBUTING, CI).

**Approvazioni**: commit, push, rebase, merge e cancellazione di branch richiedono l'ok esplicito dell'utente, con l'elenco di repo, branch e operazioni. Creare un branch locale non lo richiede.

## Branch di lavoro
Si staccano dal branch di integrazione del progetto (es. `develop` o `main`).

| Prefisso | Uso |
|---|---|
| `feature/` | nuove funzionalità o attività esplorative |
| `fix/` | correzioni di bug |
| `refactor/` | miglioramenti interni senza cambi di comportamento |
| `docs/`, `chore/`, `test/` | se il progetto li usa, allineati ai type dei commit |

**Naming:**
- solo minuscole, numeri e trattini;
- 4-5 parole significative al massimo;
- con un ticket, l'ID in testa: `feature/456-export-report`.

## Ciclo di vita
1. **Creazione**: aggiorna il branch base e stacca il nuovo branch.
2. **Sviluppo**:
   - commit atomici (vedi skill `commit`);
   - riallinea spesso al branch base, di norma con `git fetch` più `rebase` sul branch *non ancora condiviso*;
   - se il branch è condiviso, fai merge.
3. **MR/PR** verso il branch base: pipeline verde e almeno una review.
4. **Dopo il merge**: elimina il branch locale e remoto.

## MR piccole
- Una MR, un solo obiettivo.
- Dimensione da review in circa 5 minuti: idealmente meno di 5 file, o un singolo obiettivo chiaro.
- Se una feature è grande, spezzala in una catena di MR dipendenti.

## Catene di MR dipendenti
Per feature composte da più parti dipendenti:

```
develop
└── feature/a   ← MR verso develop
    └── feature/b   ← MR verso feature/a
        └── feature/c   ← MR verso feature/b
```

- Ogni branch si stacca dal precedente e la sua MR punta al branch padre.
- **Riallineamento**: quando il padre cambia, riallinea i figli con `merge --no-ff`. Non usare il rebase, per non riscrivere la history già in review.
- **Review**:
  - una prima review rapida su `a` per validare l'impostazione;
  - poi le review operative dal basso verso l'alto: `c` → `b` → `a`.
- **Ordine di merge**:
  - prima `c` → `b`, poi `b` → `a`;
  - infine `a` → base, con squash merge se il progetto lo prevede.

## Template MR/PR
```markdown
### Scopo
<breve descrizione dell'obiettivo>

### Collegamenti
- 🔼 MR padre: #<id> (<branch>)   ← se in catena
- 🔽 MR figlia: #<id> (<branch>)  ← se presente
- Ticket: <id>
```
Anche nelle MR e PR, nessun riferimento a Claude o all'AI.

## Tag e versioning
- SemVer: `vMAJOR.MINOR.PATCH`.
- Il bump segue i commit: `fix` → PATCH, `feat` → MINOR, breaking change → MAJOR.
- Il tag si crea sul commit rilasciato, secondo il flusso del progetto.
