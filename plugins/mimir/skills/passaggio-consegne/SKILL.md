---
name: passaggio-consegne
description: Scrive il documento per riprendere il lavoro in una nuova sessione o passarlo a un collega. Solo su richiesta esplicita.
disable-model-invocation: true
---

# Passaggio di consegne

Si applica insieme alle regole sempre attive, in particolare `rules/git-and-safety.md` (niente segreti) e `rules/working-style.md` (verificato non è plausibile). Se l'utente ha indicato su cosa verterà la prossima sessione, adatta il documento a quello.

Scopo: chi riparte, senza la conversazione, deve capire in pochi minuti dove si è arrivati e cosa fare dopo.

## Prima: serve davvero un passaggio?
- `/compact`: il lavoro continua nella stessa sessione e il contesto è solo pieno. Si conserva il filo, si perdono i dettagli: va bene a metà di un compito con una direzione chiara.
- `/clear`: il compito è chiuso o cambia argomento, e il contesto già prodotto non serve. Ciò che conta è già nel repo (commit, file) o in un piano salvato.
- Passaggio di consegne: la sessione si interrompe con lavoro a metà, riprende un'altra persona, o la nuova sessione deve partire da uno stato pulito ma sapere decisioni e punti aperti.

Se `/compact` o `/clear` bastano, dillo all'utente invece di scrivere il documento.

## Raccogli prima di scrivere
Non ricostruire a memoria: controlla lo stato reale.
- `git status`, `git diff --stat`, `git log` del branch, branch e repo coinvolti;
- test o comandi eseguiti e il loro esito (rilanciali se serve saperlo con certezza);
- piani, specifiche, ticket già esistenti: si citano, non si ricopiano.

## Contenuto
Documento breve, in italiano, con queste sezioni (salta quelle vuote):
1. **Obiettivo**: cosa si vuole ottenere e per chi, in poche righe, con il perimetro e ciò che resta fuori.
2. **Stato**: fatto (con evidenza: commit, file, test), in corso (a che punto esatto, cosa manca), da fare (in ordine).
3. **Decisioni prese e perché**: scelta, alternative scartate, motivo. Sono ciò che si perde di più.
4. **File e commit rilevanti**: percorsi con una riga di spiegazione, hash dei commit, branch. Indica se ci sono modifiche non committate.
5. **Per riprendere**: i comandi esatti (checkout, build, test, avvio), l'ambiente e le variabili necessarie (solo i nomi, mai i valori).
6. **Punti aperti e rischi**: domande senza risposta, assunzioni non verificate, cose che potrebbero rompersi.
7. **Da non rifare**: tentativi falliti e strade già escluse, con il motivo.
8. **Skill e agent utili** alla prossima sessione (per esempio `debugging`, `pianificazione`, la skill del linguaggio).

Distingui sempre ciò che è accertato da ciò che è ipotesi, con l'evidenza dei fatti.

## Dati sensibili
Oscura con `<OMESSO>` password, token, chiavi, stringhe di connessione, dati personali e riferimenti interni al cliente non necessari. Indica dove si trova il valore (nome della variabile, gestore dei segreti), non il valore. Nel dubbio, oscura.

## Dove salvarlo
- Nel percorso indicato dall'utente.
- Altrimenti nello scratchpad della sessione o nella cartella temporanea del sistema, fuori dal repo.
- Mai nei repo dei clienti senza l'ok dell'utente, e mai committato senza approvazione esplicita.

Alla fine indica all'utente il percorso e, in una riga, come avviare la nuova sessione ("leggi <percorso> e riprendi dal punto 'Per riprendere'").

## Verifica
Rileggi il documento come se non conoscessi il lavoro: obiettivo e prossimo passo devono essere chiari senza altro contesto. Controlla che i percorsi e i comandi citati esistano e che non ci siano segreti (cerca token, password, chiavi). Non inventare stati che non hai verificato.
