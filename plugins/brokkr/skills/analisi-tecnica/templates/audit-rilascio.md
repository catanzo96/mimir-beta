# Prontezza al rilascio: <evolutiva o sistema>

**Aggiornato**: gg/mm/aaaa · **Rilascio previsto**: <data o finestra> · **Ambiente di destinazione**: <…>

**Verificato su**

| Repository | Commit o tag | Percorsi | Note |
|---|---|---|---|

## Esito
**Go** | **No-Go** | **Go con riserva**, in una riga con il motivo principale.

| Bloccanti (impediscono il go) | Evidenza |
|---|---|

| Riserve (si rilascia, ma vanno gestite) | Evidenza | Chi e quando |
|---|---|---|

## Cosa entra in produzione
<Componenti, commit o tag, diff rispetto alla versione in esercizio. Funzioni nuove e comportamenti cambiati.>

## Controlli
Per ogni area: cosa si è controllato, l'esito e l'evidenza. "Non verificato" è un esito ammesso, se dichiarato.

| Area | Domanda | Esito | Evidenza |
|---|---|---|---|
| Accessi | Le funzioni nuove controllano ruolo e proprietà della risorsa lato server? | | |
| Dati | Migrazioni provate su volumi realistici, reversibili o dichiarate irreversibili? Dati esistenti compatibili? | | |
| Integrazioni | Contratti verso altri sistemi invariati o concordati? Timeout e gestione degli errori sulle chiamate esterne? | | |
| Job e code | Lavori schedulati e consumatori tollerano la nuova versione e un riavvio a metà? Le ripetizioni sono idempotenti? | | |
| Configurazione | Proprietà e segreti nuovi presenti nell'ambiente di destinazione? | | |
| Test e build | Build e test verdi sulla versione da rilasciare? Collaudo concluso? | | |
| Osservabilità | Log ed errori permettono di capire se qualcosa va storto dopo il rilascio? | | |
| Rollback | Procedura scritta, versione precedente disponibile, segnali di rollback definiti? | | |

## Non verificato
<Cosa non si è potuto controllare e perché.>
