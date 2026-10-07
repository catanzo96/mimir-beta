# Test in Vue: casi specifici

Si applica insieme a `clean-code/references/test.md`. Runner e librerie sono quelli del progetto; nessuna nuova dipendenza senza ok.

## Componenti
- `mount(Componente, { props, slots, global })`. Cambia le props con `wrapper.setProps(...)` e attendi il DOM aggiornato.
- Gli aggiornamenti del DOM sono asincroni: `await wrapper.find('button').trigger('click')` o `await nextTick()`.
- Selettori stabili: ruolo ed etichetta o un attributo dedicato (`data-testid`), non le classi CSS. Con Testing Library per Vue, se già nel progetto, valgono le query per ruolo.
- Eventi: `wrapper.emitted('salva')` contiene gli argomenti di ogni emissione. Verifica payload e numero di chiamate.
- `v-model` / `defineModel`: passa `modelValue` e `'onUpdate:modelValue'` e verifica l'evento, senza guardare lo stato interno.

## Pinia
- Test del componente: `createTestingPinia({ createSpy: vi.fn })` in `global.plugins`; le azioni sono stub, lo stato si imposta con `initialState`. Se vuoi le azioni vere, `stubActions: false`.
- Test dello store: `setActivePinia(createPinia())` e usa lo store come funzione.

## Router
- Con router reale e `createRouter` + `createMemoryHistory`; `router.push(...)` e `await router.isReady()` prima del `mount`. Verifica la route risultante, non una chiamata mockata.

## Composable
- Se non usa hook del ciclo di vita né `inject`, si chiama direttamente. Altrimenti monta un componente minimo che lo usa nel `setup`.

## Rete e asincronia
- Rete simulata con MSW se il progetto lo usa. `flushPromises()` per attendere le promise in sospeso. Prova anche le risposte di errore.
- Timer finti del runner (`vi.useFakeTimers`) per debounce e simili; ripristinali a fine test.

## Suspense e componenti async
- Un componente con `await` nel `setup` va montato dentro `<Suspense>`: usa un wrapper di test, poi `await flushPromises()`.

## End-to-end
- Playwright o Cypress del progetto, pochi flussi critici, selettori per ruolo ed etichetta. Per Nuxt, il suo layer di test se già configurato.
