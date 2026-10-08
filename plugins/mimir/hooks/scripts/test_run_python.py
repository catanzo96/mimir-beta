#!/usr/bin/env python3
"""Test del wrapper run-python.sh: sceglie un interprete che funziona e, senza Python, blocca solo i commit.

Uso: python3 test_run_python.py [percorso del wrapper da provare]
Su Windows bash deve essere quello di Git for Windows: se nel PATH c'è prima un altro bash
(per esempio quello di WSL), indicane il percorso in MIMIR_TEST_BASH.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
WRAPPER = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "run-python.sh")
BASH = os.environ.get("MIMIR_TEST_BASH") or shutil.which("bash")

TMP = tempfile.mkdtemp(prefix="claude-hook-test-")
EMPTY = os.path.join(TMP, "senza-python")
FAKE = os.path.join(TMP, "finti")
FAKE_PY = os.path.join(TMP, "solo-py")
SCRIPT = os.path.join(TMP, "eco.py")
for folder in (EMPTY, FAKE, FAKE_PY):
    os.makedirs(folder)
with open(SCRIPT, "w", encoding="utf-8") as fh:
    fh.write("import sys\nsys.stdout.write(sys.stdin.read())\nsys.exit(3)\n")
REAL = Path(sys.executable).as_posix()


def fake(folder, name, body):
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("#!/bin/sh\n" + body + "\n")
    os.chmod(path, 0o755)


# python3 come lo stub dello Store (esce con 9009, che come codice di uscita vale 49); python funziona
fake(FAKE, "python3", "exit 49")
fake(FAKE, "python", f'exec "{REAL}" "$@"')
# come su Windows con python.org: python3 è lo stub, python è troppo vecchio (il controllo della versione
# fallisce), funziona solo il launcher py, che va chiamato con -3
fake(FAKE_PY, "python3", "exit 49")
fake(FAKE_PY, "python", "exit 1")
fake(FAKE_PY, "py", f'[ "$1" = -3 ] || exit 1\nshift\nexec "{REAL}" "$@"')


def run(path_dir, args, stdin):
    env = dict(os.environ, PATH=path_dir)
    return subprocess.run([BASH, WRAPPER, *args, SCRIPT], input=stdin.encode("utf-8"),
                          capture_output=True, env=env, timeout=30)


def bash_command(command):
    return json.dumps({"tool_input": {"command": command}})


failures = []


def check(name, res, code, stdout=None, stderr=None):
    ok = (res.returncode == code
          and (stdout is None or res.stdout.decode("utf-8") == stdout)
          and (stderr is None or stderr in res.stderr.decode("utf-8")))
    if not ok:
        failures.append(f"{name} (exit {res.returncode}, atteso {code}, "
                        f"stdout {res.stdout[:60]!r}, stderr {res.stderr[:120]!r})")


CASES = 0
try:
    commit, ls = bash_command("git commit -m x"), bash_command("ls")
    ls_in_commit_dir = json.dumps({"cwd": "/home/x/git-commit-tools", "tool_input": {"command": "ls"}})
    for name, args in [
        ("senza Python, fail-closed, ls passa", (EMPTY, ["--fail-closed"], ls, 0)),
        ("senza Python, fail-closed, ls in una cartella con commit nel nome passa",
         (EMPTY, ["--fail-closed"], ls_in_commit_dir, 0)),
        ("senza Python, fail-closed, stdin vuoto passa", (EMPTY, ["--fail-closed"], "", 0)),
        ("senza Python, fail-closed, Git COMMIT bloccato",
         (EMPTY, ["--fail-closed"], bash_command("Git COMMIT -m x"), 2)),
        ("senza Python, senza flag, git commit passa", (EMPTY, [], commit, 0)),
        ("senza Python, fail-closed, git push bloccato",
         (EMPTY, ["--fail-closed"], bash_command("git push origin main"), 2)),
        ("senza Python, fail-closed, git tag bloccato", (EMPTY, ["--fail-closed"], bash_command("git tag v1"), 2)),
        ("senza Python, fail-closed, git commit-tree bloccato",
         (EMPTY, ["--fail-closed"], bash_command("git commit-tree abc -m x"), 2)),
        ("senza Python, fail-closed, git send-pack bloccato",
         (EMPTY, ["--fail-closed"], bash_command("git send-pack origin main"), 2)),
        ("senza Python, fail-closed, git e push separati da tab bloccato",
         (EMPTY, ["--fail-closed"], bash_command("git\tpush"), 2)),
        ("senza Python, fail-closed, git e push separati da a capo bloccato",
         (EMPTY, ["--fail-closed"], bash_command("git status\ngit push"), 2)),
        ("senza Python, fail-closed, git \"push\" tra virgolette bloccato",
         (EMPTY, ["--fail-closed"], bash_command('git "push" origin'), 2)),
        ("senza Python, fail-closed, git fetch --tags passa",
         (EMPTY, ["--fail-closed"], bash_command("git fetch --tags"), 0)),
        ("senza Python, fail-closed, docker tag passa",
         (EMPTY, ["--fail-closed"], bash_command("docker tag img:1 img:latest"), 0)),
    ]:
        path_dir, flags, stdin, code = args
        check(name, run(path_dir, flags, stdin), code)
        CASES += 1
    check("senza Python, fail-closed, git commit bloccato con il motivo",
          run(EMPTY, ["--fail-closed"], commit), 2, stderr="comando bloccato")
    check("python3 rotto, si usa python: exit e stdout dello script",
          run(FAKE, ["--fail-closed"], commit), 3, stdout=commit)
    check("python3 stub e python vecchio, si usa py -3",
          run(FAKE_PY, ["--fail-closed"], commit), 3, stdout=commit)
    CASES += 3
finally:
    shutil.rmtree(TMP, ignore_errors=True)

if failures:
    print("FALLITI:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print(f"OK: {CASES} casi")
