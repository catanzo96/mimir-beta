# Rifare la grafica di un'interfaccia esistente

Il rischio più grande di un rifacimento è sbagliare il modo: trattare come pagina nuova ciò che andava conservato, o il contrario.

## 1. Il modo
- **Conservativo**: si modernizza senza perdere il riconoscimento. Si estraggono i token esistenti e si evolve.
- **Rifacimento visivo**: linguaggio visivo nuovo sopra contenuti e struttura esistenti. Per la grafica è come una pagina nuova; contenuti e architettura delle informazioni restano.
- **Nuovo brand**: cambia l'identità stessa; è un progetto nuovo e lo decide chi ne ha l'autorità.

Se il modo non è chiaro, chiedi una volta: "Conserviamo l'identità attuale o ripartiamo da zero sulla grafica?"

## 2. Audit prima di toccare
Documenta lo stato attuale, con i percorsi dei file:
- **token di fatto**: colori, font, raggi, spaziature, anche quando sono sparsi nei componenti;
- **architettura delle informazioni**: pagine, navigazione principale, percorsi che contano (acquisto, invio, ricerca);
- **blocchi di contenuto**: cosa lavora e cosa riempie;
- **da conservare**: interazioni caratteristiche, elementi riconoscibili, tono del testo;
- **da ritirare**: i default di `anti-pattern.md`, layout rotti, link morti, immagini generiche, trappole di prestazioni;
- **accessibilità già raggiunta**: focus, testi alternativi, tastiera, contrasto. Non deve peggiorare;
- **misure di partenza**: pagine indicizzate, titoli e meta, dati strutturati, eventi di analytics, Core Web Vitals.

Il rischio più sottovalutato è la SEO: URL, titoli e contenuti indicizzati che cambiano senza un piano di redirect.

## 3. Le leve, dalla meno rischiosa
Applicale in ordine e fermati quando la richiesta è soddisfatta:
1. tipografia: il guadagno visivo più grande per unità di rischio;
2. spazi e ritmo verticale;
3. colore: neutri unificati, accento di brand mantenuto e ricalibrato;
4. stati e feedback mancanti (hover, focus, caricamento, vuoto, errore);
5. movimento, secondo `animazioni-ui`;
6. ricomposizione del primo schermo e delle sezioni chiave;
7. sostituzione di un blocco intero, solo se non è recuperabile.

Se architettura, contenuti e SEO sono sani, bastano le prime cinque leve: si ottiene la maggior parte del valore con una frazione del rischio. Se il debito è strutturale (navigazione rotta, nessun design system, mobile inutilizzabile), si rifà, conservando con rigore i contenuti.

## 4. Cosa non cambia in silenzio
Solo con l'approvazione esplicita dell'utente:
- struttura degli URL, slug e ancore;
- etichette della navigazione principale;
- nomi e ordine dei campi dei form (rompono analytics e compilazione automatica);
- identificativi ed etichette su cui poggiano eventi di analytics o test end-to-end;
- logo e marchio;
- testi legali, di consenso e sui cookie;
- tono del testo: rifare la grafica non è riscrivere i contenuti.

## 5. Omissioni frequenti
Controlla che ci siano, e se mancano proponile (non aggiungerle senza ok se cambiano il comportamento):
- pagina 404 utile, con una via d'uscita;
- percorso indietro da ogni pagina, voce attiva evidenziata nella navigazione;
- link per saltare al contenuto;
- validazione dei form nel browser oltre a quella del server;
- link legali e consenso ai cookie dove dovuti;
- `title`, `description`, immagini di anteprima, favicon, `lang`;
- stati di caricamento, vuoto ed errore.

## 6. Resoconto
Per ogni leva applicata: cosa è cambiato, dove, e la verifica fatta (screenshot prima e dopo se disponibili, contrasto, misure). Elenca a parte ciò che hai notato e non hai toccato perché fuori perimetro o da approvare.
