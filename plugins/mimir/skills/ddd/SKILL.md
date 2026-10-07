---
name: ddd
description: Domain-Driven Design pragmatico. Usala quando modelli un dominio, definisci aggregati o bounded context, o il progetto ha package come domain o aggregate.
---

# Domain-Driven Design

Si applica insieme a `clean-code` e ad `architettura-esagonale` (che copre layer, porte e mapping: qui non si ripete). Prevalgono le convenzioni del progetto: se usa già un vocabolario o una struttura di dominio, estendili.

## Quando NON usarlo
DDD costa: modellazione, confronto con gli esperti, mapping. Non conviene se:
- il dominio è CRUD: poche regole, validazioni di campo, nessuna transizione di stato significativa;
- la complessità è tutta tecnica (integrazione, performance) e non nelle regole di business;
- non c'è accesso a persone che conoscano il dominio.

In questi casi servono entity semplici e un service sottile. Proponi DDD solo dove le regole sono ricche e cambiano spesso (il "core domain"); per i sottodomini di supporto o generici scegli la soluzione più economica, anche comprata o configurata.

## Linguaggio comune
- Il vocabolario del dominio sta nel codice: classi, metodi ed eventi hanno i nomi che usano gli esperti, non sinonimi tecnici (`Ordine.annulla()`, non `Order.setStatus(3)`).
- Prima di modellare, ricava i termini da analisi, ticket, codice e conversazioni. Se esiste un glossario del progetto, aggiornalo; altrimenti proponine uno breve (termine, significato, contesto in cui vale), senza crearlo se non richiesto.
- **Segnala i termini in conflitto**: lo stesso nome con significati diversi ("cliente" per vendite e per fatturazione) o nomi diversi per la stessa cosa. Non sceglierne uno in silenzio: è quasi sempre il segnale di un confine tra contesti (vedi sotto) e va chiesto a chi conosce il dominio.
- Un termine tecnico (`Manager`, `Handler`, `Data`) nel dominio è un campanello: manca un concetto.

## Bounded context
- Un contesto è il perimetro dentro cui un modello e il suo linguaggio hanno un significato unico. Un modello unico per tutta l'azienda non funziona: meglio più modelli piccoli e coerenti.
- Si individuano da: conflitti di linguaggio, team diversi, ritmi di cambiamento diversi, regole che non si parlano. Non da tabelle o da schermate.
- Ogni contesto possiede i suoi dati e il suo modello. Un concetto condiviso (es. il cliente) ha una rappresentazione per contesto, con riferimenti per identificativo.
- Dentro un monolite i contesti sono moduli con un'interfaccia pubblica esplicita e senza accesso alle tabelle altrui. Se diventeranno servizi è una decisione a parte: vedi `sistemi-distribuiti`.
- Relazioni tra contesti e mappa: `references/mappa-contesti.md`.

## Mattoni del modello
**Entity**: ha identità e ciclo di vita; due entity sono uguali se hanno lo stesso id, anche con attributi diversi.
**Value object**: definito dai valori, immutabile, confrontato per valore, valida se stesso alla creazione. Usalo per ciò che ha regole proprie (`Importo`, `Iban`, `Periodo`) invece di `String` e `BigDecimal` sparsi: elimina la primitive obsession e sposta le validazioni in un solo punto.
- Nel dubbio tra i due, parti da value object: è più semplice da ragionare e da testare.
- Un `record` (Java) o un tipo readonly (TypeScript) è il veicolo naturale, ma l'immutabilità vale più dello strumento.

**Servizio di dominio**: logica del dominio che non appartiene a una sola entity o a un solo value object (es. un calcolo che coinvolge più aggregati). È senza stato e usa il linguaggio comune. Se la logica dipende solo dai dati di un'entity, resta nell'entity: un servizio di dominio nato per comodità svuota il modello (vedi `architettura-esagonale`, dominio ricco).
**Servizio applicativo**: orchestra (carica, chiama il dominio, salva, pubblica). Non contiene regole di business.

## Aggregati
Un aggregato è un gruppo di oggetti trattato come unità di consistenza, con una radice (aggregate root) che è l'unico punto d'accesso.
- **Il confine segue le invarianti**: dentro l'aggregato le regole sono sempre vere dopo ogni operazione. Ciò che non deve essere consistente nello stesso istante sta fuori.
- **Piccoli**: parti da un'entity sola con i suoi value object e aggiungi altre entity solo se un'invariante lo impone. Aggregati grandi causano conflitti di concorrenza e caricamenti pesanti.
- **Una transazione modifica un solo aggregato.** Se un caso d'uso ne tocca due, la consistenza tra i due è eventuale: usa eventi di dominio (`references/eventi-repository.md`, e `sistemi-distribuiti` per i casi tra servizi).
- **Riferimenti tra aggregati per id**, non per oggetto: niente navigazione `ordine.getCliente().getIndirizzi()`. Si carica l'altro aggregato tramite il suo repository, nel servizio applicativo.
- Le modifiche passano dalla radice, con metodi che esprimono l'intenzione e proteggono le invarianti. Niente setter pubblici né collezioni interne esposte modificabili (restituisci copie o viste immutabili).
- La concorrenza si gestisce sull'aggregato (versione ottimistica), non con lock sui singoli oggetti interni.
- Trappola frequente: l'aggregato che modella la "relazione uno-a-molti" del database e non una regola. Chiediti quale invariante giustifica di tenere insieme i figli; se non c'è, sono aggregati separati.

## Eventi di dominio e repository
Un evento di dominio è un fatto avvenuto, nel passato e nel linguaggio comune (`OrdineConfermato`). Un repository è la collezione di un aggregato, con un'interfaccia nel dominio. Regole di dettaglio, pubblicazione degli eventi e query di lettura: `references/eventi-repository.md`. Leggilo quando aggiungi un evento o un repository.

## Come lavorare
1. Parti dalle regole e dagli scenari ("quando X, allora Y"), non dalle tabelle.
2. Nomina i concetti con gli esperti; annota i dubbi sul linguaggio invece di decidere da solo.
3. Disegna i confini (contesto, aggregato) prima delle classi e motiva ogni scelta con un'invariante o un conflitto di linguaggio.
4. Testa le regole sul modello con unit test puri, senza framework e senza database (vedi `clean-code`, test).
5. Su codice esistente non riscrivere il modello per renderlo "più DDD": segnala le incongruenze e proponi passi piccoli, come commit `refactor` separati.

## Verifica
- Le regole di business sono testate nel dominio, senza mock di infrastruttura.
- Il dominio non importa framework, ORM o trasporto (controllalo con gli strumenti già presenti, es. ArchUnit, dependency-cruiser, o con una ricerca degli import).
- Nessun aggregato ha riferimenti a oggetti di altri aggregati; nessuna transazione ne modifica due.
- Test, linter e build del progetto puliti: i comandi sono quelli già configurati (es. `mvn verify`, `npm test`, `npm run lint`).
