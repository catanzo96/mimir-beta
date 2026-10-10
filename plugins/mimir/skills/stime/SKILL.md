---
name: stime
description: Stima attività di sviluppo e manutenzione con intervalli e assunzioni. Usala quando l'utente deve stimare un ticket, una MEV o un progetto, dare tempi al cliente o rivedere una stima.
when_to_use: 'Es.: "quanto ci vuole?", "quante giornate servono?", "il cliente vuole una data", "questa stima è realistica?".'
---

# Stime

Si applica insieme a `analisi-funzionale` e `analisi-tecnica` (se disponibili): una stima senza analisi è un'ipotesi. Per scomporre il lavoro in passi di esecuzione usa `pianificazione`. Prevalgono il modello di stima e le unità del cliente o dell'azienda (giorni/uomo, punti, fasce).

Scopo: produrre una stima onesta, cioè un intervallo con assunzioni dichiarate, che si possa difendere e rivedere. Una stima è una previsione, non una promessa.

## Quando non usarla
- Decidere se fare o no un lavoro: `decisioni`.
- Fare lo stato di un lavoro in corso: `stato-e-rischi`, se disponibile.

## 1. Fissa cosa si stima
- Scrivi il perimetro in poche righe: cosa è dentro, cosa è fuori, cosa serve consegnare (codice, test, documentazione, rilascio).
- Se i requisiti sono vaghi, dillo e stima l'analisi, non il lavoro. Chiedi ciò che manca prima di inventare.
- Chiedi a cosa serve il numero: budget, pianificazione, offerta? Cambia il livello di precisione e il margine.

## 2. Scomponi
- Scomponi fino a parti che sai valutare con un'occhiata: di solito da mezza giornata a pochi giorni. Una parte di tre settimane nasconde incognite.
- Parti dall'evidenza nel codice: moduli toccati, test esistenti, ambienti. Per la manutenzione, la parte di comprensione del legacy pesa spesso più della modifica.
- Elenca esplicitamente le attività che altrimenti spariscono (vedi [references/costi-nascosti.md](references/costi-nascosti.md)): collaudo, rilascio, documentazione, riunioni, revisione del codice, correzione dei difetti del collaudo, supporto al cliente.

## 3. Stima a intervallo
Per ogni parte tre valori: **ottimistico** (va tutto bene), **probabile**, **pessimistico** (le incognite si avverano, non il disastro). Il valore atteso con la formula a tre punti (`(O + 4·P + Pe) / 6`) è un'indicazione, non una verità. Quello che comunichi è l'intervallo.

- Non sommare i pessimistici di tutto: è irrealistico e gonfia il totale. Non sommare nemmeno solo i probabili: l'errore tende al ritardo, non alla media.
- Un intervallo molto largo è un'informazione: dice che serve ridurre l'incertezza, non allargare il margine.
- Più la fase è iniziale, più l'intervallo è largo (cono di incertezza). Dichiara in che fase è la stima.

## 4. Riduci l'incertezza
Per le parti con intervallo largo prevedi uno **spike**: un'indagine a tempo fisso (mezza giornata, un giorno) con un risultato preciso (una domanda a cui rispondere o un prototipo minimo). Lo spike si stima a parte e non è la stima del lavoro.

## 5. Usa le evidenze storiche
Prima di fidarti dell'intuito, confronta con lavori simili già fatti:
- `git log` e diff delle modifiche passate sullo stesso modulo (commit, giorni di calendario tra primo e ultimo commit del ticket);
- ticket chiusi simili con il tempo effettivamente impiegato;
- ricorda che il calendario non è l'impegno: dai giorni trascorsi sottrai interruzioni e attese.

Dichiara la fonte e il campione ("3 ticket simili, da 2 a 5 giorni"). Un campione piccolo si dice piccolo. Se non ci sono dati, scrivi che la stima è di giudizio. Dettagli in [references/costi-nascosti.md](references/costi-nascosti.md).

## 6. Assunzioni, esclusioni, contingenza
- **Assunzioni**: ciò che deve essere vero perché la stima regga (ambienti disponibili, risposte del cliente entro X giorni, nessuna modifica ai requisiti). Ognuna ha un proprietario e, se cade, la stima si rivede.
- **Esclusioni**: cosa non è incluso, scritto.
- **Contingenza**: un margine per i rischi noti, mostrato come riga separata con la motivazione. Mai nascosto dentro i singoli numeri: altrimenti chi legge lo toglie come "gonfiatura".

Usa [templates/stima.md](templates/stima.md). Dove salvarlo lo proponi tu e lo decide l'utente.

## 7. Comunica
Distingui tre cose, perché spesso vengono confuse:
- **stima**: ciò che ci si aspetta, con l'incertezza;
- **obiettivo**: ciò che il cliente vorrebbe;
- **impegno**: ciò a cui ci si obbliga, con una data, accettando il rischio.

Un impegno si prende dopo la stima, non al suo posto; se l'obiettivo è più stretto dell'intervallo, dillo e proponi leve: ridurre il perimetro, fasi, più persone dove il lavoro è parallelizzabile. Al cliente presenta intervallo, assunzioni principali e la data di quando la stima sarà più precisa. Per il testo al cliente usa le virgolette dritte "…". La decisione di inviare è dell'utente.

## 8. Rivedi
Quando cambia il perimetro, cade un'assunzione o si apprende qualcosa di rilevante, rifai la stima e comunica la differenza con la causa. Confronta a consuntivo stima ed effettivo: è l'evidenza storica della prossima volta.

## Verifica
- Perimetro, esclusioni e assunzioni scritti; nessuna attività ricorrente dimenticata.
- Ogni parte ha tre valori e nessuna è più grande di qualche giorno senza motivo.
- La contingenza è una riga a parte con il motivo.
- Le fonti storiche sono dichiarate; il giudizio è marcato come tale.
- Chi legge capisce se è una stima, un obiettivo o un impegno.
- I totali sono ricalcolati (somma delle righe) e coerenti con quanto comunicato.

## File di supporto
- [references/costi-nascosti.md](references/costi-nascosti.md): elenco di ciò che si dimentica e uso dei dati storici. Leggilo prima di chiudere il totale.
- [templates/stima.md](templates/stima.md): tabella delle attività, assunzioni, rischi.
