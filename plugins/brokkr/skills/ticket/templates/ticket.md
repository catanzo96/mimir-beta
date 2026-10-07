# <Titolo che dice il problema, non la richiesta>

| Campo | Valore |
|---|---|
| Codice ticket | <CODICE> |
| Sistema / applicativo | <repo e componenti> |
| Infrastruttura | <DB, code, share, servizi esterni coinvolti> |
| Ambiente | <dove si manifesta> |
| Tipologia | difetto del codice / dati incoerenti / configurazione / intervento manuale / richiesta di informazioni |
| Esito | <in analisi / fix pronto / rilasciato il gg/mm/aaaa / risolto operativamente / chiuso senza intervento> |

## 0. Stato
<Dove siamo, riscritto a ogni passo: cosa è fatto, cosa manca, chi deve fare cosa.>

## 1. Richiesta e cronologia
<La segnalazione riformulata in una riga, poi come la interpretiamo. Cronologia con date.>

## 2. Causa radice
<Sintomo → causa, con il ragionamento. Distingui accertato e ipotesi.>

| Ipotesi | Verifica | Esito |
|---|---|---|

<Se la causa non è stata trovata: cosa è escluso e con quale evidenza.>

## 3. Evidenze
<Log, `file:riga` sul commit di produzione, esiti delle query con ambiente e data.>

## 4. Soluzione
<Tipo di intervento (fix / dati / configurazione / rimedio operativo) e cosa si fa. Per i dati: conteggio atteso, backup, transazione, rollback.>

## 5. Verifica PRIMA/DOPO
| Controllo | Prima | Dopo |
|---|---|---|

## 6. Perché NON si fa <alternativa>
<Le alternative scartate, e perché.>

## 7. Raccomandazioni e cosa resta
<Attività a carico del cliente, rischi residui, fix pronti e non rilasciati, difetti correlati fuori perimetro (anche nel registro del debito). Osservabilità aggiunta o da aggiungere per riconoscere il problema se si ripresenta.>

## 8. Vincoli da non violare
<Comportamenti che questo ticket ha rivelato e che una modifica o una reimplementazione futura deve rispettare.>

## 9. Query di riferimento
```sql
-- diagnosi e verifica, in sola lettura, con l'ambiente
```

## Riferimenti
<Commit, PR, ticket collegati, documenti.>
