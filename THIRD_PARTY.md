# Materiale di terzi

L'elenco del materiale di terzi e le licenze dei plugin stanno nella cartella di ciascun plugin, perché arrivino a chi lo installa: [plugins/mimir/THIRD_PARTY.md](plugins/mimir/THIRD_PARTY.md) e [plugins/brokkr/THIRD_PARTY.md](plugins/brokkr/THIRD_PARTY.md). Qui restano le voci dei file fuori dai plugin (`rules/`, `CLAUDE.md`, `profile/profile.example.md`); gli altri file sono sotto la licenza MIT di Mímir ([LICENSE](LICENSE)).

## Regole

Confronto del 10/10 su `rules/`, `CLAUDE.md` e `profile/profile.example.md`, insieme al resto di Mímir, contro i repo di Matt Pocock, superpowers, ECC, hermes-agent, openclaw, system-design-primer e developer-roadmap. Metodo, limiti e voci dei plugin sono nella sezione "Skill e agent" di [plugins/mimir/THIRD_PARTY.md](plugins/mimir/THIRD_PARTY.md).

### hermes-agent

- **Fonte**: https://github.com/NousResearch/hermes-agent
- **Licenza**: MIT (testo in fondo, con il copyright di Nous Research).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `rules/working-style.md` | `SOUL.md` (due frasi: d'accordo perché è giusto; cosa è cambiato, cosa è verificato, cosa resta) | traduzione di due frasi |

## Valutati e non inclusi
Sovrapposizioni di sola idea, senza frasi, struttura o costanti in comune; restano qui perché un controllo futuro non le rifaccia da capo.
- superpowers: `rules/` ha solo temi in comune.
- hermes-agent: `growth` e il resto di `working-style` solo temi in comune.
- openclaw (`AGENTS.md`, template dei ruoli, skill e documentazione): solo temi in comune con `rules/` e `CLAUDE.md`.

## Testi della licenza MIT

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
