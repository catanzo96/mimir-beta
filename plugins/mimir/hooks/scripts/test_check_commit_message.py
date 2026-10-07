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
# Percorso Windows relativo alla cwd del test: su POSIX è un file con il backslash nel nome
WIN_REL = "attr\\msg.txt"
WIN_FILE = os.path.join(TMP, "attr", "msg.txt") if os.name == "nt" else os.path.join(TMP, WIN_REL)
os.makedirs(os.path.dirname(WIN_FILE), exist_ok=True)
shutil.copyfile(DIRTY_FILE, WIN_FILE)

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
    "intestazione accentata di 73 caratteri": 'git commit -m "feat: ' + "è" * 67 + '"',
    "opzione globale -c prima di commit": f'git -c user.name=x commit -m "{LONG}"',
    "opzione --no-pager prima di commit": f'git --no-pager commit -m "{LONG}"',
    "commit dentro un gruppo { }": f'{{ git commit -m "{LONG}"; }}',
    "commit dopo then": f'if true; then git commit -m "{LONG}"; fi',
}

# comandi del tool PowerShell
PS_BLOCK = {
    "git.exe con intestazione lunga": f'git.exe commit -m "{LONG}"',
    "maiuscole con intestazione lunga": f'Git COMMIT -m "{LONG}"',
    "-F con percorso Windows e attribuzione nel file": f"git commit -F {WIN_REL}",
    "here-string con attribuzione": 'git commit -m @"\nfeat: x\n\nCo-Authored-By: Claude <noreply@anthropic.com>\n"@',
}
PS_PASS = {
    "here-string pulita": 'git commit -m @"\nfeat: x\n\nCorpo breve.\n"@',
    "comando non git": "Get-ChildItem -Path C:\\repo -Filter *.md",
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
    # 72 caratteri ma 138 byte: la lunghezza si conta sul testo decodificato in UTF-8
    "intestazione accentata di 72 caratteri": 'git commit -m "feat: ' + "è" * 66 + '"',
    "comando PowerShell con backtick": "Get-ChildItem -Path C:\\repo `\n  -Filter *.md | Select-Object Name",
}

# input che fa fallire il controllo: blocca solo se sembra un commit
BROKEN = {
    "JSON rotto con git commit": ('{"tool_input": {"command": "git commit -m x"', 2),
    "JSON rotto senza commit": ('{"tool_input": {"command": "ls"', 0),
    "JSON rotto, commit solo nella cwd": ('{"cwd": "/home/x/git-commit-tools", "tool_input": {"command": "ls"', 0),
    "JSON rotto, commit in maiuscolo": ('{"tool_input": {"command": "Git COMMIT -m x"', 2),
}


def run_raw(payload):
    # byte UTF-8 come li manda Claude Code, indipendenti dalla codifica di default del sistema
    res = subprocess.run([sys.executable, SCRIPT], input=payload.encode("utf-8"), capture_output=True)
    return res.returncode


def run(command, tool="Bash"):
    return run_raw(json.dumps({"tool_name": tool, "tool_input": {"command": command}, "cwd": TMP},
                              ensure_ascii=False))


failures = 0
for tool, block, allow in (("Bash", BLOCK, PASS), ("PowerShell", PS_BLOCK, PS_PASS)):
    for name, cmd in block.items():
        code = run(cmd, tool)
        if code != 2:
            failures += 1
            print(f"FALLITO ({tool}, doveva bloccare, exit {code}): {name}")
    for name, cmd in allow.items():
        code = run(cmd, tool)
        if code != 0:
            failures += 1
            print(f"FALLITO ({tool}, doveva passare, exit {code}): {name}")
for name, (payload, expected) in BROKEN.items():
    code = run_raw(payload)
    if code != expected:
        failures += 1
        print(f"FALLITO (atteso exit {expected}, exit {code}): {name}")

shutil.rmtree(TMP, ignore_errors=True)
total = len(BLOCK) + len(PASS) + len(PS_BLOCK) + len(PS_PASS) + len(BROKEN)
print(f"{total - failures}/{total} casi corretti")
sys.exit(1 if failures else 0)
