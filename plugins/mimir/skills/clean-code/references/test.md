# Test

## Cosa testare
- La logica: regole di dominio, orchestrazione, conversioni e mapper, validatori.
- La logica critica è sempre coperta. Le soglie di coverage le decide il progetto.
- Escludi dalla coverage ciò che non ha logica: test, dati di test, codice generato, configurazione.

## Come scriverli
- **Un test, un comportamento.**
- **Struttura Arrange, Act, Assert** (o Given, When, Then), con le tre parti visibili.
- **Nome parlante**: comportamento e condizione (vedi [naming.md](naming.md)). Se il framework lo consente, aggiungi una descrizione discorsiva.
- **Deterministici**: niente dipendenze da ora corrente, ordine, rete o casualità non controllata. Tempo e generatori vanno iniettati.
- **Isolati, senza over-mocking**: negli unit test si sostituiscono con mock o fake solo le dipendenze ai confini (porte, client, repository, orologio).
  - Oggetti di dominio e value object restano reali: mockarli rende i test fragili e legati all'implementazione.
  - Gli adapter verso tecnologie reali si verificano con test di integrazione.
- Verifica il comportamento osservabile, non i dettagli di implementazione.

## Livelli
- **Molti unit test** (logica, veloci), **alcuni test di integrazione** (adapter, persistenza, contratti tra componenti), **pochi end-to-end** (flussi critici).
- Un bug trovato in produzione diventa prima un test che fallisce, poi la correzione.

## Organizzazione
- I test rispecchiano la struttura del codice di produzione (stessi package e moduli).
- **Dati di test centralizzati** in factory o builder riusabili (Object Mother, Test Data Builder), con valori di default validi. Riducono la duplicazione e reggono meglio quando i modelli cambiano.
- **Niente mystery guest**: nel test imposta esplicitamente i dati da cui dipende l'asserzione, anche se coincidono con il default. Chi legge deve capire il test senza aprire la factory.
  ```java
  var ordine = OrdineMockFactory.builder().importo(ZERO).build();   // l'importo è ciò che il test verifica
  ```

## Prima del merge
- Suite verde, e quality gate del progetto (es. Sonar) verde.
