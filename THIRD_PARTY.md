# Materiale di terzi

Alcuni file di Mímir sono traduzioni o adattamenti in italiano di opere di terzi, usati secondo la loro licenza. Gli altri file sono sotto la licenza MIT di Mímir ([LICENSE](LICENSE)).

L'elenco viene da un confronto sistematico del 10/10, fonte per fonte e file per file, sui file di design (`design-ui`, `animazioni-ui`, `ui-casi-limite`, `prototipi-ui`, agent `design-reviewer`): ordine delle sezioni, frasi tradotte, esempi e costanti. Va svuotato, riscrivendo o eliminando i file, oppure giustificato voce per voce prima che il repo diventi pubblico.

## skills di Emil Kowalski

- **Fonte**: https://github.com/emilkowalski/skills
- **Licenza**: MIT (testo in fondo, con il copyright di Emil Kowalski).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `plugins/mimir/skills/animazioni-ui/SKILL.md` | `skills/animate/SKILL.md` (frequenza, scopo, strumenti, proprietà, curve e durate, interruzione, accessibilità); "Revisione" da `skills/review-animations/SKILL.md` e `skills/find-animation-opportunities/SKILL.md`; spring e accessibilità in parte da `skills/apple-design/SKILL.md` | traduzione con modifiche |
| `plugins/mimir/skills/animazioni-ui/references/ricette.md` | `skills/animate/RECIPES.md` (stesse ricette nello stesso ordine, tranne il trascinamento, spostato in `gesti-e-spring.md`); tabella "Mai" da `skills/animate/SKILL.md` ("Never Ship"); tabella "Prestazioni" da `performance-cheatsheet.md` | traduzione con modifiche |
| `plugins/mimir/skills/animazioni-ui/references/gesti-e-spring.md` | `skills/apple-design/SKILL.md` (a sua volta ricavata dai talk WWDC di Apple); trascinamento e soglie da `skills/animate/RECIPES.md` | traduzione con modifiche |
| `plugins/mimir/skills/animazioni-ui/references/vocabolario.md` | `skills/animation-vocabulary/SKILL.md` (selezione dei termini, categorie, coppie da distinguere) | adattamento |
| `plugins/mimir/skills/ui-casi-limite/SKILL.md` | `skills/break-ui/SKILL.md` | traduzione con modifiche |
| `plugins/mimir/skills/ui-casi-limite/references/catalogo.md` | "Firme dei guasti" da `skills/break-ui/SKILL.md`; tabelle per tipo di dato da `skills/break-ui/CATALOG.md` | traduzione (firme); adattamento con dati d'esempio propri (tabelle) |
| `plugins/mimir/skills/prototipi-ui/SKILL.md` | `skills/prototype/SKILL.md`, `skills/prototype/PICKER.md` | traduzione con modifiche |
| `plugins/mimir/skills/design-ui/references/mobile-web.md` | `skills/mobile-native/SKILL.md` (tabella dei sintomi, base di partenza, prova) | traduzione con modifiche |

## taste-skill

- **Fonte**: https://github.com/Leonxlnx/taste-skill
- **Licenza**: MIT (testo in fondo, con il copyright di Leonxlnx).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `plugins/mimir/skills/design-ui/SKILL.md` | `skills/taste-skill/SKILL.md`: lettura della richiesta e frase da dichiarare (§0), tre assi (§1, anche `skills/taste-skill-v1/SKILL.md`), base e design system (§2), costruzione (§4), default da rifiutare (§9), verifica (§14) | adattamento, con parti tradotte |
| `plugins/mimir/skills/design-ui/references/pagine-marketing.md` | `skills/taste-skill/SKILL.md` (§4.7-4.10 soglie della pagina marketing, §6.D prestazioni) | traduzione con modifiche |
| `plugins/mimir/skills/design-ui/references/anti-pattern.md` | `skills/redesign-skill/SKILL.md`, `skills/taste-skill/SKILL.md` (§4, §9) | adattamento, con parti tradotte |
| `plugins/mimir/skills/design-ui/references/rifacimento.md` | `skills/taste-skill/SKILL.md` (§11); `skills/redesign-skill/SKILL.md` (priorità delle correzioni, omissioni) | traduzione con modifiche |

## impeccable

- **Fonte**: https://github.com/pbakaus/impeccable
- **Licenza**: Apache License 2.0, Copyright 2025 Paul Bakaus. Testo in [LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt). Il `NOTICE.md` di impeccable riguarda solo `skill/reference/ios.md` e `android.md`, che Mímir non usa.
- **Modifiche**: testo tradotto in italiano, ridotto e riorganizzato dentro procedure di Mímir.
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `plugins/mimir/skills/design-ui/SKILL.md` | `skill/reference/craft-floor.md` (default da rifiutare, verifica, elementi del browser, tema, copy); `skill/reference/mode-operate.md`, `mode-read.md`, `mode-persuade.md`, `operate.md` (superfici: lavorare, leggere, convincere); `skill/reference/clarify.md` (copy e stati); `skill/SKILL.src.md` (giri di correzione) | adattamento, con parti tradotte |
| `plugins/mimir/skills/design-ui/references/pagine-marketing.md` | `skill/reference/mode-persuade.md` (azione principale nella forma funzionante) | traduzione di un punto |
| `plugins/mimir/skills/design-ui/references/anti-pattern.md` | `skill/reference/craft-floor.md` (selezione delle voci) | adattamento |
| `plugins/mimir/agents/design-reviewer.md` | `skill/reference/critique.md` (euristiche, carico cognitivo, due utenti, cosa funziona, gravità); `skill/agents/impeccable-finish-reviewer.md` (solo l'idea del revisore a contesto separato che confronta con i default da rifiutare; nessuna frase in comune) | adattamento |

## Skill, agent e regole

Confronto del 10/10 sul resto di Mímir (skill di `plugins/mimir` tranne quelle di design, skill di `plugins/brokkr`, agent, `rules/`, `CLAUDE.md`, `profile/profile.example.md`, testi degli hook) contro i repo di Matt Pocock, superpowers, ECC, hermes-agent, openclaw, system-design-primer e developer-roadmap. Metodo di `plugins/mimir/skills/scrivi-skill/references/fonti-esterne.md`; ogni derivazione è stata ricontrollata a mano sulle righe dei due file. Limiti: le controparti nelle fonti grandi (ECC, openclaw, hermes-agent, system-design-primer, developer-roadmap) sono state individuate per nome e descrizione dei file, con in più una ricerca di 26 frasi e costanti distintive di otto file di Mímir (`tdd`, `debugging`, `retro`, `pianificazione`, `delega`, `contesto-e-costi`, `code-reviewer`, `security-reviewer`); un file della fonte con un nome lontano dal tema può essere sfuggito. Un file di Mímir può avere più fonti: compare in ognuna. Nella colonna "Origine" le sezioni tra parentesi sono quelle di Mímir in cui sta la parte derivata, non i titoli della fonte.

### skills di Matt Pocock

- **Fonte**: https://github.com/mattpocock/skills
- **Licenza**: MIT (testo in fondo, con il copyright di Matt Pocock).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `plugins/mimir/skills/decisioni/SKILL.md` | `skills/productivity/to-questionnaire/SKILL.md` (sezione "Quando mancano le informazioni": a chi va, cosa deve tornare, domande una per idea in ordine d'importanza, copertura) | adattamento, con parti tradotte |
| `plugins/brokkr/skills/analisi-funzionale/templates/domande.md` | `skills/productivity/to-questionnaire/SKILL.md` (sezione "Forma da inviare" e domande non composte) | adattamento |
| `plugins/mimir/skills/clean-code/references/smell.md` | `skills/engineering/code-review/SKILL.md` (smell come giudizi, elenco e correzioni); test di eliminazione da `skills/engineering/codebase-design/SKILL.md` | traduzione con modifiche |
| `plugins/mimir/agents/code-reviewer.md` | `skills/engineering/code-review/SKILL.md` (diff a tre punti, aderenza alla richiesta) | adattamento, con parti tradotte |
| `plugins/mimir/skills/debugging/SKILL.md` | `skills/engineering/diagnosing-bugs/SKILL.md` (ciclo di riproduzione e modi di costruirlo, stringere il ciclo, `git bisect run`, causa non trovata, strumentazione ai confini) | adattamento |
| `plugins/mimir/skills/debugging/references/tecniche.md` | `skills/engineering/diagnosing-bugs/SKILL.md` ("misura prima" per le prestazioni) | adattamento di un punto |
| `plugins/mimir/skills/passaggio-consegne/SKILL.md` | `skills/productivity/handoff/SKILL.md` (le cinque istruzioni: cartella temporanea, skill suggerite, rimandi invece di copie, dati oscurati, prossima sessione) | adattamento |
| `plugins/mimir/skills/pianificazione/SKILL.md` | `skills/productivity/grilling/SKILL.md` (interrogatorio a round: frontiera delle decisioni con premesse chiuse, risposta consigliata, fatti cercati nel codice) | adattamento |

### superpowers

- **Fonte**: https://github.com/obra/superpowers
- **Licenza**: MIT (testo in fondo, con il copyright di Jesse Vincent).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `plugins/mimir/skills/clean-code/references/ricevere-review.md` | `skills/receiving-code-review/SKILL.md` (leggere tutto, chiarire prima, verificare sul codice, controllo YAGNI, ordine delle correzioni, risposta motivata) | adattamento, con parti tradotte |
| `plugins/mimir/agents/code-reviewer.md` | `skills/requesting-code-review/code-reviewer.md` (passate dichiarate, tre gravità, esito a tre stati, forma della segnalazione) | adattamento, con parti tradotte |
| `plugins/mimir/skills/debugging/SKILL.md` | `skills/systematic-debugging/SKILL.md` (§3 "Restringere", §4 "Dopo 2-3 fix falliti"); arriva anche tramite la copia di hermes-agent | adattamento |

### ECC

- **Fonte**: https://github.com/affaan-m/ECC
- **Licenza**: MIT (testo in fondo, con il copyright di Affaan Mustafa).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `plugins/brokkr/skills/rilascio/references/migrazioni-db.md` | `skills/database-migrations/SKILL.md` (principi, volumi realistici, espandi e contrai, rinomina di colonna) | adattamento, con parti tradotte |
| `plugins/mimir/skills/database/SKILL.md` | `skills/database-migrations/SKILL.md` (sezione "Migrazioni dello schema", nel dubbio) | adattamento |
| `plugins/brokkr/skills/analisi-funzionale/SKILL.md` | `agents/spec-miner.md` (regole come requisiti o invarianti con ID, punto che le impone e test; lettura dai punti d'ingresso un livello alla volta; segnalare senza correggere) | adattamento |
| `plugins/brokkr/skills/analisi-funzionale/templates/scheda-modulo.md` | `agents/spec-miner.md` (ID stabile, commit di riferimento) | adattamento |
| `plugins/brokkr/skills/manutenzione-legacy/SKILL.md` | `skills/inherit-legacy-style/SKILL.md`, contributo della community, licenza del contributore non verificata (§3 "Diff minimo": file esemplari, dichiarazione, maggioranza, difetti da non copiare) | adattamento, con parti tradotte |
| `plugins/mimir/skills/clean-code/references/errori-logging.md` | `agents/silent-failure-hunter.md` (sezione "Fallimenti silenziosi": stesso esempio e stessa sequenza, nel dubbio) | adattamento |
| `plugins/mimir/agents/code-reviewer.md` | `agents/silent-failure-hunter.md` (la frase sui fallimenti silenziosi della correttezza) | adattamento di un punto |
| `plugins/mimir/skills/typescript/references/progettazione-tipi.md` | `agents/type-design-analyzer.md` (le quattro domande). Lo stesso schema c'è nell'agent `type-design-analyzer` del plugin pr-review-toolkit di Anthropic: possibile fonte comune, non verificata | adattamento |
| `plugins/mimir/skills/vue/SKILL.md` | `rules/vue/patterns.md`, `rules/vue/security.md` (composable, provide/inject, Pinia, router, sicurezza: selezione, ordine e frasi, nel dubbio) | adattamento |
| `plugins/mimir/skills/vue/references/test-vue.md` | `rules/vue/testing.md` (Pinia e composable, nel dubbio) | adattamento |
| `plugins/mimir/skills/decisioni/references/prospettive.md` | `skills/council/SKILL.md` (sezione "Con i subagent": voci indipendenti, forma del resoconto, disaccordo visibile; nel dubbio) | adattamento |

### hermes-agent

- **Fonte**: https://github.com/NousResearch/hermes-agent
- **Licenza**: MIT (testo in fondo, con il copyright di Nous Research). Diverse skill dichiarano nel frontmatter un autore diverso e `license: MIT`: l'autore è indicato nella riga. I repo originali di questi autori non sono stati consultati.
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `plugins/mimir/skills/retro/SKILL.md` | `agent/background_review.py` (cosa non catturare, ordine delle destinazioni, forma della lezione, leggere prima di scrivere) | adattamento, con parti tradotte |
| `plugins/mimir/skills/pianificazione/SKILL.md` | `optional-skills/software-development/grill-me/SKILL.md`, di Rafael Zendron con Hermes Agent (quando usarlo, copertura delle domande, "non so", niente codice, sintesi finale) | adattamento |
| `plugins/mimir/skills/pianificazione/SKILL.md` | `skills/software-development/spike/SKILL.md`, di Hermes Agent, adattata da gsd-build/get-shit-done (sezione "Spike"); la licenza dell'originale non è verificata | adattamento, con parti tradotte |
| `plugins/mimir/skills/decisioni/SKILL.md`, `plugins/mimir/skills/decisioni/templates/registro-decisioni.md` | `optional-skills/communication/one-three-one-rule/SKILL.md`, di Willard Moore (brief 1-3-1) | adattamento, con parti tradotte |
| `plugins/mimir/skills/riunioni/SKILL.md`, `plugins/mimir/skills/riunioni/templates/verbale.md` | `skills/productivity/meeting-action-items/SKILL.md`, di Ben Barclay con Hermes Agent (sezione "Da appunti o trascrizioni", tabella delle azioni) | adattamento, con parti tradotte |
| `plugins/brokkr/skills/stato-e-rischi/SKILL.md` | `skills/productivity/document-to-action-items/SKILL.md`, di Ben Barclay con Hermes Agent (sezione "Da documenti") | adattamento, con parti tradotte |
| `plugins/mimir/skills/ricerca/SKILL.md`, `plugins/mimir/skills/ricerca/references/citazioni.md` | `skills/research/grounded-citations/SKILL.md` e `references/citation-formats.md`, di Hermes Agent con Teknium (citazioni durante la lettura, massimo tre per frase, posizione per formato) | adattamento |
| `plugins/mimir/skills/documentazione-tecnica/SKILL.md` | `optional-skills/software-development/code-wiki/SKILL.md`, di Teknium con Hermes Agent (sezione "Mappa del codice") | adattamento, con parti tradotte |
| `plugins/mimir/agents/code-reviewer.md` | `skills/software-development/simplify-code/SKILL.md`, ispirata a `/simplify` di Claude Code (git blame prima di togliere, nomi pubblici come contratti, costo della segnalazione) | adattamento, con parti tradotte |
| `rules/working-style.md` | `SOUL.md` (due frasi: d'accordo perché è giusto; cosa è cambiato, cosa è verificato, cosa resta) | traduzione di due frasi |

## Valutati e non inclusi
Sovrapposizioni di sola idea, senza frasi, struttura o costanti in comune; restano qui perché un controllo futuro non le rifaccia da capo.
- `prototipi-ui`: `skills/engineering/prototype` di Matt Pocock (`github.com/mattpocock/skills`) e `skill/reference/live.md` di impeccable hanno la stessa idea (varianti su assi diversi, barra in basso, variante nell'URL), con testo diverso.
- `ui-casi-limite`: `skill/reference/harden.md` di impeccable, elenchi tematici simili, struttura e ordine diversi.
- `design-ui`: `skill/reference/typeset.md` di impeccable (cifre tabulari) solo tematico; la famiglia unica con scala fissa di `design-ui` è già coperta da `operate.md`; il resto del repo ECC (`make-interfaces-feel-better`, `motion-*`, `design-system`) solo luoghi comuni.
- `pianificazione`: la frase sul piano più lungo del codice ricorda `skills/writing-plans/SKILL.md` di superpowers (stesso inizio, conclusione diversa); va comunque riformulata. Il resto della skill, `tdd`, `delega`, `scrivi-skill`, `git-workflow` e `rules/` hanno con superpowers solo temi in comune.
- `retro`: `docs/tools/self-learning.md` di openclaw ha un elenco di esclusioni simile, comune anche a hermes-agent; i tratti specifici di `retro` vengono da hermes-agent (sopra).
- `sicurezza-claude-code/references/inventario.md`: i segnali di attacco (hook con `curl`/`wget`, `enableAllProjectMcpServers`, `ANTHROPIC_BASE_URL`) compaiono anche in `the-security-guide.md` di ECC; sono i risultati pubblici di Check Point Research (CVE-2025-59536, CVE-2026-21852), fonte comune.
- `typescript`, `nodejs/references/framework.md` (NestJS), `database` (indici, transazioni, paginazione), `angular/references/test-angular.md`: voci in comune con `agents/typescript-reviewer.md`, `skills/nestjs-patterns`, `agents/database-reviewer.md`, `rules/angular/testing.md` di ECC, tutte dalla documentazione ufficiale, con struttura diversa e nessuna frase distintiva. Le altre skill di linguaggio, processo e architettura hanno con ECC solo temi in comune; `script-shell`, `ddd`, `sistemi-distribuiti` nessuno.
- Matt Pocock: `tdd`, `retro`, `ricerca`, `ddd`, `refactoring`, `ticket`, `scrivi-skill` e `delega`, l'hook `git-guard` (rispetto a `git-guardrails`) solo temi in comune.
- hermes-agent: `growth`, l'hook di retro, `manutenzione-mimir`, `scrivi-skill`, `contesto-e-costi`, `delega`, `tdd`, `security-reviewer`, `refactoring`, `clean-code`, `commit`, `container`, `passaggio-consegne` e il resto di `working-style` solo temi in comune.
- openclaw (`AGENTS.md`, template dei ruoli, skill e documentazione): solo temi in comune con `rules/`, `CLAUDE.md`, `code-reviewer`, `debugging`, `scrivi-skill`, `documentazione-tecnica`, `contesto-e-costi`.
- system-design-primer (CC BY 4.0): `sistemi-distribuiti`, `database`, `design-api`, `stime`, `architetto` hanno solo temi in comune, senza cifre né elenchi ripresi.
- developer-roadmap (licenza proprietaria): nessuna derivazione; `code-reviewer`, `design-api`, `gestione-persone`, `clean-code` e i nodi su Claude Code hanno solo temi in comune (ricerca di frasi distintive: nessun riscontro).

## Testi della licenza MIT

### skills di Emil Kowalski
```
MIT License

Copyright (c) 2026 Emil Kowalski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### taste-skill
```
MIT License

Copyright (c) 2026 Leonxlnx

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### skills di Matt Pocock
```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### superpowers
```
MIT License

Copyright (c) 2025 Jesse Vincent

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### ECC
```
MIT License

Copyright (c) 2026 Affaan Mustafa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### hermes-agent
```
MIT License

Copyright (c) 2025 Nous Research

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
