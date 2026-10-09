---
name: animazioni-ui
description: Animazioni e transizioni delle interfacce web. Usala quando aggiungi, correggi o rivedi movimento in una UI (transizioni, comparse, menu, drawer, gesti di trascinamento) o un'interfaccia sembra lenta o legnosa.
when_to_use: 'Es.: "anima l''apertura del menu", "aggiungi una transizione", "il drawer scatta", "rivedi le animazioni", "come si chiama l''effetto in cui…". Aspetto statico della pagina: design-ui.'
---

# Animazioni delle interfacce

Si applica insieme a `design-ui` (l'asse del movimento si decide lì) e alla skill del framework. Prevalgono i token di movimento e la libreria già presenti nel progetto: estendili, non creare un sistema parallelo. Una libreria di animazione nuova chiede l'ok.

Due errori, e il primo è peggiore: animare ciò che non va animato, e animare la cosa giusta con gli ingredienti sbagliati (`ease-in` su una comparsa, `scale(0)`, keyframe su un elemento che si riattiva subito). Decidi tu e spiega la scelta in una riga: un menu di opzioni sul movimento non aiuta l'utente.

## Procedura
Segui l'ordine: i primi due passi possono chiudere il lavoro senza codice, ed è un esito valido.

### 1. Va animato?
| Quante volte la vede chi la usa | Decisione |
|---|---|
| Centinaia di volte al giorno: scorciatoie da tastiera, palette dei comandi, navigazione in una lista | Nessuna animazione |
| Decine di volte al giorno: hover, cambi di scheda, apertura di un menu frequente | Appena percettibile e veloce, oppure niente |
| Ogni tanto: modali, drawer, notifiche | Animazione standard |
| Raramente: primo accesso, completamento, onboarding | Qui c'è spazio per qualcosa di espressivo |

Le scorciatoie e le azioni ripetute da tastiera (navigazione in una lista, palette dei comandi) non si animano: chi le usa vuole l'esito immediato. Aprire un menu o una modale con Invio o Spazio segue invece la stessa regola del clic. Se la richiesta non passa, dillo e proponi l'alternativa statica.

### 2. A cosa serve?
Dagli un nome prima di continuare: **feedback** (l'interfaccia ha sentito l'azione), **continuità spaziale** (da dove viene, dove va), **cambio di stato** reso leggibile, **evitare un salto** di contenuto, **spiegazione** (solo onboarding e marketing), **piacere** (solo per ciò che si vede raramente). Senza un nome non si fa.

I dati che l'utente sta leggendo o usando non si muovono per stile.

### 3. Lo strumento più semplice che basta
1. Transizione CSS: hover, pressione, colore, stati governati da una classe o un attributo.
2. `@starting-style`: comparsa al montaggio senza stato JavaScript.
3. Animazione CSS: movimento predeterminato che deve restare fluido mentre la pagina carica, perché non dipende dal thread principale.
4. Web Animations API (`element.animate()`): controllo da codice senza dipendenze.
5. Libreria di animazione del progetto: spring, uscite, animazioni di layout, gesti.

Se serve un componente (dropdown, drawer, notifiche, palette dei comandi), usa quello della libreria di componenti del progetto: costruirlo a mano porta a un `div` senza gestione del focus.

### 4. Proprietà
- Solo `transform` e `opacity`, che non ricalcolano il layout; `clip-path` e `filter` leggeri se restano fluidi. `height` è tollerata per le fisarmoniche, brevi.
- Mai partire da `scale(0)`: parti da 0.95-0.97 con opacità zero.
- Menu, popover e tooltip si aprono dal loro attivatore (`transform-origin` sull'attivatore). Le modali no: restano centrate.
- Mai `transition: all`: elenca le proprietà.
- Non guidare la trasformazione dei figli con una variabile CSS del genitore: ricalcola lo stile di tutti i figli. Imposta `transform` sull'elemento.

### 5. Curva e durata, oppure spring
| Situazione | Curva |
|---|---|
| Entrata e uscita | ease-out deciso |
| Movimento sullo schermo da un punto a un altro | ease-in-out |
| Hover e colore | ease |
| Movimento costante (barra di avanzamento, scorrimento continuo) | linear |

Mai `ease-in` sull'interfaccia: parte lento proprio nel momento in cui l'utente guarda. Le curve predefinite del CSS sono deboli. Valori di partenza, da trasformare in token se il progetto non li ha:
- ease-out: `cubic-bezier(0.23, 1, 0.32, 1)`
- ease-in-out: `cubic-bezier(0.77, 0, 0.175, 1)`
- drawer: `cubic-bezier(0.32, 0.72, 0, 1)`

| Elemento | Durata |
|---|---|
| Pressione di un bottone | 100-160 ms |
| Tooltip, popover piccoli | 125-200 ms |
| Dropdown, select | 150-250 ms |
| Modali, drawer | 200-500 ms |

Nell'interfaccia resta sotto i 300 ms, salvo i drawer; le pagine di marketing possono andare oltre.

Usa una **spring** quando l'utente può afferrare, lanciare o invertire il movimento: parte dal valore corrente e conserva la velocità. Di base senza rimbalzo; un rimbalzo leggero solo se il gesto aveva slancio (un lancio, un rilascio). Dettagli: `references/gesti-e-spring.md`.

### 6. Interruzione e uscita
- Per ciò che si riattiva in fretta (notifiche, interruttori) usa transizioni, non keyframe: una transizione riparte dal valore corrente, un keyframe da zero.
- Mai bloccare l'input durante un'animazione.
- Si esce per la stessa strada da cui si è entrati.
- Tempi asimmetrici dove l'utente decide: lento nella fase deliberata (tenere premuto per confermare), rapido nella risposta del sistema.
- Più elementi che entrano insieme: sfasali di 30-80 ms, senza bloccare l'interazione.

### 7. Accessibilità e puntatore
Vanno con l'animazione, non dopo:
- `prefers-reduced-motion: reduce`: niente spostamenti, spring e parallasse; restano dissolvenze brevi e cambi di colore che aiutano a capire. Movimento ridotto non significa nessun feedback.
- Hover animati solo dentro `@media (hover: hover) and (pointer: fine)`.
- Niente sfondi in movimento a tutto schermo né oscillazioni lente in ciclo.

## Revisione
Per rivedere animazioni esistenti o un diff:
1. Per ogni animazione: frequenza, scopo, strumento, proprietà, curva, durata, interruzione, accessibilità. Cita `file:riga`.
2. Correggi nell'ordine dal più forte al più fine: **eliminala** se non passa i passi 1-2, poi **riducila**, poi curva e durata, origine, interrompibilità, proprietà, asimmetria, rifinitura.
3. Resoconto: una tabella con prima, dopo e perché, poi un esito netto (da correggere o approvata) con il criterio che lo decide.

Per cercare dove *mancano* animazioni utili (stati che saltano, feedback assente): stesse domande dei passi 1-2, al massimo 5-7 proposte, ed elenca anche i candidati scartati con la domanda che li ha fermati.

## Verifica
- Per ogni animazione: frequenza e scopo dichiarati, valori dalle tabelle o dai token del progetto.
- Nessun elemento della tabella "mai" in `references/ricette.md`.
- Riduzione del movimento e hover condizionato presenti.
- La resa si giudica guardandola, non dal codice: rallentala di 2-5 volte o usa l'ispettore delle animazioni del browser, scorrila fotogramma per fotogramma, prova i gesti su un dispositivo vero. Se non puoi guardarla, dichiaralo e indica cosa deve controllare l'utente.

## File di supporto
- `references/ricette.md`: pressione, dropdown, tooltip, modale, drawer, notifica, fisarmonica, sfasamento, tenere premuto, indicatore di scheda, comparsa allo scorrimento, dissolvenza incrociata; tabella "mai" e prestazioni. Parti da qui quando la richiesta è uno di questi casi.
- `references/gesti-e-spring.md`: trascinamento, velocità al rilascio, proiezione dello slancio, resistenza ai bordi, parametri delle spring. Per tutto ciò che si afferra.
- `references/vocabolario.md`: nomi degli effetti a partire da una descrizione vaga. Quando l'utente descrive un effetto senza nominarlo.
