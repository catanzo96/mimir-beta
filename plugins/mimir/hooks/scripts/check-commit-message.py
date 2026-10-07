#!/usr/bin/env python3
"""PreToolUse (Bash e PowerShell): controlla i messaggi dei commit creati da Claude Code.

Blocca (exit 2, motivo su stderr):
- le attribuzioni a un'AI: trailer come Co-Authored-By con un nome di AI,
  frasi "Generated with/by" o "Generato con/da" seguite da un'AI, link a Claude Code;
- intestazione o righe del corpo oltre 72 caratteri (le righe con un URL sono escluse).

Le parole da sole (un file CLAUDE.md, un percorso, "integra l'API di Anthropic")
non bloccano: conta la forma dell'attribuzione, non l'argomento del commit.

Un errore inatteso blocca (exit 2) solo se il comando contiene "git" e "commit": per Claude Code
un hook che esce con 1 è un errore non bloccante, e il commit passerebbe senza controllo.
"""
import json
import os
import re
import shlex
import sys

MAX_LINE = 72

AI = r"(claude|anthropic|openai|chatgpt|gpt-?\d|copilot|gemini|cursor|codeium|tabnine|\bai\b|assistant|assistente|llm)"
ATTRIBUTION = [
    re.compile(r"^\s*(co-authored-by|co-developed-by|assisted-by|generated-by)\s*:.*" + AI, re.I | re.M),
    re.compile(r"(generated|created|written)\s+(with|by|using)\b[^\n]{0,40}" + AI, re.I),
    re.compile(r"(generat[oa]|creat[oa]|scritt[oa])\s+(con|da|tramite)\b[^\n]{0,40}" + AI, re.I),
    re.compile(r"claude\.(ai|com)/(code|claude-code)", re.I),
]

# git commit come comando (a inizio riga, dopo ; & | ( { o dopo then/do/else), non citato dentro una
# stringa di un altro comando. Ammette git.exe, le opzioni globali prima del sottocomando e le maiuscole
# (PowerShell non le distingue).
GIT_OPTION = r"(?:\s+(?:-C|-c|--git-dir|--work-tree|--namespace)\s+\S+|\s+--?[\w-]+(?:=\S+)?)"
COMMIT = re.compile(r"(?:^|[;&|({\n]|\b(?:then|do|else)\b)\s*git(?:\.exe)?" + GIT_OPTION + r"*\s+commit(?:-tree)?\b",
                    re.I)
# il valore di "command" nel JSON, per quando l'input non si riesce a leggere
RAW_COMMAND = re.compile(r'"command"\s*:\s*"((?:[^"\\]|\\.)*)')
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n(.*?)\n[ \t]*\2[ \t]*(?:\n|$)", re.S)


def heredoc_bodies(cmd):
    """Restituisce i corpi degli heredoc e il comando senza di essi."""
    bodies = [m.group(3) for m in HEREDOC.finditer(cmd)]
    return bodies, HEREDOC.sub(" __HEREDOC__ ", cmd)


def message_from_args(tokens, bodies, cwd):
    """Ricostruisce il messaggio da -m/--message, -F/--file e --trailer. None se non determinabile."""
    parts, trailers, i = [], [], 0
    while i < len(tokens):
        tok = tokens[i]
        value = None
        if tok == "--trailer" and i + 1 < len(tokens):
            trailers.append(tokens[i + 1])
            i += 2
            continue
        if tok.startswith("--trailer="):
            trailers.append(tok.split("=", 1)[1])
            i += 1
            continue
        if tok in ("-m", "--message", "-F", "--file") and i + 1 < len(tokens):
            value, i = tokens[i + 1], i + 1
            is_file = tok in ("-F", "--file")
        elif tok.startswith("--message="):
            value, is_file = tok.split("=", 1)[1], False
        elif tok.startswith("--file="):
            value, is_file = tok.split("=", 1)[1], True
        elif tok.startswith("-m") and len(tok) > 2:
            value, is_file = tok[2:], False
        if value is not None:
            if not is_file:
                parts.append(value)
            elif value == "-":
                if not bodies:
                    return None
                parts.append(bodies[0])
            else:
                path = value if os.path.isabs(value) else os.path.join(cwd, value)
                try:
                    with open(path, encoding="utf-8") as fh:
                        parts.append(fh.read())
                except OSError:
                    return None
        i += 1
    if trailers:
        parts.append("\n".join(trailers))
    return "\n\n".join(p.strip("\n") for p in parts) if parts else None


def length_problems(message):
    lines = message.splitlines()
    problems = []
    if lines and len(lines[0]) > MAX_LINE:
        problems.append(f"intestazione di {len(lines[0])} caratteri (massimo {MAX_LINE})")
    for n, line in enumerate(lines[1:], start=2):
        if len(line) > MAX_LINE and "://" not in line and not line.startswith("#"):
            problems.append(f"riga {n} di {len(line)} caratteri (massimo {MAX_LINE})")
    return problems


def split_command(flat, tool_name):
    """Divide il comando in argomenti con le regole della sua shell."""
    if tool_name != "PowerShell":
        return shlex.split(flat)
    # PowerShell non usa il backslash come escape: in modalità POSIX C:\tmp\m.txt diventerebbe C:tmpm.txt
    return [tok[1:-1] if len(tok) > 1 and tok[0] == tok[-1] and tok[0] in "\"'" else tok
            for tok in shlex.split(flat, posix=False)]


def command_of(raw):
    """Il comando dell'input, anche quando il JSON non si riesce a leggere; se non si trova, tutto l'input."""
    try:
        cmd = (json.loads(raw).get("tool_input") or {}).get("command")
        if isinstance(cmd, str):
            return cmd
    except (ValueError, AttributeError):
        pass
    match = RAW_COMMAND.search(raw)
    return match.group(1) if match else raw


def check(raw):
    data = json.loads(raw)
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if not COMMIT.search(cmd):
        return 0
    cwd = data.get("cwd") or os.getcwd()

    bodies, flat = heredoc_bodies(cmd)
    try:
        tokens = split_command(flat, data.get("tool_name"))
    except ValueError:
        tokens = []
    message = message_from_args(tokens, bodies, cwd) if tokens else None

    # Attribuzioni: nel messaggio ricostruito. Se non si riesce a ricostruirlo, in tutto il comando
    # (heredoc compresi): i pattern sono abbastanza specifici da non scattare su percorsi o nomi di file.
    for text in [message if message is not None else cmd]:
        for pattern in ATTRIBUTION:
            if pattern.search(text):
                print("Commit bloccato: il messaggio contiene un'attribuzione all'AI "
                      "(trailer come Co-Authored-By, 'Generated with…', link a Claude Code). "
                      "Rimuovila e riproponi il commit.", file=sys.stderr)
                return 2

    if message is not None:
        problems = length_problems(message)
        if problems:
            print("Commit bloccato: " + "; ".join(problems)
                  + ". Vedi la skill commit: intestazione e righe del corpo entro 72 caratteri.",
                  file=sys.stderr)
            return 2
    return 0


def main():
    # Su Windows la codifica di default della console non è UTF-8: messaggi accentati e motivi del blocco si rovinerebbero.
    sys.stderr.reconfigure(encoding="utf-8")
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    try:
        return check(raw)
    except Exception as exc:  # confine dell'hook: nessun errore deve far passare un commit
        cmd = command_of(raw).lower()
        if "git" in cmd and "commit" in cmd:
            print(f"Commit bloccato: il controllo del messaggio è fallito ({type(exc).__name__}: {exc}). "
                  "Riprova o segnala il problema dell'hook.", file=sys.stderr)
            return 2
        return 0


if __name__ == "__main__":
    sys.exit(main())
