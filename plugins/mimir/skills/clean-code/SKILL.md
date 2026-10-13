---
name: clean-code
description: Best practice trasversali di codice. Usala quando scrivi, modifichi, rifattorizzi o rivedi codice in qualsiasi linguaggio, o l'utente chiede come renderlo pulito e manutenibile.
---

# Clean Code

Linee guida trasversali. Precedenza: **convenzioni del progetto > skill del linguaggio o dell'architettura > questa skill**.

I limiti numerici (righe, campi, argomenti) sono **segnali**: superarli richiede una ragione, non è vietato. L'obiettivo è la leggibilità, non rispettare una soglia.

## Riferimenti
Leggi solo quelli pertinenti al compito:

| File | Quando |
|---|---|
| [references/principi.md](references/principi.md) | Sempre, quando scrivi o rivedi codice: principi, struttura di metodi e condizioni, organizzazione del file |
| [references/oop.md](references/oop.md) | Codice a oggetti: SOLID, Demetra, coesione, polimorfismo, classi utility |
| [references/naming.md](references/naming.md) | Quando dai nomi o rivedi nomi |
| [references/errori-logging.md](references/errori-logging.md) | Gestione di eccezioni ed errori, logging |
| [references/test.md](references/test.md) | Quando scrivi o organizzi test |
| [references/sicurezza.md](references/sicurezza.md) | Codice che tratta input esterni, autenticazione, dati sensibili, dipendenze, parsing |
| [references/prestazioni.md](references/prestazioni.md) | Query, filtri, chiamate di rete, paginazione o lavoro a ogni interazione dell'utente |
| [references/a11y.md](references/a11y.md) | Interfacce web: elementi e ruoli, form, focus e tastiera, contenuti dinamici, contrasto (per ogni framework) |
| [references/smell.md](references/smell.md) | Review e refactoring: segnali di design da valutare, non regole |
| [references/ricevere-review.md](references/ricevere-review.md) | Quando arrivano osservazioni da una review (umana o di un agent) |

## Checklist rapida (review)
- [ ] La soluzione è la più semplice che risolve il problema?
- [ ] I nomi rendono superflui i commenti sul *cosa*?
- [ ] Le condizioni complesse hanno un nome?
- [ ] Niente magic number o stringhe magiche?
- [ ] Complessità cognitiva contenuta (≤ 15), guard clause invece di annidamenti profondi (massimo 2 livelli)?
- [ ] Niente flag booleani che selezionano comportamenti diversi?
- [ ] Niente `null` restituiti, niente eccezioni inghiottite, niente fallback che nascondono un errore?
- [ ] Le eccezioni rilanciate conservano la causa? Le chiamate esterne hanno un timeout?
- [ ] I commenti toccati dicono ancora il vero?
- [ ] I log hanno contesto e nessun dato sensibile?
- [ ] Input esterni validati, query parametrizzate, autorizzazione verificata sulla risorsa?
- [ ] Le chiamate e le query per azione dell'utente sono contate, e i filtri usano un indice?
- [ ] Nessuna nuova dipendenza non motivata?
- [ ] La logica nuova è coperta da test che descrivono un comportamento?
- [ ] Analisi statica e linter del progetto puliti?

### Quale review
Strumenti diversi per domande diverse; non lanciarli tutti sullo stesso diff.
- **Agent `mimir:code-reviewer`**: la review di default prima di un commit o di una MR. Sola lettura, aderenza alla richiesta, correttezza, sicurezza, perimetro, con le skill e le regole di Mímir.
- **Agent `mimir:design-reviewer`**: esperienza e qualità visiva di una UI (aderenza, usabilità, accessibilità, stati, aspetto), non il codice. Accanto a `mimir:code-reviewer` quando il diff tocca un'interfaccia.
- **`/simplify`**: pulizia del diff (riuso, semplificazione, efficienza, livello di astrazione), non cerca bug e **applica** le modifiche. Proponilo dopo che il codice funziona e i test sono verdi; poi guarda il diff e rilancia i test.
- **`/code-review`**: caccia ai bug di Claude Code su un diff, un branch o una PR, utile come seconda opinione indipendente da Mímir. `--fix` applica le correzioni e, se gira in background, `/rewind` non le annulla (serve git); `--comment` pubblica sulla PR o MR e `ultra` manda il codice a una revisione nel cloud: entrambi solo su richiesta esplicita dell'utente.

## File e formattazione
- Rispetta `.editorconfig`, `.gitattributes` e il formatter del progetto. In mancanza: UTF-8, fine riga LF.
- Non riformattare codice che non stai modificando: sporca il diff.
