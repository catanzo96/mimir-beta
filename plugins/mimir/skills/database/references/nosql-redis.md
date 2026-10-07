# NoSQL e Redis: quando scegliere e trappole

Un database non relazionale si sceglie per un requisito che il relazionale non soddisfa in modo misurabile, non per moda. Il costo: niente join né vincoli, transazioni limitate, meno strumenti di analisi e competenze da costruire.

## Quando sceglierli
| Tipo | Quando | Trappole principali |
|---|---|---|
| Documentale (MongoDB e simili) | Documenti con struttura variabile, letti e scritti per intero, aggregato unico per accesso | Duplicazione dei dati e allineamento a carico tuo; schema "libero" che diventa caos senza validazione; join e transazioni multi-documento costosi o limitati; documenti che crescono senza limite |
| Chiave-valore / wide column (DynamoDB, Cassandra) | Volumi molto grandi, accessi noti in anticipo per chiave | Il modello si progetta sulle query: una query non prevista richiede una nuova tabella o scansione; chiavi di partizione sbilanciate (hot partition); consistenza finale |
| Colonnare analitico (ClickHouse e simili) | Aggregazioni su miliardi di righe, dati quasi immutabili, inserimenti in blocco | Pessimo per aggiornamenti puntuali e letture di singole righe; inserimenti piccoli e frequenti; modifiche e cancellazioni costose |
| Ricerca (Elasticsearch, OpenSearch) | Ricerca testuale, filtri a faccette | Non è la fonte di verità: si riempie dal DB e va riallineato; consistenza non immediata |
| Grafo | Relazioni profonde e variabili (percorsi, raccomandazioni) | Poche squadre ne hanno bisogno davvero: una ricorsione SQL spesso basta |

Prima di scegliere: il relazionale con indici, JSON/JSONB per la parte flessibile e viste materializzate copre molti casi.

## Redis
Usalo per cache, sessioni, contatori, rate limit, code leggere, lock distribuiti con scadenza.

- **Redis non è la fonte di verità** salvo scelta consapevole di persistenza (AOF/RDB) e alta affidabilità: tutto ciò che si perde con un riavvio deve essere ricostruibile.
- **Ogni chiave ha una scadenza (TTL)** salvo motivo contrario; senza, la memoria cresce fino a politiche di eviction che cancellano ciò che non vuoi. Imposta `maxmemory` e una policy esplicita.
- **Nomi di chiave** con prefisso per dominio (`app:ordine:123`), mai input utente non validato dentro il nome.
- **`KEYS *` e comandi O(N)** su grandi dataset bloccano il server (è single-thread per i comandi): usa `SCAN` con cursore. Occhio anche a `HGETALL`, `SMEMBERS` e `LRANGE` su strutture enormi (chiavi "grosse").
- **Cache-aside**: leggi la cache, se manca leggi il DB e scrivi la cache; alla modifica invalida o aggiorna. Trappole: **stampede** (molte richieste insieme su una chiave scaduta: lock breve o TTL con jitter), dati vecchi dopo scritture concorrenti, cache di risultati "non trovato" senza TTL breve.
- **Lock distribuiti**: `SET chiave valore NX PX ms` con valore univoco e rilascio solo se il valore corrisponde. Dà una garanzia debole: per correttezza forte serve un fencing token o il vincolo nel DB. Non è un sostituto di un vincolo `UNIQUE`.
- **Sicurezza**: mai esposto su rete pubblica, autenticazione e TLS attivi, comandi pericolosi (`FLUSHALL`, `CONFIG`) limitati da ACL. Mai segreti o dati personali in chiaro nelle chiavi o nei valori senza una ragione.
- **Transazioni**: `MULTI/EXEC` non fa rollback degli errori di un comando; per atomicità su più chiavi usa script Lua o funzioni, e in cluster le chiavi coinvolte devono stare nello stesso slot.
- **Code e stream**: per messaggi che non puoi perdere valuta un broker dedicato; le liste semplici perdono i messaggi se il consumatore cade a metà.

## Verifica
Misura con dati e carico realistici prima di adottare. Documenta dove sta la fonte di verità e come si ricostruisce il resto.
