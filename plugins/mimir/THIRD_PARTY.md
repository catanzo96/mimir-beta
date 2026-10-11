# Materiale di terzi

Alcuni file di questo plugin sono traduzioni o adattamenti in italiano di opere di terzi, usati secondo la loro licenza. Gli altri file sono sotto la licenza MIT di Mímir (file `LICENSE` nella radice del repository). I percorsi qui sotto sono relativi alla cartella del plugin.

L'elenco viene da un confronto sistematico del 10/10, fonte per fonte e file per file, sui file di design (`design-ui`, `animazioni-ui`, `ui-casi-limite`, `prototipi-ui`, agent `design-reviewer`): ordine delle sezioni, frasi tradotte, esempi e costanti. Le fonti hanno licenze permissive, quindi i file derivati restano con questa attribuzione; quelli derivati da fonti Apache-2.0 portano anche l'avviso di modifica nel file. Le regole sono in `skills/scrivi-skill/references/fonti-esterne.md` (§5).

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

## Valutati e non inclusi
Sovrapposizioni di sola idea, senza frasi, struttura o costanti in comune; restano qui perché un controllo futuro non le rifaccia da capo.
- `prototipi-ui`: `skills/engineering/prototype` di Matt Pocock (`github.com/mattpocock/skills`) e `skill/reference/live.md` di impeccable hanno la stessa idea (varianti su assi diversi, barra in basso, variante nell'URL), con testo diverso.
- `ui-casi-limite`: `skill/reference/harden.md` di impeccable, elenchi tematici simili, struttura e ordine diversi.
- `design-ui`: `skill/reference/typeset.md` di impeccable (cifre tabulari) solo tematico; la famiglia unica con scala fissa di `design-ui` è già coperta da `operate.md`; il resto del repo ECC (`make-interfaces-feel-better`, `motion-*`, `design-system`) solo luoghi comuni.

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
