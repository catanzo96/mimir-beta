# Test in Angular: casi specifici

Si applica insieme a `clean-code/references/test.md`. Il runner e le librerie sono quelli del progetto. Le API indicate valgono per le versioni recenti: nel legacy controlla quella installata.

## Componenti
- Input signal: impostali con `fixture.componentRef.setInput('nome', valore)`, non assegnando la proprietà.
- Output: iscriviti all'output dell'istanza e verifica i valori emessi dopo un'azione sul DOM.
- Con change detection zoneless (default dalla v21), dopo un'azione attendi `await fixture.whenStable()` invece di contare solo su `detectChanges()`.
- Component harness (`TestbedHarnessEnvironment.loader(fixture)`) per i componenti di Material e CDK, e per quelli del progetto che ne hanno uno: i test non dipendono dalla struttura interna del DOM.

## Pipe, guard e resolver
- Le pipe pure sono funzioni: istanziale direttamente, senza TestBed.
- Guard e resolver funzionali: eseguili in un contesto di injection (`TestBed.runInInjectionContext(() => guard(route, state))`), con le dipendenze sostituite tramite provider.
- Navigazione e componenti di route con `RouterTestingHarness` e `provideRouter(routes)`: verifichi l'esito reale (componente mostrato, redirect) invece di mockare il router.

## HTTP
- `provideHttpClient()` e `provideHttpClientTesting()`, poi `HttpTestingController` per attendere e rispondere alle richieste.
- `verify()` dopo ogni test: segnala richieste inattese o mai risposte.
- Prova anche le risposte di errore (404, 500, timeout), non solo quella felice.

## End-to-end
- Il framework è quello del progetto (Playwright, Cypress…). Nessuno nuovo senza ok.
- Pochi flussi critici, non tutta l'applicazione: il grosso dei controlli sta negli unit test.
- Selettori stabili: ruolo ed etichetta accessibile, oppure un attributo dedicato (es. `data-testid`). Non classi CSS né testi che cambiano con le traduzioni.
- Niente attese fisse: si attende una condizione (elemento visibile, richiesta completata).
- Ogni test prepara i propri dati e non dipende dall'ordine degli altri.
- Un test instabile si indaga (tempi, dati condivisi, animazioni, ambiente) invece di aggiungere tentativi automatici. Se va messo da parte, con un ticket e il motivo.
- In CI, traccia e screenshot sui fallimenti, se il progetto li conserva.
