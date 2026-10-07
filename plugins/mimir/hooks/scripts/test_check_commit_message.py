#!/usr/bin/env python3
"""Test dell'hook check-commit-message: casi che devono bloccare e casi che devono passare.

Uso: python3 test_check_commit_message.py [percorso dello script da provare]
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "check-commit-message.py")

TMP = tempfile.mkdtemp(prefix="claude-hook-test-")
CLEAN_FILE = os.path.join(TMP, "msg-pulito.txt")
DIRTY_FILE = os.path.join(TMP, "msg-attribuito.txt")
with open(CLEAN_FILE, "w", encoding="utf-8") as fh:
    fh.write("feat(core): aggiungi una skill\n\nCorpo breve.\n")
with open(DIRTY_FILE, "w", encoding="utf-8") as fh:
    fh.write("feat: aggiungi una skill\n\nCo-Authored-By: GitHub Copilot <copilot@github.com>\n")

LONG = "feat(core): " + "x" * 70
HEREDOC = "git commit -F - <<'EOF'\n{}\nEOF"

BLOCK = {
    "trailer Claude in heredoc": HEREDOC.format(
        "feat: aggiungi x\n\nCo-Authored-By: Claude <noreply@anthropic.com>"),
    "Generated with Claude Code": 'git commit -m "feat: x" -m "🤖 Generated with [Claude Code](https://claude.com/claude-code)"',
    "trailer passato con --trailer": 'git commit -m "feat: x" --trailer "Co-authored-by: Claude <noreply@anthropic.com>"',
    "attribuzione in un file -F": f"git commit -F {DIRTY_FILE}",
    "frase italiana": HEREDOC.format("feat: aggiungi x\n\nGenerato con Claude Code."),
    "intestazione oltre 72": f'git commit -m "{LONG}"',
    "riga del corpo oltre 72": HEREDOC.format("feat: x\n\n" + "y" * 80),
    "commit-tree con attribuzione": "git commit-tree abc -p def -F - <<'EOF'\nfeat: x\n\nCo-Authored-By: Claude <noreply@anthropic.com>\nEOF",
}

PASS = {
    "percorso con claude nel file -F": f"git commit -F {CLEAN_FILE}",
    "git add di .claude-plugin nello stesso comando": 'git add .claude-plugin/marketplace.json && git commit -m "feat: aggiorna il marketplace"',
    "CLAUDE.md nel corpo": HEREDOC.format("feat(agents): sostituisci Explore\n\nGira senza CLAUDE.md e in sola lettura."),
    "argomento AI": 'git commit -m "feat(api): integra l\'API di Anthropic"',
    "co-autore umano": HEREDOC.format("feat: x\n\nCo-Authored-By: Mario Rossi <mario.rossi@example.com>"),
    "URL lungo nel corpo": HEREDOC.format("docs: x\n\nVedi https://example.com/" + "a" * 90),
    "comando che non è un commit": 'echo "Co-Authored-By: Claude"',
    "amend senza messaggio": "git commit --amend --no-edit",
    "git commit citato in una stringa di un altro comando": "python3 - <<'X'\nnota = 'dopo `git commit` il trailer Generated with Claude Code'\nX",
    "messaggio che descrive l'hook": 'git commit -m "fix(core): l\'hook ignora i nomi di file come CLAUDE.md"',
    "intestazione di 72 esatti": 'git commit -m "' + "feat: " + "z" * 66 + '"',
}


def run(command):
    payload = json.dumps({"tool_input": {"command": command}, "cwd": TMP})
    res = subprocess.run([SCRIPT], input=payload, capture_output=True, text=True)
    return res.returncode


failures = 0
for name, cmd in BLOCK.items():
    code = run(cmd)
    if code != 2:
        failures += 1
        print(f"FALLITO (doveva bloccare, exit {code}): {name}")
for name, cmd in PASS.items():
    code = run(cmd)
    if code != 0:
        failures += 1
        print(f"FALLITO (doveva passare, exit {code}): {name}")

shutil.rmtree(TMP, ignore_errors=True)
total = len(BLOCK) + len(PASS)
print(f"{total - failures}/{total} casi corretti")
sys.exit(1 if failures else 0)
