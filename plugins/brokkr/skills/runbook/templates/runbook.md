# <Sistema>: controllo, riavvio e diagnosi

**Stato**: bozza | verificato il gg/mm/aaaa · **Aggiornato**: gg/mm/aaaa · **Ambienti**: <preproduzione, produzione>

## 0. Se hai fretta
```bash
# 1. è vivo?            <comando>   → atteso: <…>
# 2. risponde?          <comando>   → atteso: <…>
# 3. riavvio            <comando>   → atteso: <…>
# 4. verifica           <comando>   → atteso: <…>
```

## 1. Coordinate
| Ambiente | Host / istanza | Servizio | Percorsi | Porte | Versione |
|---|---|---|---|---|---|

Accessi: <chi li ha, come si ottengono. Nessun segreto in questo documento.>

## 2. Controllo dello stato
Per ogni controllo: comando, esito atteso, cosa significa un esito diverso.

## 3. Riavvio
<Per ambiente, con le differenze (es. watchdog da fermare in produzione). Verifiche dopo il riavvio: si attende una condizione (porta in ascolto, health verde, riga nel log) con un tempo massimo, non un numero fisso di secondi.>

## 4. Diagnostica
<Quando serve capire *perché*: memoria, log, disco, rete, dipendenze esterne.>

## 5. Caso di riferimento
<Un intervento reale che ha usato questo runbook: cosa si è visto, sequenza, esito. Link al resoconto.>

## 6. Proposte (non applicate)
| # | Proposta | Beneficio | Rischio | Stato |
|---|---|---|---|---|

## 7. Riferimento rapido
<Tabella comando → a cosa serve.>

## 8. Trappole note

## 9. Documenti collegati
