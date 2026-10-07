---
name: nodejs
description: Best practice backend su Node.js. Usala quando scrivi o rivedi servizi, API e script Node (JavaScript o TypeScript), o in progetti con package.json ed engines node.
---

# Node.js

Si applica insieme a `clean-code` e, per i tipi, a `typescript`. Le convenzioni del progetto prevalgono: versione di Node (`engines`, `.nvmrc`, `.node-version`, Dockerfile), gestore di pacchetti (npm, pnpm, yarn: riconoscilo dal lockfile), framework e librerie già adottati. Express, Fastify e NestJS: `references/framework.md`.

## Prima di tutto: la versione
Verificato su nodejs.org il 03/10/2026: v26 è Current, v24 e v22 sono LTS. In produzione usa solo versioni LTS (il calendario è su nodejs.org). **Su progetti con Node fuori supporto (20 o precedente), CommonJS puro o senza test, vale `manutenzione-legacy` (se disponibile).**

Feature utili (dalla documentazione ufficiale):
- **Test runner nativo** `node:test` (stabile dalla 20): `node --test`, mock e snapshot inclusi; la coverage è ancora sperimentale.
- **`--watch`**: ricarica in sviluppo, senza nodemon.
- **`--env-file`**: carica un `.env` senza dotenv; non più sperimentale dalla 22.21 e 24.10. Solo per lo sviluppo: in produzione le variabili le fornisce l'ambiente.
- **`fetch`** e `AbortSignal.timeout()` sono globali: niente `node-fetch` o axios per usi semplici (se il progetto già usa axios, resta lì).
- **Type stripping**: Node esegue `.ts` rimuovendo i tipi, attivo di default dalla 23.6 e 22.18, stabile dalla 24.12. Limiti: niente `enum`, `namespace` a runtime né parameter property; `tsconfig.json` ignorato; estensione nell'import (`./a.ts`) e `import type` obbligatori; nessun `.ts` in `node_modules`. Usa `erasableSyntaxOnly` nel tsconfig. Per build di produzione resta valido `tsc`/un bundler, se il progetto li usa.
- **`require(esm)`**: un modulo ESM senza top-level await si carica con `require` (senza flag dalla 22.12 e 20.19). Toglie gran parte del dolore dei pacchetti solo-ESM.
- **Permission model** (`--permission`): ancora in sviluppo attivo, non fidarti come unico confine di sicurezza.

## Moduli: ESM vs CommonJS
- Segui il progetto (`"type"` in `package.json`). Per codice nuovo: ESM, con `import`.
- In ESM mancano `__dirname` e `__filename`: usa `import.meta.dirname` e `import.meta.filename` (Node 20.11+), non ricostruirli.
- Gli import ESM relativi vogliono l'estensione. Prefisso `node:` per i moduli built-in (`node:fs/promises`).
- `import()` dinamico per caricare ESM da CommonJS dove `require` non basta; non mescolare i due sistemi senza motivo.

## Errori asincroni
- Ogni promise è attesa, restituita o gestita: una promise rifiutata senza handler **termina il processo** (default dalla 15). Non disattivarlo; usa `unhandledRejection` solo per loggare e uscire.
- Gestisci `uncaughtException` solo per logging e uscita controllata: dopo non puoi fidarti dello stato del processo.
- `async` dentro un callback che si aspetta un valore sincrono (`forEach`, `EventEmitter.on`, middleware Express 4) perde gli errori. Avvolgi o usa un handler che li inoltra.
- Un `EventEmitter` che emette `'error'` senza listener lancia: registra sempre il listener (stream, socket, client).
- Callback e promise non si mischiano: `util.promisify` o le API `node:fs/promises`.
- `Promise.all` per il parallelo. `Promise.all` non limita la concorrenza: con molti elementi serve un limite (coda, `p-limit` se già presente, o un semplice pool), perché migliaia di richieste insieme saturano risorse e connessioni.
- Timeout e annullamento con `AbortSignal` su `fetch`, query e operazioni lunghe.

## Event loop
- Il thread è uno: CPU lunga (parsing grossi, crittografia sincrona, regex patologiche, `JSON.parse` su MB, `*Sync` di fs) blocca tutte le richieste. Le API `*Sync` vanno bene solo all'avvio.
- Lavoro CPU-bound in `worker_threads` (con un pool, se il progetto ha già una libreria come piscina) o in un processo/servizio separato. I worker non servono per l'I/O, che è già asincrono.
- Spezza i cicli lunghi o spostali; misura prima di ottimizzare (`--cpu-prof`, `perf_hooks`, event loop delay).
- `setImmediate` e `queueMicrotask` per cedere il controllo; `process.nextTick` solo se serve davvero, può affamare l'I/O.

## Stream e backpressure
- Per file e payload grandi: stream, non `readFile` in memoria. `pipeline` da `node:stream/promises` collega gli stream, propaga gli errori e chiude tutto; mai `.pipe()` a mano, che non pulisce in caso di errore.
- Backpressure: se `write()` torna `false`, aspetta `'drain'`. `pipeline` e `for await (const chunk of stream)` la rispettano da soli.
- Limiti di dimensione sul body in ingresso; stream anche per risposte lunghe, con gestione della chiusura del client.

## Configurazione
- Variabili d'ambiente lette e validate **una volta** all'avvio in un modulo di configurazione tipizzato (schema del progetto: Zod, Valibot, Joi…); se manca qualcosa il processo non parte. `process.env` non si legge sparso nel codice.
- I valori sono stringhe: converti e valida (`"false"` è truthy).
- Segreti mai nel repository né nei log; `.env` in `.gitignore`.

## Logging
- Log strutturato in JSON con la libreria del progetto (pino, winston): livello, messaggio costante e campi a parte, non stringhe concatenate.
- Un identificatore di correlazione per richiesta (header o `AsyncLocalStorage`), propagato ai log e alle chiamate a valle.
- Mai password, token, header `Authorization`, dati personali; usa la redazione dei campi della libreria. Non loggare lo stesso errore a ogni livello: una volta al confine.
- `console.log` non è logging applicativo.

## Sicurezza
- **Dipendenze**: `npm audit` (o equivalente) in CI, lockfile versionato e `npm ci` nelle build; ogni dipendenza nuova va motivata e approvata. Occhio ai pacchetti con script `postinstall` e ai typosquatting.
- **Prototype pollution**, `eval`, regex (ReDoS): vedi `typescript` sezione sicurezza.
- **`child_process`**: `execFile`/`spawn` con array di argomenti, mai `exec` con stringhe composte; `shell: true` solo su valori costanti.
- **Percorsi**: normalizza e confina (`path.resolve` e controllo del prefisso) prima di leggere file indicati dall'utente.
- Validazione di ogni input (body, query, header) con schema; header di sicurezza (helmet o equivalente), rate limiting sugli endpoint sensibili, CORS ad elenco esplicito.
- Query parametrizzate sempre. Altri punti: `clean-code/references/sicurezza.md`.

## Processi e graceful shutdown
- Gestisci `SIGTERM` e `SIGINT`: smetti di accettare connessioni (`server.close()`), attendi le richieste in corso con un timeout massimo, chiudi pool, code e client, poi `process.exit`. Gli orchestratori (Kubernetes, Docker) inviano `SIGTERM` e dopo un po' `SIGKILL`.
- Un solo processo per container; la scalabilità la fa l'orchestratore. Se serve il clustering fuori dai container, un process manager già in uso nel progetto.
- Il processo è il PID 1 in Docker: usa `node` direttamente o un init (`tini`), non `npm start`, che non inoltra i segnali.
- Endpoint di liveness e readiness distinti; la readiness diventa negativa all'inizio dello shutdown.
- `process.exit()` brusco tronca scritture in corso: imposta `process.exitCode` e lascia finire il loop quando possibile.

## Test
Framework del progetto (`node:test`, Vitest, Jest). Test dei servizi senza avviare il server; test di integrazione sugli endpoint (supertest o `fastify.inject`) con le dipendenze esterne sostituite. Niente timer reali: mock dei timer. Principi in `clean-code/references/test.md`.

## Verifica
Gli script sono in `package.json`; usa quelli, tipicamente:
```bash
npm run lint && npm run typecheck   # eslint/biome, tsc --noEmit
npm test                            # node --test, vitest o jest
npm audit --omit=dev                # solo lettura; non applicare fix automatici senza ok
```
Se avvii il servizio per provarlo, verifica anche l'arresto pulito con `SIGTERM`. Riporta gli esiti reali.

## Riferimenti
`references/framework.md`: leggilo quando lavori con Express, Fastify o NestJS (struttura, middleware, validazione, errori).
