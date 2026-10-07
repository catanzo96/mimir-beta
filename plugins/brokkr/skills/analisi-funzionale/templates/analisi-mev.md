# <CODICE>: <evolutiva in una riga>

| Campo | Valore |
|---|---|
| Codice | <codice MEV o ticket> |
| Origine | <ticket o richiesta da cui nasce, data> |
| Richiedente | <ruolo, non nome> |
| Rilascio previsto | <finestra o lotto> |
| Componenti | <repo e moduli toccati> |

## 0. Stato
<Dove siamo, in una-tre righe, riscritto a ogni aggiornamento.>

## 1. Perché è un'evolutiva e non un fix
<Il comportamento attuale è quello previsto? Cosa cambia nel contratto con l'utente?>

## 2. Contesto
<Il problema in una riga, poi il contesto funzionale. Rimanda alla scheda del modulo, se esiste.>

## 3. Requisiti
| ID | Requisito | Regola o fonte | Priorità (must/should/could) |
|---|---|---|---|
| RF-01 | | | |

## 4. Perimetro a lotti
| Lotto | Contenuto | Requisiti | Stato |
|---|---|---|---|

## 5. Fuori perimetro
<Cosa non si fa, detto esplicitamente, e perché.>

## 6. Impatti
| Area | Impatto |
|---|---|
| Ruoli e permessi | |
| Stati e transizioni | |
| Dati e modello | |
| Flussi esterni | |
| Documenti e comunicazioni | |

## 7. Criteri di accettazione
Per ogni requisito, almeno un criterio verificabile. Dove c'è un rischio di effetti collaterali, anche cosa **non** deve succedere.
| Requisito | Dato | Quando | Allora | Non deve | Verifica |
|---|---|---|---|---|---|
| RF-01 | <situazione iniziale> | <azione> | <esito osservabile> | <effetto vietato, es. altri stati invariati> | test automatico / caso di collaudo / query |

## 8. Decisioni da chiudere prima del codice
| # | Decisione | Opzioni | Chi decide | Stato |
|---|---|---|---|---|

## Riferimenti
