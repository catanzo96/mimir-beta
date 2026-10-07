---
name: design-api
description: "Progettare o rivedere API HTTP/REST: errori, paginazione, versioning, contratti. Usala quando definisci endpoint, o in progetti con openapi.yaml o controller REST."
---

# Design delle API

Si applica insieme a `clean-code` (e `sicurezza.md` al suo interno). Per Spring rimanda a `spring-boot`, per la persistenza a `database`. Prevalgono le convenzioni e il contratto già presenti nel progetto: un'API esistente si estende con il suo stile, non si "sistema".

## Prima di tutto: chi sono i consumatori
Un'API con un solo consumatore nel tuo stesso repo si cambia con un commit. Un'API con consumatori che non controlli (altri team, mobile già rilasciato, clienti) è un contratto: ogni modifica va valutata per compatibilità. Chiediti sempre chi la chiama e se puoi rilasciare insieme a lui.

## Risorse e URL
- Sostantivi al plurale per le collezioni (`/ordini/{id}/righe`), niente verbi nel percorso. Le azioni che non sono CRUD si modellano come sotto-risorsa (`POST /ordini/{id}/annullamento`) invece di inventare verbi ovunque.
- Annidamento al massimo di un livello: oltre, l'identificativo della risorsa figlia deve bastare da solo.
- Identificatori opachi e stabili (UUID, ULID), non contatori che rivelano volumi o si indovinano (verifica sempre l'autorizzazione sull'oggetto, non solo sul tipo).
- Nomi dei campi coerenti in tutta l'API (una sola convenzione di case), enumerazioni come stringhe stabili, mai numeri d'ordine.

## Metodi, idempotenza, status code
| Metodo | Sicuro | Idempotente | Note |
|---|---|---|---|
| GET | sì | sì | Mai effetti collaterali, anche se "innocui" |
| PUT | no | sì | Sostituisce la risorsa intera |
| PATCH | no | dipende | Specifica il formato (merge patch o JSON Patch) e non assumere l'idempotenza |
| DELETE | no | sì | Il secondo `DELETE` può rispondere `404` o `204`: scegli e documenta |
| POST | no | no | Crea o esegue un'azione: vedi chiavi di idempotenza |

- `201` + `Location` per le creazioni, `204` senza body, `202` per lavori asincroni con una risorsa di stato da interrogare.
- `400` richiesta malformata, `422` valida nella forma ma non nel significato, `409` conflitto di stato, `404` non trovata, `401` non autenticato, `403` autenticato ma non autorizzato, `429` rate limit.
- Non rispondere `200` con `{"errore": ...}` nel body: i client, le cache e le metriche leggono lo status.
- Se per non rivelare l'esistenza di una risorsa usi `404` al posto di `403`, fallo ovunque e in modo consistente.

## Errori
- Formato unico per tutti gli errori: **Problem Details** (RFC 9457, che sostituisce la 7807), `Content-Type: application/problem+json`, con `type`, `title`, `status`, `detail`, `instance`.
- Aggiungi estensioni per ciò che il client deve gestire: un `codice` stabile leggibile dalle macchine e, per la validazione, l'elenco `errori` con campo e motivo.
- Il `detail` è per le persone e può cambiare; il client decide sul `type` o sul `codice`.
- Mai stack trace, query o nomi di classi nella risposta. Il dettaglio va nei log, con un identificativo di correlazione che compare anche nella risposta.

## Collezioni: paginazione, filtri, ordinamento
- Ogni collezione che può crescere è paginata dal primo giorno: aggiungere la paginazione dopo è un cambio incompatibile.
- **Offset** (`page`/`size`): semplice, permette di saltare a una pagina, ma costa O(offset) sul DB e duplica o perde elementi se i dati cambiano durante lo scorrimento. Va bene per backoffice con dati piccoli.
- **Cursore** (`after=<token opaco>`): costante, stabile sui dati che cambiano, niente salto alla pagina N. Ordinamento deterministico con un campo univoco come spareggio. È la scelta per feed, esportazioni e tabelle grandi (`database`, paginazione per chiave).
- Fissa una dimensione massima di pagina lato server. Restituisci il cursore successivo o i link, non lasciare al client il calcolo.
- Filtri come parametri di query con nomi dei campi della risorsa; ordinamento su una lista bianca di campi (`sort=-creatoIl`), mai nomi di colonna passati al DB.
- Non offrire un totale esatto su tabelle grandi se non serve: il `count(*)` è spesso la parte più costosa.

## Versioning e compatibilità
- **Compatibile** (non serve una nuova versione): nuovo campo opzionale in risposta, nuovo endpoint, nuovo parametro opzionale, nuovo valore di enum solo se i client sono tolleranti.
- **Rompe un client**: rimuovere o rinominare un campo, cambiarne tipo, formato o semantica (anche solo l'unità o l'arrotondamento), rendere obbligatorio un parametro, restringere la validazione, cambiare uno status code o il formato degli errori, aggiungere un valore a un enum che i client trattano come chiuso.
- Regola per i client: ignorano i campi sconosciuti. Scrivila nel contratto e rispettala nei tuoi.
- Strategie: versione nel percorso (`/v2/`, la più semplice da instradare e da cacheare), header o media type (più puro, più difficile da usare). Segui quella del progetto.
- Per ritirare qualcosa: marca `deprecated` nel contratto, misura chi la usa ancora (log o metriche per client), annuncia una data, poi rimuovi. Gli header `Deprecation` e `Sunset` aiutano i consumatori automatici.

## Contratti OpenAPI
- Con più consumatori o team: **contract-first**. Il file OpenAPI è l'artefatto condiviso e rivisto per primo; server e client si generano o si verificano contro di esso. Con un consumatore solo e lo stesso team va bene code-first, purché il contratto sia comunque pubblicato.
- Il contratto vive nel repo, è rivisto nelle PR come il codice. Un test di contratto o un controllo di compatibilità in pipeline (`ci-cd`) intercetta le modifiche incompatibili prima del rilascio.
- Descrivi anche gli errori e le risposte non-200, con esempi. Lo schema con `additionalProperties` e la possibilità di `null` esplicita (`nullable: true` in OpenAPI 3.0, `type: [string, "null"]` in 3.1) evita ambiguità tra "assente" e "null".
- Un codice generato non si modifica a mano: se non basta, si cambia il template o il contratto.

## Scritture sicure
- **Chiavi di idempotenza** per i `POST` che creano o che pagano: il client invia un header (`Idempotency-Key`, standard ancora in bozza IETF ma di fatto diffuso) con un valore unico per tentativo logico. Il server salva chiave, impronta della richiesta e risposta; un ripetuto restituisce la stessa risposta, la stessa chiave con body diverso è un errore `422`. La chiave si registra nella stessa transazione dell'effetto.
- **Concorrenza ottimistica**: `ETag` sulla risorsa (versione o hash) e `If-Match` sulle modifiche; versione non corrispondente: `412 Precondition Failed` (o `409` se il progetto lo usa). Previene gli aggiornamenti persi, che con `PUT` sono la norma.
- Per le operazioni lunghe: `202` e una risorsa `/operazioni/{id}` con stato, non una richiesta aperta per minuti.

## Sicurezza
- Autenticazione sul gateway o in un filtro unico; **autorizzazione sempre nel servizio, per oggetto** (il difetto più frequente è l'accesso a risorse altrui cambiando un id). Negare di default.
- Rate limit per chiave o utente con `429` e `Retry-After`; limiti su dimensione del body e profondità del JSON.
- Mai segreti o dati personali negli URL (finiscono nei log e nelle cache): vanno in header o body.
- Risposte minime: non esporre le entity del DB, i campi interni o quelli di cui il chiamante non ha diritto (mass assignment in ingresso: lista bianca dei campi scrivibili).
- CORS con origini esplicite. Dettagli generali in `clean-code/references/sicurezza.md`.

## Dati nel JSON
- **Date e ore**: ISO 8601. Un istante in UTC con `Z` (`2026-03-01T10:15:00Z`); una data di calendario senza ora (`2026-03-01`) quando l'ora non esiste (compleanno, scadenza). Non usare un istante per rappresentare un giorno: il fuso lo sposta di un giorno. Per un evento locale futuro (appuntamento) salva ora locale e nome del fuso (`Europe/Rome`), non l'offset.
- **Denaro**: importo come stringa decimale (`"19.90"`) o intero in unità minime (`1990`) con la valuta (`EUR`) accanto. Mai `float`: il JSON numerico viene letto come double da molti client.
- **Interi grandi** (oltre 2^53) come stringa: JavaScript li altera.
- Booleani e assenza: distingui campo assente, `null` e valore vuoto solo se il contratto lo richiede (soprattutto in `PATCH`).

## Webhook
- Il ricevente risponde subito `2xx` e lavora in modo asincrono; il mittente ritenta con backoff, quindi gli eventi arrivano **almeno una volta e fuori ordine**: ogni evento ha un `id` per la deduplicazione e un timestamp o numero di sequenza.
- Firma HMAC del body con un segreto per sottoscrittore e timestamp nella firma contro i replay; il ricevente verifica prima di fare altro e confronta in tempo costante.
- Payload piccolo con l'identificativo della risorsa; il dettaglio si rilegge via API se serve.

## Quando non REST
- **gRPC**: comunicazione interna tra servizi, bassa latenza, streaming, contratti protobuf rigidi. Poco adatto ai browser e a chi non controlli.
- **GraphQL**: molti client diversi con esigenze di dati molto variabili (mobile, dashboard). Costa in caching, autorizzazione per campo e controllo della complessità delle query.
- Nel dubbio resta REST: strumenti, cache e competenze sono ovunque.

## Verifica
Con gli strumenti già nel progetto:
- valida il contratto (linter OpenAPI come Spectral o quello configurato) e, se c'è, il controllo di compatibilità contro la versione rilasciata;
- lancia i test dell'API e del contratto (`./mvnw test`, offline nella sandbox se la cache locale c'è; `npm test`, a seconda dello stack);
- prova a mano gli status code e i casi di errore di ogni endpoint toccato (`curl -i`) e leggi gli header di risposta;
- cerca nel diff campi rimossi, rinominati o resi obbligatori e dichiaralo come rottura nel resoconto.
