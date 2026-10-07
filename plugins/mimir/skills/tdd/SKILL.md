---
name: tdd
description: Ciclo rosso-verde-refactor come strumento. Usala per logica di dominio, parser e calcoli, per riprodurre un bug con un test prima di correggerlo, o se si chiede TDD.
---

# TDD

Si applica insieme a `clean-code` (principi dei test in `clean-code/references/test.md`), alla skill del linguaggio e a `refactoring` per il terzo passo. Framework, struttura dei test e convenzioni del progetto prevalgono.

Il TDD è uno strumento, non un obbligo. Mímir chiede che la logica critica sia coperta da test; come ci arrivi e quali soglie di coverage valgano lo decide il progetto. Usa il ciclo quando ti aiuta a pensare, lascialo quando ti rallenta.

## Quando conviene
- Logica di dominio con regole e casi limite: calcoli, tariffe, stati, validazioni.
- Parser, formattatori, conversioni, algoritmi: input e output ben definiti.
- Bug da riprodurre: il test rosso dimostra che l'hai capito e che la correzione funziona. Vale anche quando il resto del progetto non usa TDD.
- API di una libreria o di un modulo: scrivere prima l'uso mostra se l'interfaccia è scomoda.
- Refactoring di codice senza rete: i test di caratterizzazione vanno scritti prima (vedi `refactoring`).

## Quando no
- Spike e prototipi che butterai: esplora, poi scrivi i test sul codice che tieni.
- UI esplorativa, dove non sai ancora cosa vuoi vedere: prima il risultato, poi i test sui comportamenti che si stabilizzano.
- Codice di integrazione e configurazione (wiring, adapter sottili): i test unitari qui duplicano l'implementazione. Servono test di integrazione, anche dopo.
- Codice generato o senza logica.

Se rinunci al ciclo, i test sul codice che rimane restano dovuti quando la logica è critica.

## Il ciclo
1. **Rosso.** Scrivi un solo test, per il prossimo comportamento. Eseguilo e **guardalo fallire per il motivo giusto**.
   - Giusto: l'asserzione fallisce perché il comportamento manca (valore atteso diverso, eccezione non lanciata).
   - Sbagliato: errore di compilazione, import mancante, setup rotto, NPE nel test. Correggi il test finché fallisce per il comportamento. Un test mai visto fallire può non verificare nulla.
2. **Verde.** Scrivi il codice più semplice che fa passare quel test, anche banale o costante. Rieseguilo: tutti i test devono essere verdi.
3. **Refactoring.** Con la rete verde, ripulisci codice e test (duplicazioni, nomi, struttura) a piccoli passi, rieseguendo i test. Non aggiungi comportamento in questo passo.
4. Ripeti con il comportamento successivo.

## Il passo più piccolo
- Un test = un comportamento, non un metodo. Il nome lo descrive ("applica lo sconto oltre 100 euro"), non dice `testCalcola`.
- Se il passo verde ti sembra troppo grande (molte righe, più rami), il test era troppo ambizioso: ricomincia con un caso più semplice.
- Ordina i test dal più semplice (caso vuoto, un elemento, valore zero) al più ricco. Il codice cresce guidato dai casi, non da un disegno anticipato.
- Se rosso e verde non arrivano in pochi minuti, riduci il passo.

## Triangolazione
Con un solo esempio, il codice più semplice è restituire la costante attesa. Un secondo esempio con un altro valore ti obbliga a generalizzare. Usala quando la regola non è ovvia; se la formula è chiara, scrivila subito e metti negli esempi i casi di confine (zero, negativo, massimo, vuoto, duplicati, fuso orario).

## Test come specifica
- Il test dice **cosa** deve fare il codice osservabile da fuori, non **come**. Un test che si rompe a ogni refactoring verifica l'implementazione: riscrivilo sul comportamento.
- Leggi i nomi dei test in sequenza: devono raccontare le regole del modulo. Sono la documentazione che non invecchia.
- Un bug in produzione diventa un test che riproduce il caso reale (con dati anonimi), poi la correzione.
- I test che hai scritto sono codice: leggibili, senza logica condizionale, con i dati rilevanti visibili (niente mystery guest, vedi `test.md`).

## Outside-in e inside-out
- **Inside-out**: parti dal dominio (le unità piccole), poi componi verso l'esterno. Adatto quando le regole sono il cuore e l'interfaccia è semplice.
- **Outside-in**: parti da un test che attraversa il caso d'uso (un endpoint, un comando), lo lasci rosso, e scendi realizzando le parti che servono. Adatto quando conta il flusso e vuoi evitare codice che nessuno usa. Rischio: test grossi e lenti. Tienine pochi, e guida i dettagli con test unitari.
- Si possono alternare: un test di accettazione a guidare, un ciclo interno rosso-verde-refactor per ogni pezzo.

## Doppi di test
- Solo ai confini: database, rete, tempo, casualità, servizi esterni. Dominio e value object restano reali (`test.md`).
- Preferisci un fake semplice (repository in memoria) a un mock con aspettative sulle chiamate: sopravvive meglio ai refactoring.
- Se per testare un'unità devi mockare molte cose, il segnale è di design (troppe dipendenze), non di test: vedi `smell.md`.
- Tempo e casualità si iniettano; niente `sleep` nei test.

## Trappole
- Scrivere molti test insieme e poi il codice: si perde il feedback e il motivo per cui un test fallisce.
- Test verdi al primo colpo: dubita finché non li hai visti fallire.
- Modificare il test per farlo passare quando il codice è sbagliato.
- Ottimizzare la coverage: un test senza asserzioni significative alza il numero e non protegge nulla.
- Test dipendenti dall'ordine o da stato condiviso tra casi.

## Verifica
- Lancia i test del modulo e poi l'intera suite con lo strumento del progetto (`mvn test`, `gradle test`, `npm test`, `pytest`, `go test ./...`…), più linter e analisi statica.
- Per i test nuovi dichiara di averli visti fallire prima della correzione (o su quale mutazione del codice).
- Nel resoconto: comportamenti coperti, comandi con esito, cosa resta non testato e perché.
