#!/usr/bin/env python3
"""Test dell'hook maven-sandbox: parla solo con la variabile del launcher e un pom.xml.

Uso: python3 test_maven_sandbox.py [percorso dello script da provare]
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "maven-sandbox.py")

TMP = tempfile.mkdtemp(prefix="claude-hook-test-")
MAVEN = os.path.join(TMP, "maven")
OTHER = os.path.join(TMP, "altro")
SETTINGS = os.path.join(TMP, "maven-settings.xml")
for folder in (MAVEN, OTHER):
    os.makedirs(folder)
open(os.path.join(MAVEN, "pom.xml"), "w").close()
open(SETTINGS, "w").close()

BASE_ENV = {k: v for k, v in os.environ.items() if k not in ("MIMIR_MAVEN_SETTINGS", "CLAUDE_PROJECT_DIR")}


def run(stdin, settings=None):
    env = dict(BASE_ENV)
    if settings is not None:
        env["MIMIR_MAVEN_SETTINGS"] = settings
    return subprocess.run([sys.executable, SCRIPT], input=stdin, capture_output=True,
                          text=True, env=env, timeout=10)


def start(cwd):
    return json.dumps({"session_id": "s", "hook_event_name": "SessionStart", "source": "startup", "cwd": cwd})


failures = []


def check(name, res, speaks):
    ok = res.returncode == 0
    if speaks:
        try:
            ctx = json.loads(res.stdout)["hookSpecificOutput"]["additionalContext"]
            ok = ok and "MIMIR_MAVEN_SETTINGS" in ctx and "-llr" in ctx
        except (json.JSONDecodeError, KeyError, TypeError):
            ok = False
    else:
        ok = ok and res.stdout.strip() == ""
    if not ok:
        failures.append(f"{name} (exit {res.returncode}, stdout {res.stdout[:60]!r})")


try:
    check("progetto Maven con il launcher", run(start(MAVEN), SETTINGS), speaks=True)
    check("progetto senza pom.xml", run(start(OTHER), SETTINGS), speaks=False)
    check("sessione senza launcher", run(start(MAVEN)), speaks=False)
    check("variabile verso un file che non esiste", run(start(MAVEN), os.path.join(TMP, "manca.xml")), speaks=False)
    check("input non JSON", run("non json", SETTINGS), speaks=False)
    check("JSON non oggetto", run("[1]", SETTINGS), speaks=False)
finally:
    shutil.rmtree(TMP, ignore_errors=True)

if failures:
    print("FALLITI:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print("OK: 6 casi")
