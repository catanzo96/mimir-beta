# <Sistema>: <cosa è successo o cosa si fa>

| Campo | Valore |
|---|---|
| Tipo | incidente / manutenzione programmata / modifica di configurazione / rinnovo (certificati, chiavi) |
| Data | gg/mm/aaaa, hh:mm-hh:mm |
| Sintomo | <cosa si osservava, oppure il motivo dell'intervento> |
| Sistema | <componenti> |
| Host / ambiente | <…> |
| Esito | <risolto / mitigato / annullato con rollback / in corso> |

## 0. Se hai fretta
<Se si ripresenta: i passi essenziali, oppure il link al runbook.>

## 1. Contesto
<Cosa si è visto, da quando, chi l'ha segnalato, impatto sugli utenti.>

## 2. Percorso d'indagine
| Ipotesi | Verifica | Esito |
|---|---|---|

## 3. Stato prima e dopo
| Elemento | Prima | Dopo |
|---|---|---|
| Versione / configurazione | | |
| Processi e servizi | | |
| Spazio, connessioni, code | | |
| Errori nei log | | |

## 4. Procedura
| # | Passo | Comando | Esito atteso | Esito reale |
|---|---|---|---|---|
| 1 | Backup | `cp … …bak-aaaammgg` | copia presente | |
| 2 | Modifica | | | |
| 3 | Verifica | | | |

## 5. Verifica finale
<La prova end-to-end che il problema è risolto (non solo "servizio attivo"), con l'evidenza. Se la causa non è stata trovata: cosa è escluso e quale osservabilità si aggiunge.>

## 6. Rollback
<La procedura inversa, passo per passo. Scritta prima dell'intervento.>

## 7. Proposte (non applicate)

## 8. Cronologia
| Ora | Evento |
|---|---|

## Note
