# Pagine che devono convincere

Per landing, siti di prodotto, pagine di eventi e portfolio. Una pagina così vive della prima impressione, non della lettura completa: si taglia molto. Le soglie sono punti di partenza verificabili, non leggi: la richiesta può cambiarle, e allora lo si dice.

## Primo schermo
- Sta tutto nella prima schermata desktop: titolo, sottotitolo e azione principale visibili senza scorrere.
- Titolo al massimo su due righe su desktop. Se va su quattro righe è un errore di corpo, non di testo: prima pianifica corpo e immagine insieme.
- Sottotitolo di circa 20 parole. Se il valore non si spiega in 20 parole, il problema è il valore, non la soglia.
- Al massimo quattro elementi di testo: un'etichetta o niente, titolo, sottotitolo, azioni (una principale e al più una secondaria).
- L'azione principale è quella per cui il visitatore è venuto, nella sua forma funzionante: la ricerca, la prenotazione, la prova gratuita. Un link che porta altrove non conta.
- Fuori dal primo schermo: righe di loghi dei clienti, anteprime di prezzo, elenchi di funzioni, file di avatar. Vanno nelle sezioni subito sotto.
- Il primo schermo ha un contenuto visivo vero. Testo con una macchia di gradiente è un segnaposto.
- Navigazione su una riga a 1024px e alta al massimo circa 80px; se non ci sta, accorcia le voci o toglile.
- Spazio sopra il titolo contenuto: un primo schermo con il contenuto a metà altezza sembra un errore di layout.

## Ritmo delle sezioni
- Ogni sezione ha un compito: agganciare, provare, spiegare o convertire. Se non ne ha uno, toglila.
- Forma di base: titolo breve (fino a 8 parole), un paragrafo breve (fino a 25 parole), un elemento visivo oppure un'azione. Il di più va giustificato dal compito della sezione.
- Famiglie di layout varie: la stessa famiglia (tre card, citazione a tutta larghezza, testo e immagine affiancati) compare una volta. Su otto sezioni, almeno quattro famiglie diverse.
- Al massimo due sezioni consecutive con testo e immagine affiancati e alternati; alla terza spezza con una sezione a tutta larghezza o verticale.
- Una griglia a mosaico ha tante celle quanti contenuti: nessuna cella vuota o di riempimento. Almeno due o tre celle con una variazione visiva vera (immagine, colore, motivo).
- Elenchi oltre cinque voci: un componente diverso invece di un elenco più lungo (gruppi, schede, colonne, scorrimento orizzontale). Tabelle lunghe di specifiche: raggruppa in due o tre blocchi, metti in evidenza le tre o quattro voci chiave e comprimi il resto.
- Nessuna sezione-discarica: per molti dati c'è una pagina dedicata.
- Ogni layout a più colonne dichiara il suo comportamento sotto i 768px nello stesso componente.

## Prova sociale
- Citazioni di al massimo tre righe, con nome, ruolo e azienda. Il nome da solo non è credibile.
- I loghi dei clienti sono loghi veri (SVG), leggibili in entrambi i temi, senza etichette di categoria sotto.
- Numeri e risultati solo se veri e forniti dalla richiesta.

## Immagini
- Le immagini vere vengono prima: quelle fornite, quelle del brand, uno strumento di generazione se il progetto lo prevede.
- Se mancano, segnaposto dichiarati con dimensioni e soggetto, e alla fine l'elenco delle immagini da procurare. Non riempire con illustrazioni SVG fatte a mano o schermate finte.
- Dimensioni e formati moderni, `width` e `height` dichiarati (niente salti di layout), caricamento differito fuori dal primo schermo.

## Contenuti
- Rileggi ogni stringa visibile prima di chiudere: titoli, bottoni, didascalie, testo alternativo, piè di pagina. Riscrivi ciò che è sgrammaticato, ha riferimenti non chiari o suona come un modello che vuole sembrare profondo. Una frase piatta e chiara batte una frase brillante e vuota.
- Un registro per pagina.

## Prestazioni e pubblicazione
- Obiettivi: LCP sotto 2,5 s, INP sotto 200 ms, CLS sotto 0,1. Misurali con gli strumenti del progetto o del browser e riporta i valori, non le impressioni.
- Font: pochi pesi, caricati con `font-display` adeguato e precaricati se servono al primo schermo.
- Meta: `title`, `description`, immagine e testi di anteprima per i social, favicon, `lang` della pagina.
- Link legali (privacy, cookie se dovuti, note legali) nel piè di pagina.
