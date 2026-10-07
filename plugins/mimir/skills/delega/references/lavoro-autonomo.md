# Lavoro che prosegue da solo

Comandi verificati sulla documentazione di Claude Code 2.1.292 (`commands`, `goal`, `scheduled-tasks`, `agent-view`, 07/10/2026). Riverificali quando cambia la versione.

Il modello di sicurezza di Mímir è "assistito": l'utente approva le azioni. Questi comandi riducono le conferme turno per turno, quindi si propongono, non si avviano, e mai su azioni difficili da annullare.

## Quale comando
| Comando | Il turno successivo parte quando | Adatto a |
|---|---|---|
| `/goal <condizione>` | il turno precedente finisce, finché un modello giudica la condizione soddisfatta | portare a termine un compito con un esito verificabile (test verdi, build pulita) |
| `/loop [intervallo] <prompt>` | passa l'intervallo, finché la sessione resta aperta | controllare qualcosa che cambia nel tempo (un deploy, una pipeline) |
| `/batch <istruzione>` | dopo l'ok al piano, un subagent per unità, ciascuno in un worktree | una modifica meccanica uguale su molte parti indipendenti del codice |
| `/background`, `/fork` | la sessione (o una sua copia) prosegue staccata dal terminale | lasciare finire un lavoro lungo mentre fai altro |
| `/schedule` (routine) | a orario, nel cloud | lavori ricorrenti senza il tuo computer acceso |

## Paletti
- **Condizione dimostrabile.** Il valutatore di `/goal` legge solo la conversazione: non lancia comandi e non apre file. Scrivi la condizione come un output che Claude mostra ("tutti i test di `test/auth` passano, con l'output del comando"), non come un giudizio ("il codice è pulito").
- **Limite esplicito.** Aggiungi sempre un tetto alla condizione ("o fermati dopo 15 turni"). Un `/loop` ricorrente scade comunque dopo 7 giorni, ma va fermato appena non serve.
- **I permessi non cambiano.** `/goal` e `/loop` usano la modalità della sessione: in modalità predefinita Claude chiede comunque per ciò che non è già consentito. Non proporre la modalità auto per far girare un ciclo senza conferme fuori da un dev container (vedi `sicurezza-claude-code`).
- **Dentro un ciclo niente commit, push, invii, migrazioni o cancellazioni.** Il ciclo si ferma prima e chiede.
- **`/batch` tocca molte parti insieme.** Prima di usarlo: repo pulito, piano letto dall'utente unità per unità, chiarito cosa fa ogni subagent alla fine (la documentazione dice che "pubblica" la sua modifica: verifica se significa branch, push o pull request nel tuo ambiente). Su repo con remote condivisi, nessuna pubblicazione senza ok.
- **Routine e revisioni nel cloud** (`/schedule`, `/code-review ultra`) girano fuori dalla tua macchina e senza conferme: codice e dati del cliente ci vanno solo se l'utente lo chiede e la policy aziendale lo consente.
- **`/background` e `/fork`**: la copia lavora in un worktree suo se modifica codice. Non lanciarne due sugli stessi file.

## Prima di proporlo
Scrivi all'utente in tre righe: comando, condizione o intervallo con il limite, cosa farà e cosa non farà (niente commit, niente invii). Se l'utente non lo conferma, procedi a turni normali.

## Quando non usarli
- Compiti che richiedono decisioni dell'utente a metà: il ciclo le prenderebbe da solo o si bloccherebbe.
- Diagnosi aperte: senza un'ipotesi chiara, un ciclo ripete tentativi invece di capire (`debugging`).
- Lavori che toccano produzione, dati condivisi o sistemi del cliente.
