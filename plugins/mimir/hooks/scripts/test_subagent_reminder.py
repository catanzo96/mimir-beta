#!/usr/bin/env python3
"""Test dell'hook subagent-reminder: richiamo solo a Explore e Plan, mai un blocco.

Uso: python3 test_subagent_reminder.py [percorso dello script da provare]
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "subagent-reminder.py")
TIMEOUT = 5  # come in hooks.json

REMINDER = (
    "Regole di Mímir per questo subagent: rispondi in italiano; separa ciò che hai "
    "accertato dalle ipotesi e per ogni fatto indica l'evidenza (file:riga o comando); "
    "per dire che qualcosa non c'è serve una ricerca che non salti file; resta nel "
    "perimetro della richiesta e segnala il resto senza farlo."
)


def run(stdin):
    return subprocess.run([sys.executable, SCRIPT], input=stdin.encode("utf-8"),
                          capture_output=True, timeout=TIMEOUT)


def event(agent_type):
    return json.dumps({"session_id": "s1", "hook_event_name": "SubagentStart",
                       "agent_id": "a1", "agent_type": agent_type}, ensure_ascii=False)


failures = []


def check(name, ok, detail=""):
    if not ok:
        failures.append(f"{name} {detail}".strip())


for agent_type in ("Explore", "Plan"):
    res = run(event(agent_type))
    check(f"{agent_type}: exit 0", res.returncode == 0, f"(exit {res.returncode})")
    try:
        out = json.loads(res.stdout.decode("utf-8"))["hookSpecificOutput"]
        check(f"{agent_type}: evento", out.get("hookEventName") == "SubagentStart", repr(out))
        check(f"{agent_type}: testo del richiamo", out.get("additionalContext") == REMINDER,
              repr(out.get("additionalContext")))
    except (json.JSONDecodeError, KeyError, TypeError, UnicodeDecodeError):
        check(f"{agent_type}: JSON del richiamo", False, repr(res.stdout[:80]))

# gli altri vedono già le regole (general-purpose, agent di Mímir) o non sono previsti:
# il matcher di hooks.json li esclude, lo script li ignora comunque
for agent_type in ("general-purpose", "mimir:code-reviewer", "explore", "Explorer", ""):
    res = run(event(agent_type))
    check(f"{agent_type!r}: silenzio", res.returncode == 0 and res.stdout.strip() == b"",
          f"(exit {res.returncode}, stdout {res.stdout[:60]!r})")

for name, stdin in {
    "input non JSON": "non json",
    "JSON non oggetto": "[1, 2]",
    "agent_type mancante": json.dumps({"hook_event_name": "SubagentStart"}),
    "agent_type non stringa": json.dumps({"agent_type": ["Explore"]}),
}.items():
    res = run(stdin)
    check(name, res.returncode == 0 and res.stdout.strip() == b"",
          f"(exit {res.returncode}, stdout {res.stdout[:60]!r})")

if failures:
    print("FALLITI:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print("OK: Explore e Plan ricevono il richiamo, 5 altri tipi e 4 input non validi in silenzio")
