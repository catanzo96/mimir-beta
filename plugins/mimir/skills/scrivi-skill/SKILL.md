---
name: scrivi-skill
description: Standard per creare o modificare skill, agent, regole e hook di Mímir. Usala ogni volta che ne scrivi o ne cambi uno, anche durante /retro.
---

# Scrivere i componenti di Mímir

Dove va una cosa (regola, hook, skill, agent, CLAUDE.md di progetto) è deciso nel README di Mímir, sezione "Dove va una cosa". Qui c'è **come** si scrive.

## Plugin
- `mimir`: vale in ogni ambito (metodo, linguaggi, git, review).
- `brokkr`: solo per il lavoro (analisi, ticket, manutenzione, rilasci, interventi).
- `frigg` (vita privata): arriverà più avanti.

Nel dubbio, `mimir` solo se serve davvero anche fuori dal lavoro.

## Skill

### Frontmatter
- **`name`**: kebab-case in italiano, uguale alla cartella.
- **`description`**: dice **quando** usarla, non come funziona.
  - In testa il caso d'uso principale, poi i segnali concreti: richieste tipiche, file o manifest (`pom.xml`, `angular.json`), parole chiave.
  - Niente elenco dei contenuti né dei passi. Se la description riassume il metodo, Claude segue il riassunto e salta il corpo.
  - Al massimo ~300 caratteri. Il limite tecnico è 1.536, ma tutte le description condividono un budget di contesto: quando si supera, alcune vengono scartate e quelle skill non si attivano più.
- **`when_to_use`**: richieste tipiche con le parole dell'utente (`Es.: "documenta il rinnovo del certificato", …`) e, se serve, a quale skill vicina lasciare un caso. Viene accodato alla description e conta nello stesso limite: insieme restano entro ~400 caratteri. Usalo per le skill di metodo e di lavoro, dove la richiesta non nomina una tecnologia.
- **`disable-model-invocation: true`** per le procedure che partono solo su richiesta esplicita (es. `/retro`): la description esce dal contesto. Non usarlo se Claude deve trovare la skill da sola.
- **`model`**: non impostarlo. In una skill cambia modello solo per quel turno e fa perdere la cache della conversazione, quindi il turno costa di più. Un lavoro che merita un altro modello va in un agent.
- **`effort`**: solo se la skill richiede un ragionamento molto diverso da quello della sessione.
- **`allowed-tools`**: evitalo. Mai Bash senza restrizioni.
- **`paths`**: non usarlo per risparmiare contesto. Provato il 03/10 (Claude Code 2.1.288, skill di plugin): la description resta nella lista anche senza file corrispondenti.

### Corpo
- Al massimo ~150 righe. Il dettaglio va in file separati, citati dal corpo con l'indicazione di quando leggerli:
  - `references/`: conoscenza da consultare;
  - `templates/`: documenti da compilare.
- Struttura:
  1. scopo in una riga;
  2. quando non usarla, se rischia di sovrapporsi a un'altra skill;
  3. procedura o principi;
  4. verifica: come si dimostra che il lavoro è fatto (raccogli → modifica → prova → resoconto);
  5. file di supporto.
- Tono imperativo e calmo. Niente maiuscole o "assolutamente": dai il motivo delle regole non ovvie, funziona meglio.
- Non ripetere le regole sempre attive: dalle per scontate o rimanda.
- Coerenza con le regole: italiano, commit e push solo con approvazione, nessuna attribuzione all'AI, verificato ≠ plausibile, nessun file di metodo creato nei repo dei progetti se non richiesto.
- Niente dati di aziende o clienti: il metodo qui, i dati nei progetti.
- Da fonti esterne prendi idee e strutture, non testo: riscrivi con parole tue.

## Agent
Servono quando occorre un contesto isolato (molta lettura che non va tenuta nella conversazione), lavoro in parallelo, tool ristretti o un modello diverso da quello della sessione.

- **`description`**: quando delegare, come per le skill.
- **`tools`**: il minimo indispensabile. Per un agent di sola lettura, `disallowedTools: Edit, Write, NotebookEdit`.
- **`skills`**: quelle da precaricare, con il nome del plugin (`mimir:clean-code`).
- **`model`**: sempre esplicito. `inherit` solo con un motivo scritto nel corpo dell'agent.

| Lavoro | Modello |
|---|---|
| Ricerca, lettura, riassunti, lavori meccanici | `haiku` |
| Implementazione, review, analisi ordinarie | `sonnet` |
| Architettura, decisioni difficili, problemi che resistono | `opus` |

- Le review non scendono sotto `sonnet`: un modello economico che impiega 2-3 volte i turni non fa risparmiare.
- Mai `haiku` su contenuti esterni non fidati (mail, pagine web, allegati, ticket di terzi) se l'agent può scrivere o inviare: è più esposto alla prompt injection.
- L'agent restituisce un resoconto compatto con le evidenze. Il dettaglio resta nel suo contesto.

## Regole
- Solo ciò che vale per ogni compito: sono in contesto in ogni sessione.
- Una riga quando basta.
- Se la regola si può controllare meccanicamente, preferisci un hook o un permesso.

## Hook
- Per ciò che deve valere al 100%.
- Script in `hooks/scripts/` del plugin: timeout breve, niente rete, nessun dato sensibile nei log.
- Prima di affidarti all'hook, provalo su un caso che deve bloccare e su uno che deve passare.
- Eventi, exit code, output JSON, matcher, variabili e trappole (falsi positivi): `references/hook.md`, da leggere prima di scrivere o cambiare un hook.

## File protetti
La sandbox, il classificatore della modalità auto e le regole di Mímir proteggono settings, hook, plugin e regole: una modifica può essere bloccata. Non aggirare il blocco (niente uscita dalla sandbox, niente strade alternative). Prepara invece la modifica nello scratchpad:
- uno script che cerca il testo atteso (una sola occorrenza) e si rifiuta senza toccare nulla se non lo trova, valida il risultato (per esempio il JSON), scrive in modo atomico e al secondo lancio non fa niente; oppure una patch da applicare con `git apply --check` e poi `git apply`;
- provalo su una copia dei file o su un clone, compreso il caso di rifiuto, e confronta il risultato con i file attesi;
- dai all'utente i comandi per il suo terminale, senza `!`, in righe brevi, con `S=` per i percorsi lunghi: incollata, una riga lunga si spezza e il comando fallisce a metà, e ogni `!` parte in una shell nuova (le variabili non restano). `!` solo per un comando breve e autonomo;
- dopo il lancio controlla lo stato reale (confronto con la copia provata, test).

## Prima di consegnare
1. **Prova di attivazione.** Scrivi 2-3 richieste che devono attivare la skill e una che non deve. Per le skill di comportamento, aggiungi uno scenario che senza la skill porta all'errore. Quando conviene, prova con un subagent con e senza la skill. Come provare in headless, leggere skill e modelli dai log, usare `claude plugin eval`, controllare il YAML e il budget della lista: `references/prova-skill.md`.
2. **Validazione.** Lancia `claude plugin validate plugins/<plugin>` e controlla che i file citati in `references/` e `templates/` esistano.
3. **Documentazione.**
   - Aggiorna gli indici nel README e il `CHANGELOG.md`.
   - Incrementa `version` in `plugins/<plugin>/.claude-plugin/plugin.json`.
