#!/usr/bin/env python3
"""Test dell'hook retro-nudge: tace sotto la soglia, parla alla soglia, non blocca mai.

Uso: python3 test_retro_nudge.py [percorso dello script da provare]
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "retro-nudge.py")
EVERY = 25

DATA = tempfile.mkdtemp(prefix="claude-hook-test-")
ENV = dict(os.environ, CLAUDE_PLUGIN_DATA=DATA)


def run(stdin):
    return subprocess.run([sys.executable, SCRIPT], input=stdin, capture_output=True,
                          text=True, env=ENV, timeout=10)


def prompt(session_id):
    return run(json.dumps({"session_id": session_id, "hook_event_name": "UserPromptSubmit",
                           "prompt": "ciao"}))


failures = []


def check(name, ok, detail=""):
    if not ok:
        failures.append(f"{name} {detail}".strip())


try:
    for n in range(1, 2 * EVERY + 2):
        res = prompt("sessione-a")
        check(f"prompt {n}: exit", res.returncode == 0, f"(exit {res.returncode})")
        if n % EVERY == 0:
            try:
                ctx = json.loads(res.stdout)["hookSpecificOutput"]["additionalContext"]
                check(f"prompt {n}: promemoria", "/retro" in ctx)
            except (json.JSONDecodeError, KeyError, TypeError):
                check(f"prompt {n}: JSON del promemoria", False, repr(res.stdout[:80]))
        else:
            check(f"prompt {n}: silenzio", res.stdout.strip() == "", repr(res.stdout[:80]))

    res = prompt("sessione-b")
    check("sessione separata riparte da 1", res.stdout.strip() == "", repr(res.stdout[:80]))

    for name, stdin in {
        "input non JSON": "non json",
        "session_id mancante": json.dumps({"prompt": "x"}),
        "session_id con percorso": json.dumps({"session_id": "../../etc/x"}),
        "JSON non oggetto": "[1, 2]",
    }.items():
        res = run(stdin)
        check(name, res.returncode == 0 and res.stdout.strip() == "",
              f"(exit {res.returncode}, stdout {res.stdout[:60]!r})")

    # risale di un livello: senza il controllo sul session_id creerebbe DATA/fuori
    run(json.dumps({"session_id": "../fuori"}))
    check("session_id con percorso non crea file", not os.path.exists(os.path.join(DATA, "fuori")))
finally:
    shutil.rmtree(DATA, ignore_errors=True)

if failures:
    print("FALLITI:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print(f"OK: {2 * EVERY + 1} prompt, sessione separata, 4 input non validi")
