---
name: design-ui
description: Qualità visiva delle interfacce web. Usala quando crei o rivedi l'aspetto di pagine, schermate e componenti (layout, tipografia, colore, stati, copy) o rifai la grafica di un'interfaccia esistente.
when_to_use: 'Es.: "fai una landing per…", "rendi più professionale questa pagina", "rifai la grafica della dashboard", "sembra fatta con l''AI". Struttura e stato dell''app: architettura-frontend.'
---

# Design delle interfacce

Si applica insieme a `architettura-frontend` (componenti e design system nel codice), alla skill del framework e a `clean-code/references/a11y.md` per l'accessibilità, che qui non si ripete. Le animazioni sono in `animazioni-ui`, la prova con dati estremi in `ui-casi-limite`. Prevalgono design system, brand e convenzioni del progetto.

Senza una direzione il modello ripiega su default riconoscibili: tre card uguali, gradiente viola, etichette maiuscole sopra ogni titolo. Qui c'è come decidere invece di ripiegare.

## 1. Leggi la richiesta
Prima del codice raccogli i segnali:
- **superficie**: gestionale, dashboard, documentazione, landing, sito di marca, singolo componente;
- **pubblico**: chi la usa, quanto spesso, con che fretta;
- **parole di stile e riferimenti**: "sobrio", "come Linear", screenshot, siti citati;
- **materiale esistente**: design system, libreria di componenti, token, logo, colori, font;
- **vincoli impliciti**: pubblica amministrazione e accessibilità per legge, settori regolati, utenti interni che lavorano sullo strumento tutto il giorno. Prevalgono sul gusto.

Poi dichiara in una riga come la leggi, così l'utente corregge subito la direzione: *"La leggo come: \<superficie> per \<pubblico>, linguaggio \<stile>, base \<design system o stack>; varietà \<…>, movimento \<…>, densità \<…>."*

Se la lettura è davvero ambigua, fai **una** domanda. Se si deduce dal contesto, dichiarala e procedi.

### Tre assi
Varietà (dalla simmetria all'audacia compositiva), movimento (da statico a scenografico), densità (da arioso a fitto). Punti di partenza:

| Caso | Varietà | Movimento | Densità |
|---|---|---|---|
| Gestionale, back office, dashboard | bassa | bassa | alta |
| Servizio pubblico o settore regolato | bassa | bassa | media |
| Documentazione, guide, articoli | bassa | bassa | media |
| Landing di prodotto B2B | media | media | media |
| Sito di marca, evento, portfolio | alta | media o alta | bassa |
| Rifacimento conservativo | come l'esistente | come l'esistente | come l'esistente |

Una correzione dell'utente ("più sobrio", "più vivace") sposta un asse: non ripartire da un'altra interpretazione.

## 2. La superficie decide le priorità
- **Lavorare** (gestionali, strumenti, dashboard): chi la usa deve trovare tutto dove se lo aspetta prima di notare lo stile. Navigazione e controlli standard; l'identità passa solo da tipografia, palette, densità e al più un tratto distintivo. Qui il difetto tipico non è la piattezza ma la stranezza senza scopo. Una famiglia tipografica, una scala fissa a passi piccoli.
- **Leggere** (documentazione, articoli, guide): la colonna di testo resta calma, con 60-75 caratteri per riga, corpo intorno a 16px e contrasto pieno. L'identità sta nella cornice: testata, navigazione, titoli, resa di codice e tabelle. Chi legge sa sempre dove si trova e dove andare.
- **Convincere** (landing, marketing, eventi): il design fa parte del messaggio. Nel primo schermo l'offerta è comprensibile e l'azione principale è visibile e funzionante. Regole in `references/pagine-marketing.md`.

Un prodotto può avere superfici diverse (landing pubblica, area riservata): decidi per superficie.

## 3. Base: design system e token
- Se il progetto ha un design system o una libreria di componenti, usali: niente componenti paralleli, niente valori fuori dai token.
- Se la richiesta richiama un design system pubblico (Material, Fluent, Carbon, Bootstrap Italia per la PA), usa il pacchetto ufficiale invece di rifarlo in CSS, e uno solo per progetto. Importarne i token per poi sovrascriverli quasi tutti è il peggio dei due mondi. Una dipendenza nuova chiede l'ok.
- Uno stile (glass, bento, editoriale) non è un design system: implementalo con CSS nativo e dichiaralo come approssimazione.
- Senza una base, fissa pochi token prima dei componenti: scala tipografica, scala delle spaziature, neutri di una sola famiglia, un accento, i colori di stato, un sistema di raggi, un solo modo di dare profondità (bordo oppure ombra).

## 4. Costruisci
- **Gerarchia** da peso, dimensione e spazio. Spazio stretto dentro un gruppo, largo tra i gruppi, più sopra un titolo che sotto.
- **Un tema per pagina**, scelto dal contesto d'uso (luce ambiente, ore di lavoro) e non dalla categoria. Le sezioni non si invertono a metà pagina.
- **Card** solo per separare oggetti davvero distinti; mai card dentro card. Altrimenti raggruppa con spazio o divisori.
- **Dati**: cifre tabulari nelle tabelle, numeri allineati a destra, colori di stato solo dove portano un significato.
- **Stati** per ogni elemento interattivo e ogni dato:
  - hover solo con un puntatore fine, focus visibile, attivo, disabilitato;
  - caricamento con uno scheletro della forma finale;
  - vuoto, che dice come riempirlo;
  - errore vicino alla causa, con la via d'uscita.
- **Copy** nella lingua del prodotto: i bottoni nominano l'azione, un'etichetta sola per ogni intento, gli errori dicono problema e rimedio. Niente frasi riempitive né giochi di parole.
- **Contenuti**: dati reali o dichiarati come esempio. Niente numeri finti precisi, nomi di comodo, lorem ipsum.
- **Elementi del browser**: selezione del testo, anello di focus, scrollbar, sottolineatura dei link e `theme-color` prendono la palette. Il modello li dimentica quasi sempre.
- **Telefono**: `references/mobile-web.md`.

## 5. Default da rifiutare
Valgono quando nessuno li ha chiesti: una richiesta esplicita li riammette. Se ti accorgi di usarne uno senza averlo deciso, riscrivi l'elemento invece di attenuarlo.
- Righe di card uguali (icona, titolo, testo) come struttura della pagina.
- Etichette maiuscole sopra ogni titolo, numeri di sezione decorativi.
- Gradienti viola e blu, testo in gradiente, bagliori, vetro sfocato come decorazione.
- Bordo laterale colorato e spesso su card, elenchi e avvisi.
- Monospace come costume "tecnico" fuori da codice e dati.
- Emoji o caratteri al posto delle icone; icone di set diversi.
- Una modale per un compito che non chiede interruzione.
- Schermate di prodotto finte fatte di `div`.
- Testo secondario grigio neutro su sfondo colorato: tingilo con la tinta dello sfondo.

Catalogo completo con le alternative: `references/anti-pattern.md`.

## 6. Rifacimento
Su un'interfaccia esistente leggi `references/rifacimento.md` prima di toccare. In breve: capisci se va conservata o rifatta (nel dubbio chiedi), fai l'audit prima delle modifiche, procedi dalla leva meno rischiosa e non cambiare mai in silenzio URL, voci di navigazione, campi dei form, eventi di analytics e testi legali.

## Verifica
Sul risultato costruito, non sulle intenzioni:
1. La lettura dichiarata è rispettata; ogni requisito della richiesta c'è e si trova in pochi secondi.
2. Contrasto almeno 4.5:1 per il testo e 3:1 per testo grande e controlli, compresi placeholder, form e bottoni sopra immagini.
3. Coerenza contabile:
   - un accento e una famiglia di neutri;
   - un sistema di raggi e un modo di dare profondità;
   - un tema;
   - nessun colore o misura scritti a mano fuori dai token: cercali nel diff.
4. Con il testo reale a ogni breakpoint: niente overflow, bottoni su una riga, righe di testo nella misura, titoli bilanciati.
5. Stati presenti; tastiera e focus secondo `a11y.md`.
6. Copy riletto per intero, etichette comprese.
7. Controllo nel browser almeno a 360px e alla larghezza desktop, in entrambi i temi se previsti. Se non puoi aprirlo, dichiaralo.
8. Alla fine i default del punto 5: per ciascuno usato, la richiesta che lo giustifica.

Una passata di controllo e una di correzioni, al massimo un secondo giro; oltre, riporta ciò che resta aperto. Per una revisione con contesto pulito c'è l'agent `design-reviewer`; per i dati estremi, `ui-casi-limite`.

## File di supporto
- `references/anti-pattern.md`: i default riconoscibili con l'alternativa. Leggilo quando rivedi una UI o una pagina "sembra generata".
- `references/pagine-marketing.md`: primo schermo, ritmo delle sezioni, immagini, contenuti, prestazioni. Per landing e siti.
- `references/rifacimento.md`: modi, audit, leve in ordine, cosa non cambia, omissioni frequenti. Prima di toccare un'interfaccia esistente.
- `references/mobile-web.md`: sintomi tipici sul telefono e correzioni.
