---
name: typescript
description: Best practice TypeScript. Usala quando scrivi, modifichi o rivedi codice TypeScript (.ts, .tsx, .mts), o in progetti con tsconfig.json.
---

# TypeScript

Si applica insieme a `clean-code`. Prevalgono le convenzioni del progetto: `tsconfig.json`, ESLint, Prettier o Biome, versione di TypeScript e runtime. Non usare feature non supportate dalla versione in uso. Framework (React, Angular, Node/Nest…) e librerie hanno le proprie convenzioni: se esiste una skill dedicata, usala.

## Tipi
- **Niente `any`.** Per dati di forma ignota usa `unknown` e restringi il tipo. Un `any` inevitabile va isolato e commentato.
- **Niente asserzioni superflue** (`as`, `!`): sono promesse non verificate. Preferisci il narrowing o i type guard. `as const` e `satisfies` sono ammessi.
- **`satisfies`** per verificare che un valore rispetti un tipo senza perdere l'inferenza.
- **Lascia lavorare l'inferenza** per le variabili locali. Tipa esplicitamente parametri, ritorni delle funzioni esportate e API pubbliche.
- **Union discriminate** per stati e varianti, invece di campi opzionali combinati:
  ```ts
  type Stato =
    | { tipo: 'caricamento' }
    | { tipo: 'successo'; dati: Ordine[] }
    | { tipo: 'errore'; messaggio: string };
  ```
- **Switch esaustivo** con controllo `never`, così un caso nuovo non gestito diventa un errore di compilazione:
  ```ts
  default: {
    const nonGestito: never = stato;
    throw new Error(`Stato non gestito: ${JSON.stringify(nonGestito)}`);
  }
  ```
- **`type` o `interface`**: segui il progetto. In mancanza di una convenzione: `interface` per contratti di oggetti estendibili, `type` per union, intersezioni e tipi derivati.
- **Tipi derivati** (`Pick`, `Omit`, `Partial`, `ReturnType`, tipi indicizzati) invece di duplicare le definizioni.
- **Niente tipi primitivi ambigui per concetti di dominio.** Se confondere due ID è un rischio reale, usa branded type (`type IdOrdine = string & { readonly __brand: 'IdOrdine' }`).
- Per progettare o rivedere tipi di dominio (invarianti, stati impossibili, incapsulamento): [references/progettazione-tipi.md](references/progettazione-tipi.md).

## Immutabilità
- `const` di default, `let` solo se la variabile viene riassegnata, mai `var`.
- `readonly` su proprietà e `ReadonlyArray`/`readonly T[]` per dati che non devono cambiare.
- `as const` per oggetti e tuple letterali.
- Non mutare gli argomenti ricevuti: restituisci nuovi valori.

## Enum e costanti
- Preferisci **union di letterali** o oggetti `as const` agli `enum`:
  ```ts
  const StatoOrdine = { Aperto: 'APERTO', Chiuso: 'CHIUSO' } as const;
  type StatoOrdine = (typeof StatoOrdine)[keyof typeof StatoOrdine];
  ```
  Gli `enum`, soprattutto quelli numerici, generano codice a runtime e non sono compatibili con il type stripping di Node (`erasableSyntaxOnly`). Se il progetto li usa già, continua a usarli.
- Costanti con nome per i magic value. `UPPER_SNAKE_CASE` solo per le costanti vere a livello di modulo.

## null e undefined
- Scegli una convenzione e mantienila. Di norma si usa `undefined` per "assente" e si riserva `null` alle API o ai dati che lo usano esplicitamente.
- Usa `?.` e `??`. Non usare `||` per i default quando `0`, `''` o `false` sono valori validi.
- Con `noUncheckedIndexedAccess`, gestisci l'`undefined` di array e record invece di forzarlo con `!`.
- Array vuoti invece di `null` o `undefined` per le collezioni.

## Errori
- Lancia solo `Error` o sue sottoclassi, mai stringhe o oggetti letterali.
- Errori di dominio come sottoclassi con un nome, mantenendo la causa: `new ErroreOrdine(msg, { cause: e })`.
- Nel `catch` l'errore è `unknown`: restringilo (`e instanceof Error`) prima di usarlo.
- Se il progetto usa un tipo `Result` o `Either`, segui quello per gli errori attesi. Le eccezioni restano per gli errori inattesi.

## Async
- **Nessuna promise fluttuante**: ogni promise viene attesa con `await`, restituita o gestita esplicitamente (`void` solo se intenzionale e commentato).
- `async`/`await` invece di catene di `.then()`.
- Operazioni indipendenti in parallelo con `Promise.all`. Usa `Promise.allSettled` se gli esiti parziali sono accettabili.
- Niente `await` dentro cicli su operazioni indipendenti.
- **`forEach` con una callback `async` non attende nulla**: le promise partono e nessuno le aspetta né ne gestisce gli errori. Usa `for…of` con `await` (in sequenza) o `Promise.all` su `map` (in parallelo).
- Operazioni annullabili o con timeout tramite `AbortSignal`.

## Moduli
- ESM (`import`/`export`).
- **Export con nome** invece di `export default`: refactoring e ricerca più affidabili. Fanno eccezione i framework che richiedono il default (es. pagine Next.js).
- `import type` per gli import solo di tipo.
- Barrel file (`index.ts`) con parsimonia: possono creare cicli e rallentare build e test.
- Un modulo espone poco e nasconde molto: i tipi e le funzioni interne non si esportano "perché potrebbero servire". Gli altri moduli importano dal punto d'ingresso, non dai file interni.

## Confini e validazione
- I tipi TypeScript non esistono a runtime. Ai confini valida i dati con uno schema: input HTTP, risposte di API esterne, `JSON.parse`, variabili d'ambiente, storage.
- Usa la libreria del progetto (Zod, Valibot…) e ricava il tipo dallo schema (`z.infer<typeof schema>`) invece di duplicarlo. Se il progetto non ne ha una, un type guard scritto a mano; una libreria nuova solo con ok.
- `JSON.parse` lancia su input non valido: gestisci l'errore e valida il risultato, che è `any` mascherato.
- Variabili d'ambiente lette e validate una volta all'avvio, in un modulo di configurazione tipizzato: se manca qualcosa, l'applicazione non parte invece di fallire più tardi.

## Sicurezza (JavaScript e Node)
- **Prototype pollution**: mai copiare in profondità o fondere oggetti con chiavi che arrivano dall'esterno senza escludere `__proto__`, `constructor` e `prototype`. Per mappe con chiavi arbitrarie usa `Map` o `Object.create(null)`.
- Niente `eval`, `new Function` o `setTimeout` con stringhe.
- In Node, comandi esterni con `execFile`/`spawn` e argomenti separati, mai `exec` con stringhe concatenate. Percorsi da input normalizzati e confinati (vedi `clean-code/references/sicurezza.md`).
- Regex su input esterno: attenzione ai pattern con ripetizioni annidate, che possono bloccare il processo (ReDoS).

## Naming
- `PascalCase`: tipi, interfacce, classi, componenti. `camelCase`: variabili e funzioni.
- Niente prefisso `I` sulle interfacce, niente suffisso `Type` ridondante.
- Nomi dei file: segui il progetto (`kebab-case.ts` è il default più diffuso).

## Classi e funzioni
- In TypeScript le funzioni e i moduli sono cittadini di prima classe. Usa le classi quando c'è stato incapsulato o polimorfismo, non come semplici contenitori di funzioni statiche.
- Le parti OOP di `clean-code` si applicano quando usi le classi.

## Tooling
- `tsconfig` con `strict: true`. Se il progetto lo consente, anche `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes` e `noImplicitOverride`.
- Lint con `typescript-eslint` (regole type-aware, come `no-floating-promises`) o Biome, secondo il progetto.
- Prima di dichiarare finito: type check (`tsc --noEmit` o lo script del progetto), lint e test puliti.
- In review, segnala le modifiche al `tsconfig` o alla configurazione del linter che allentano i controlli (`strict` disattivato, regole spente, `skipLibCheck` aggiunto per nascondere un errore).
- Con il type stripping di Node o con transpiler che lavorano file per file (esbuild, SWC), `isolatedModules` e `verbatimModuleSyntax` evitano costrutti che non si possono tradurre senza il type checker.
- Sonar, se presente nel progetto, analizza anche TypeScript. Le esclusioni dalla coverage si configurano come in `clean-code`.

## Test
- Il framework del progetto (Vitest, Jest…).
- Test tipizzati: niente `any` neanche nei test. Per i mock parziali usa helper tipizzati.
- Test dei tipi (`expectTypeOf`, `tsd`) solo per librerie o tipi complessi pubblici.
