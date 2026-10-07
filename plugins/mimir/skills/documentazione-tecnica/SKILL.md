---
name: documentazione-tecnica
description: README, guide e documentazione di progetto. Usala quando scrivi o aggiorni un README, una guida, una documentazione tecnica o di onboarding, o in progetti con cartella docs o file .md.
when_to_use: 'Es.: "aggiorna il README", "scrivi una guida di installazione", "documenta l''architettura", "fammi una mappa di questo repo". Per un intervento operativo usa runbook, per un rilascio rilascio.'
---

# Documentazione tecnica

Si applica insieme a `clean-code`. Le convenzioni del progetto (struttura di docs, strumenti come wiki o sito) prevalgono. Per i documenti di analisi usa `analisi-funzionale` e `analisi-tecnica` (se disponibili); per i runbook `runbook`.

Non creare o modificare file nei repo dei clienti senza ok: proponi prima cosa scrivere e dove.

## Quattro tipi, non mescolarli
Ogni documento ha un solo scopo; se ne serve più di uno, sono file diversi che si rimandano.

| Tipo | Per | Forma |
|---|---|---|
| Tutorial | imparare facendo | percorso guidato, risultato garantito, niente alternative |
| Guida pratica | portare a termine un compito | passi in ordine, partendo da un obiettivo preciso |
| Riferimento | consultare | completo, ordinato, senza narrazione (API, configurazioni, comandi) |
| Spiegazione | capire il perché | contesto, scelte, alternative scartate |

Il segnale di un documento mescolato: una guida che si ferma a spiegare la storia, un riferimento con ragionamenti.

## README minimo utile
1. **Cos'è**: cosa fa il progetto e per chi, in poche righe.
2. **Come si avvia**: prerequisiti con versioni e comandi che funzionano copiati.
3. **Come si testa**: comando dei test e di linter.
4. **Dove sta il resto**: link a docs, ticket, runbook, contatti.

Prova i comandi in un ambiente pulito (o rileggili contro lo script di build): un comando non provato è un'ipotesi.

## Vicino al codice, aggiornata subito
- La documentazione sta nel repo, accanto a ciò che descrive.
- Chi cambia un comportamento aggiorna il documento **nello stesso commit** (il commit lo approva l'utente, come sempre).
- Ciò che invecchia porta **data e versione** a cui si riferisce, e un **responsabile**.
- **Link invece di copie**: una informazione vive in un solo posto. Una tabella copiata in tre file diverge in tre modi.
- Prima di scrivere, cerca se esiste già un documento da aggiornare.

## Diagrammi
Solo se chiariscono più del testo. Meglio mermaid nel markdown (versionabile) e, per le strutture, solo come vista di una tabella o di un elenco che resta la fonte. Un diagramma senza legenda o senza data è rumore.

## Cosa non documentare
- Ciò che il codice dice già: nomi, firme, struttura evidente. Se serve un commento per capirlo, migliora il codice (vedi `clean-code`).
- Dettagli volatili che cambiano a ogni commit.
- Segreti, credenziali, dati personali o del cliente: mai nei file versionati.
- Opinioni e storia del lavoro (appartengono a commit e ticket).

## Documentare ciò che esiste
Per capire un progetto sconosciuto, leggi manifest, config, struttura e test; scrivi ciò che hai verificato e segna come "da verificare" il resto. Un documento generato dall'AI è un indice, non una fonte: ricontrolla sul codice prima di darlo per vero.

### Mappa del codice (wiki)
Quando serve orientarsi in un repo intero (onboarding, presa in carico di un progetto) scrivi una mappa di **riferimento**: cosa c'è e come si collega, non perché è fatto così. Per ricostruire un comportamento preciso con evidenze, a supporto di una diagnosi o di una decisione, usa `analisi-tecnica`, se disponibile.
1. **Perimetro e costo prima di partire**: annota il commit di riferimento (hash), scegli 6-10 moduli principali (per peso, numero di dipendenze in ingresso, citazioni nel README) e mostra all'utente l'elenco con una stima della lettura (moduli per 3-5 file ciascuno) prima di scrivere. Niente moduli di test, codice generato o librerie copiate nel repo. La lettura dei moduli è ampia: delegala a subagent, uno per gruppo di moduli, e verifica a campione ciò che riportano.
2. **Struttura**: una pagina d'indice (cos'è, mappa dei moduli, come si avvia), una pagina sull'architettura, una per modulo (scopo, responsabilità, file chiave, interfaccia pubblica, da chi è usato e cosa usa, trappole note).
3. **Per ogni modulo leggi davvero 3-5 file chiave**: la descrizione nasce da ciò che hai letto, non dal nome della cartella.
4. **Diagrammi Mermaid** solo con componenti che esistono nel codice: ogni nodo corrisponde a qualcosa di reale, e un diagramma di sequenza segue chiamate che hai tracciato. Al massimo una ventina di nodi; oltre, dividi.
5. **Dove salvarla**: chiedi all'utente dove metterla. Nel repo del progetto solo su sua richiesta; lo scratchpad va bene per una bozza, non per una mappa da tenere. In testa il commit di riferimento. Una mappa senza commit non dice a quale versione del codice si riferisce.

Il rischio principale è inventare: componenti plausibili ma assenti, frasi generiche che varrebbero per qualunque progetto, il codice riscritto a parole. Prima di consegnare, ricontrolla a campione 2-3 link e un diagramma sul codice.

## Verifica
- Il documento ha un solo tipo e un solo scopo dichiarato.
- Comandi, percorsi, versioni e link citati esistono e li hai controllati.
- Nello stesso commit sono aggiornati i documenti toccati dal cambiamento.
- Data, versione e responsabile presenti dove il contenuto invecchia.
- Nessun segreto o dato personale, nessuna copia di contenuti già presenti altrove.
- In una mappa del codice: commit di riferimento in testa, ogni nodo dei diagrammi esiste nel codice.
