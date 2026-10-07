---
name: delega
description: Scrivere il brief per un subagent o un workflow e usarne l'esito. Usala quando deleghi una ricerca o un lavoro, o lanci più subagent in parallelo.
---

# Delega

Si applica insieme a `contesto-e-costi` (perché delegare) e `pianificazione` (la delega dentro un piano). Le regole sul modello dei subagent sono in `rules/working-style.md` e in `scrivi-skill`: qui c'è come scrivere il brief e come usare il risultato.

Un subagent parte da zero, salvo un fork (che eredita la conversazione): vede il suo system prompt, il messaggio del compito che scrivi tu e i CLAUDE.md del progetto (non Explore e Plan, che li saltano). Non vede la conversazione, le skill già invocate, la tua memoria né ciò che hai deciso. Quello che non scrivi nel brief, per lui non esiste. Torna alla conversazione solo il suo resoconto finale.

## Quando delegare
- **Sì**: ricerche e letture ampie (molti file o fonti), lavori indipendenti e paralleli, review con contesto pulito, lavori meccanici, un modello diverso da quello della sessione.
- **No**: compiti piccoli che sai già fare (il costo del brief supera il lavoro), lavori che dipendono da ciò che stai scoprendo, decisioni e scelte di design finali, approvazioni, comunicazioni verso terzi, tutto ciò che richiede una domanda all'utente (un subagent non può porla).

## Il brief
Scrivilo come per un collega bravo che non ha seguito la conversazione. Ogni brief ha:
1. **Obiettivo e perché**: una frase sul risultato e su come verrà usato. Il motivo orienta le scelte che il brief non prevede.
2. **Compito chiuso e verificabile**: cosa deve esserci alla fine e come si capisce che è finito. "Trova dove si calcola l'IVA e dimmi quali percorsi la usano" è chiuso; "guarda il modulo fatture" no.
3. **Contesto minimo ma sufficiente**: percorsi, nomi, versione, vincoli del progetto, ciò che hai già escluso (altrimenti lo rifà). Non incollare la conversazione.
4. **Vincoli**: sola lettura o cosa può modificare; niente commit, push, installazioni, rete; cartelle da non toccare. Ripeti i vincoli che contano: Explore e Plan non leggono CLAUDE.md e, negli altri casi, il brief è ciò che il subagent ha in primo piano.
5. **Modello**: sempre esplicito (vedi sotto).
6. **Formato del resoconto**: cosa e quanto restituire (vedi sotto).

Un brief buono sta in 8-15 righe. Se ne servono molte di più, il compito è troppo grande: spezzalo. Esempi buoni e cattivi: `references/brief-esempi.md`, da leggere prima di scrivere il primo brief della sessione.

## Modello
Dichiaralo a ogni lancio; senza indicazione il subagent usa il modello della sessione (quello dell'agent, se la sua definizione ne ha uno), e un modello costoso su una ricerca meccanica è spreco.

La scelta del modello segue la tabella e le eccezioni di `scrivi-skill` (sezione Agent), riassunte in `rules/working-style.md`: non le ripeto qui per non avere copie che divergono.
- Il parametro del lancio ha la precedenza sul `model` dell'agent; l'`Explore` di Mímir (`.claude/agents/`) è già su `haiku`.

## Formato del resoconto
Chiedilo nel brief, perché il subagent non sa cosa ti serve:
- compatto: prima la risposta in una o due righe, poi le evidenze;
- evidenze per ogni fatto: `file:riga`, comando, query con l'ambiente;
- **accertato** separato da **ipotesi**, con la verifica che confermerebbe l'ipotesi;
- cosa non è riuscito a fare o non ha controllato, dichiarato in modo esplicito;
- nessun file di report (il resoconto torna nel messaggio finale), salvo richiesta.

## Parallelo
- Solo per lavori indipendenti: nessuno usa l'output di un altro, nessuno condivide uno stato.
- Mai sugli stessi file: due subagent che scrivono sullo stesso file si sovrascrivono. Dai a ciascuno il proprio perimetro (cartelle, file) oppure usa `isolation: worktree` per le modifiche. In sola lettura il parallelo è sicuro.
- Lancia i subagent indipendenti nello stesso messaggio, così girano insieme. Il limite predefinito è 20 subagent attivi, ma ogni subagent consuma il tuo budget: pochi e mirati.
- Un lavoro con passi dipendenti resta sequenziale. Se i subagent trovano la stessa causa, avevi un solo problema.

## Lavoro che prosegue da solo
`/goal`, `/loop`, `/batch`, `/background` e le routine (`/schedule`) fanno lavorare Claude per più turni senza che tu scriva ogni passo. Quando usarli e con quali paletti: [references/lavoro-autonomo.md](references/lavoro-autonomo.md), da leggere prima di proporne uno.

## Usare l'esito
Il resoconto è un indice, non una fonte.
- Apri i `file:riga` che sorreggono le conclusioni importanti prima di basarci una decisione o di citarle all'utente.
- Un'assenza ("non esiste") è accertata solo se la ricerca non saltava file (encoding diversi, binari, cartelle escluse).
- Dopo le modifiche di un subagent: guarda il diff e lancia tu test e linter. Un "tutto passa" riferito non è un test eseguito.
- Un resoconto sicuro ma senza evidenze vale come ipotesi.
- Se l'esito è sbagliato o incompleto, non rilanciare lo stesso brief: correggi il brief (cosa mancava) o continua lo stesso subagent con un messaggio mirato, se è ancora disponibile.
- Riporta all'utente la fonte: cosa hai verificato tu e cosa viene dal subagent.

## Cosa non delegare
- Le decisioni dell'utente e le approvazioni (commit, push, piani grandi, invii al cliente): le chiedi tu, con l'elenco previsto da `rules/git-and-safety.md`.
- La sintesi finale e la responsabilità del risultato.
- Azioni distruttive o difficili da annullare.
- Un subagent non fa commit né push, salvo richiesta esplicita dell'utente nel suo ambito.

## Verifica
- Il brief si regge da solo: un lettore che non ha visto la conversazione sa cosa fare, dove, entro quali vincoli e come si capisce che ha finito.
- Modello dichiarato, coerente con la tabella.
- Se in parallelo: perimetri disgiunti o worktree, nessun file condiviso in scrittura.
- Il resoconto è stato controllato su almeno le evidenze che pesano sulla decisione.
- Nulla di ciò che spetta all'utente è stato deciso dal subagent.

## File di supporto
- `references/brief-esempi.md`: brief buoni e cattivi per ricerca, review, modifica e parallelo, con il motivo. Leggilo prima di scrivere un brief nuovo.
- `references/lavoro-autonomo.md`: `/goal`, `/loop`, `/batch`, `/background` e routine, con i paletti di sicurezza.
