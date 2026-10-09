---
name: vue
description: Best practice Vue 3 moderno. Usala quando scrivi, modifichi o rivedi componenti .vue, composable, store Pinia e test Vue, o in progetti con vue nel package.json (Vite, Nuxt).
---

# Vue

Si applica insieme a `typescript` e `clean-code`; per l'aspetto visivo e le animazioni, `design-ui` e `animazioni-ui`. Prevalgono le convenzioni del progetto: stile dei componenti, store, libreria di UI, framework (Nuxt…) e versione di Vue.

## Prima di tutto: la versione
Leggi la versione di `vue` in `package.json` e usa solo le API disponibili lì. **Vue 2 è a fine vita dal 31/12/2023: per i progetti Vue 2 o senza test vale `manutenzione-legacy`** (se disponibile): non migrare pattern esistenti (Options API, mixin, Vuex) se non è richiesto, segnala l'opportunità.

| Feature | Da |
|---|---|
| Composition API, `<script setup>` | 3.0 / 3.2 |
| `defineModel` | 3.4 |
| Destructuring reattivo di `defineProps`, `useTemplateRef`, `useId`, `onWatcherCleanup` | 3.5 |

Nelle versioni precedenti alla 3.5, le variabili destrutturate da `defineProps` perdono la reattività nei `watch` e nei `computed`: usa `props.x` o `toRefs`.

## Componenti
- **`<script setup lang="ts">`** con Composition API, se il progetto la usa. Un componente, una responsabilità; presentazionali separati da quelli che recuperano i dati.
- **Props tipizzate** con `defineProps<Props>()`, **eventi tipizzati** con `defineEmits<{ salva: [ordine: Ordine] }>()`. Gli eventi si chiamano con un verbo (`salva`, `chiudi`).
- **Mai mutare una prop**: il flusso è props giù, eventi su. Per il two-way usa `defineModel()` (dalla 3.4), non una coppia `modelValue` + `update:modelValue` scritta a mano.
- **Valori di default** di oggetti e array tramite funzione; con il destructuring (3.5+) basta il default nel pattern.
- **Slot** per la composizione, invece di una prop per ogni variante di contenuto.
- **Template ref** con `useTemplateRef` (3.5+), altrimenti `ref(null)` con lo stesso nome dell'attributo.
- **Id univoci** per `label`/`for` con `useId` (3.5+): stabile tra server e client.
- **`v-for` sempre con `:key`** stabile (l'id del dato, non l'indice se la lista cambia). Mai `v-if` e `v-for` sullo stesso elemento.
- Nomi dei componenti in PascalCase, a più parole (`OrdineRiga`, non `Riga`), per non collidere con gli elementi HTML.

## Reattività
- **`ref`** come scelta di default: vale per primitivi e oggetti, si legge con `.value` nello script, senza nel template. `reactive` solo per un oggetto che non viene mai riassegnato.
- **Perdita di reattività**: destrutturare un `reactive` o assegnare una sua proprietà a una variabile la stacca. Usa `toRefs(stato)` o `toRef(stato, 'k')`; riassegnare un intero `reactive` non funziona.
- `shallowRef` per grandi strutture o istanze di classi esterne che non servono reattive in profondità.
- **`computed` per lo stato derivato**: puro, senza effetti collaterali, senza modificare altro stato. Mai un `watch` che copia o trasforma un valore in un altro `ref`.
- **`watch`** per effetti collaterali in risposta a un cambiamento preciso (chiamata, storage, navigazione), con sorgente esplicita. `watchEffect` quando le dipendenze sono molte e ovvie; traccia solo ciò che legge **prima del primo `await`**.
- Richieste annullabili dentro un watcher: `onWatcherCleanup` (3.5+) o il parametro `onCleanup`, per evitare risposte vecchie che sovrascrivono quelle nuove.
- `watch` su un oggetto non è profondo per default: `deep: true` solo se serve e con costo noto.

## Composable
- Funzioni `useNome()` che incapsulano logica con stato e restituiscono ref e funzioni (non un `reactive`, per poter destrutturare).
- Accettano input reattivi con `toValue()` / `MaybeRefOrGetter`, non solo valori statici.
- Gli effetti si registrano nel `setup` e si ripuliscono in `onUnmounted` (listener, timer, socket). Un composable chiamato fuori da `setup` non ha un'istanza a cui agganciarsi.
- Non devono diventare un contenitore di stato globale nascosto: per lo stato condiviso c'è lo store.

## Provide / inject
- Per dati di un sottoalbero (tema, form, contesto di una famiglia di componenti). Usa un `InjectionKey<T>` tipizzato, esponi il valore in sola lettura (`readonly`) con le funzioni che lo modificano.
- Non è una scorciatoia per saltare le props nel codice di tutti i giorni: rende le dipendenze implicite.

## Stato condiviso: Pinia
- Lo store del progetto è Pinia (Vuex è deprecato). Preferisci i **setup store** o gli option store secondo lo stile presente.
- Lo stato dei dati remoti va in una libreria dati (TanStack Query per Vue, o le API del framework), non copiato nello store.
- Destrutturare lo store perde la reattività: `storeToRefs(store)` per stato e getter, le azioni si destrutturano normalmente.
- Un store per dominio, non uno per componente. Gli errori delle azioni asincrone si gestiscono, non si inghiottono.

## Router
- Route in lazy loading: `component: () => import('./Pagina.vue')`.
- Guard (`beforeEach`, `beforeEnter`) per l'esperienza; l'autorizzazione vera è sul server. Ritorna `false`, una route o niente: evita il vecchio `next()`.
- Parametri come props (`props: true`) per disaccoppiare il componente dal router. Cambiando solo il parametro il componente **non** viene ricreato: osserva `route.params` o usa `:key`.

## Sicurezza
- **`v-html` solo con HTML sanificato** (DOMPurify o equivalente già nel progetto), con un commento sul perché. Il contenuto non viene compilato come template ma non è escapato: è una via diretta verso l'XSS.
- Niente template compilati a runtime da input utente. Niente URL non fidati in `:href` senza controllare lo schema.
- Niente segreti nel codice del frontend: tutto ciò che arriva al browser è pubblico, comprese le variabili `VITE_*`.

## Accessibilità
HTML semantico (`button`, non `div @click`), `label` collegate, focus gestito dopo cambi di route e dialog, annunci con `aria-live`. Checklist completa in `clean-code/references/a11y.md`; `eslint-plugin-vuejs-accessibility` se già presente.

## Test
- **Vue Test Utils** con **Vitest** (o il runner del progetto). `mount` per il comportamento, `shallowMount` raramente: nasconde le integrazioni.
- Interagisci come l'utente (`trigger`, `setValue`), poi `await` il risultato (`nextTick` o la promise ritornata). Verifica DOM ed eventi emessi (`wrapper.emitted()`), non lo stato interno.
- Store, router e dettagli (Pinia con `createTestingPinia`, rete, async) in [references/test-vue.md](references/test-vue.md).

## Nuxt
Se il progetto usa Nuxt (`nuxt.config`), valgono la sua struttura e le sue convenzioni (auto-import, `useFetch`/`useAsyncData`, route da `pages/`): segui la documentazione della versione installata. Il codice che gira in SSR non tocca `window` o `document` fuori da `onMounted` o da `import.meta.client`.

## Verifica
Prima di dichiarare finito: lint, type check (`vue-tsc --noEmit`), test e la build di produzione, con gli script del progetto. Errori di tipo nei template emergono solo con `vue-tsc`, non con `tsc`.
