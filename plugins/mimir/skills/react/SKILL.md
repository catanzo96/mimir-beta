---
name: react
description: Best practice React moderno. Usala quando scrivi, modifichi o rivedi componenti, hook, form e test React, o in progetti con react nel package.json (Vite, Next.js).
---

# React

Si applica insieme a `typescript` e `clean-code`; per l'aspetto visivo e le animazioni, `design-ui` e `animazioni-ui`; per la prova con dati estremi, `ui-casi-limite`. Prevalgono le convenzioni del progetto: framework (Vite, Next.js, Remix…), libreria dati (TanStack Query…), store, libreria di UI e versione di React.

## Prima di tutto: la versione
Leggi la versione di `react` in `package.json` e usa solo le API disponibili lì. **Sotto la 16.8 (senza hook) o senza una rete di test vale `manutenzione-legacy`** (se disponibile). Non convertire i class component esistenti se non è richiesto: segnalalo.

| Feature | Da |
|---|---|
| Hook, `memo` | 16.8 / 16.6 |
| `useId`, `useTransition`, `useDeferredValue`, `createRoot`, Suspense per i dati | 18 |
| Actions, `useActionState`, `useOptimistic`, `useFormStatus`, `use()`, `ref` come prop, `<form action>` | 19 |
| `useEffectEvent` | 19.2 |
| React Compiler 1.0 (plugin Babel, stabile) | compatibile con 17, 18 e 19; sotto la 19 serve `react-compiler-runtime` |

Con il compiler attivo (cerca `babel-plugin-react-compiler` o l'opzione del framework) la memoizzazione manuale è quasi sempre superflua. Verifica che sia davvero attivo prima di fare questa assunzione.

## Componenti
- **Funzioni**, uno per responsabilità. Presentazionali (props in, JSX out) separati da quelli che recuperano dati.
- **Props tipizzate** con un `type`/`interface` locale. Niente `React.FC` se il progetto non lo usa. Con la 19, `ref` è una prop normale: `forwardRef` non serve più.
- **Composizione prima della configurazione**: `children` e slot (props che sono JSX) invece di una prop booleana per ogni variante.
- Nessun componente definito dentro un altro componente: a ogni render diventa un tipo nuovo e perde lo stato.
- **Handler con il nome dell'azione**: `salvaOrdine`, passati come `onSalva` nelle props.

## Hook
- Solo al livello superiore di componenti e custom hook, mai in condizioni, cicli o dopo un `return` anticipato. Il plugin ESLint `react-hooks` va tenuto attivo e rispettato, `exhaustive-deps` compreso: non spegnerlo, correggi la causa.
- **Custom hook** (`use…`) per riusare logica con stato, non per spostare codice. Ritorna un oggetto se i valori sono più di due.
- Lo stato non si muta: nuovi oggetti e array (`[...a, x]`, `{...o, k: v}`), aggiornamenti funzionali (`set(n => n + 1)`) quando dipendono dal valore precedente.

## Quando NON usare useEffect
Un effetto serve a sincronizzarsi con **sistemi esterni** (socket, DOM non gestito da React, librerie terze, analytics). Negli altri casi:
- **Stato derivato**: calcolalo nel render (`const totale = righe.reduce(...)`), non in `useState` + `useEffect`. Se costa davvero, misura prima di memoizzare.
- **Reset dello stato al cambio di una prop**: dai una `key` al componente, invece di un effetto che chiama `set…`.
- **Risposta a un evento** (clic, submit): la logica sta nell'handler, non in un effetto che osserva lo stato.
- **Fetch dei dati**: usa la libreria del progetto (TanStack Query, SWR) o il loader del framework. Un `useEffect` con `fetch` a mano porta con sé race condition, niente cache, niente retry. Se proprio serve, cleanup con `AbortController` e flag di annullamento.
- **Valore letto da un effetto senza doverlo ri-eseguire** (es. callback di un socket): `useEffectEvent` se disponibile, altrimenti un ref.
- In StrictMode gli effetti girano due volte in sviluppo: è voluto, il cleanup deve rendere il secondo giro innocuo.

## Liste e chiavi
- `key` stabile e univoca tra i fratelli: l'id del dato. Mai l'indice se la lista può essere riordinata, filtrata o modificata (si mescolano stato e DOM). Mai `Math.random()` o `crypto.randomUUID()` nel render.

## Stato locale e condiviso
- **Stato il più vicino possibile** a chi lo usa; solleva (*lifting*) solo quando due fratelli lo condividono.
- **Context** per valori che cambiano di rado (tema, utente, locale). Un context con stato che cambia spesso ri-renderizza tutti i consumer: dividilo (stato e dispatch separati) o passa a uno store.
- **Stato del server** (dati remoti) nella libreria dati, non copiato in Redux/Zustand.
- Per lo stato di UI condiviso usa lo store già presente nel progetto (Redux Toolkit, Zustand…). Nessuna nuova libreria senza ok.
- `useReducer` quando le transizioni sono molte e collegate.

## Prestazioni
- Misura prima (React DevTools Profiler). `memo`, `useMemo`, `useCallback` solo se il profilo mostra un problema, o dove il compiler non c'è e serve una referenza stabile (dipendenza di un effetto, prop di un componente `memo`).
- Con il compiler attivo non aggiungerli di riflesso; in codice esistente non rimuoverli in blocco.
- `useTransition` / `useDeferredValue` per aggiornamenti pesanti non urgenti (filtri su liste grandi). Lazy loading con `React.lazy` e `Suspense` per route e parti pesanti.

## Form e Actions
- **Con la 19**: `<form action={fn}>`, `useActionState` per lo stato dell'esito e `isPending`, `useFormStatus` nei componenti figli, `useOptimistic` per l'aggiornamento ottimistico (si ripristina da solo se l'azione fallisce). Dettagli in [references/form-actions.md](references/form-actions.md).
- **Prima o con form complessi**: la libreria del progetto (React Hook Form, Formik…) più una validazione a schema (Zod…). Controlled solo quando serve il valore a ogni digitazione.
- La validazione sul client migliora l'esperienza; quella vera è sul server.

## Error boundary e Suspense
- Un error boundary (class component o `react-error-boundary`) attorno alle zone che possono fallire, con un fallback utile e un modo di riprovare. Non intercetta errori negli handler né nel codice asincrono: quelli si gestiscono a mano.
- `Suspense` con un fallback per ogni parte che si carica in modo indipendente; `use(promise)` solo con una promise creata fuori dal render (cache, libreria, server), mai creata nel componente.
- Mai inghiottire un errore per "non rompere la pagina": si mostra e si registra.

## Server Components
Solo se il framework li usa (Next.js App Router…). Note e trappole in [references/nextjs.md](references/nextjs.md): leggilo quando il progetto ha `app/` o direttive `"use client"` / `"use server"`.

## Sicurezza e accessibilità
- `dangerouslySetInnerHTML` solo con HTML sanificato (DOMPurify o equivalente già nel progetto), con un commento sul perché. Mai un URL non fidato in `href` senza controllare lo schema (`javascript:`).
- Niente segreti nel bundle: tutto ciò che arriva al browser è pubblico, comprese le variabili `VITE_*` e `NEXT_PUBLIC_*`.
- Accessibilità WCAG AA: HTML semantico (`button`, non `div onClick`), `label` collegate (`useId` per gli id), focus gestito dopo cambi di route e dialog, annunci con `aria-live`. Checklist completa in `clean-code/references/a11y.md`; `eslint-plugin-jsx-a11y` se presente.

## Test
- **Testing Library**: query per ruolo ed etichetta (`getByRole`, `getByLabelText`), non per classi, id o struttura. `findBy…` per ciò che compare in modo asincrono.
- **`userEvent`** (con `setup()`) invece di `fireEvent`; verifica ciò che vede l'utente, non lo stato interno né i dettagli di implementazione.
- Runner del progetto: Vitest o Jest. Dettagli (rete con MSW, hook, timer, provider) in [references/test-react.md](references/test-react.md).

## Verifica
Prima di dichiarare finito: lint (con `react-hooks`), type check (`tsc --noEmit`), test e la build di produzione, con gli script del progetto. Alcuni errori (import, direttive server/client, budget) emergono solo nella build.
