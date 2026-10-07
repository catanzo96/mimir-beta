# Cache dei prompt: cosa la invalida

Claude Code rimanda a ogni richiesta l'intero contesto e l'API riusa ciò che ha già elaborato confrontando l'inizio della richiesta (il prefisso). Il confronto è esatto: una modifica nel prefisso ricalcola tutto ciò che segue. L'ordine è sempre: system prompt e tool, poi CLAUDE.md, memoria e regole senza `paths`, poi la conversazione.

## Invalidano la cache (il turno successivo rilegge tutto, più lento e più caro)
- **Cambio di modello** (`/model`): ogni modello ha una cache propria. `opusplan` cambia modello a ogni ingresso e uscita dalla modalità plan. Una skill con `model` nel frontmatter cambia modello per quel turno.
- **Cambio di effort**: invalida su quasi tutti i modelli. Su Opus 5.5, Sonnet 5.5 e Fable 5.1 con chiave API o abbonamento la cache resta intatta (non vale su Bedrock, Agent Platform di Google Cloud, gateway delle app Claude).
- **Fast mode**: attivarla cambia un header che fa parte della chiave di cache; il costo si paga una volta per conversazione.
- **Collegare o rimuovere un server MCP, negare un intero tool**: cambia le definizioni dei tool, quindi il system prompt. Con la ricerca dei tool attiva (default sui modelli che la supportano) le definizioni sono differite e il prefisso non cambia.
- **Compattazione**: sostituisce la storia con un riassunto, quindi il livello della conversazione si ricostruisce. A cache calda la richiesta di riassunto legge il prefisso dalla cache; dopo una pausa oltre la durata della cache rilegge tutto: è il caso più caro (ripresa di una sessione vecchia).
- **Molte immagini o PDF accumulati**: oltre i limiti Claude Code toglie le più vecchie a lotti, con un turno lento per lotto.
- **Aggiornamento di Claude Code**: la prima conversazione dopo il riavvio ricostruisce la cache.

## Non la invalidano
- Modificare file del repository (arriva solo una nota di sistema in coda).
- Modificare CLAUDE.md a sessione avviata: non invalida, ma nemmeno si applica fino a `/clear`, `/compact` o riavvio. Vale anche per le regole di Mímir.
- Cambiare modalità di permessi o stile di output.
- Invocare skill e comandi (le istruzioni sono aggiunte in coda). Abilitare o disabilitare un plugin con soli skill, agent, hook: contenuto in coda, cache intatta.
- `/recap` e `/rewind`: quest'ultimo torna a un prefisso già in cache.
- Lanciare un subagent: ha una conversazione e una cache proprie, quella del padre non cambia. Un fork, invece, eredita prefisso e cache del padre.

## Durata
La cache scade per inattività; ogni richiesta che la colpisce riavvia il timer. Un'ora (TTL lungo) su abbonamento entro i limiti del piano; cinque minuti con chiave API, provider cloud o dopo il passaggio ai crediti d'uso. I subagent hanno di default cinque minuti. Si può scegliere con `promptCacheTtl` e `subagentPromptCacheTtl` (2.1.242 o successivo). Il TTL lungo conviene a chi lascia sessioni ferme e le riprende; costa di più nelle sessioni brevi e continue.

## Come leggerne lo stato
- `/usage`, riga `Prompt cache (main)`: richieste, quota di input dalla cache, miss con ultimo orario e, dalla 2.1.260, la causa probabile (per esempio "tool definitions changed"); freddo o caldo.
- Statusline: campo `current_usage` con `cache_creation_input_tokens` e `cache_read_input_tokens`. Letture alte rispetto alle creazioni = cache che funziona; creazioni alte turno dopo turno = qualcosa cambia nel prefisso.
