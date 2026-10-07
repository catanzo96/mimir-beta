# Errori e logging

## Gestione degli errori
- **Gestisci ai confini del sistema**: controller, handler globali, consumer, job. Evita try/catch nella logica centrale.
- **Cattura localmente solo per**:
  - recuperare, cioè completare lo scopo con un'alternativa;
  - arricchire l'errore con informazioni di contesto;
  - compensare, per esempio con un rollback o un cleanup.

  Dopo l'azione locale, rilancia l'errore originale o uno più significativo.
- **Mai inghiottire un'eccezione**: niente catch vuoti o che si limitano a loggare e proseguire come se nulla fosse.
- **Errori di dominio espressivi**: traduci gli errori tecnici di librerie e I/O in errori che descrivono il problema nel linguaggio del dominio. Mantieni la causa originale.
- **Messaggi utili**: dicono cosa è successo e con quale dato (ID, valore), senza dati sensibili.
- **Estrai i blocchi try/catch** in metodi con nomi descrittivi: il flusso principale resta lineare.

## Fallimenti silenziosi
Sono i difetti più costosi da trovare: il sistema sembra funzionare e intanto produce dati sbagliati. In review e in scrittura cerca:
- **fallback che nascondono il guasto**: una lista vuota, uno zero o un valore di default restituiti al posto di un errore (`catch` → `return emptyList()`, `.catch(() => [])`). Il chiamante non distingue "nessun dato" da "non sono riuscito a leggere";
- **causa persa**: un'eccezione rilanciata senza quella originale, o con il solo messaggio;
- **errori asincroni senza gestore**: promise senza `catch`, `CompletableFuture` di cui nessuno legge l'esito, subscription senza callback di errore, job schedulati che falliscono senza log;
- **I/O senza timeout**: una chiamata esterna che può restare appesa blocca un thread o una connessione;
- **operazioni a metà**: più scritture correlate senza transazione o compensazione, in cui un errore a metà lascia dati incoerenti;
- **controlli disattivati**: validazioni o asserzioni commentate, `@SuppressWarnings` o `// eslint-disable` che coprono un errore reale.

Un fallback è legittimo solo se è una decisione di dominio esplicita (es. un valore di default documentato), e anche allora il guasto si logga.

## Messaggi
- Il messaggio per l'utente dice cosa può fare. Quello per lo sviluppatore (log) dice cosa è successo e con quali dati. Non sono lo stesso testo.

## Logging
**Cosa loggare:**
- eventi funzionali rilevanti (creazione, modifica, cancellazione) → INFO;
- ingressi e uscite dei metodi di business rilevanti → DEBUG;
- anomalie gestite → WARN;
- errori non previsti → ERROR, con stack trace.

**Cosa evitare:**
- dati sensibili: password, token, dati personali;
- stack trace completi fuori da ERROR in produzione;
- messaggi ambigui o senza contesto ("errore", "qui");
- lo stesso errore loggato a ogni livello mentre risale: loggalo una volta, dove lo gestisci.

**Formato:**
- messaggi parametrizzati o log strutturati, non concatenazione di stringhe;
- identificativi di correlazione (request ID, trace ID) dove disponibili.
