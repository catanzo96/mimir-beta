# Materiale di terzi

Alcuni file di questo plugin sono adattamenti in italiano di opere di terzi, usati secondo la loro licenza. Gli altri file sono sotto la licenza MIT di Mímir (file `LICENSE` nella radice del repository). I percorsi qui sotto sono relativi alla cartella del plugin.

L'elenco viene dal confronto sistematico del 10/10 sulle skill, sugli agent e sulle regole di Mímir, fonte per fonte e file per file: ordine delle sezioni, frasi tradotte, esempi e costanti. Le fonti hanno licenze permissive, quindi i file derivati restano con questa attribuzione. Le regole sono in `skills/scrivi-skill/references/fonti-esterne.md` (§5) del plugin `mimir`.

## Skill

Confronto del 10/10 sul resto di Mímir (le skill di questo plugin; le skill e gli agent di `mimir` hanno il loro registro in `plugins/mimir/THIRD_PARTY.md`, `rules/`, `CLAUDE.md` e `profile/profile.example.md` quello nella radice del repository) contro i repo di Matt Pocock, superpowers, ECC, hermes-agent, openclaw, system-design-primer e developer-roadmap. Metodo di `fonti-esterne.md` del plugin `mimir`; ogni derivazione è stata ricontrollata a mano sulle righe dei due file. Limiti: le controparti nelle fonti grandi (ECC, openclaw, hermes-agent, system-design-primer, developer-roadmap) sono state individuate per nome e descrizione dei file, con in più una ricerca di 26 frasi e costanti distintive di otto file di Mímir; un file della fonte con un nome lontano dal tema può essere sfuggito. Un file di Mímir può avere più fonti: compare in ognuna. Nella colonna "Origine" le sezioni tra parentesi sono quelle di Mímir in cui sta la parte derivata, non i titoli della fonte.

### skills di Matt Pocock

- **Fonte**: https://github.com/mattpocock/skills
- **Licenza**: MIT (testo in fondo, con il copyright di Matt Pocock).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `skills/analisi-funzionale/templates/domande.md` | `skills/productivity/to-questionnaire/SKILL.md` (sezione "Forma da inviare" e domande non composte) | adattamento |

### ECC

- **Fonte**: https://github.com/affaan-m/ECC
- **Licenza**: MIT (testo in fondo, con il copyright di Affaan Mustafa).
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `skills/rilascio/references/migrazioni-db.md` | `skills/database-migrations/SKILL.md` (principi, volumi realistici, espandi e contrai, rinomina di colonna) | adattamento, con parti tradotte |
| `skills/analisi-funzionale/SKILL.md` | `agents/spec-miner.md` (regole come requisiti o invarianti con ID, punto che le impone e test; lettura dai punti d'ingresso un livello alla volta; segnalare senza correggere) | adattamento |
| `skills/analisi-funzionale/templates/scheda-modulo.md` | `agents/spec-miner.md` (ID stabile, commit di riferimento) | adattamento |
| `skills/manutenzione-legacy/SKILL.md` | `skills/inherit-legacy-style/SKILL.md`, contributo della community, licenza del contributore non verificata (§3 "Diff minimo": file esemplari, dichiarazione, maggioranza, difetti da non copiare) | adattamento, con parti tradotte |

### hermes-agent

- **Fonte**: https://github.com/NousResearch/hermes-agent
- **Licenza**: MIT (testo in fondo, con il copyright di Nous Research). Diverse skill dichiarano nel frontmatter un autore diverso e `license: MIT`: l'autore è indicato nella riga. I repo originali di questi autori non sono stati consultati.
- **File derivati**:

| File di Mímir | Origine | Tipo |
|---|---|---|
| `skills/stato-e-rischi/SKILL.md` | `skills/productivity/document-to-action-items/SKILL.md`, di Ben Barclay con Hermes Agent (sezione "Da documenti") | adattamento, con parti tradotte |

## Valutati e non inclusi
Sovrapposizioni di sola idea, senza frasi, struttura o costanti in comune; restano qui perché un controllo futuro non le rifaccia da capo.
- ECC: le altre skill di processo hanno con ECC solo temi in comune.
- Matt Pocock: `ticket` solo temi in comune.
- developer-roadmap (licenza proprietaria): nessuna derivazione; `gestione-persone` ha solo temi in comune (ricerca di frasi distintive: nessun riscontro).

## Testi della licenza MIT

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
