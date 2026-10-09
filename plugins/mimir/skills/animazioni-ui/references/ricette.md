# Ricette di animazione

Punti di partenza per i casi comuni, in CSS senza librerie. Adatta selettori e attributi a quelli del progetto: molte librerie di componenti espongono attributi per lo stato di entrata e uscita e una variabile con l'origine dell'attivatore; usa quelli invece di riscriverli.

Token usati negli esempi:
```css
:root {
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
}
```

## Pressione di un bottone
```css
.btn { transition: transform 140ms var(--ease-out); }
.btn:active { transform: scale(0.97); }
```
`:active` funziona anche al tocco, quindi non va condizionato. Scala anche etichetta e icona: è questo che lo fa sembrare un tasto fisico.

## Elementi chiusi: invisibili anche a tastiera e clic
Un elemento chiuso con la sola opacità resta nell'ordine del focus, viene letto dagli screen reader e, se copre la pagina (sfondo di una modale), cattura i clic. Le ricette di menu, modale e drawer lo nascondono con `visibility: hidden`, che toglie focus, lettura e clic, e ne ritardano il cambio fino alla fine della chiusura: all'apertura vale subito, alla chiusura scatta quando la dissolvenza è finita. Se l'elemento è un `<dialog>` nativo o usa l'attributo `popover`, focus e clic li gestisce il browser: anima quelli invece di ricostruirli.

## Dropdown, popover, menu
```css
.menu {
  transform-origin: var(--origine-attivatore, top left);
  transition: opacity 180ms var(--ease-out), transform 180ms var(--ease-out), visibility 0s;
}
.menu:not([data-open]) {
  opacity: 0; transform: scale(0.96); visibility: hidden;
  transition-delay: 0s, 0s, 180ms;
}
```
L'origine è il punto: il pannello deve sembrare uscito da ciò che hai cliccato.

## Tooltip
Come il popover, più rapido (circa 125 ms) e meno scalato (0.97). Il ritardo iniziale evita le aperture accidentali; quando un tooltip è già aperto, quelli vicini si aprono senza ritardo e senza animazione, così una barra di strumenti si esplora in fretta.

## Modale
```css
.modal, .modal-backdrop {
  transition: opacity 220ms var(--ease-out), transform 220ms var(--ease-out), visibility 0s;
}
.modal { transform-origin: center; }
.modal:not([data-open]), .modal-backdrop:not([data-open]) {
  opacity: 0; visibility: hidden;
  transition-delay: 0s, 0s, 220ms;
}
.modal:not([data-open]) { transform: scale(0.96); }
```
Sfondo e finestra si animano insieme, così si leggono come un'unica superficie. La modale non è ancorata a un attivatore: resta centrata. Aperta, tiene il focus al suo interno e alla chiusura lo restituisce all'attivatore: un `<dialog>` aperto con `showModal()` lo fa da solo.

## Drawer e pannelli laterali
```css
.drawer { transition: transform 400ms var(--ease-drawer), visibility 0s; }
.drawer:not([data-open]) { visibility: hidden; transition-delay: 0s, 400ms; transform: translateX(100%); }
.drawer.sinistra:not([data-open]) { transform: translateX(-100%); }
.drawer.basso:not([data-open]) { transform: translateY(100%); }
```
Il pannello esce dal bordo a cui è attaccato, di default quello destro: `translateX` per quelli laterali, `translateY` per quello dal basso. La percentuale in `translate` è relativa all'elemento: funziona qualunque sia la sua larghezza o altezza. Lo sfondo, se c'è, segue la ricetta della modale. Se si può trascinare, diventa un gesto: `gesti-e-spring.md`.

## Notifica
```css
.toast {
  transition: opacity 300ms ease, transform 300ms ease;
  @starting-style { opacity: 0; transform: translateY(100%); }
}
```
Transizione e non keyframe: se ne arrivano due di fila, la seconda riparte dal valore corrente. Esce dalla stessa parte da cui è entrata. Quando le notifiche si impilano e la lista si riassesta, opacità e altezza si compensano a occhio: regola guardandola.

## Fisarmonica
```css
.panel { overflow: hidden; transition: height 200ms var(--ease-out), opacity 200ms var(--ease-out); }
```
Una delle poche animazioni che ricalcola il layout a ogni fotogramma: tienila breve. L'altezza si misura con JavaScript o la fornisce il componente della libreria; dove è supportato, `interpolate-size: allow-keywords` permette di animare verso `height: auto`.

## Entrata sfasata di un gruppo
```css
.item { animation: entra 280ms var(--ease-out) both; animation-delay: calc(var(--i) * 50ms); }
@keyframes entra { from { opacity: 0; transform: translateY(8px); } }
```
Con `--i` impostato sull'indice. Solo per gruppi che si vedono ogni tanto, mai per una lista che si scorre tutto il giorno, e mai bloccando l'interazione.

## Tenere premuto per confermare
Per azioni distruttive dove un clic è troppo facile.
```css
.hold .fill { clip-path: inset(0 100% 0 0); transition: clip-path 200ms var(--ease-out); }
.hold:active .fill { clip-path: inset(0); transition: clip-path 2s linear; }
```
Lineare perché è un indicatore di avanzamento; rilascio rapido. Serve anche un'alternativa da tastiera e una conferma per chi non può tenere premuto.

## Indicatore della scheda attiva con cambio di colore
Interpolare i colori di più schede non viene mai sincronizzato. Duplica la lista delle schede con lo stile attivo, sovrapponila e mostra solo la scheda attiva con un `clip-path: inset(...)` animato (circa 250 ms, ease-in-out): testo e sfondo cambiano insieme perché è un solo elemento che si rivela. La copia è decorativa: `aria-hidden="true"` e fuori dall'ordine del focus.

## Comparsa allo scorrimento
Solo pagine di marketing. Una volta sola, attivata con `IntersectionObserver` o con le animazioni legate allo scorrimento del CSS. Ripeterla a ogni passaggio è un'interfaccia che combatte chi legge.

## Dissolvenza incrociata che non si fonde
Se due stati sovrapposti si vedono come due oggetti distinti e curva e durata non bastano, una sfocatura leggera (circa 2 px) durante il passaggio li fonde in una sola trasformazione. Resta sotto i 20 px: oltre costa molto, soprattutto in Safari.

## Da codice, senza libreria
```js
el.animate(
  [{ clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0)' }],
  { duration: 600, easing: 'cubic-bezier(0.77, 0, 0.175, 1)', fill: 'forwards' }
);
```
Interrompibile, senza dipendenze, con le prestazioni del CSS.

## Mai
| Mai | Invece |
|---|---|
| `transition: all` | Le proprietà, una per una |
| Comparsa da `scale(0)` | `scale(0.95)` con opacità zero |
| `ease-in` su un elemento dell'interfaccia | ease-out deciso |
| Animazione su una scorciatoia da tastiera o su un'azione ripetuta centinaia di volte | Nessuna animazione |
| Durata oltre 300 ms senza motivo | 150-250 ms |
| Popover ancorato con origine al centro | Origine sull'attivatore (le modali sono l'eccezione) |
| Keyframe su notifiche, interruttori, elementi riattivati in fretta | Transizioni |
| Animare `width`, `height`, `margin`, `padding`, `top`, `left` | `transform` e `opacity`; unica eccezione l'altezza della fisarmonica, breve |
| Hover animato senza condizione sul puntatore | `@media (hover: hover) and (pointer: fine)` |
| Nessuna variante per il movimento ridotto | Variante più gentile, non assente |
| Tutto che entra insieme | Sfasamento di 30-80 ms |
| Input bloccato durante un'animazione | Animazione interrompibile |

## Prestazioni
| Sintomo | Correzione |
|---|---|
| Scatti | Animare solo `transform` e `opacity` |
| Liste lunghe lente | Virtualizzazione o paginazione |
| Sfocatura animata pesante | Meno di 20 px, solo su elementi piccoli |
| Proprietà che si animano senza volerlo | Niente `transition: all` |
| Il framework ridisegna il componente a ogni fotogramma | Scrivere lo stile direttamente sull'elemento (riferimento al nodo) invece che nello stato |
| L'elemento si sposta di un pixel all'avvio del movimento | `will-change: transform` solo dove lo si vede, e solo durante il movimento |
| Animazioni da libreria che perdono fotogrammi sotto carico | Animazioni CSS o Web Animations API per il movimento predeterminato |
