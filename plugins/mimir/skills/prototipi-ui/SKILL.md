---
name: prototipi-ui
description: Costruisce più varianti davvero diverse di un pezzo di interfaccia, confrontabili dal vivo con un selettore, e promuove quella scelta. Solo su richiesta esplicita.
disable-model-invocation: true
---

# Prototipi di interfaccia

Si applica insieme a `design-ui` e, se le varianti si muovono, ad `animazioni-ui`: ogni variante rispetta la loro verifica. Prevalgono stack, token e convenzioni del progetto.

Il valore sta nella **divergenza**: tre sfumature della stessa idea sprecano il confronto, perché passando dall'una all'altra non si impara nulla. Divergere non autorizza però a scendere di qualità.

## Regole
- Il codice di produzione non si tocca durante l'esplorazione, salvo la registrazione della route di prova solo in sviluppo: tutto sta in una superficie di prova isolata. L'integrazione avviene solo alla fine, per la variante scelta.
- Ogni variante diverge su un **asse dichiarato**: disposizione, densità, personalità, movimento, modello di interazione. Due varianti che differiscono solo per colore o testo sono una variante sola.
- Ogni variante funziona davvero: interazioni reali, testi e dati plausibili del prodotto, niente bottoni morti né lorem ipsum.
- Il selettore è un'impalcatura, non un concorrente: neutro, uguale in ogni giro, non segue lo stile del progetto.
- Dopo la scelta la superficie di prova si cancella, salvo richiesta.

## Procedura
1. **Perimetro.** Un pezzo per volta. Se la richiesta copre più componenti ("la dashboard"), scegli il pezzo con più impatto, di' quale e perché, e proponi il resto come giri successivi. Riformula in una frase: cos'è, dove vive, cosa deve fare.
2. **Ricognizione.** Stack, sistema di stili, libreria di animazione, token, personalità del prodotto (strumento quotidiano o sito di marca: limita quanto può spingersi la variante più audace), contesto in cui il pezzo appare (sfondo, vicini, dimensioni).
3. **Direzioni.** Tre varianti di base, fino a cinque se l'utente lo chiede o lo spazio è davvero ampio. Prima del codice elenca nome e asse di ciascuna. Nomi che descrivono la direzione ("Sobria", "Editoriale", "Densa"), mai "A, B, C". Nessuna coppia nella stessa posizione dello stesso asse.
4. **Superficie di prova.**
   - In un progetto con server di sviluppo: una route o pagina isolata (es. `/prototipi/<nome>`), un file per variante e un file di raccolta. Niente import dalla superficie di prova verso il codice di produzione. La route si registra solo in sviluppo, con il meccanismo del progetto (modalità di sviluppo del bundler o del framework, file escluso dalla build): se resta fino al merge, una build di produzione non deve contenerla.
   - Senza progetto: un unico file HTML autonomo.
   - Una variante per volta, a grandezza reale, nel contesto in cui vivrà.
5. **Selettore.** Una barra fissa in basso al centro, scura e neutra, che non copre il pezzo in prova:
   - un bottone per variante con il suo nome, quella attiva segnata con `aria-current`;
   - tasti da 1 a N e frecce per cambiare, `R` per rilanciare l'animazione se le varianti ne hanno;
   - la variante attiva nell'URL (`?variante=2`), così un ricaricamento la conserva;
   - cambio istantaneo, senza animazioni proprie;
   - solo in sviluppo, mai in produzione.
6. **Verifica e consegna.** Avvia la superficie, passa tu tutte le varianti, controlla che ogni interazione risponda e che la console sia pulita; screenshot se hai lo strumento. Poi presenta e **fermati**, perché la scelta spetta all'utente:

   | # | Variante | Asse | Quando vince | Cosa costa |
   |---|---|---|---|---|

   Nessuna preferenza nella tabella. Se l'utente chiede quale sceglieresti, rispondi in base alla personalità del prodotto e alla frequenza d'uso, non al gusto. Chiudi con dove gira il selettore e i tasti.
7. **Dopo la scelta.**
   - "tieni \<variante>": integrala dove deve stare con le convenzioni del progetto, poi cancella la superficie di prova;
   - "rilancia attorno a \<variante>": nuovo giro di varianti che divergono attorno a quella direzione, tenendo la superficie.

## Verifica
- Ogni variante ha nome e asse dichiarati, e nessuna coppia coincide.
- Ogni variante si raggiunge dal selettore e funziona; console pulita.
- Il codice di produzione non è stato toccato prima della scelta, a parte la registrazione della route di prova.
- Dopo l'integrazione: test e lint del progetto, controllo nel browser della variante integrata, superficie di prova rimossa (salvo richiesta).
