# Rischi ed escalation

## Scala di valutazione
Tre livelli bastano; più livelli danno solo falsa precisione.

| | Probabilità | Impatto |
|---|---|---|
| Bassa | improbabile nel periodo | assorbibile nel margine, nessun effetto sul cliente |
| Media | possibile | ritarda una milestone o richiede lavoro extra rilevante |
| Alta | probabile o già con segnali | manca una data contrattuale, un costo fuori budget, danno al cliente |

Priorità = probabilità × impatto. Alta/Alta si tratta subito; Bassa/Alta si tiene d'occhio con un piano B pronto; Bassa/Bassa si registra e basta.

## Come formulare un rischio
"Se <causa incerta>, allora <effetto>". Esempio: "Se il cliente non fornisce l'ambiente di collaudo entro il 15, il collaudo slitta e la data di rilascio non regge". Una voce come "problemi di performance" non è un rischio ma un'etichetta.

## Segnali e mitigazione
- **Segnale precoce**: cosa si vede prima dell'evento (richieste che tardano, test che diventano instabili, requisiti che cambiano). Senza segnale, il rischio si scopre quando è un problema.
- **Mitigazione**: azione che cambia probabilità o impatto, con una data. "Monitorare" non è una mitigazione.
- **Piano B**: cosa si fa se accade.
- Gli stati utili: aperto, in mitigazione, accaduto (diventa problema), chiuso.

## Problemi
Per un problema servono: descrizione, impatto già in corso, azione, proprietario, data di risoluzione attesa. Se l'azione richiede altri, entra nelle decisioni richieste del report.

## Messaggio di escalation
```
Oggetto: richiesta di decisione entro <data> - <tema>

Situazione: <fatto verificato, con fonte e data>.
Impatto: <cosa succede e quando se non si interviene>.
Già tentato: <azioni fatte e risultato>.
Opzioni:
  A) <descrizione, costo/effetto>
  B) <descrizione, costo/effetto>
Raccomandazione: <opzione e motivo>.
Richiesta: <chi deve fare cosa, entro quando>.
```

## Trappole
- Registro come archivio: un registro con 40 voci non è letto da nessuno. Mantieni in evidenza i primi 5.
- Rischi senza proprietario: se sono di tutti, non sono di nessuno.
- Escalation per sfogo: se la richiesta non è precisa, non è un'escalation.
- Cambiare il semaforo in silenzio: le variazioni si dichiarano.
