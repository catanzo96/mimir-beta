# Provare una skill o un agent

Una skill che non si attiva, o che si attiva fuori luogo, non dà errori: si scopre solo provandola. Prova prima di consegnare e di nuovo quando cambi la description.

## 1. Richieste che devono e che non devono attivarla
Scrivi su un foglio, prima di provare:
- 2-3 richieste che **devono** attivarla, con parole diverse da quelle della description (come le scriverebbe l'utente, non copiando il nome della skill);
- 1-2 richieste che **non devono** attivarla, vicine per tema (la skill gemella, un caso al confine);
- per una skill di comportamento (che impedisce un errore tipico), uno scenario in cui, senza la skill, Claude sbaglia in modo prevedibile.

Lancia ogni richiesta in una sessione nuova (il contesto di scrittura nasconde i difetti). Se non si attiva, rivedi la description: in testa il caso d'uso, poi i segnali concreti.

## 2. Prova in headless
Senza installare nulla, carica il plugin per una sola sessione:

```bash
claude -p --plugin-dir plugins/mimir --model sonnet --max-turns 6 --max-budget-usd 1 \
  --no-session-persistence --output-format stream-json --verbose "<richiesta>" > prova.jsonl
```

`--output-format stream-json` si usa insieme a `--verbose` (come negli esempi della documentazione). Ogni riga è un evento JSON. Cosa leggere (provato il 03/10 con Claude Code 2.1.288):
- **Evento `system` con `subtype: "init"`**: campi `model` (modello della sessione), `plugins` (con `plugin_errors` se un plugin non si carica), `skills` e `agents` (nomi caricati, quelli di plugin con il prefisso `plugin:`), `tools`. Se la skill non è in `skills`, non è stata caricata: guarda il frontmatter.
- **Messaggi `assistant`**: nel contenuto, i blocchi `tool_use`. Una skill attivata è un `tool_use` di nome `Skill` con `input.skill`. Un subagent è un `tool_use` di nome `Agent` con `input.subagent_type` e, se indicato, `input.model`.
- **Modello del subagent**: i messaggi `assistant` del subagent hanno `parent_tool_use_id` valorizzato (nei messaggi della conversazione principale è `null`) e `message.model` con il modello usato. Nell'ultimo evento (`result`), `modelUsage` elenca i modelli consumati e il costo.
- Senza `--forward-subagent-text` il testo dei subagent non compare, solo i loro `tool_use` e `tool_result`.

Estrazione rapida:

```bash
jq -c 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | {tool: .name, input: (.input | tostring | .[0:120])}' prova.jsonl
jq -c 'select(.type=="system" and .subtype=="init") | {model, skills, agents, plugin_errors}' prova.jsonl
```

Limiti: il run in `-p` non mostra le richieste di permesso (negate se non pre-approvate), e un solo run è rumoroso: ripeti le richieste ambigue 2-3 volte. Un comando di controllo vale solo dopo averlo visto fallire: prova l'estrazione su una richiesta che sai non attivare la skill e verifica che la riga `Skill` manchi.

Una skill solo manuale (`disable-model-invocation: true`) si prova con `/nome` nel prompt: in `-p` le skill invocate dall'utente funzionano ("`/nome argomenti`" nella stringa del prompt).

## 3. Con e senza la skill (skill di comportamento)
Per una skill che deve cambiare ciò che Claude fa (rifiutare un'azione, seguire un ordine di passi), la prova vale solo se confrontata:
1. stessa richiesta, stessa versione, sessione pulita, **senza** la skill (togli `--plugin-dir`, oppure `"nome-skill": "off"` in `skillOverrides`);
2. stessa richiesta **con** la skill;
3. confronta il comportamento (le azioni nel flusso, non lo stile del testo). Se senza skill Claude fa già bene, la skill non serve (o la richiesta è troppo facile).

In alternativa lancia i due casi con un subagent ciascuno. Con `claude plugin eval` (sotto) il confronto è automatico.

## 4. `claude plugin eval`
Misura il **comportamento**: non controlla la sintassi (per quella c'è `claude plugin validate`). Per ogni caso lancia sessioni headless isolate con solo il plugin caricato e poi senza plugin, e confronta i punteggi (colonne `WITH`, `W/OUT`, `Δ`). Richiede Claude Code 2.1.269 o successivo; ogni run è una chiamata al modello sul tuo account, quindi costa (di default ogni caso gira 3 volte per braccio).

```bash
cd plugins/mimir && claude plugin eval init        # propone casi e controlli, scrive evals/<caso>/
claude plugin eval .                              # esegue tutto e stampa la tabella
claude plugin eval . --case <caso> --runs 1 --ablation none   # una sola prova, per iterare
```

Un caso è una cartella `evals/<caso>/` con `prompt.md` (la richiesta, scritta come la scriverebbe l'utente senza nominare la skill) e `graders/*.md` (controlli: `regex`, `tool_used`, `tool_order`, `file_exists`, `llm`, `baseline`). Il controllo `tool_used` con `tool: Skill` verifica che la skill sia partita; se passa ma `Δ` è vicino a zero, la skill non cambia il risultato. Se `Δ` è vicino a zero e `tool_used` fallisce, la description non attiva la skill. Prima di spendere, decidi se i casi servono: `evals/results/` va nel `.gitignore`. Se non hai l'ok a spendere, usa le prove 1-3.

Fonte: pagina `plugin-evals` della documentazione.

## 5. Validazione e YAML del frontmatter
```bash
claude plugin validate plugins/<plugin> --strict
```
Controlla manifest e struttura dei file di skill, agent e comandi; esce con 0 se passa, 1 se fallisce, 2 se il validatore stesso ha un errore. Non rileva uno YAML non valido nel frontmatter di una skill (verificato il 03/10: una description con `: ` non quotato passa): si controlla con un parser. Lo script (con il caso noto per provarlo) è in `manutenzione-mimir/references/misure.md`; in breve, `yaml.safe_load` sul blocco tra i due `---` di ogni SKILL.md, e uscita diversa da 0 se fallisce. Regola pratica: una description che contiene `: ` va tra virgolette doppie.

Controlla anche che i file citati in `references/` e `templates/` esistano.

## 6. Budget della lista delle skill
Tutte le description condividono il budget della lista in contesto: l'1% della finestra per default (Mímir lo alza al 3% con `skillListingBudgetFraction`). Oltre il budget Claude Code toglie le description, partendo dalle skill meno usate, e quelle skill non si attivano più per parola. Dopo aver aggiunto o allungato una skill:
- somma le lunghezze delle description (script della sezione 5) e confrontale con il totale precedente;
- `claude plugin details <plugin>`: always-on stimato in token, per componente;
- in sessione `/doctor` (stima del costo della lista) e `/context` (la riga Skills mostra la lista dopo il budget); `claude --debug` scrive un avviso quando il budget è superato.
Una skill nuova che pesa molto va accorciata o resa solo manuale.

## 7. Agent
- Il file in `agents/` compare in `agents` dell'evento `init`. Lancialo con un compito reale nel perimetro: `Usa l'agent <nome> per ...`.
- Controlla nel flusso il **modello** (sezione 2, `message.model` dei messaggi con `parent_tool_use_id`): deve essere quello del frontmatter, non quello della sessione.
- Controlla i **tool**: un agent di sola lettura non deve poter scrivere (prova a chiedergli di modificare un file e verifica che non ci riesca).
- Controlla il **resoconto**: compatto, con evidenze, accertato separato da ipotesi.
