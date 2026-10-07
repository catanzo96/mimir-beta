---
name: analisi-funzionale
description: "Analisi funzionale fondata su evidenze. Usala quando l'utente chiede di capire, documentare o specificare il comportamento funzionale di un sistema: censimento AS-IS di un modulo, richiesta del cliente, MEV, collaudo, domande al cliente."
when_to_use: 'Es.: "come funziona il modulo X?", "il cliente chiede che…", "prepara le domande per il cliente", "cosa cambia per l''utente con questa MEV?".'
---

# Analisi funzionale

Documenta **cosa fa un sistema e perché**, nel linguaggio del dominio, con evidenze verificabili. Per il *come* tecnico usa `analisi-tecnica`. Spesso i due documenti si scrivono in coppia.

Il metodo delle evidenze vale anche qui: [../analisi-tecnica/references/evidenze.md](../analisi-tecnica/references/evidenze.md). **Leggilo sempre prima di scrivere.** Una regola di business è accertata solo se hai sia il codice che la applica, sia il documento normativo o funzionale che la impone.

## Contesto del progetto
Dal `CLAUDE.md` del progetto ricava:
- dominio e glossario;
- piattaforme e dove vive la logica (codice, modello low-code, frontend);
- ambienti;
- dove vanno i documenti;
- codici di ticket ed evolutive;
- destinatari delle domande (cliente, fornitori).

Se un termine ha più significati, o due termini indicano la stessa cosa (nel codice, nei documenti, nelle parole del cliente), segnalalo subito e fissa quello da usare: un glossario ambiguo produce requisiti ambigui. Le affermazioni sul comportamento attuale, anche dell'utente, si verificano sul codice prima di scriverle come fatti.

## Criterio di completezza
Un modulo è documentato quando **uno sviluppatore che non l'ha mai visto può reimplementarlo leggendo solo il documento**. Servono sei cose:
1. **Il dato**: entità, attributi, vincoli, relazioni, cardinalità *reali*, misurate sui dati.
2. **Gli stati**: quali esistono, chi li cambia, quali transizioni sono ammesse. Anche quali stati sono definiti ma mai osservati.
3. **Le regole**: calcoli, soglie, validazioni, con la fonte normativa quando esiste. Ogni regola è un **requisito** (quando succede X, allora Y) o un'**invariante** (è sempre vero che…), con un ID stabile, il punto del codice che la impone e il test che la copre, oppure "nessuno".
4. **Le azioni**: cosa può fare l'utente, con quale ruolo, in quale stato.
5. **I confini**: cosa entra e cosa esce, verso quali sistemi, con quale tracciato.
6. **Il non detto**: comportamenti che solo il codice conosce. Effetti collaterali, ordini di operazione che contano, errori ingoiati. È ciò che distingue una reimplementazione che funziona da una che *somiglia*. I ticket risolti ne sono la miniera migliore.

## Procedura
1. **Inventario del materiale**: documenti, ticket, codice, dati disponibili.
2. **Come la interpretiamo**: scrivi la tua lettura della richiesta **prima** di partire, così un fraintendimento emerge subito.
3. **Segui l'ordine** dato → stati → regole → azioni e permessi → confini → non detto. Parti dal dato perché è la cosa più stabile e verificabile. I confini sono il vincolo più rigido: i sistemi esterni non cambiano perché cambiamo noi.
   - Nel codice parti dai punti d'ingresso (endpoint, job, schermate) e scendi un livello alla volta. Fermati ai confini esterni, o quando altri file non aggiungono regole nuove. Ciò che non hai letto va dichiarato in "Verificato su", non taciuto.
4. **Separa** accertato e ipotesi. Ogni ipotesi diventa una [domanda](templates/domande.md), con il destinatario.
5. **Scrivi** con il template adatto, togliendo le sezioni che non servono.
6. **Chiudi** con cosa replicare, cosa non replicare e cosa decidere.

## Round di chiarimento con l'utente
Quando ci sono più punti aperti che dipendono dall'utente:
- I fatti li cerchi tu (codice, dati, documenti): all'utente si chiedono solo decisioni e informazioni che non sono nel materiale.
- Ogni round contiene **tutte** le domande che si possono già porre: quelle che non dipendono da risposte ancora mancanti. Numerate, ciascuna con la **risposta consigliata** e il motivo, così si può rispondere "ok" o correggere.
- Dopo le risposte, aggiorna il documento e apri il round successivo con le domande che si sono sbloccate. Si chiude quando non resta nulla di aperto che blocchi il documento.

Le domande per il **cliente** sono un'altra cosa: vanno nel template [domande.md](templates/domande.md), nella forma da inviare, **senza** risposta consigliata.

## Profondità proporzionata al rischio
- Richiesta piccola, senza impatto su dati, permessi o sistemi esterni: formato leggero, pochi criteri di accettazione.
- Tocca dati esistenti, permessi, integrazioni, normativa o più moduli: analisi completa, con impatti e criteri anche su ciò che **non** deve cambiare.

## Template
| Template | Quando |
|---|---|
| [analisi.md](templates/analisi.md) | formato leggero: valutare una richiesta, un documento, un'ipotesi di intervento |
| [scheda-modulo.md](templates/scheda-modulo.md) | censimento AS-IS completo di un modulo (le sei cose) |
| [analisi-mev.md](templates/analisi-mev.md) | analisi funzionale di un'evolutiva: requisiti, perimetro a lotti, criteri di accettazione |
| [collaudo.md](templates/collaudo.md) | scheda di collaudo di una MEV o di un fix |
| [domande.md](templates/domande.md) | domande aperte per destinatario, con priorità; in fondo la forma da inviare al cliente |

## Stati e diagrammi
- La macchina a stati si documenta con la **tavola delle transizioni**: Da | Azione | A | Ruolo | Condizioni | Fonte.
- Un `stateDiagram-v2` mermaid si aggiunge **solo come vista** della tavola, se aiuta. Con molte azioni diventa illeggibile: in quel caso limitalo al percorso principale.

## Difetti trovati
- Si annotano nel registro del debito (vedi `analisi-tecnica`), non si correggono mentre si analizza.
- Se sono urgenti, diventano un ticket.
- Segnala sempre se un comportamento difettoso è **parte del contratto di fatto**: un dato che il cliente legge e usa, anche se sbagliato, va replicato oppure cambiato in modo esplicito. Mai cambiarlo per distrazione.

## Cosa non fare
- Non progettare il sistema nuovo mentre documenti quello vecchio. Le idee vanno in un ADR o nella sezione "da decidere".
- Non fidarti dei nomi di campi e funzioni: sono indizi, non prove.
- Non riportare dati personali. Usa codici pratica e conteggi.
- Non creare nel repo del progetto file di metodo (glossari, specifiche, indici) senza ok: i documenti vanno dove indica il `CLAUDE.md` del progetto.
- Non chiudere una MEV senza criteri di accettazione verificabili.
