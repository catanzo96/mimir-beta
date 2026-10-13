# Materiale di terzi

Alcuni file di questo plugin sono traduzioni o adattamenti in italiano di opere di terzi, usati secondo la loro licenza. Gli altri file sono sotto la licenza MIT di Mímir (file `LICENSE` nella radice del repository). I percorsi qui sotto sono relativi alla cartella del plugin.

L'elenco viene da due confronti sistematici del 10/10, fonte per fonte e file per file: uno sui file di design (`design-ui`, `animazioni-ui`, `ui-casi-limite`, `prototipi-ui`, agent `design-reviewer`), l'altro sulle altre skill, sugli agent e sui testi degli hook (sezione "Skill e agent"). Entrambi guardano ordine delle sezioni, frasi tradotte, esempi e costanti. Le fonti hanno licenze permissive, quindi i file derivati restano con questa attribuzione; quelli derivati da fonti Apache-2.0 portano anche l'avviso di modifica nel file. Le regole sono in `skills/scrivi-skill/references/fonti-esterne.md` (§5).

## skills di Emil Kowalski

- **Fonte**: https://github.com/emilkowalski/skills
- **Licenza**: MIT (testo in fondo, con il copyright di Emil Kowalski).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `skills/animazioni-ui/SKILL.md` | `skills/animate/SKILL.md` (frequenza, scopo, strumenti, proprietà, curve e durate, interruzione, accessibilità); "Revisione" da `skills/review-animations/SKILL.md` e `skills/find-animation-opportunities/SKILL.md`; spring e accessibilità in parte da `skills/apple-design/SKILL.md` | traduzione con modifiche |
| `skills/animazioni-ui/references/ricette.md` | `skills/animate/RECIPES.md` (stesse ricette nello stesso ordine, tranne il trascinamento, spostato in `gesti-e-spring.md`); tabella "Mai" da `skills/animate/SKILL.md` ("Never Ship"); tabella "Prestazioni" da `performance-cheatsheet.md` | traduzione con modifiche |
| `skills/animazioni-ui/references/gesti-e-spring.md` | `skills/apple-design/SKILL.md` (a sua volta ricavata dai talk WWDC di Apple); trascinamento e soglie da `skills/animate/RECIPES.md` | traduzione con modifiche |
| `skills/animazioni-ui/references/vocabolario.md` | `skills/animation-vocabulary/SKILL.md` (selezione dei termini, categorie, coppie da distinguere) | adattamento |
| `skills/ui-casi-limite/SKILL.md` | `skills/break-ui/SKILL.md` | traduzione con modifiche |
| `skills/ui-casi-limite/references/catalogo.md` | "Firme dei guasti" da `skills/break-ui/SKILL.md`; tabelle per tipo di dato da `skills/break-ui/CATALOG.md` | traduzione (firme); adattamento con dati d'esempio propri (tabelle) |
| `skills/prototipi-ui/SKILL.md` | `skills/prototype/SKILL.md`, `skills/prototype/PICKER.md` | traduzione con modifiche |
| `skills/design-ui/references/mobile-web.md` | `skills/mobile-native/SKILL.md` (tabella dei sintomi, base di partenza, prova) | traduzione con modifiche |

## taste-skill

- **Fonte**: https://github.com/Leonxlnx/taste-skill
- **Licenza**: MIT (testo in fondo, con il copyright di Leonxlnx).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `skills/design-ui/SKILL.md` | `skills/taste-skill/SKILL.md`: lettura della richiesta e frase da dichiarare (§0), tre assi (§1, anche `skills/taste-skill-v1/SKILL.md`), base e design system (§2), costruzione (§4), default da rifiutare (§9), verifica (§14) | adattamento, con parti tradotte |
| `skills/design-ui/references/pagine-marketing.md` | `skills/taste-skill/SKILL.md` (§4.7-4.10 soglie della pagina marketing, §6.D prestazioni) | traduzione con modifiche |
| `skills/design-ui/references/anti-pattern.md` | `skills/redesign-skill/SKILL.md`, `skills/taste-skill/SKILL.md` (§4, §9) | adattamento, con parti tradotte |
| `skills/design-ui/references/rifacimento.md` | `skills/taste-skill/SKILL.md` (§11); `skills/redesign-skill/SKILL.md` (priorità delle correzioni, omissioni) | traduzione con modifiche |

## impeccable

- **Fonte**: https://github.com/pbakaus/impeccable
- **Licenza**: Apache License 2.0, Copyright 2025 Paul Bakaus. Testo in [LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt). Il `NOTICE.md` di impeccable riguarda solo `skill/reference/ios.md` e `android.md`, che Mímir non usa.
- **Modifiche**: testo tradotto in italiano, ridotto e riorganizzato dentro procedure di Mímir. Ogni file elencato porta l'avviso di modifica (punto 4(b) della licenza) come commento nella prima riga del frontmatter o, nei file senza frontmatter, come riga in corsivo in fondo.
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `skills/design-ui/SKILL.md` | `skill/reference/craft-floor.md` (default da rifiutare, verifica, elementi del browser, tema, copy); `skill/reference/mode-operate.md`, `mode-read.md`, `mode-persuade.md`, `operate.md` (superfici: lavorare, leggere, convincere); `skill/reference/clarify.md` (copy e stati); `skill/SKILL.src.md` (giri di correzione) | adattamento, con parti tradotte |
| `skills/design-ui/references/pagine-marketing.md` | `skill/reference/mode-persuade.md` (azione principale nella forma funzionante) | traduzione di un punto |
| `skills/design-ui/references/anti-pattern.md` | `skill/reference/craft-floor.md` (selezione delle voci) | adattamento |
| `agents/design-reviewer.md` | `skill/reference/critique.md`, `skill/agents/impeccable-finish-reviewer.md` | riscritto l'11/10 da un elenco dei concetti delle due fonti; ne conserva idee e selezione |

## Skill e agent

Confronto del 10/10 sul resto di Mímir (skill di questo plugin tranne quelle di design, agent, testi degli hook; le skill di `brokkr` hanno il loro registro in `plugins/brokkr/THIRD_PARTY.md`, `rules/`, `CLAUDE.md` e `profile/profile.example.md` quello nella radice del repository) contro i repo di Matt Pocock, superpowers, ECC, hermes-agent, openclaw, system-design-primer e developer-roadmap. Metodo di `skills/scrivi-skill/references/fonti-esterne.md`; ogni derivazione è stata ricontrollata a mano sulle righe dei due file. Limiti: le controparti nelle fonti grandi (ECC, openclaw, hermes-agent, system-design-primer, developer-roadmap) sono state individuate per nome e descrizione dei file, con in più una ricerca di 26 frasi e costanti distintive di otto file di Mímir (`tdd`, `debugging`, `retro`, `pianificazione`, `delega`, `contesto-e-costi`, `code-reviewer`, `security-reviewer`); un file della fonte con un nome lontano dal tema può essere sfuggito. Un file di Mímir può avere più fonti: compare in ognuna. Nella colonna "Origine" le sezioni tra parentesi sono quelle di Mímir in cui sta la parte derivata, non i titoli della fonte.

### skills di Matt Pocock

- **Fonte**: https://github.com/mattpocock/skills
- **Licenza**: MIT (testo in fondo, con il copyright di Matt Pocock).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `skills/decisioni/SKILL.md` | `skills/productivity/to-questionnaire/SKILL.md` (sezione "Quando mancano le informazioni": a chi va, cosa deve tornare, domande una per idea in ordine d'importanza, copertura) | adattamento, con parti tradotte |
| `skills/clean-code/references/smell.md` | `skills/engineering/code-review/SKILL.md` (smell come giudizi, elenco e correzioni); test di eliminazione da `skills/engineering/codebase-design/SKILL.md` | traduzione con modifiche |
| `agents/code-reviewer.md` | `skills/engineering/code-review/SKILL.md` (diff a tre punti, aderenza alla richiesta) | adattamento, con parti tradotte |
| `skills/debugging/SKILL.md` | `skills/engineering/diagnosing-bugs/SKILL.md` (ciclo di riproduzione e modi di costruirlo, stringere il ciclo, `git bisect run`, causa non trovata, strumentazione ai confini) | adattamento |
| `skills/debugging/references/tecniche.md` | `skills/engineering/diagnosing-bugs/SKILL.md` ("misura prima" per le prestazioni) | adattamento di un punto |
| `skills/passaggio-consegne/SKILL.md` | `skills/productivity/handoff/SKILL.md` (le cinque istruzioni: cartella temporanea, skill suggerite, rimandi invece di copie, dati oscurati, prossima sessione) | adattamento |
| `skills/pianificazione/SKILL.md` | `skills/productivity/grilling/SKILL.md` (interrogatorio a round: frontiera delle decisioni con premesse chiuse, risposta consigliata, fatti cercati nel codice) | adattamento |

### superpowers

- **Fonte**: https://github.com/obra/superpowers
- **Licenza**: MIT (testo in fondo, con il copyright di Jesse Vincent).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `skills/clean-code/references/ricevere-review.md` | `skills/receiving-code-review/SKILL.md` (leggere tutto, chiarire prima, verificare sul codice, controllo YAGNI, ordine delle correzioni, risposta motivata) | adattamento, con parti tradotte |
| `agents/code-reviewer.md` | `skills/requesting-code-review/code-reviewer.md` (passate dichiarate, tre gravità, esito a tre stati, forma della segnalazione) | adattamento, con parti tradotte |
| `skills/debugging/SKILL.md` | `skills/systematic-debugging/SKILL.md` (§3 "Restringere", §4 "Dopo 2-3 fix falliti"); arriva anche tramite la copia di hermes-agent | adattamento |

### ECC

- **Fonte**: https://github.com/affaan-m/ECC
- **Licenza**: MIT (testo in fondo, con il copyright di Affaan Mustafa).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `skills/database/SKILL.md` | `skills/database-migrations/SKILL.md` (sezione "Migrazioni dello schema", nel dubbio) | adattamento |
| `skills/clean-code/references/errori-logging.md` | `agents/silent-failure-hunter.md` (sezione "Fallimenti silenziosi": stesso esempio e stessa sequenza, nel dubbio) | adattamento |
| `agents/code-reviewer.md` | `agents/silent-failure-hunter.md` (la frase sui fallimenti silenziosi della correttezza) | adattamento di un punto |
| `skills/typescript/references/progettazione-tipi.md` | `agents/type-design-analyzer.md` (le quattro domande). Lo stesso schema c'è nell'agent `type-design-analyzer` del plugin pr-review-toolkit di Anthropic: possibile fonte comune, non verificata | adattamento |
| `skills/vue/SKILL.md` | `rules/vue/patterns.md`, `rules/vue/security.md` (composable, provide/inject, Pinia, router, sicurezza: selezione, ordine e frasi, nel dubbio) | adattamento |
| `skills/vue/references/test-vue.md` | `rules/vue/testing.md` (Pinia e composable, nel dubbio) | adattamento |
| `skills/decisioni/references/prospettive.md` | `skills/council/SKILL.md` (sezione "Con i subagent": voci indipendenti, forma del resoconto, disaccordo visibile; nel dubbio) | adattamento |

### hermes-agent

- **Fonte**: https://github.com/NousResearch/hermes-agent
- **Licenza**: MIT (testo in fondo, con il copyright di Nous Research). Diverse skill dichiarano nel frontmatter un autore diverso e `license: MIT`: l'autore è indicato nella riga. I repo originali di questi autori non sono stati consultati.
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `skills/retro/SKILL.md` | `agent/background_review.py` (cosa non catturare, ordine delle destinazioni, forma della lezione, leggere prima di scrivere) | adattamento, con parti tradotte |
| `skills/pianificazione/SKILL.md` | `optional-skills/software-development/grill-me/SKILL.md`, di Rafael Zendron con Hermes Agent (quando usarlo, copertura delle domande, "non so", niente codice, sintesi finale) | adattamento |
| `skills/pianificazione/SKILL.md` | `skills/software-development/spike/SKILL.md`, di Hermes Agent, adattata da gsd-build/get-shit-done (sezione "Spike"; probabile origine comune con la spike di openclaw, sotto); licenza dell'originale MIT © 2025 Lex Christopherson secondo hermes-agent (`SKILL.md:197`), repo originale non consultato | adattamento, con parti tradotte |
| `skills/decisioni/SKILL.md`, `skills/decisioni/templates/registro-decisioni.md` | `optional-skills/communication/one-three-one-rule/SKILL.md`, di Willard Moore (brief 1-3-1) | adattamento, con parti tradotte |
| `skills/riunioni/SKILL.md`, `skills/riunioni/templates/verbale.md` | `skills/productivity/meeting-action-items/SKILL.md`, di Ben Barclay con Hermes Agent (sezione "Da appunti o trascrizioni", tabella delle azioni) | adattamento, con parti tradotte |
| `skills/ricerca/SKILL.md`, `skills/ricerca/references/citazioni.md` | `skills/research/grounded-citations/SKILL.md` e `references/citation-formats.md`, di Hermes Agent con Teknium (citazioni durante la lettura, massimo tre per frase, posizione per formato) | adattamento |
| `skills/documentazione-tecnica/SKILL.md` | `optional-skills/software-development/code-wiki/SKILL.md`, di Teknium con Hermes Agent (sezione "Mappa del codice") | adattamento, con parti tradotte |
| `agents/code-reviewer.md` | `skills/software-development/simplify-code/SKILL.md`, ispirata a `/simplify` di Claude Code (git blame prima di togliere, nomi pubblici come contratti, costo della segnalazione) | adattamento, con parti tradotte |

### openclaw

- **Fonte**: https://github.com/openclaw/openclaw
- **Licenza**: MIT (testo in fondo, con il copyright di OpenClaw Foundation).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `skills/pianificazione/SKILL.md` | `skills/spike/SKILL.md` (sezione "Spike": spazio temporaneo di default e repo solo su richiesta, codice da non unire alla produzione, smentita utile; probabile origine comune con la spike di hermes-agent, sopra) | adattamento, nel dubbio |

### agent-skills di Addy Osmani

- **Fonte**: https://github.com/addyosmani/agent-skills
- **Licenza**: MIT (testo in fondo, con il copyright di Addy Osmani).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `skills/delega/SKILL.md` | `skills/doubt-driven-development/SKILL.md`, Step 2 e 3 (paragrafo "Review e verifiche": niente tesi al revisore, perché lo spinge a dare ragione, e richiesta di cercare i problemi rispetto al criterio) | adattamento (un paragrafo) |

### ponytail di DietrichGebert

- **Fonte**: https://github.com/DietrichGebert/ponytail
- **Licenza**: MIT (testo in fondo, con il copyright di DietrichGebert).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `skills/clean-code/references/principi.md` | `AGENTS.md`, sezione "The smallest complete change", punti 2-4 (ordine di riuso: repo, libreria standard, piattaforma, dipendenza installata) e marcatore `shortcut: <limite>, <quando rivedere>` | adattamento (due voci) |

## Valutati e non inclusi
Sovrapposizioni di sola idea, senza frasi, struttura o costanti in comune; restano qui perché un controllo futuro non le rifaccia da capo.
- `prototipi-ui`: `skills/engineering/prototype` di Matt Pocock (`github.com/mattpocock/skills`) e `skill/reference/live.md` di impeccable hanno la stessa idea (varianti su assi diversi, barra in basso, variante nell'URL), con testo diverso.
- `ui-casi-limite`: `skill/reference/harden.md` di impeccable, elenchi tematici simili, struttura e ordine diversi.
- `design-ui`: `skill/reference/typeset.md` di impeccable (cifre tabulari) solo tematico; la famiglia unica con scala fissa di `design-ui` è già coperta da `operate.md`; il resto del repo ECC (`make-interfaces-feel-better`, `motion-*`, `design-system`) solo luoghi comuni.
- `pianificazione`: la frase sul piano più lungo del codice ricorda `skills/writing-plans/SKILL.md` di superpowers (stesso inizio, conclusione diversa); va comunque riformulata. Il resto della skill, `tdd`, `delega`, `scrivi-skill` e `git-workflow` hanno con superpowers solo temi in comune.
- `retro`: `docs/tools/self-learning.md` di openclaw ha un elenco di esclusioni simile, comune anche a hermes-agent; i tratti specifici di `retro` vengono da hermes-agent (sopra).
- `sicurezza-claude-code/references/inventario.md`: i segnali di attacco (hook con `curl`/`wget`, `enableAllProjectMcpServers`, `ANTHROPIC_BASE_URL`) compaiono anche in `the-security-guide.md` di ECC; sono i risultati pubblici di Check Point Research (CVE-2025-59536, CVE-2026-21852), fonte comune.
- `typescript`, `nodejs/references/framework.md` (NestJS), `database` (indici, transazioni, paginazione), `angular/references/test-angular.md`: voci in comune con `agents/typescript-reviewer.md`, `skills/nestjs-patterns`, `agents/database-reviewer.md`, `rules/angular/testing.md` di ECC, tutte dalla documentazione ufficiale, con struttura diversa e nessuna frase distintiva. Le altre skill di linguaggio, processo e architettura hanno con ECC solo temi in comune; `script-shell`, `ddd`, `sistemi-distribuiti` nessuno.
- Matt Pocock: `tdd`, `retro`, `ricerca`, `ddd`, `refactoring`, `scrivi-skill` e `delega`, l'hook `git-guard` (rispetto a `git-guardrails`) solo temi in comune.
- hermes-agent: l'hook di retro, `manutenzione-mimir`, `scrivi-skill`, `contesto-e-costi`, `delega`, `tdd`, `security-reviewer`, `refactoring`, `clean-code`, `commit`, `container`, `passaggio-consegne` solo temi in comune.
- openclaw (`AGENTS.md`, template dei ruoli, skill e documentazione): solo temi in comune con `code-reviewer`, `debugging`, `scrivi-skill`, `documentazione-tecnica`, `contesto-e-costi`. La sezione "Spike" di `pianificazione` deriva da `skills/spike/SKILL.md` (sopra).
- system-design-primer (CC BY 4.0): `sistemi-distribuiti`, `database`, `design-api`, `stime`, `architetto` hanno solo temi in comune, senza cifre né elenchi ripresi.
- developer-roadmap (licenza proprietaria): nessuna derivazione; `code-reviewer`, `design-api`, `clean-code` e i nodi su Claude Code hanno solo temi in comune (ricerca di frasi distintive: nessun riscontro).

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

### openclaw
```
MIT License

Copyright (c) 2026 OpenClaw Foundation

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

### agent-skills di Addy Osmani
```
MIT License

Copyright (c) 2025 Addy Osmani

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

### ponytail di DietrichGebert
```
MIT License

Copyright (c) 2026 DietrichGebert

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
