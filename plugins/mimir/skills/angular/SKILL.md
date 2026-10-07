---
name: angular
description: Best practice Angular moderno. Usala quando scrivi, modifichi o rivedi codice Angular (componenti, template, servizi), o in progetti con angular.json o @angular/core.
---

# Angular

Si applica insieme a `typescript` e `clean-code`. Prevalgono le convenzioni del progetto: struttura, state management (es. NgRx), librerie di UI e la versione di Angular.

## Prima di tutto: la versione
Leggi la versione di `@angular/core` in `package.json` e usa solo le API disponibili lì. **Sotto la v14, o senza una rete di test, vale `manutenzione-legacy`.** Non migrare pattern esistenti (NgModule, `*ngIf`, decorator `@Input`) se non è richiesto: segnala l'opportunità.

Disponibilità indicativa. Diverse API nascono **sperimentali** o in **developer preview** e si stabilizzano in versioni successive. Prima di usarle in produzione verifica lo stato nella documentazione della versione in uso.

| Feature | Da |
|---|---|
| `inject()` | v14 |
| Control flow `@if`/`@for`/`@switch`, `@defer` | v17 |
| `input()`, `output()`, `model()`, query signal | v17.x, stabili dalla v19 |
| Standalone come default | v19 |
| `linkedSignal`, `resource` (sperimentali) | v19; `linkedSignal` stabile dalla v20 |
| `httpResource` (sperimentale) | v19.2 |
| Zoneless stabile | v20.2 |
| Vitest come test runner di default, zoneless di default | v21 |
| OnPush come change detection di default (`Default` rinominata `Eager`), Signal Forms consigliate, `resource` stabile | v22 |

## Componenti
- **Standalone.** Niente nuovi NgModule, niente import di `CommonModule`: importa solo ciò che il template usa.
- **Piccoli, con una sola responsabilità.**
  - *Container* (smart): recuperano i dati e orchestrano;
  - *presentazionali*: ricevono input ed emettono output, senza dipendere da servizi di dominio.
- **API signal**: `input()`, `input.required()`, `output()`, `model()` per il two-way binding, `viewChild()`/`contentChild()` per le query. Tutti `readonly`.
- **`protected`** per i membri usati solo dal template.
- **OnPush.** Dalla v22 è il default. Nelle versioni precedenti dichiaralo esplicitamente (`changeDetection: ChangeDetectionStrategy.OnPush`).
- **Host binding** nell'oggetto `host` del decorator, non con `@HostBinding` o `@HostListener`.
- **Ordine dei membri**: prima dipendenze iniettate, input, output e query, poi stato, infine metodi.
- **Handler con il nome dell'azione**: `salvaDatiUtente()`, non `onClick()` o `handleClick()`.
- **Lifecycle hook** snelli: delegano a metodi con un nome e implementano la relativa interfaccia (`OnInit`…).

## Stato e reattività
- **Signals** per lo stato locale. Usa `computed()` per lo stato derivato e `linkedSignal()` per uno stato derivato ma scrivibile, per esempio una selezione che si resetta quando cambiano le opzioni.
- `set()` o `update()` con valori nuovi. Non mutare oggetti o array dentro un signal.
- **`effect()` solo per effetti verso l'esterno**: logging, storage, DOM non gestito da Angular, librerie terze.
  - Mai per propagare stato tra signal: per quello usa `computed` o `linkedSignal`.
- **Stato condiviso**: in servizi con signal privati scrivibili ed esposti in sola lettura (`asReadonly()`), oppure con lo store del progetto (NgRx Signal Store…).

## Dati asincroni e HTTP
- **`httpResource()` o `resource()`** per caricare dati che dipendono da signal. Gestisci gli stati `isLoading`, `error` e `value` nel template.
  - `resource` riceve `params` e un `loader({ params, abortSignal })`. Nelle prime versioni sperimentali l'opzione si chiamava `request`: segui la forma della versione installata.
  - Leggi `value()` dopo `hasValue()`: in stato di errore `value()` lancia un'eccezione.
  - Solo per letture: le scritture passano da un servizio, non da una resource.
- **HttpClient** incapsulato in servizi dedicati, mai chiamato direttamente dai componenti presentazionali.
- **RxJS** per flussi di eventi complessi: debounce, combinazioni, websocket.
  - Interoperabilità con `toSignal()` e `toObservable()`.
  - Evita `subscribe()` manuali. Se servono, `takeUntilDestroyed()`.
  - Mai `subscribe` annidati: usa `switchMap`, `concatMap` e simili.
  - Scegli l'operatore per intento: `switchMap` quando conta solo l'ultima richiesta (ricerca, navigazione), `exhaustMap` per ignorare i clic ripetuti (submit), `concatMap` quando l'ordine conta, `mergeMap` per operazioni parallele indipendenti.
  - `catchError` dentro l'operatore interno: messo sul flusso esterno, al primo errore il flusso si chiude e smette di reagire.
- Interceptor funzionali (`HttpInterceptorFn`) per auth, errori e header trasversali.

## Template
- **Control flow nativo**: `@if`, `@for`, `@switch` al posto di `*ngIf`, `*ngFor`, `ngSwitch`.
- **`@for` sempre con un `track`** stabile (es. `track item.id`), non l'indice se gli elementi possono cambiare ordine.
- **Logica fuori dal template**: niente espressioni complesse o chiamate a metodi costosi. Usa `computed()` o pipe pure.
- **Binding `[class]` e `[style]`** invece di `NgClass` e `NgStyle`.
- **`@defer`** per le parti pesanti o sotto la piega.
- **`NgOptimizedImage`** (`ngSrc`) per le immagini statiche.

## Form
- **Nuovi form**: Signal Forms se la versione lo consente. Altrimenti Reactive Forms tipizzati. Evita i template-driven forms per form non banali.
- Validatori riusabili come funzioni pure, testati.

## Dependency injection e servizi
- **`inject()`** invece dell'injection da costruttore. È la raccomandazione ufficiale e sostituisce, solo in Angular, la regola generale "injection da costruttore".
- Servizi singleton con `providedIn: 'root'`. Provider a livello di route o componente solo quando serve uno scope ridotto.
- Un servizio, una responsabilità.

## Routing
- Feature caricate in lazy loading (`loadComponent`, `loadChildren`).
- Guard, resolver e interceptor **funzionali**, non classi.
- `canMatch` quando l'utente non deve nemmeno scaricare il codice della route: `canActivate` agisce dopo il caricamento del chunk.
- I controlli dei guard migliorano l'esperienza, non proteggono i dati: l'autorizzazione vera è sul server.
- Parametri di route come input del componente (`withComponentInputBinding()`), se il progetto lo usa.

## Struttura e naming
- **Organizzazione per feature**, non per tipo: niente cartelle globali `components/`, `services/`. File correlati, test inclusi, nella stessa cartella.
- **File in `kebab-case`**, con lo stesso nome per `.ts`, `.html`, `.css` e `.spec.ts`.
  - Suffissi (`.component.ts`, `.service.ts`): segui il progetto. Dalla v20 la CLI genera file senza suffisso.
- **Prefisso del progetto** per i selettori (`app-`, o quello del progetto). Direttive attributo in camelCase (`[appTooltip]`).
- Ogni feature espone poche cose da un punto d'ingresso. Le altre feature non importano file dalle sue cartelle interne.

## Sicurezza e accessibilità
- Niente `bypassSecurityTrust*` né `innerHTML` con contenuti non fidati, se non motivato e commentato.
- Niente segreti nel codice del frontend, `environment.ts` compreso: tutto ciò che arriva al browser è pubblico.
- Con SSR o prerendering, niente accesso diretto a `window`, `document`, `localStorage`: vedi [references/ssr-sicurezza.md](references/ssr-sicurezza.md).
- Accessibilità WCAG AA: HTML semantico, etichette sui controlli, navigazione da tastiera, focus gestito, contrasto adeguato. Dettagli e controlli in `clean-code/references/a11y.md`.

## Test
- Il runner del progetto: Vitest dalla v21, Karma o Jest nei progetti precedenti.
- Testa il comportamento attraverso il DOM e l'API pubblica del componente (input, output), non i membri interni.
- Usa i component harness (Angular Material/CDK) quando disponibili.
- HTTP con `provideHttpClientTesting()` e `HttpTestingController`.
- I servizi con logica si testano in isolamento, con le dipendenze sostituite tramite provider di test.
- Router, signal input, pipe ed e2e: [references/test-angular.md](references/test-angular.md).

## Verifica
Prima di dichiarare finito: lint, test e **`ng build`** con la configurazione di produzione. Alcuni errori dei template e dei budget emergono solo nella build, non in `tsc` né nei test.
