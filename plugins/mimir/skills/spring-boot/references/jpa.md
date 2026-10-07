# JPA e database: oltre le basi

Da leggere quando una modifica tocca prestazioni del DB, volumi di dati, concorrenza sulle stesse righe o migrazioni.

## Pool di connessioni (HikariCP)
- Il pool si dimensiona sulla capacità del database e sul numero di istanze dell'applicazione, non "più grande è meglio": 10 connessioni (il default) bastano a molte applicazioni.
- `connectionTimeout` esplicito: meglio un errore rapido che richieste in coda all'infinito.
- `leakDetectionThreshold` attivo in sviluppo o collaudo per trovare connessioni non rilasciate.
- Con i virtual thread il collo di bottiglia resta il pool: migliaia di thread non danno più connessioni.

## Capire le query
- In locale, log SQL con i parametri:
  - Hibernate 6 (Boot 3+): `org.hibernate.SQL=debug`, `org.hibernate.orm.jdbc.bind=trace`;
  - Hibernate 5 (Boot 2): `org.hibernate.SQL=debug`, `org.hibernate.type.descriptor.sql.BasicBinder=trace`.
- Mai con questo livello in produzione: i parametri possono contenere dati personali.
- Per un N+1 sospetto, conta le query in un test (statistiche di Hibernate) invece di dedurlo leggendo il codice.
- Indici sulle colonne di foreign key e su quelle usate in filtri e ordinamenti frequenti. Prima di aggiungerne uno, guarda il piano di esecuzione su dati realistici: ogni indice costa in scrittura.

## Scritture in blocco
- `hibernate.jdbc.batch_size` (es. 50), con `order_inserts` e `order_updates`, per inserimenti e aggiornamenti numerosi.
- Con `GenerationType.IDENTITY` Hibernate non può raggruppare gli insert. Se il batch conta, serve `SEQUENCE` con `allocationSize` uguale all'incremento della sequenza.
- Gli update e delete JPQL in blocco scavalcano il persistence context, i listener e `@Version`: dopo, l'entity in memoria è vecchia. Pulisci il contesto o rileggi.
- Su lotti grandi, `flush()` e `clear()` periodici per non far crescere il persistence context.

## Concorrenza sui dati
- `@Version` (lock ottimistico) sulle entity modificabili da più utenti: chi salva per secondo riceve un errore invece di sovrascrivere.
- Lock pessimistico (`@Lock(PESSIMISTIC_WRITE)`) solo quando serve davvero, sempre con un timeout (`jakarta.persistence.lock.timeout`). Livelli di isolamento, deadlock e indici: `database`.

## Paginazione
- `Pageable` esegue anche una query di conteggio: su tabelle grandi può costare più della pagina. Valuta `Slice` o una query di conteggio dedicata.
- Con offset molto alti, paginazione per chiave invece di `OFFSET`: in Spring Data con una query che filtra "dopo l'ultimo valore" o con lo scrolling per chiave (`Window`, `ScrollPosition`) se la versione lo prevede. La tecnica e le differenze tra database sono in `database`.
- `JOIN FETCH` su una collection insieme alla paginazione fa paginare Hibernate in memoria (lo segnala con un warning): carica prima gli id della pagina, poi le entity con le relazioni.

## Migrazioni (Flyway, Liquibase)
- Una migrazione già applicata in un ambiente non si modifica: ogni cambiamento è una migrazione nuova. Altrimenti il checksum fallisce o gli ambienti divergono.
- Per migrazioni su dati esistenti (colonne nuove, backfill, lock, rollback) vedi la skill `rilascio`, se disponibile.
