# Checklist di rilascio: <cosa> in <ambiente>, gg/mm/aaaa

Si copia per ogni rilascio e si spunta durante l'esecuzione. Ogni voce ha un **esito atteso**: se l'esito reale è diverso ci si ferma, non si prosegue "per vedere".

## A. Prima
- [ ] Cosa si rilascia, per componente (commit o tag): `____`
- [ ] Stesso artefatto collaudato nell'ambiente precedente (non ricompilato)
- [ ] Backup del DB eseguito e **verificato leggibile**: file e ora `____`
- [ ] Conteggi di riferimento salvati (tabelle toccate)
- [ ] Versione attualmente in esercizio annotata, per il rollback: `____`
- [ ] Servizi in stato verde prima di iniziare
- [ ] Configurazione dell'ambiente di destinazione verificata (proprietà e variabili nuove presenti)
- [ ] Baseline salvata: errori nei log, tempi dei flussi principali, code e job: `____`
- [ ] Segnali che fanno scattare il rollback e chi decide: `____`
- [ ] Rollback riletto; utenti avvisati, se serve un fermo

## B. Deploy <componente 1: DB, modello o schema>
- [ ] Avviato alle `____`, esito `____`
- [ ] Oggetti nuovi presenti e oggetti rimossi assenti (conteggio atteso)
- [ ] Conteggi delle tabelle esistenti **invariati** rispetto ad A
- [ ] Migrazioni applicate tutte, nell'ordine atteso, nessuna in errore (tabella di storico di Flyway o Liquibase)
- [ ] Nessun errore nei log all'avvio

## C. Deploy <componente 2: backend, frontend>
- [ ] Pipeline o tag avviato: `____`, esito `____`
- [ ] Versione esposta corretta (endpoint di info, footer, hash)
- [ ] Nessun errore nei log dopo l'avvio

## D. Smoke
| Flusso | Esito atteso | Esito | OK |
|---|---|---|---|

## E. Confronto con la baseline
| Segnale | Prima | Dopo | OK |
|---|---|---|---|
| Errori nei log (nuovi tipi?) | | | |
| Tempi dei flussi principali | | | |
| Code e job | | | |

## F. Chiusura
- [ ] Osservazione a T+1 giorno: `____`
- [ ] Osservazione a T+3 giorni: `____`
- [ ] Registro dei rilasci aggiornato
- [ ] Ticket e MEV aggiornati, comunicazione inviata
