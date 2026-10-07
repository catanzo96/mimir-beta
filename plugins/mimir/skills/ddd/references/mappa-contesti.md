# Mappa dei contesti

Leggi questo file quando devi decidere come due contesti (moduli o servizi) si parlano, o documentare i confini esistenti.

## La mappa
Un diagramma o un elenco breve: i contesti, e per ogni coppia che comunica la relazione e la direzione. Serve a vedere dove un cambiamento si propaga e dove c'è dipendenza tra team. Mettila nei documenti del progetto solo se richiesto.

## Relazioni
- **Shared kernel**: due contesti condividono una piccola parte di modello e di codice, modificabile solo di comune accordo. Costa coordinamento a ogni cambio: tienilo minuscolo e coperto da test condivisi. Se cresce, è un contesto nascosto.
- **Customer/supplier**: a monte (supplier) fornisce, a valle (customer) consuma, e il valle può far pesare le proprie esigenze nella pianificazione del monte. Funziona se i team parlano; i contratti si concordano e si testano (contract test).
- **Conformist**: il valle adotta il modello del monte così com'è, perché non ha potere di negoziare (es. un sistema esterno grande). Va bene se il modello del monte è accettabile; altrimenti serve un anticorruption layer.
- **Anticorruption layer (ACL)**: il valle traduce il modello del monte nel proprio, in un adapter dedicato. Protegge il dominio da modelli esterni, legacy o instabili. Regole pratiche:
  - sta nel contesto che consuma, come adapter di una porta outbound (vedi `architettura-esagonale`);
  - traduce anche gli errori e i valori speciali, non solo i campi;
  - ha test con risposte reali (anche registrate) del sistema esterno;
  - non è necessario se i due modelli coincidono: non crearlo per abitudine.
- **Open host service / published language**: il monte espone un'interfaccia stabile e documentata per molti consumatori, con un formato condiviso e versionato (vedi `sistemi-distribuiti`, contratti).
- **Partnership**: due team evolvono insieme e si coordinano a ogni rilascio. Sostenibile solo tra team vicini.
- **Separate ways**: nessuna integrazione, perché il costo supera il beneficio.

## Scegliere
- Sistema legacy o di terzi con modello scomodo: ACL.
- Consumatori molteplici e anonimi: open host con linguaggio pubblicato e versionato.
- Stesso team, stesso ritmo di rilascio: shared kernel minimo o un unico contesto; non spezzare per principio.
- Se non sai quale relazione c'è tra due contesti, chiedi: è un dato organizzativo, non si deduce dal codice.

## Segnali di confini sbagliati
- Cambi che toccano sempre due contesti insieme.
- Join o accessi diretti alle tabelle di un altro contesto.
- Lo stesso concetto modificato da più contesti senza un proprietario chiaro.
- Un contesto che conosce gli stati interni di un altro (`if (ordine.stato == 7)`).
