# Ricevere una review

Vale per le osservazioni di un collega, di un reviewer sulla MR o dell'agent `code-reviewer`. Un'osservazione è un'ipotesi da verificare, non un ordine da eseguire.

## Procedura
1. **Leggi tutto prima di toccare qualcosa.** Se un punto non è chiaro, chiedi chiarimenti prima di applicare gli altri: spesso i punti sono collegati.
2. **Verifica ogni osservazione sul codice reale**: il problema esiste davvero, in questa versione, in questo contesto? Una segnalazione può essere sbagliata o basata su un'idea del codice che non corrisponde al vero.
3. **Classifica**:
   - *correzione*: un difetto reale nel perimetro della modifica;
   - *miglioramento*: utile ma aggiunge funzioni o cambia comportamento;
   - *preferenza*: stile non coperto dalle convenzioni del progetto;
   - *non applicabile*: sbagliata o fuori contesto.
4. **Prima di aggiungere ciò che viene suggerito, controlla che serva**: se la review chiede di gestire un caso o rendere configurabile qualcosa, cerca se quel caso o quel bisogno esiste davvero.
5. **Applica una correzione per volta**, verificando dopo ciascuna. Ordine: prima ciò che blocca, poi le correzioni semplici, poi quelle complesse.

## Cosa si fa con ciascuna
- *Correzione*: si applica.
- *Miglioramento*: si propone con l'opzione consigliata e si aspetta l'ok (regola "resta nel perimetro").
- *Preferenza*: si segue la convenzione del progetto. Se non c'è, si segnala e decide l'utente.
- *Non applicabile*: si risponde con la motivazione tecnica e l'evidenza (`file:riga`, test, documentazione). Non si accetta per cortesia.

## Review di un controllo di sicurezza
Per un hook, una validazione o un filtro, ogni giro di review trova nuove forme di aggiramento. Correggi subito solo ciò che una prova sullo script dimostra che passa in silenzio, oltre l'obiettivo del controllo. Le ipotesi, i casi che danno solo un esito più prudente e quelli fuori dai limiti dichiarati si annotano per dopo. Se lo stesso approccio mostra buchi a ogni giro, cambia approccio invece di aggiungere casi.

## Resoconto
Per ogni osservazione: esito (applicata, proposta, respinta) e motivo. Le risposte da pubblicare sulla MR si propongono all'utente, non si inviano.
