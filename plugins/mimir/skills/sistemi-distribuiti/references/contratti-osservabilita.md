# Contratti, versionamento, osservabilità

Leggi questo file quando definisci o cambi un'API o un evento tra servizi, o quando devi poter seguire una richiesta su più servizi.

## Contract-first
- Scrivi prima il contratto (OpenAPI, AsyncAPI, schema Avro/JSON Schema/Protobuf, secondo ciò che usa il progetto) e poi l'implementazione; chi consuma può lavorare sul contratto prima che il servizio esista.
- Il contratto è la fonte: codice e documentazione se ne derivano o si verificano contro di esso, non viceversa.
- Test di contratto (es. consumer-driven) tra produttore e consumatore, se il progetto li adotta: rompono la build quando un cambio non è compatibile.

## Compatibilità
- Compatibili: aggiungere un campo opzionale, un nuovo tipo di evento, un nuovo endpoint.
- Incompatibili: rimuovere o rinominare un campo, cambiarne il tipo o il significato, rendere obbligatorio un campo nuovo, restringere i valori ammessi.
- Regola del consumatore: ignora i campi sconosciuti, non dare significato a valori non previsti di un enumerato (gestiscili con un caso di default).
- Per un cambio incompatibile: pubblica la nuova versione accanto alla vecchia, migra i consumatori, ritira la vecchia con una data comunicata. Per gli eventi: nuovo tipo o nuova versione dello schema, e per un periodo pubblica entrambe.
- Gli eventi già in coda o archiviati restano nella vecchia forma: il consumatore deve leggerla finché ne esistono. Con event sourcing questo vale per sempre.
- Versione nel messaggio (campo o header) o nel nome del tipo, mai dedotta dalla forma del payload.
- Eventi di integrazione separati dagli eventi interni del dominio (`ddd`): il contratto pubblico cambia più lentamente del modello.

## Osservabilità
- **Trace id** generato al bordo (primo servizio, gateway) e propagato in ogni chiamata (header, es. W3C `traceparent`) e in ogni messaggio (header o metadato). Un messaggio prodotto in una richiesta porta il trace id della richiesta.
- Il trace id compare in **ogni riga di log** (tramite il contesto di log del framework, MDC o equivalente) e nelle risposte d'errore verso il cliente, perché sia citabile in un'assistenza.
- Distingui trace id (una richiesta end-to-end) da id di business/correlazione (un ordine, una saga): servono entrambi e si loggano entrambi.
- Metriche per dipendenza: latenza, tasso d'errore, saturazione; per le code: profondità, età del messaggio più vecchio, dead letter.
- Health check che distinguono "vivo" da "pronto" (dettagli in `container/references/kubernetes.md`).
- Usa gli strumenti di tracing già adottati (es. OpenTelemetry, Micrometer Tracing); non aggiungerne senza ok.
- Mai loggare payload con dati personali o segreti: logga id e tipi, non contenuti.
