# Interfacce web sul telefono

Problemi che l'emulazione del browser da desktop non mostra. Si risolvono con CSS e meta tag, senza riconoscere il dispositivo dallo user agent: si interrogano le capacità (`hover`, `pointer`), perché touch e mouse possono convivere sullo stesso dispositivo.

## Sintomi e correzioni
| Sintomo | Causa | Correzione |
|---|---|---|
| Lo stato hover resta attivo dopo un tocco | Il touch simula l'hover | Regole di hover dentro `@media (hover: hover) and (pointer: fine)` |
| Lampo grigio o blu al tocco | Evidenziazione predefinita di WebKit | `-webkit-tap-highlight-color: transparent`, con un feedback di pressione proprio |
| Altezza sbagliata, contenuto sotto la barra del browser | `100vh` ignora le barre che appaiono e scompaiono | Guscio dell'app e elementi ancorati in basso: `100dvh`; primo schermo di una pagina: `100svh`, che non salta durante lo scorrimento |
| La pagina si ingrandisce entrando in un campo | Testo dei campi sotto i 16px su iOS | Campi a 16px o più. Mai bloccare lo zoom con `user-scalable=no` o `maximum-scale=1`: è una barriera di accessibilità |
| Il tocco sembra in ritardo | Attesa del doppio tocco, feedback solo al `click` | `touch-action: manipulation` sui controlli; feedback su `:active` o `pointerdown` |
| Il trascinamento verso il basso ricarica la pagina o fa rimbalzare l'app | Comportamento di overscroll | `overscroll-behavior: none` sul documento di un'app, `contain` sui pannelli che scorrono. Non bloccare `touchmove` con `preventDefault` |
| Il contenuto finisce sotto la tacca o la barra di sistema | Area sicura non considerata | `viewport-fit=cover` nel meta viewport e margini con `env(safe-area-inset-*)`; senza il meta i valori sono zero |
| Una pressione lunga seleziona il testo dei bottoni | Selezione predefinita | `user-select: none` solo sui controlli, mai sull'intera pagina |
| Un carosello orizzontale fa scorrere la pagina in verticale, o il contrario | Direzione del gesto non dichiarata | `touch-action: pan-y` (o `pan-x`) sulla superficie del gesto; `none` solo dove l'utente non deve mai scorrere |
| La barra di stato ha un colore che stona | `theme-color` mancante o unico | Un `theme-color` per ciascun `prefers-color-scheme` |
| Caroselli a scorrimento libero imprecisi | Scorrimento gestito a mano | `scroll-snap` nativo |
| Bersagli troppo piccoli | Dimensioni pensate per il mouse | Area di tocco di almeno 44x44 px, anche con l'icona più piccola |

## Base di partenza
- Meta viewport con `width=device-width, initial-scale=1` e, se servono le aree sicure, `viewport-fit=cover`.
- `theme-color` per tema chiaro e scuro.
- Hover condizionato al puntatore fine, feedback di pressione su `:active`.
- Altezze con `dvh` o `svh`, mai `vh` per gusci a schermo intero.
- Campi a 16px o più.

## Prova
- L'emulazione da desktop non basta per dichiarare corretto un problema di tocco, altezza o area sicura.
- Su un telefono vero: server di sviluppo sull'indirizzo di rete locale, ispezione remota (Safari su iOS, `chrome://inspect` su Android).
- Prova con la tastiera aperta, in orizzontale almeno una volta, su un telefono di qualche anno, e come app installata se è una PWA.
- Se non puoi provarlo su un dispositivo, separa nel resoconto ciò che hai verificato dal codice da ciò che l'utente deve confermare sul telefono.
