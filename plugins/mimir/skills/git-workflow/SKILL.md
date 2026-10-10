---
name: git-workflow
description: Flusso di lavoro con git. Usala quando crei, cambi, unisci o riallinei un branch, prepari o descrivi una MR/PR, gestisci feature dipendenti o crei un tag di rilascio.
---

# Git workflow

Si applica insieme alla skill `commit` e alle regole in `git-and-safety`. Il modello di branching del progetto (branch permanenti, default branch, protezioni) prevale: prima ricavalo dal repo (`git branch -r`, CONTRIBUTING, CI).

**Approvazioni**: oltre a ciò che chiede `git-and-safety`, anche rebase e merge richiedono l'ok esplicito, con lo stesso elenco. Creare un branch locale non lo richiede.

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
1. **Creazione**: aggiorna il branch base e stacca il nuovo branch con `git switch -c <nome>`. Per cambiare branch usa `git switch`: `git checkout` può sovrascrivere file e chiede sempre conferma.
2. **Sviluppo**:
   - commit atomici (vedi skill `commit`);
   - riallinea spesso al branch base, di norma con `git fetch` più `rebase` sul branch *non ancora condiviso*;
   - se il branch è condiviso, fai merge.
3. **MR/PR** verso il branch base: pipeline verde e almeno una review. Il merge sul branch base, anche locale o in fast-forward, si fa solo con la CI del branch verde, letta job per job: un rosso "estraneo" arriva sul base insieme al merge. Il lavoro di più sessioni o di un worktree si porta su main da un branch, con la CI del branch verde; un commit diretto su main va bene solo per modifiche piccole di una sola sessione.
4. **Dopo il merge**, con la CI del branch base verde:
   1. l'utente cancella il branch remoto (dalla pagina della MR/PR o del repo);
   2. la sessione cancella quello locale con `git branch -d <nome>`, che rifiuta un branch non unito e chiede conferma;
   3. un solo blocco di comandi per il terminale dell'utente: `git config --remove-section branch.<nome>` (nella sandbox `-d` non la toglie), poi `git fetch --prune origin` e `git branch -a` per verificare.

## Più commit da modifiche sovrapposte
Se i temi di un lavoro toccano gli stessi file, `git add` per file non li separa e `git add -p` è interattivo. A fine di ogni tema fotografa lo stato come tree, con un indice temporaneo che lascia intatto quello reale (la variabile su ogni comando: tra un comando e l'altro della sessione non resta):

```bash
I="$TMPDIR/temi/idx"; mkdir -p "$TMPDIR/temi"
GIT_INDEX_FILE="$I" git read-tree HEAD                          # una volta, all'inizio
GIT_INDEX_FILE="$I" git add -u && GIT_INDEX_FILE="$I" git write-tree > "$TMPDIR/temi/t1"   # a fine tema 1, poi t2…
```

- `-u` vede solo i file tracciati: quelli nuovi si aggiungono per nome. Dopo l'ultimo tema, `git diff --quiet <ultimo tree>` conferma che coincide con l'albero di lavoro.
- Una correzione tardiva a un file di un solo tema si aggiunge a quel tree e ai successivi (`read-tree`, `add`, `write-tree` su ognuno).
- Dopo l'ok, per ogni commit in ordine: `git read-tree <tree>`, controllo con `git diff --cached --name-only`, poi `git commit -F` come comando a sé (skill `commit`).

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

## Nella sandbox
- `.git/config` è protetto: `git config`, `git remote add`/`set-url`, `git branch -m` e il primo `push -u` falliscono con "could not lock config file". Proponili subito fuori dalla sandbox, con conferma, dicendo il perché. Se fallisce solo l'aggiornamento della config, l'operazione sui ref è già avvenuta: verifica con `git branch -vv` e `git config --get-regexp '^branch\.'` prima di ripetere.
- Prima di `switch` o `checkout` tra branch, controlla con `git diff --name-only <da> <a>` se cambiano file protetti (`.github`, `plugins`, …): in quel caso dai all'utente il comando da lanciare fuori dalla sandbox. Un file protetto in scrittura ferma a metà `git switch`, `checkout` e `stash` ("Device or resource busy" o "unable to unlink"): controlla `git status`, riporta il file al contenuto atteso con Edit e ricontrolla. Per lo stesso motivo (`.git/config` in sola lettura) `git branch -d` e `-D` non tolgono la sezione `branch.<nome>`: la pulizia è al punto 4 del ciclo di vita.
- `gh` dentro la sandbox non si autentica quando il token è nel keyring (fuori sì): i comandi in sola lettura girano fuori dalla sandbox, con conferma. Salva ciò che scaricano nello scratchpad con un percorso esplicito, perché fuori dalla sandbox `$TMPDIR` non punta lì.
- Push e fetch autenticati: la sessione non legge le credenziali e non ha un terminale per chiederle. Prepara il comando esatto (remote e branch) e lascialo lanciare all'utente dal suo terminale.
