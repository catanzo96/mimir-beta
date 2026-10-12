#!/usr/bin/env python3
"""Controllo di somiglianza meccanico tra un file di Mímir e le sue possibili fonti.

Uso: python3 -I somiglianza.py [--ignora VALORE]... FILE FONTE [FONTE...]
Esito: 0 verde, 1 rosso, 2 errore d'uso.

Confronta solo ciò che sopravvive alla traduzione: costanti rare (durate, curve, soglie, decimali
che non compaiono in qualunque testo sul tema), righe di codice identiche e ordine delle sezioni,
ricostruito dalle costanti rare che ogni sezione divide con la fonte. È un segnale per chi rivede,
non una prova di originalità: frasi tradotte e selezione delle voci restano al confronto bilingue
descritto in references/fonti-esterne.md.
"""
import argparse
import re
import sys
from pathlib import Path

# Soglie fissate prima della validazione, non adattate ai casi: una o due costanti rare uguali
# possono capitare per caso, tre indicano che i valori vengono dalla fonte.
CONSTANTS_THRESHOLD = 3
ORDER_THRESHOLD = 3
MIN_CODE_LINE = 12
UNITS = r"(?:ms|s|px|%|rem|em|ch|dvh|svh|vh|vw|deg|fps|x)"
FUNCTION = re.compile(r"\b[a-zA-Z][\w-]*\([^()]*\d[^()]*\)")
RANGE = re.compile(r"(?<![\w.,])(\d+(?:[.,]\d+)?)\s?[-–]\s?(\d+(?:[.,]\d+)?)\s?(" + UNITS + r")(?!\w)")
WITH_UNIT = re.compile(r"(?<![\w.,])(\d+(?:[.,]\d+)?)\s?(" + UNITS + r")(?!\w)")
DECIMAL = re.compile(r"(?<![\w.,])(\d+[.,]\d+)(?![\w]|[.,]\d)")
HEADING = re.compile(r"^#{1,6}\s+(.*)$")
FENCE = re.compile(r"^\s*```")
# Valori che compaiono in qualunque testo di interfaccia: in comune non dicono nulla
TRIVIAL = {"0", "1", "0px", "1px", "0%", "100%", "0s", "0ms", "1s", "1x"}
# Posizioni di riposo (translateY(0), scale(1)): sono l'assenza di trasformazione
RESTING = re.compile(r"^(translate[xyz3d]*\((0(px|%)?,?)+\)|scale[xyz3d]*\((1,?)+\))$")

# Valori comuni: li sceglie chiunque scriva sul tema, quindi si riportano ma non contano.
# Sono famiglie di valori, non i valori trovati nei casi di prova: un elenco di singoli valori si
# adatta ai testi da cui nasce. Mai allargarle per far tornare verde un derivato.
COMMON = {
    # curve documentate da Material Design (standard, decelerata, accelerata, sharp)
    "cubic-bezier(0.4,0,0.2,1)", "cubic-bezier(0,0,0.2,1)", "cubic-bezier(0.4,0,1,1)",
    "cubic-bezier(0.4,0,0.6,1)",
    # curve delle parole chiave CSS scritte per esteso (ease, ease-in, ease-out, ease-in-out)
    "cubic-bezier(0.25,0.1,0.25,1)", "cubic-bezier(0.42,0,1,1)", "cubic-bezier(0,0,0.58,1)",
    "cubic-bezier(0.42,0,0.58,1)",
    # interlinea tipica e rapporti di contrasto WCAG
    "1.2", "1.25", "1.3", "1.4", "1.5", "1.6", "1.75", "4.5",
}
COMMON_FUNCTION = re.compile(
    r"(env\(safe-area-inset-[a-z]+(,0(px)?)?\)"  # aree sicure, con o senza ripiego
    r"|scale\(0\.9\d?\)"                        # leggero rimpicciolimento (0.9-0.99)
    r"|translate[xy]?\(-?(\d|1\d|20)px\)"         # piccoli spostamenti, fino a 20px
    r"|translate[xy]?\(-?100%\))$")                # fuori schermo, per pannelli e drawer
SIMPLE = re.compile(r"^(\d+(?:\.\d+)?)(ms|s|px|rem|em|ch|vh|vw|dvh|svh|%)$")


def common_number(value, unit):
    if unit == "ms":
        return value % 50 == 0 and value <= 1000  # durate tonde
    if unit == "s":
        return (value * 1000) % 50 == 0 and value <= 2
    if unit == "px":
        return (value % 4 == 0 and value <= 128) or 10 <= value <= 24  # griglia da 4 e corpi di testo
    if unit in ("rem", "em"):
        return (value * 4) % 1 == 0 and value <= 8  # multipli di un quarto
    if unit == "ch":
        return 45 <= value <= 80  # misura della riga di lettura
    if unit in ("vh", "vw", "dvh", "svh", "%"):
        return value % 25 == 0  # frazioni intere dello schermo
    return False


def is_common(constant):
    if constant in COMMON or COMMON_FUNCTION.match(constant):
        return True
    if re.match(r"^0\.\d$", constant):  # frazioni a una cifra: opacità, smorzamento, pesi
        return True
    ends = re.match(r"^(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)(\w+|%)$", constant)
    if ends:  # un intervallo è comune se lo sono entrambi gli estremi
        return all(is_common(f"{end}{ends.group(3)}") for end in ends.group(1, 2))
    simple = SIMPLE.match(constant)
    return bool(simple) and common_number(float(simple.group(1)), simple.group(2))


def number(text):
    return text.replace(",", ".")


def normalize_value(value):
    """Forma canonica di un valore passato con --ignora: stessa resa delle costanti estratte."""
    found = constants(value)
    return found if found else {number(value.strip().lower())}


def constants(text):
    """Costanti distintive di un testo, in forma canonica (virgola decimale, unità attaccata)."""
    text = text.replace("×", "x")
    found = set()
    for match in FUNCTION.findall(text):
        found.add(re.sub(r"\s+", "", match).lower())
    text = FUNCTION.sub(" ", text)
    for low, high, unit in RANGE.findall(text):
        found.add(f"{number(low)}-{number(high)}{unit}")
    text = RANGE.sub(" ", text)
    for value, unit in WITH_UNIT.findall(text):
        found.add(f"{number(value)}{unit}")
    text = WITH_UNIT.sub(" ", text)
    for value in DECIMAL.findall(text):
        found.add(number(value))
    return {value for value in found if value not in TRIVIAL and not RESTING.match(value)}


def rare(values):
    return {value for value in values if not is_common(value)}


def code_lines(text, ignored):
    """Righe dei blocchi di codice con almeno una costante rara: le altre sono sintassi
    (`@media (prefers-reduced-motion: reduce) {`) o valori comuni, che chiunque scriverebbe uguali."""
    lines, inside = set(), False
    for line in text.splitlines():
        if FENCE.match(line):
            inside = not inside
            continue
        normalized = " ".join(line.split())
        if inside and len(normalized) >= MIN_CODE_LINE and rare(constants(normalized)) - ignored:
            lines.add(normalized)
    return lines


def sections(text):
    """Sezioni come (titolo, testo); il testo prima del primo titolo è la sezione "(inizio)"."""
    result, title, body, inside = [], "(inizio)", [], False
    for line in text.splitlines():
        if FENCE.match(line):
            inside = not inside
        heading = None if inside else HEADING.match(line)
        if heading:
            result.append((title, "\n".join(body)))
            title, body = heading.group(1).strip(), []
        else:
            body.append(line)
    result.append((title, "\n".join(body)))
    return result


def longest_increasing(pairs):
    """Sottosequenza più lunga di coppie (sezione, sezione della fonte) con indici della fonte crescenti."""
    best = []
    for i, (_, source_index, _) in enumerate(pairs):
        chain = [pairs[i]]
        for j in range(i):
            if pairs[j][1] < source_index and len(best[j]) + 1 > len(chain):
                chain = best[j] + [pairs[i]]
        best.append(chain)
    return max(best, key=len, default=[])


def section_order(mimir_text, source_text, ignored):
    source_sections = [(title, rare(constants(body)) - ignored) for title, body in sections(source_text)]
    pairs = []
    for title, body in sections(mimir_text):
        own = rare(constants(body)) - ignored
        scores = [len(own & theirs) for _, theirs in source_sections]
        if scores and max(scores) > 0:
            index = scores.index(max(scores))
            pairs.append((title, index, source_sections[index][0]))
    return longest_increasing(pairs)


class ReadError(Exception):
    pass


def read(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ReadError(f"Impossibile leggere {path}: {exc}") from exc


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ignora", action="append", default=[], metavar="VALORE",
                        help="valore di uno standard pubblico da non contare (es. 4.5, 200ms)")
    parser.add_argument("file", help="file di Mímir da controllare")
    parser.add_argument("fonti", nargs="+", help="file della fonte esterna")
    args = parser.parse_args(argv)
    try:
        mimir_text = read(args.file)
        sources = [(path, read(path)) for path in args.fonti]
    except ReadError as exc:
        print(exc, file=sys.stderr)
        return 2

    ignored = set()
    for value in args.ignora:
        ignored |= normalize_value(value)
    source_constants = set().union(*(constants(text) for _, text in sources)) - ignored
    shared = (constants(mimir_text) - ignored) & source_constants
    shared_constants = sorted(rare(shared))
    shared_common = sorted(shared - rare(shared))
    source_code = set().union(*(code_lines(text, ignored) for _, text in sources))
    shared_code = sorted(code_lines(mimir_text, ignored) & source_code)
    orders = [(path, section_order(mimir_text, text, ignored)) for path, text in sources]

    reasons = []
    print(f"Confronto: {args.file} (fonti: {len(sources)})")
    print(f"Costanti rare in comune ({len(shared_constants)}, soglia {CONSTANTS_THRESHOLD}): "
          f"{', '.join(shared_constants) or '-'}")
    print(f"Valori comuni in comune (non contano): {', '.join(shared_common) or '-'}")
    if len(shared_constants) >= CONSTANTS_THRESHOLD:
        reasons.append("costanti")
    print(f"Righe di codice identiche ({len(shared_code)}):")
    for line in shared_code:
        print(f"  {line}")
    if shared_code:
        reasons.append("codice")
    for path, chain in orders:
        print(f"Sezioni nello stesso ordine di {path} ({len(chain)}, soglia {ORDER_THRESHOLD}):")
        for title, _, source_title in chain:
            print(f"  {title} -> {source_title}")
        if len(chain) >= ORDER_THRESHOLD and "ordine" not in reasons:
            reasons.append("ordine")
    print(f"Esito: ROSSO ({', '.join(reasons)})" if reasons else "Esito: VERDE")
    print("Frasi tradotte e selezione delle voci non sono coperte: serve il confronto bilingue.")
    return 1 if reasons else 0


if __name__ == "__main__":
    # I titoli stampati possono contenere caratteri fuori da cp1252 (console di Windows):
    # un errore di codifica uscirebbe con 1, indistinguibile da un esito rosso
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
