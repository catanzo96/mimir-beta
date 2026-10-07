# Test in React: casi specifici

Si applica insieme a `clean-code/references/test.md`. Runner e librerie sono quelli del progetto (Vitest o Jest, Testing Library); nessuna nuova dipendenza senza ok.

## Componenti
- `render` dentro un helper del progetto se esiste (provider di router, tema, QueryClient): non ricostruire a mano i provider in ogni test.
- `const utente = userEvent.setup()` prima del `render`; `await utente.click(...)`. Le interazioni sono asincrone.
- Query nell'ordine di preferenza: `getByRole` (con `name`), `getByLabelText`, `getByText`, solo infine `getByTestId`. `getByRole` fallito spesso segnala un problema reale di accessibilità.
- `queryBy…` per verificare un'assenza, `findBy…` per un'attesa. Niente `setTimeout` né attese fisse; `waitFor` con un'asserzione sola.
- Niente snapshot di interi componenti: poco leggibili e fragili.
- Non testare né mockare i dettagli di React (che `useState` sia chiamato); testa l'esito visibile.

## Rete
- Mock a livello di rete con MSW se il progetto lo usa, invece di mockare `fetch` o il client in ogni test. Prova anche le risposte di errore (404, 500), non solo quella felice.
- Con TanStack Query: un `QueryClient` nuovo per ogni test, con `retry: false`, altrimenti i test sono lenti e condividono la cache.

## Hook
- `renderHook` per i custom hook con logica propria; per quelli banali basta testare il componente che li usa. Gli aggiornamenti vanno dentro `act` (Testing Library lo fa già con le sue utility).

## Timer e asincronia
- Timer finti (`vi.useFakeTimers` / `jest.useFakeTimers`) con `userEvent.setup({ advanceTimers })` collegato al runner, altrimenti i test si bloccano.
- Un warning `act(...)` indica uno stato che cambia fuori dal test: aspetta l'esito invece di silenziarlo.

## Error boundary e Suspense
- Per l'error boundary, silenzia `console.error` solo in quel test e verifica il fallback. Per Suspense, `findBy…` sul contenuto finale.

## End-to-end
- Per il flusso critico e per i server component: Playwright o Cypress del progetto. Selettori per ruolo ed etichetta, non classi CSS.
