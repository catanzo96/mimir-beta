#!/usr/bin/env python3
"""Test di somiglianza.py: segnala un testo che conserva costanti, codice o ordine della fonte.

Uso: python3 -I test_somiglianza.py
I testi d'esempio sono scritti qui: italiano contro inglese, come nei casi reali.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "somiglianza.py"

SOURCE = """# Recipes

## Press
Scale the button down on press.
```css
.button:active { transform: scale(0.97); transition: transform 160ms var(--ease-out); }
```

## Dropdown
Open from the trigger with `cubic-bezier(0.23, 1, 0.32, 1)` over 200ms and scale 0.95.

## Toast
Slide in over 400ms, stagger 50ms.

## Drag
Project momentum with deceleration 0.998, rubber band constant 0.55.
"""

DERIVED = """# Ricette

## Pressione
Il bottone si rimpicciolisce alla pressione.
```css
.button:active { transform: scale(0.97); transition: transform 160ms var(--ease-out); }
```

## Menu a tendina
Si apre dall'attivatore con `cubic-bezier(0.23, 1, 0.32, 1)` in 200 ms e scala 0,95.

## Notifica
Entra in 400 ms, sfasamento di 50 ms.

## Trascinamento
Proietta lo slancio con decelerazione 0,998 e costante di resistenza 0,55.
"""

ORIGINAL = """# Movimento

## Quando muovere
Muovi solo ciò che l'utente ha toccato. Un elemento lontano dal dito non si anima.

## Uscite
Chiudi più in fretta di come apri: 120 ms bastano.

## Pagine lunghe
Nelle pagine di contenuto, niente comparse allo scorrimento.
"""

# Ogni sezione divide con la fonte una sola costante rara: l'ordine si ricostruisce da quelle.
ORDERED_SOURCE = """# A
## One
Value 11ms and 0.31.
## Two
Value 12ms and 0.32.
## Three
Value 13ms and 0.33.
"""

SAME_ORDER = """# A
## Uno
Valore 11 ms.
## Due
Valore 0,32.
## Tre
Valore 13 ms.
"""

SHUFFLED = """# A
## Tre
Valore 13 ms.
## Uno
Valore 11 ms.
## Due
Valore 0,32.
"""


class Somiglianza(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="somiglianza-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def write(self, name, text):
        path = self.tmp / name
        path.write_text(text, encoding="utf-8")
        return str(path)

    def run_script(self, *args):
        return subprocess.run([sys.executable, "-I", str(SCRIPT), *args],
                              capture_output=True, text=True, encoding="utf-8", timeout=30)

    def rare_count(self, result):
        return result.stdout.split("Costanti rare in comune (", 1)[1].split(",", 1)[0]

    def test_traduzione_con_costanti_e_codice_uguali_e_rossa(self):
        result = self.run_script(self.write("ricette.md", DERIVED), self.write("RECIPES.md", SOURCE))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("ROSSO", result.stdout)
        self.assertIn("cubic-bezier(0.23,1,0.32,1)", result.stdout)
        self.assertIn("0.998", result.stdout)
        self.assertIn("scale(0.97)", result.stdout)

    def test_virgola_decimale_e_unita_staccata_si_normalizzano(self):
        result = self.run_script(self.write("ricette.md", DERIVED), self.write("RECIPES.md", SOURCE))
        self.assertIn("0.55", result.stdout)
        self.assertIn("400ms", result.stdout)

    def test_riga_di_codice_identica_e_segnalata(self):
        result = self.run_script(self.write("ricette.md", DERIVED), self.write("RECIPES.md", SOURCE))
        self.assertIn(".button:active", result.stdout)

    def test_testo_originale_e_verde(self):
        result = self.run_script(self.write("movimento.md", ORIGINAL), self.write("RECIPES.md", SOURCE))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("VERDE", result.stdout)

    def verdict(self, result):
        lines = [line for line in result.stdout.splitlines() if line.startswith("Esito:")]
        self.assertEqual(len(lines), 1, result.stdout + result.stderr)
        return lines[0]

    def test_stesso_ordine_delle_sezioni_e_segnalato(self):
        result = self.run_script(self.write("a.md", SAME_ORDER), self.write("src.md", ORDERED_SOURCE))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("ordine", self.verdict(result))

    def test_stesse_costanti_in_ordine_diverso_non_segnalano_l_ordine(self):
        result = self.run_script(self.write("a.md", SHUFFLED), self.write("src.md", ORDERED_SOURCE))
        self.assertNotIn("ordine", self.verdict(result), result.stdout)

    def test_valori_banali_non_contano(self):
        trivial_src = self.write("src.md", "# S\n## A\nUse 0 and 1px, 100% width, 0ms.\n")
        trivial_it = self.write("it.md", "# S\n## A\nUsa 0, 1px, 100% di larghezza, 0 ms.\n")
        result = self.run_script(trivial_it, trivial_src)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_valori_ignorati_da_riga_di_comando(self):
        src = self.write("src.md", "# S\n## A\nLCP 2.4s, INP 175ms, CLS 0.08.\n")
        it = self.write("it.md", "# S\n## A\nLCP 2,4 s, INP 175 ms, CLS 0,08.\n")
        self.assertEqual(self.run_script(it, src).returncode, 1)
        result = self.run_script("--ignora", "2.4s", "--ignora", "175ms", "--ignora", "0,08", it, src)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_piu_fonti_si_sommano(self):
        half_a = self.write("a.md", "# A\n## X\nScale 0.97 over 160ms.\n")
        half_b = self.write("b.md", "# B\n## Y\nDeceleration 0.998, stagger 50ms.\n")
        it = self.write("it.md", "# I\n## Z\nScala 0,97 in 160 ms, decelerazione 0,998, sfasamento 50 ms.\n")
        result = self.run_script(it, half_a, half_b)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_valori_comuni_non_contano(self):
        src = self.write("src.md", "# S\n## A\nFade in over 200ms with scale(0.95) and translateY(8px), "
                                   "cubic-bezier(0.4, 0, 0.2, 1), exit in 300ms.\n")
        it = self.write("it.md", "# S\n## A\nComparsa in 200 ms con scale(0.95) e translateY(8px), "
                                 "cubic-bezier(0.4, 0, 0.2, 1), uscita in 300 ms.\n")
        result = self.run_script(it, src)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.rare_count(result), "0", result.stdout)

    def test_ogni_famiglia_di_valori_comuni_da_sola(self):
        families = {
            "durate tonde": "150ms, 250ms, 600ms, 0.35s",
            "griglia e corpi": "12px, 40px, 18px, 96px",
            "quarti di rem": "0.75rem, 2.5rem, 6rem",
            "misura": "50ch, 66ch, 72ch",
            "frazioni dello schermo": "50vh, 75vw, 100svh",
            "frazioni a una cifra": "0.3, 0.6, 0.8",
            "interlinea e WCAG": "1.25, 1.6, 4.5",
            "curve standard": "cubic-bezier(0.4, 0, 0.2, 1), cubic-bezier(0.42, 0, 0.58, 1)",
            "scale": "scale(0.92), scale(0.97), scale(0.9)",
            "piccoli spostamenti": "translateY(6px), translateX(-12px), translateY(-100%)",
            "aree sicure": "env(safe-area-inset-top), env(safe-area-inset-bottom, 0px)",
        }
        for name, values in families.items():
            with self.subTest(name):
                result = self.run_script(self.write("it.md", "# I\n" + values + "\n"),
                                         self.write("src.md", "# S\n" + values + "\n"))
                self.assertEqual(self.rare_count(result), "0", result.stdout)

    def test_due_costanti_rare_sono_sotto_soglia(self):
        result = self.run_script(self.write("it.md", "# I\nValori 0,123 e 0,456.\n"),
                                 self.write("src.md", "# S\nValues 0.123 and 0.456.\n"))
        self.assertEqual(self.rare_count(result), "2", result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_intervallo_con_trattino_e_unita_staccata(self):
        result = self.run_script(self.write("it.md", "# I\nTra 110–170 ms.\n"),
                                 self.write("src.md", "# S\nBetween 110-170ms.\n"))
        self.assertIn("110-170ms", result.stdout)
        self.assertEqual(self.rare_count(result), "1", result.stdout)  # l'estremo 170ms non conta di nuovo

    def test_ignora_vale_anche_per_le_righe_di_codice(self):
        block = "```css\n.x { transition: opacity 2.37s linear; }\n```\n"
        it, src = self.write("it.md", "# I\n" + block), self.write("src.md", "# S\n" + block)
        self.assertEqual(self.run_script(it, src).returncode, 1)
        result = self.run_script("--ignora", "2.37s", it, src)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_titoli_non_ascii_con_console_non_utf8(self):
        # senza -I, perché -I ignora PYTHONIOENCODING: simula una console Windows cp1252
        text = "# A\n## Pressione → rilascio\nValore 0,123 e 0,456 e 0,789.\n"
        env = dict(os.environ, PYTHONIOENCODING="cp1252")
        result = subprocess.run([sys.executable, str(SCRIPT), self.write("it.md", text), self.write("src.md", text)],
                                capture_output=True, env=env, timeout=30)
        self.assertEqual(result.returncode, 1, result.stderr.decode("utf-8", "replace"))
        self.assertIn("Esito: ROSSO", result.stdout.decode("utf-8"))

    def test_famiglie_di_valori_comuni_non_contano(self):
        values = "opacity 0.4, 0.6 and 0.8, gap 40px, 6rem, 250ms, 65ch, env(safe-area-inset-top, 0px), 50vh"
        src = self.write("src.md", "# S\n## A\n" + values + "\n")
        it = self.write("it.md", "# S\n## A\n" + values.replace("and", "e") + "\n")
        result = self.run_script(it, src)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_posizioni_di_riposo_sono_banali(self):
        # aggiunto dopo la prova su testi nuovi: translateY(0) contava come costante rara
        values = "translateY(0), translateX(0), translate(0, 0), scale(1)"
        result = self.run_script(self.write("it.md", "# I\n## A\n" + values + "\n"),
                                 self.write("src.md", "# S\n## A\n" + values + "\n"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_riga_di_codice_comune_non_conta(self):
        block = "```css\n@media (prefers-reduced-motion: reduce) {\n  * { animation: none; }\n}\n```\n"
        result = self.run_script(self.write("it.md", "# I\n" + block), self.write("src.md", "# S\n" + block))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_file_mancante_e_errore_d_uso(self):
        result = self.run_script(self.write("it.md", ORIGINAL), str(self.tmp / "manca.md"))
        self.assertEqual(result.returncode, 2)

    def test_senza_fonti_e_errore_d_uso(self):
        result = self.run_script(self.write("it.md", ORIGINAL))
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
