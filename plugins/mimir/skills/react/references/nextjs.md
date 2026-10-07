# Next.js e Server Components

Nota breve: la fonte è la documentazione della versione di Next.js installata. Leggi `package.json`: l'App Router (`app/`) e le sue API cambiano tra versioni maggiori, quindi non andare a memoria su caching e API asincrone (`params`, `cookies()`, `headers()`).

## Server e client
- In App Router i componenti sono **server** per default. `"use client"` in cima a un file segna il confine: tutto ciò che importa diventa client. Mettilo il più in basso possibile nell'albero (le foglie interattive), non sulle pagine.
- I server component possono essere `async` e leggere dati direttamente; non possono usare stato, effetti, handler né API del browser.
- Passare dati da server a client: solo valori serializzabili (niente funzioni, istanze di classi). Non passare al client oggetti interi del database: serializzi anche campi che non devono uscire.
- `"use server"` marca **Server Function**: sono endpoint pubblici raggiungibili da chiunque. Ogni funzione verifica autenticazione, autorizzazione e valida l'input (schema) come una route API.

## Sicurezza
- Variabili d'ambiente senza prefisso `NEXT_PUBLIC_` restano sul server; quelle con il prefisso finiscono nel bundle. Mai segreti con il prefisso.
- Codice solo server (accesso al DB, segreti) in moduli protetti con `server-only`, se il progetto lo usa, così un import errato da un client component fallisce in build.

## Dati e cache
- Preferisci il fetch nel server component alla `useEffect`. Chiarisci con la documentazione della versione cosa viene messo in cache per default e come si invalida (`revalidatePath`, `revalidateTag`): il comportamento di default è cambiato più volte.
- `loading.tsx` e `error.tsx` sono Suspense ed error boundary a livello di segmento.

## Test
- I server component async non si testano bene con Testing Library: testa la logica come funzioni pure o con un test e2e (Playwright) sul flusso.
