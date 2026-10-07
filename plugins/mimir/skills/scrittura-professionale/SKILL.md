---
name: scrittura-professionale
description: Mail e documenti di lavoro per cliente, colleghi, direzione. Usala quando devi scrivere, rivedere o rispondere a una mail, una comunicazione al cliente, un sollecito o un documento.
when_to_use: 'Es.: "rispondi a questa mail", "scrivi al cliente che…", "rendi più chiaro questo messaggio", "devo sollecitare…".'
---

# Scrittura professionale

Si applica insieme alle regole di comunicazione di Mímir. Le convenzioni del cliente o del progetto (modelli, formule, canali) prevalgono. Per i documenti di analisi usa `analisi-funzionale` e `analisi-tecnica` (se disponibili); per il formato Word o PDF le skill dedicate.

## Regole fisse
- Italiano, salvo che il destinatario usi un'altra lingua. Le regole di `rules/communication.md` (virgolette dritte) valgono sempre.
- Niente dati personali o del cliente che non servono al destinatario.
- Non inviare mai: proponi il testo e aspetta l'ok. Una mail a un cliente è un impegno.

## Prima di scrivere
Rispondi a due domande, se non sono chiare chiedile all'utente:
1. **Chi legge** e quanto sa già (PA, collega, fornitore, direzione)?
2. **Cosa deve fare dopo** averla letta: decidere, rispondere, fornire un dato, solo sapere?

Se non sai dire cosa deve succedere dopo la lettura, il testo non è pronto da scrivere.

## Struttura
- **Oggetto** che dice il contenuto e, se serve, l'azione: "Richiesta di accesso all'ambiente di collaudo entro il 12/10", non "Aggiornamento".
- **In testa** la conclusione o la richiesta, poi il contesto minimo. Chi legge solo due righe deve capire cosa gli si chiede.
- **Una richiesta per mail**, se possibile. Con più richieste, un elenco numerato e, per ognuna, chi e entro quando.
- **Paragrafi brevi**. Elenchi per azioni e opzioni; prosa per il ragionamento.
- Date assolute ("venerdì 10/10") invece di "domani" o "la prossima settimana".
- Allegati citati nel testo, con il nome del file.

## Tono
- Cortese e diretto. Il registro segue il destinatario: più formale con PA e direzione, più asciutto con i colleghi, preciso e fermo con i fornitori.
- Via il burocratese: "si resta in attesa di cortese riscontro" diventa "Mi serve la risposta entro giovedì".
- Niente scuse a vuoto né toni accusatori: descrivi i fatti, non le persone.
- Non promettere date o esiti che non dipendono da te. Se una data è una stima, dillo.

## Cattive notizie
Nell'ordine: **fatto**, **impatto**, **cosa si sta facendo**, **cosa serve dal destinatario**. Il fatto va detto subito, senza preamboli. Non nascondere un ritardo dietro il contesto.

## Revisione
Prima di consegnare il testo all'utente:
1. Togli ciò che non cambia cosa farà il lettore.
2. Controlla nomi, ruoli, date, numeri di ticket e versioni contro le fonti (ticket, repo, thread), non a memoria.
3. Verifica che gli allegati citati esistano e siano quelli giusti.
4. Rileggi l'oggetto e le prime due righe: reggono da sole?
5. Cerca dati personali o interni non necessari al destinatario.

## Verifica
- Il testo dichiara in testa cosa si chiede o si comunica.
- Ogni fatto (data, numero, versione) ha una fonte che hai controllato; ciò che è stima è marcato come tale.
- Il registro è adatto al destinatario.
- Nulla è stato inviato: all'utente consegni il testo e segnali i punti incerti.

## Riferimenti
| File | Quando |
|---|---|
| [references/varianti.md](references/varianti.md) | Risposta a una segnalazione, richiesta di informazioni, comunicazione di un rilascio, sollecito, gestione di un reclamo |
