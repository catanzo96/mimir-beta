# Eventi di dominio e repository

Leggi questo file quando aggiungi un evento di dominio, un repository o una query di lettura.

## Eventi di dominio
- Nome al passato nel linguaggio comune: `PagamentoRicevuto`, non `PagamentoEvent` né `AggiornaOrdine`.
- Immutabile; porta l'id dell'aggregato, l'istante e i dati che servono ai consumatori, non l'aggregato intero.
- Lo genera l'aggregato quando una regola si compie; lo raccoglie chi salva e lo pubblica solo dopo il commit. Pubblicarlo prima del commit rischia di annunciare un fatto poi annullato.
- I consumatori nello stesso contesto reagiscono in modo asincrono rispetto alla transazione dell'aggregato; ognuno modifica un solo aggregato in una propria transazione.
- Se l'evento deve arrivare davvero (altri servizi, code), la pubblicazione va resa affidabile con outbox: `sistemi-distribuiti`. In un unico processo bastano gli eventi applicativi del framework agganciati al commit (es. `@TransactionalEventListener(AFTER_COMMIT)` in Spring).
- Evento di dominio (interno al contesto, può cambiare) e evento di integrazione (contratto verso altri contesti, versionato) sono cose diverse: non esporre il primo come secondo.
- Non usare un evento per nascondere una chiamata di cui serve il risultato: se il chiamante ne ha bisogno subito, è una chiamata.

## Repository
- Uno per aggregato (radice), con l'interfaccia nel dominio e l'implementazione nell'adapter di persistenza (vedi `architettura-esagonale`).
- Vocabolario di collezione: `trova(id)`, `salva(aggregato)`, `rimuovi`. Assenza esplicita (`Optional`, o un'eccezione di dominio per "deve esistere"), mai `null`.
- Carica e salva l'aggregato intero e coerente. Niente metodi che restituiscono pezzi interni o che aggiornano un campo senza passare dalla radice: aggirano le invarianti.
- Niente repository per entity interne all'aggregato.
- Un repository non contiene regole di business né esegue transazioni: le gestisce il servizio applicativo.

## Letture e report
Le query per schermate, elenchi e report non devono caricare aggregati: attraversano più aggregati e servono solo dati. Usa query dedicate (proiezioni, read model, view) che restituiscono DTO. Mantengono semplice il modello di scrittura. Se le letture diventano un modello a parte con dati replicati, è CQRS: vedi `sistemi-distribuiti` per quando conviene.

## Factory
Se la creazione di un aggregato è complessa o ha regole proprie, usa un metodo statico sulla radice o una factory di dominio. Il costruttore non deve poter produrre un oggetto invalido.
