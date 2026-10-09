# Gesti e spring

Un'interfaccia sembra fluida quando si comporta come un oggetto fisico: risponde subito, segue il dito, conserva lo slancio, resiste ai bordi e si può fermare a metà. Questo file serve per tutto ciò che si afferra: drawer trascinabili, caroselli, elementi da scartare con un gesto, slider.

## Risposta immediata
- Feedback alla pressione (`pointerdown`, `:active`), non al rilascio.
- Togli ogni ritardo non essenziale dal percorso dell'input: debounce, timer, attese di transizione, il ritardo del doppio tocco (`touch-action: manipulation`).
- Durante il gesto l'interfaccia segue il puntatore di continuo, non solo alla fine.

## Manipolazione diretta
- Pointer Events con `setPointerCapture` appena parte il trascinamento: il tracciamento continua anche se il puntatore esce dall'elemento.
- Rispetta il punto di presa: l'elemento non salta col centro sotto il dito.
- Tieni una breve storia di posizioni e tempi (gli ultimi movimenti) per calcolare la velocità al rilascio.
- Prima di decidere la direzione aspetta un piccolo spostamento (circa 10 px), poi segui uno a uno.
- Ignora un secondo dito durante un trascinamento, o l'elemento salta.
- Imposta `transform` direttamente sull'elemento trascinato, non tramite una variabile CSS del genitore.

## Interrompibilità
- L'utente può afferrare un elemento in movimento e invertirlo senza aspettare.
- La nuova animazione parte dal valore **visibile** in quel momento, non dal valore logico di destinazione: altrimenti salta.
- Per ciò che si afferra, niente transizioni CSS né keyframe: non si possono riprendere a metà in modo fluido. Le spring partono dal valore corrente per costruzione.
- Movimento in due dimensioni: due spring indipendenti per X e Y, perché hanno velocità diverse.

## Spring
Pensa la spring con due parametri:
- **smorzamento**: 1 = nessun rimbalzo, assestamento pulito; sotto 1 rimbalza, di più quanto più è basso;
- **risposta**: quanto rapidamente raggiunge la destinazione, in secondi. Non è una durata: il tempo di assestamento deriva dai parametri.

| Interazione | Smorzamento | Risposta |
|---|---|---|
| Spostamento, riposizionamento | 1 | 0.4 s |
| Rotazione | 0.8 | 0.4 s |
| Drawer, pannello | 0.8 | 0.3 s |

Di base smorzamento 1. Un po' di rimbalzo (0.8, o un "bounce" 0.1-0.3 nelle librerie che lo esprimono così) solo se il gesto aveva slancio: su un menu che appare il rimbalzo stona, su una card lanciata è naturale. Usa i parametri che la libreria del progetto espone, convertendo da questa tabella.

## Velocità al rilascio
Quando il dito si stacca, l'animazione continua alla stessa velocità: non deve vedersi la cucitura tra trascinamento e animazione. Passa la velocità di rilascio come velocità iniziale della spring. Alcune API la vogliono relativa alla distanza residua: `velocità / (destinazione − posizione)`.

## Proiezione dello slancio
Non scegliere la destinazione dal punto di rilascio: proietta dove arriverebbe l'elemento con quella velocità, poi aggancia il punto di arrivo più vicino alla proiezione.
```js
// decelerazione ≈ 0.998 per un comportamento da scorrimento normale, 0.99 più secco
function proiezione(velocitaPxAlSecondo, decelerazione = 0.998) {
  return (velocitaPxAlSecondo / 1000) * decelerazione / (1 - decelerazione);
}
const destinazione = puntoPiuVicino(posizione + proiezione(velocita));
```
Per chiudere un elemento con un gesto, basta la distanza **oppure** la velocità: un colpo rapido e corto deve chiudere (soglia indicativa: 0.1 px/ms).

## Bordi morbidi
Oltre un limite naturale l'elemento si muove sempre meno, invece di fermarsi di colpo: un arresto netto sembra un blocco, una resistenza crescente dice "risponde, ma qui non c'è altro".
```js
function resistenza(oltre, dimensione, k = 0.55) {
  return (oltre * dimensione * k) / (dimensione + k * Math.abs(oltre));
}
```

## Coerenza spaziale
- Si esce per la stessa strada da cui si è entrati.
- Ciò che nasce da un attivatore parte da lì.
- Il movimento intermedio anticipa la destinazione: chi guarda prevede l'esito dalla traiettoria.

## Gesti
- Tocco: evidenzia alla pressione, conferma al rilascio; un margine di qualche pixel attorno al bersaglio; annullabile trascinando via e tornando.
- Riconosci in parallelo tutti i gesti plausibili dal primo movimento e scarta gli altri appena l'intenzione è chiara. Evita gli eventi che riportano solo lo stato finale: perdi il tracciamento continuo.
- Il doppio tocco ritarda il tocco singolo: usalo solo dove serve davvero.
- Per ogni gesto serve un'alternativa accessibile (bottone, tastiera).

## Accessibilità
- `prefers-reduced-motion: reduce`: niente spring con rimbalzo né spostamenti ampi; dissolvenze brevi.
- `prefers-reduced-transparency: reduce`: superfici traslucide più piene, senza sfocatura.
- `prefers-contrast: more`: sfondi pieni e bordi netti.

## Prova
Su un dispositivo vero e su uno di fascia bassa; con la build di produzione; rallentando le animazioni. Prova anche l'interruzione: afferra l'elemento mentre si muove e invertilo.
