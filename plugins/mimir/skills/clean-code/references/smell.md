# Segnali di design (smell)

Sono **segnali da valutare, non violazioni**. In review si riportano come giudizio motivato ("possibile…, perché…"), mai come errore. Se il progetto ha una convenzione diversa, prevale. Nel codice legacy si segnalano, non si correggono dentro un fix.

| Segnale | Come si riconosce | Direzione possibile |
|---|---|---|
| Nome misterioso | Serve leggere il corpo per capire cosa fa | Rinominare (vedi `naming.md`) |
| Gruppo di dati ricorrente | Gli stessi 3-4 parametri o campi viaggiano sempre insieme | Un tipo che li raccoglie |
| Ossessione per i primitivi | Stringhe e numeri per concetti con regole (codici, importi, intervalli) | Value object (vedi `oop.md`) |
| Switch ripetuti | Lo stesso switch su tipo o stato in più punti | Polimorfismo o una mappa unica |
| Modifica a pioggia | Un cambiamento logico obbliga a toccare molti file diversi | Raccogliere la responsabilità in un punto |
| Cambiamento divergente | La stessa classe cambia per motivi non collegati | Separare le responsabilità |
| Generalità speculativa | Parametri, hook, astrazioni o interfacce "per il futuro", senza un secondo uso reale | Togliere (YAGNI) |
| Intermediario | Una classe o un metodo che si limita a inoltrare le chiamate | Chiamare direttamente il destinatario |
| Catena di messaggi | `a.getB().getC().getD()` | Tell, Don't Ask (vedi `oop.md`) |
| Eredità rifiutata | Una sottoclasse ignora o svuota metodi del padre | Composizione invece di ereditarietà |
| Commento deodorante | Un commento spiega un blocco confuso invece di renderlo chiaro | Estrarre un metodo con un nome |

## Test di eliminazione
Per capire se un modulo, un livello o un'interfaccia servono: immagina di cancellarli e di far chiamare direttamente il destinatario.
- Se la complessità sparisce, era un passaggio inutile.
- Se la complessità si sparge in tutti i chiamanti, il modulo la stava contenendo: è utile.

Un'interfaccia con una sola implementazione e nessun secondo uso previsto è un confine ipotetico, non reale.
