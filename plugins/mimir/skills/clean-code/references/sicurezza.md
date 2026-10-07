# Sicurezza

Base trasversale, ispirata a OWASP Top 10 e ASVS. Le skill di linguaggio e framework aggiungono gli strumenti specifici.

## Input
- **Tutto ciò che arriva dall'esterno è non fidato**: richieste HTTP, header, file, messaggi, risposte di servizi terzi, variabili d'ambiente.
- Valida ai confini con whitelist (formato, lunghezza, intervallo, tipo), non con blacklist.
- Rifiuta e segnala l'input non valido. Non correggerlo in silenzio.

## Injection
- **Query sempre parametrizzate** o tramite ORM o query builder. Mai concatenare input nelle query SQL, NoSQL, LDAP o nei comandi di shell.
- Niente `eval` né esecuzione dinamica di codice con dati esterni.
- Percorsi di file costruiti da input: normalizzali e verifica che restino nella directory prevista (path traversal).

## Output
- Codifica l'output nel contesto in cui finisce: HTML, attributi, URL, JavaScript. Usa i meccanismi del framework, che di norma lo fanno in automatico, e non aggirarli.
- Messaggi di errore verso l'esterno generici. I dettagli vanno nei log, non nella risposta.

## Autenticazione e autorizzazione
- Usa le librerie e i meccanismi del framework. Non implementare crittografia, hashing delle password o gestione dei token da zero.
- **Autorizzazione verificata lato server a ogni richiesta**, sulla risorsa specifica, non solo sul ruolo: è la difesa contro l'IDOR.
- Minimo privilegio: nega di default e apri esplicitamente.

## Segreti e dati sensibili
- Mai segreti nel codice, nei file versionati o nei log. Si leggono da variabili d'ambiente o da un secret manager.
- Dati personali: raccogli e conserva solo ciò che serve (GDPR), e mascherali nei log.
- Password solo con hash dedicati (bcrypt, scrypt, Argon2), mai con hash generici né cifratura reversibile.

## Dipendenze
- Nuove dipendenze solo se necessarie, mantenute e con licenza compatibile.
- Tieni conto delle segnalazioni di vulnerabilità (Dependabot, Renovate, OWASP Dependency-Check, `npm audit`). Non ignorarle senza una ragione documentata.

## Deserializzazione e parsing
- Mai deserializzare dati non fidati in tipi arbitrari: niente serializzazione nativa di Java su input esterno, polimorfismo di Jackson solo con tipi ammessi espliciti.
- Parser XML con le entità esterne disabilitate (XXE).
- Limiti di dimensione su payload, upload e collezioni in ingresso.
