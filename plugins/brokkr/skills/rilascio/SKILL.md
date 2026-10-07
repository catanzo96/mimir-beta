---
name: rilascio
description: Rilasci verificabili e reversibili. Usala quando prepari, esegui o documenti un rilascio in collaudo, preproduzione o produzione, o pianifichi più rilasci di un'evolutiva.
when_to_use: 'Es.: "domani rilasciamo in produzione", "prepara le note di rilascio", "serve un piano di rollback", "deploy in collaudo".'
---

# Rilascio

Porta in esercizio ciò che è stato sviluppato e collaudato, **in modo verificabile e reversibile**. Si usa insieme a `git-workflow` (tag e versioning), `runbook` (interventi sulle macchine) e `analisi-funzionale` (collaudo).

## Contesto del progetto
Dal `CLAUDE.md` del progetto ricava:
- come si rilascia (tag che attivano la pipeline, deploy manuale, piattaforma);
- ambienti e il loro ordine;
- componenti e dipendenze tra loro (modello o DB prima del backend, backend prima del frontend);
- chi approva;
- dove si tiene il registro dei rilasci.

## Principi
- **Lo stesso artefatto** collaudato va in produzione: non si ricompila tra un ambiente e l'altro.
- **Un passo alla volta**, ciascuno reversibile. Un rilascio che non si può annullare va dichiarato come tale e approvato come tale.
- **Esito atteso per ogni voce** della checklist. Se l'esito reale diverge, ci si ferma.
- **Comandi e query di verifica** li esegue chi ha l'accesso, uno alla volta. Le query di modifica vanno in transazione, con il conteggio prima del commit.
- **Il tag si crea solo con l'ok dell'utente**: spesso è ciò che avvia il deploy (vedi `git-workflow` e le regole di approvazione).
- **Esito letto, non atteso**: ogni voce si chiude con l'output reale del controllo. "Dovrebbe essere andato" non è un esito.

## Procedura per un rilascio
1. **Preparazione**
   - Cosa si rilascia: commit o tag per componente.
   - Diff rispetto al rilascio precedente.
   - Configurazione per ambiente: proprietà o variabili nuove presenti nell'ambiente di destinazione.
   - Migrazioni del database: segui [migrazioni-db.md](references/migrazioni-db.md).
   - Note di rilascio dal [template](templates/note-di-rilascio.md).
2. **Checklist**: copia la [checklist](templates/checklist-rilascio.md) per questo rilascio e compilala durante l'esecuzione, non dopo.
3. **Prima**: backup verificato, conteggi di riferimento, versione attualmente in esercizio annotata per il rollback, stato dei servizi verde, rollback riletto. Fissa una **baseline** dei segnali che guarderai dopo (errori nei log nell'ultima ora, tempi di risposta delle pagine o API principali, code e job): senza un "prima" non si capisce se il "dopo" è peggiorato.
4. **Deploy** nell'ordine delle dipendenze, con le verifiche dopo ogni componente.
5. **Smoke**: i flussi principali, con esito atteso.
6. **Osservazione**: gli stessi segnali della baseline, confrontati subito, poi dopo un giorno e dopo tre giorni. Cerca gli errori **nuovi** (tipi di errore mai visti prima), non solo il loro numero.
7. **Chiusura**: registro dei rilasci aggiornato, ticket e MEV aggiornati, comunicazione a chi deve saperlo.

## Più rilasci: il piano
Per un'evolutiva a lotti, o per più evolutive che si intrecciano, usa il [piano rilasci](templates/piano-rilasci.md). Un solo documento per perimetro: due piani che si sovrappongono divergono.

## Rollback
- Scritto **prima** del rilascio, per ogni passo.
- Distingui ciò che si annulla ripristinando l'artefatto precedente (codice) da ciò che richiede una procedura inversa (dati, schema, flussi già partiti verso sistemi esterni).
- Se un passo non è reversibile (una migrazione distruttiva, un invio a un sistema esterno), dichiaralo nel Go/No-Go.
- **Quando si torna indietro**, deciso prima: quali segnali fanno scattare il rollback (es. un flusso di smoke fallito, errori nuovi sopra una soglia, tempi raddoppiati), chi decide ed entro quanto tempo dal rilascio. Durante il rilascio non si negozia.
- Lo schema del database raramente si annulla all'indietro: di solito si rimette il codice precedente, compatibile con lo schema nuovo, oppure si scrive una migrazione in avanti che corregge.
