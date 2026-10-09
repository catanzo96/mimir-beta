---
name: contesto-e-costi
description: Tenere sotto controllo contesto e costi di una sessione. Usala quando la sessione si allunga, i costi o i limiti salgono, prima di letture ampie o cambi di modello.
---

# Contesto e costi

Si applica insieme a `delega` (per spostare le letture ampie fuori dalla conversazione) e alla regola di triage in `rules/working-style.md`. I numeri e i comandi dipendono dalla versione di Claude Code: nel dubbio verifica con `/context` e con la documentazione ufficiale.

Il costo di una sessione cresce con la dimensione del contesto: a ogni richiesta Claude Code rimanda l'intera conversazione, riletta dalla cache a tariffa ridotta. Una domanda di una riga in una sessione aperta da ore paga comunque tutta la storia.

## Cosa entra nel contesto
- **Fisso, a ogni sessione**: system prompt e definizioni dei tool, CLAUDE.md e regole senza `paths` (nel caso di Mímir: profilo e sei regole), memoria automatica (prime 200 righe o 25 KB), informazioni sull'ambiente e stato git.
- **Lista delle skill**: nome e description di ogni skill, tranne quelle con `disable-model-invocation: true`. Il corpo entra solo quando la skill parte.
- **Tool MCP**: di default entrano solo i nomi (definizioni caricate su richiesta). Un server con molti tool pesa poco in lista, ma ogni schema caricato resta.
- **Conversazione**: messaggi, risultati dei tool (letture di file, output dei comandi), corpi delle skill invocate. È la parte che cresce e quella su cui agisci tu.

## Misurare
Misura prima di ottimizzare: spesso il peso sta dove non te lo aspetti.
- `/context`: ripartizione per categoria (system prompt, tool, MCP, memoria, skill, messaggi). Il primo comando da lanciare.
- `/usage`: blocco Session con token e costo stimato per modello, riga `Prompt cache (main)` con la quota di input servita dalla cache e i miss (richiede Claude Code 2.1.251 o successivo). Su piani Pro/Max/Team/Enterprise mostra anche a chi sono attribuiti i consumi (skill, subagent, plugin, MCP) e segnala i comportamenti oltre il 10%, come contesto lungo e cache miss.
- `/doctor`: stima il costo della lista delle skill e i maggiori contributori; segnala le estensioni inutilizzate.
- `/skill-doctor` (2.1.252 o successivo): costo di ogni skill e quali non sono mai state invocate.
- Statusline: mostra in modo continuo l'uso del contesto e i campi della cache (`prompt_cache`).
- `claude plugin details <plugin>`: costo fisso (always-on) di un plugin, in token stimati.

Ordini di grandezza dalla documentazione, da leggere come indicazioni e non come soglie: costo medio circa 13 dollari per sviluppatore per giorno attivo, con il 90% sotto i 30; le attività in background (riassunti per `--resume`) restano sotto i 0,04 dollari per sessione. Nella simulazione della pagina sul context window, un file di codice letto pesa circa 2.400 token e l'output di una suite di test circa 1.200; un subagent che ha letto 6.100 token di file restituisce un resoconto da 420.

## Cosa costa davvero
- **Letture di file grandi**: restano nel contesto per tutta la sessione e vengono rimandate a ogni richiesta. Leggi l'intervallo che serve (`offset` e `limit`) o cerca prima con grep.
- **Output lunghi dei comandi** (log, test, build): filtra a monte (`| tail`, `| grep`, opzioni quiet). Un hook può filtrare l'output prima che Claude lo veda.
- **MCP con molti tool**: dove esiste una CLI equivalente (`gh`, `aws`, `gcloud`), la CLI non aggiunge nulla alla lista. Disattiva i server inutilizzati con `/mcp`.
- **Pensiero esteso**: i token di thinking sono fatturati come output. Su Opus 5.5, Sonnet 5.5 e Fable non si disattiva: la leva è l'effort.
- **Cambi di modello e di effort a metà lavoro**: ogni modello ha la sua cache, quindi il primo turno dopo `/model` rilegge tutto senza cache. Anche una skill con `model` nel frontmatter è un cambio di modello (per questo `scrivi-skill` lo vieta). Per l'effort vale lo stesso su quasi tutti i modelli; fanno eccezione Opus 5.5, Sonnet 5.5 e Fable 5.1 con chiave API o abbonamento. Dettagli e altre cause di invalidazione: `references/cache.md`.
- **Pause lunghe**: la cache scade (un'ora su abbonamento entro i limiti del piano, cinque minuti con chiave API o crediti). Il primo messaggio dopo la pausa rilegge l'intero contesto.
- **Subagent**: le loro richieste pesano sul tuo consumo e hanno una cache separata. Il vantaggio è che le letture non entrano nella tua conversazione.

## Leve, in ordine di convenienza
1. **Scegli modello ed effort a inizio sessione** e non cambiarli a metà compito. Segui la tabella di `scrivi-skill`; per il triage vedi sotto.
2. **Delega le letture ampie** a un subagent (`delega`): tornano il resoconto e le evidenze, non i file.
3. **Leggi solo ciò che serve**: richieste specifiche ("aggiungi la validazione a `login` in `auth.ts`") evitano scansioni larghe.
4. **`/clear` quando cambi compito**. Costa zero e azzera anche i totali di `/usage`. Prima `/rename`, poi `/resume` per tornare.
5. **`/compact` ai confini di fase**, quando decidi tu (a cache calda costa una frazione di quel che suggerisce la dimensione). Passa le istruzioni su cosa conservare: `/compact conserva i percorsi dei file modificati e l'esito dei test`. Dopo la compattazione la lista delle skill non viene reiniettata; i corpi delle skill invocate sì, con tetto di 5.000 token per skill e 25.000 in totale.
6. **`/rewind` per abbandonare un percorso**: torna a un prefisso già in cache, quindi è più economico di una compattazione e non lascia nel contesto il tentativo sbagliato.
   - **`/branch`** per provare un'altra strada senza perdere quella attuale: crea un ramo della conversazione e ci entra; all'originale si torna con `/resume`.
   - **`/btw`** per una domanda a margine ("quale file avevi letto per X?"): risponde da ciò che è già in contesto, senza strumenti, e non entra nella conversazione. A cache calda costa quasi solo la risposta.
   - **`/subtask`** per un lavoro collaterale il cui esito deve tornare qui (un subagent che eredita la conversazione); **`/fork`** per una copia che prosegue da sola in background. Chi modifica codice lo fa in un worktree suo: i passi che toccano gli stessi file restano in sequenza (`delega`).
7. **Piano prima del codice** nei lavori grandi (modalità plan): evita il rifacimento quando la direzione iniziale è sbagliata.
8. **Indica come verificare** (test, output atteso): Claude corregge da solo prima che tu chieda un secondo giro.

L'auto-compattazione scatta da sola vicino al limite del modello (circa 967.000 token sui modelli con finestra da 1M, 200.000 sugli altri); `/autocompact <token>` la anticipa. Preferisci comunque la compattazione manuale a un confine naturale: quella automatica può scattare a metà compito.

Nelle sessioni avviate dal launcher, l'hook `handoff.py` (Ratatoskr) interviene molto prima: oltre 200.000 token (`MIMIR_HANDOFF_TOKENS`) chiede il passaggio di consegne e `/clear`, e la sessione successiva riparte dal documento con il contesto pulito. Dettagli nel README di Mímir.

## Triage di Mímir
`rules/working-style.md` classifica il compito prima di agire:
- **piccolo**: procedi direttamente, senza esplorare oltre il necessario;
- **medio**: una riga su cosa farai, poi procedi;
- **grande**: piano breve e ok prima di toccare file; per design e piani complessi delega a `architetto`.

Le ricerche ampie vanno a un subagent con il modello dichiarato (`haiku` per cercare e leggere). Dopo tre tentativi falliti con lo stesso approccio ci si ferma: insistere gonfia il contesto senza avvicinare la soluzione.

## Peso fisso di Mímir
Il contesto fisso di Mímir è CLAUDE.md, profilo e regole (sempre in contesto) più la lista delle skill. Per tenerlo leggero: regole solo per ciò che vale per ogni compito, description che dicono solo "quando", dettaglio in `references/`, skill di sola procedura manuale con `disable-model-invocation: true`. Il budget della lista è l'1% della finestra di contesto per default; Mímir lo porta al 3% (`skillListingBudgetFraction`). Il controllo periodico è la skill `manutenzione-mimir`.

## Verifica
- Hai misurato (`/context` o `/usage`) prima di agire sul consumo, e riporti il dato, non una sensazione.
- Le letture ampie sono state delegate o limitate agli intervalli utili.
- Nessun cambio di modello o effort a metà compito senza un motivo.
- Prima di `/clear` o `/compact` hai conservato ciò che serve (decisioni, percorsi, stato dei test); se serve un documento di ripresa usa `passaggio-consegne`.
- Dove hai dato un numero, dichiara la fonte e la versione di Claude Code.

## File di supporto
- `references/cache.md`: cosa invalida la cache e cosa no, durata della cache, come leggerne lo stato. Leggilo prima di cambiare modello, effort, plugin o server MCP a sessione avviata, o quando il consumo sale senza motivo.
