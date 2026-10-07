# Tecniche per tipo di problema

Strumenti e segnali tipici per quando il metodo generale non basta. Usa quelli già presenti nel progetto; installarne di nuovi richiede l'ok dell'utente.

## Prestazioni e memoria
- **Misura prima**: un numero di partenza ripetibile (tempo, memoria, query eseguite) e lo stesso numero dopo. Senza misura non c'è miglioramento accertato.
- **Profila, non indovinare**: profiler del runtime (JFR o async-profiler per la JVM, `perf`, profiler di Node o del browser), piano di esecuzione delle query (`EXPLAIN`). Il collo di bottiglia raramente è dove lo si immagina.
- **Lentezza che cresce con i dati**: conta le query o le chiamate per richiesta (tipico N+1) e prova con 10 e 1000 elementi: la forma della curva dice se è lineare o peggio.
- **Memoria che cresce**: confronta due dump dell'heap a distanza di tempo; cerca collezioni statiche, cache senza limite, listener non rimossi, sessioni, thread locali.
- **Avvii lenti**: log di avvio con i tempi, bean o moduli caricati, chiamate di rete all'avvio.
- Dopo il fix rimisura nelle stesse condizioni e riporta prima e dopo.

## Concorrenza
- Segnali: succede solo sotto carico, cambia a ogni esecuzione, sparisce aggiungendo un log (il log cambia i tempi).
- Cerca stato mutabile condiviso (campi di singleton, statici, cache non sicure), check-then-act senza atomicità, ordine di acquisizione dei lock diverso tra percorsi, transazioni sovrapposte sugli stessi record.
- Rendi il difetto più frequente invece di aspettarlo: più thread, ritardi iniettati nei punti sospetti, ripetizione in ciclo del test (centinaia di volte).
- Per i blocchi: dump dei thread (`jstack`, `kill -3`) presi a distanza di secondi; thread nello stesso punto in entrambi i dump indicano il blocco.
- Nei test non attendere con pause fisse: attendi la condizione con un timeout.
- Il fix riduce lo stato condiviso o lo protegge a un livello solo; un `synchronized` aggiunto a caso sposta il problema.

## Rete e integrazioni
- Separa i tre soggetti: il tuo codice, il trasporto, il sistema remoto. Riproduci la chiamata fuori dal codice (`curl`, client dedicato) con lo stesso payload: se fallisce uguale, il difetto non è nel tuo codice.
- Controlla: URL e ambiente effettivi, header e content type, codifica, fuso e formato delle date, timeout, redirect, proxy, certificati e loro scadenza, risoluzione DNS, limiti di frequenza.
- Registra richiesta e risposta ai confini (metodo, URL, stato, durata, id di correlazione), mai credenziali o dati personali.
- Errori sporadici: guarda retry, connessioni riusate cadute (keep-alive), timeout più corti lato client che lato server.
- Per i test di integrazione preferisci un server simulato o container reali a mock che riproducono la tua ipotesi.

## Dati e cache
- Parti dal dato concreto: il record, il messaggio, il file che produce l'errore. Cerca valori limite (null, vuoto, spazi, codifica, date a cavallo di fusi o cambio ora, importi con arrotondamenti).
- Confronta un record corretto con uno errato campo per campo.
- Se il dato è già sbagliato nel database, cerca chi lo ha scritto e quando (colonne di audit, log, migrazioni); correggere i dati pregressi è un'attività a parte, da proporre all'utente.
- **Cache**: verifica chiave, durata e invalidazione; riproduci con cache vuota e con cache piena. Se il difetto sparisce disattivandola, la causa è nella chiave o nell'invalidazione.
- **Migrazioni e schema**: confronta lo schema reale con quello atteso dal codice; ordine e stato delle migrazioni applicate.
- Le query di verifica sono in sola lettura, con ambiente e data nel resoconto.
