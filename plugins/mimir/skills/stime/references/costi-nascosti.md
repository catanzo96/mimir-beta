# Costi nascosti e dati storici

## Cosa si dimentica
Verifica uno per uno e, se non è incluso, scrivilo tra le esclusioni.
- Comprensione del codice e del dominio, soprattutto su sistemi datati.
- Ambiente: preparazione, dati di prova, accessi, attese per le autorizzazioni.
- Test scritti, test di regressione, correzione dei difetti trovati.
- Revisione del codice: tempo di chi rivede e giri di correzioni.
- Collaudo del cliente: assistenza, correzioni, secondi giri.
- Rilascio: pacchetto, finestra concordata, verifica post-rilascio, eventuale rollback (`rilascio`, se disponibile).
- Documentazione e passaggio di consegne.
- Riunioni, allineamenti, rendicontazione.
- Supporto dopo il rilascio.
- Ferie, formazione e interruzioni dei ticket urgenti: incidono sul calendario, non sull'impegno.

## Impegno e durata
Giorni di lavoro non sono giorni di calendario. Se una persona dedica il 60% al progetto, 10 giorni di impegno sono circa 17 di calendario, senza contare le attese. Dichiara entrambi quando comunichi una data.

## Usare i dati storici
- Cerca commit e PR di lavori simili con `git log --oneline -- <percorso>` e la durata tra primo e ultimo commit del ticket.
- Confronta con ticket chiusi simili per tipo e dimensione, non solo per titolo.
- Registra il rapporto tra stimato ed effettivo: se il team sfora di norma del 30%, l'intuito va corretto, non il margine nascosto.
- Una fonte vecchia o di un contesto diverso (altra tecnologia, altro team) va ridimensionata o scartata.
- Questi dati restano nel progetto o nel ticket, non nei file di Mímir.

## Trappole
- Ancoraggio: un numero buttato in riunione diventa il riferimento. Rispondi "ti do un intervallo dopo un'ora di analisi".
- Stima in gruppo senza confronto: se due persone divergono molto, il motivo vale più della media.
- Il lavoro si dilata fino alla scadenza: stima dall'attività, non dalla data.
- Stimare con la persona più brava e assegnare al meno esperto.
