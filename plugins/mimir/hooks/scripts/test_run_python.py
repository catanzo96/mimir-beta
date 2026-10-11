#!/usr/bin/env python3
"""Test del wrapper run-python.sh: sceglie un interprete che funziona e, senza Python, blocca solo i comandi
git che scrivono.

Uso: python3 test_run_python.py [percorso del wrapper da provare]
Su Windows bash deve essere quello di Git for Windows: se nel PATH c'è prima un altro bash
(per esempio quello di WSL), indicane il percorso in MIMIR_TEST_BASH.
"""
import atexit
import importlib.util
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

# accanto ai test e non nella cartella temporanea: il wrapper scarta gli interpreti nelle cartelle scrivibili
# dalla sandbox, e nella sandbox la cartella temporanea è una di queste (/tmp/claude-<uid>)
TMP = tempfile.mkdtemp(prefix=".tmp-test-run-python-", dir=HERE)
# rimosse anche se il setup fallisce: la cartella sta nel repo
SANDBOX_TMP = []


@atexit.register
def remove_test_folders():
    for folder in [TMP, *SANDBOX_TMP]:
        shutil.rmtree(folder, ignore_errors=True)


# la cwd di ogni caso, vuota: senza CLAUDE_PROJECT_DIR il progetto è la cwd, e non deve contenere i finti
CWD = os.path.join(TMP, "cwd")
EMPTY = os.path.join(TMP, "senza-python")
FAKE = os.path.join(TMP, "finti")
FAKE_PY = os.path.join(TMP, "solo-py")
SCRIPT = os.path.join(TMP, "eco.py")
for folder in (CWD, EMPTY, FAKE, FAKE_PY):
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
# un python3 piantato nel progetto (.venv/bin attivato, node_modules/.bin, .): supera il controllo della
# versione ma non esegue lo script, così un test vede se il wrapper l'ha scelto
PROJECT = os.path.join(TMP, "progetto")
PLANTED = "if [ \"$1\" = -c ]; then exec \"" + REAL + "\" \"$@\"; fi\necho piantato >&2\nexit 7"
for folder in (os.path.join(PROJECT, ".venv", "bin"), PROJECT):
    os.makedirs(folder, exist_ok=True)
    fake(folder, "python3", PLANTED)
# lo stesso fuori dal progetto, in una cartella dove Claude può fare cd (/tmp/x): ELSEWHERE e il suo bin
ELSEWHERE = os.path.join(TMP, "altrove", "bin")
os.makedirs(ELSEWHERE)
fake(ELSEWHERE, "python3", PLANTED)
# una home finta con python3 in ~/.local/bin, per i progetti che la contengono (home, /home, /)
HOME_PARENT = os.path.join(TMP, "home")
HOME = os.path.join(HOME_PARENT, "utente")
HOME_BIN = os.path.join(HOME, ".local", "bin")
os.makedirs(HOME_BIN)
fake(HOME_BIN, "python3", f'exec "{REAL}" "$@"')
# un fratello del progetto con lo stesso prefisso nel nome (progetto-altro): è fuori, il suo python3 si usa
SIBLING = os.path.join(TMP, "progetto-altro", "bin")
os.makedirs(SIBLING)
fake(SIBLING, "python3", PLANTED)
# link: una voce del PATH fuori che porta nel progetto, il progetto raggiunto da un link, una voce nel
# progetto che porta fuori (ELSEWHERE); su Windows creare link richiede privilegi, quei casi si saltano
LINKS = os.name != "nt"
LINK_TO_VENV = os.path.join(TMP, "link-al-venv")
LINK_TO_PROJECT = os.path.join(TMP, "link-al-progetto")
LINK_OUT = os.path.join(PROJECT, "bin-collegato")
# un python3 vero raggiunto da un link di cartella: il wrapper deve lanciare il percorso reale
REAL_BIN = os.path.join(TMP, "vero", "bin")
os.makedirs(REAL_BIN)
fake(REAL_BIN, "python3", f'echo "lanciato:$0" >&2\nexec "{REAL}" "$@"')
LINK_TO_REAL = os.path.join(TMP, "link-al-vero")
if LINKS:
    os.symlink(os.path.join(PROJECT, ".venv", "bin"), LINK_TO_VENV)
    os.symlink(PROJECT, LINK_TO_PROJECT)
    os.symlink(ELSEWHERE, LINK_OUT)
    os.symlink(os.path.dirname(REAL_BIN), LINK_TO_REAL)
# una home con le cartelle che la sandbox può scrivere (allowWrite di sandbox.settings.json)
SANDBOX_HOME = os.path.join(TMP, "casa")
ROOT = Path(HERE).parents[3]
ALLOW_WRITE = json.loads(Path(ROOT, "sandbox.settings.json").read_text(encoding="utf-8"))["sandbox"]["filesystem"]["allowWrite"]
SANDBOX_TMPDIR = os.path.join(TMP, "tmpdir-sandbox")
SANDBOX_DIRS = [os.path.join(SANDBOX_HOME, entry[2:]) for entry in ALLOW_WRITE] + [SANDBOX_TMPDIR]
for folder in SANDBOX_DIRS:
    os.makedirs(folder)
    fake(folder, "python3", PLANTED)
# le cartelle temporanee della sandbox stanno fuori da TMP: una sottocartella dove si può creare
# (in sandbox /tmp/claude non si crea, su Windows /tmp è altrove)
if os.name != "nt":
    for base in ("/tmp/claude", f"/tmp/claude-{os.getuid()}"):
        try:
            folder = tempfile.mkdtemp(prefix="test-run-python-", dir=base) if os.path.isdir(base) else None
        except OSError:
            folder = None
        if folder:
            SANDBOX_TMP.append(folder)
            fake(folder, "python3", PLANTED)
        else:
            print(f"saltato: python3 in {base}, cartella non disponibile")
os.makedirs(PROJECT + "2")


def run(path_dir, args, stdin, env_extra=None, cwd=CWD):
    # CLAUDE_PROJECT_DIR e TMPDIR della sessione che lancia i test non devono contare: solo quelle del caso
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR", "TMPDIR")}
    env.update(PATH=path_dir, **(env_extra or {}))
    return subprocess.run([BASH, WRAPPER, *args, SCRIPT], input=stdin.encode("utf-8"),
                          capture_output=True, env=env, timeout=30, cwd=cwd)


def bash_command(command):
    return json.dumps({"tool_input": {"command": command}})


failures = []
CASES = 0


def check(name, res, code, stdout=None, stderr=None):
    global CASES
    CASES += 1
    ok = (res.returncode == code
          and (stdout is None or res.stdout.decode("utf-8") == stdout)
          and (stderr is None or stderr in res.stderr.decode("utf-8")))
    if not ok:
        failures.append(f"{name} (exit {res.returncode}, atteso {code}, "
                        f"stdout {res.stdout[:60]!r}, stderr {res.stderr[:120]!r})")


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
for command in ("git status", "git merge-base main HEAD", "git log --oneline", "git stash-x"):
    check(f"senza Python, fail-closed, {command} passa",
          run(EMPTY, ["--fail-closed"], bash_command(command)), 0)
# senza Python il wrapper deve bloccare ogni sottocomando che git-guard tratta come scrittura,
# anche le letture di branch e stash (falso positivo accettato: senza Python non si distinguono)
spec = importlib.util.spec_from_file_location("git_guard", os.path.join(HERE, "git-guard.py"))
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
for sub in sorted(guard.WRITE_SUBCOMMANDS):
    check(f"senza Python, fail-closed, git -C . {sub} bloccato",
          run(EMPTY, ["--fail-closed"], bash_command(f"git -C . {sub} x")), 2)
check("senza Python, fail-closed, git commit bloccato con il motivo",
      run(EMPTY, ["--fail-closed"], commit), 2, stderr="comando bloccato")
check("python3 rotto, si usa python: exit e stdout dello script",
      run(FAKE, ["--fail-closed"], commit), 3, stdout=commit)
check("python3 stub e python vecchio, si usa py -3",
      run(FAKE_PY, ["--fail-closed"], commit), 3, stdout=commit)
# (C) un interprete sotto la cartella del progetto non si usa: si passa al successivo fuori
venv_first = os.pathsep.join([os.path.join(PROJECT, ".venv", "bin"), FAKE])
check("python3 nel .venv del progetto scartato, si usa python",
      run(venv_first, ["--fail-closed"], commit, {"CLAUDE_PROJECT_DIR": PROJECT}), 3, stdout=commit)
check("python3 in . scartato con la cwd come progetto, si usa python",
      run(os.pathsep.join([".", FAKE]), ["--fail-closed"], commit, cwd=PROJECT), 3, stdout=commit)
# HOME vuota non è la cwd: l'esclusione resta
check("HOME vuota, python3 nel .venv del progetto scartato",
      run(venv_first, ["--fail-closed"], commit, {"CLAUDE_PROJECT_DIR": PROJECT, "HOME": ""}, cwd=PROJECT),
      3, stdout=commit)
# un progetto che contiene la home non ha un fuori: l'esclusione non si applica (limite documentato)
for root in (HOME, HOME_PARENT, "/"):
    check(f"progetto {root!r} che contiene la home, python3 in ~/.local/bin usato",
          run(HOME_BIN, ["--fail-closed"], commit, {"CLAUDE_PROJECT_DIR": root, "HOME": HOME}), 3, stdout=commit)
# tutti gli interpreti dentro il progetto: si blocca con il motivo vero, non con "non trovato"
only_project = os.path.join(PROJECT, ".venv", "bin")
check("python3 solo nel progetto, git commit bloccato con il motivo",
      run(only_project, ["--fail-closed"], commit, {"CLAUDE_PROJECT_DIR": PROJECT}), 2,
      stderr="scartati")
check("python3 solo nel progetto, ls passa",
      run(only_project, ["--fail-closed"], ls, {"CLAUDE_PROJECT_DIR": PROJECT}), 0)
check("python3 solo nel progetto, senza flag lo script è saltato con il motivo",
      run(only_project, [], commit, {"CLAUDE_PROJECT_DIR": PROJECT}), 0, stderr="scartati")
# una voce relativa del PATH (., bin, vuota) segue i cd di Claude: scartata anche fuori dal progetto
for entry in (".", "bin", ""):
    check(f"python3 dalla voce relativa {entry!r} fuori dal progetto scartato, si usa python",
          run(os.pathsep.join([entry, FAKE]), ["--fail-closed"], commit, {"CLAUDE_PROJECT_DIR": PROJECT},
              cwd=ELSEWHERE if entry != "bin" else os.path.dirname(ELSEWHERE)), 3, stdout=commit)
# senza CLAUDE_PROJECT_DIR il progetto è la cwd anche con una voce assoluta del PATH
check("cwd come progetto, python3 nel .venv con voce assoluta scartato",
      run(venv_first, ["--fail-closed"], commit, cwd=PROJECT), 3, stdout=commit)
# progetto-altro ha lo stesso prefisso nel nome ma è fuori: il suo python3 si usa (exit 7 del finto)
check("python3 in un fratello con lo stesso prefisso usato",
      run(os.pathsep.join([SIBLING, FAKE]), ["--fail-closed"], commit, {"CLAUDE_PROJECT_DIR": PROJECT}), 7)
# una home con lo stesso prefisso del progetto (progetto2) non lo contiene: l'esclusione resta
check("home con lo stesso prefisso del progetto, python3 nel .venv scartato",
      run(venv_first, ["--fail-closed"], commit, {"CLAUDE_PROJECT_DIR": PROJECT, "HOME": PROJECT + "2"}),
      3, stdout=commit)
if LINKS:
    check("voce del PATH fuori che porta nel progetto, scartata",
          run(os.pathsep.join([LINK_TO_VENV, FAKE]), ["--fail-closed"], commit, {"CLAUDE_PROJECT_DIR": PROJECT}),
          3, stdout=commit)
    check("progetto raggiunto da un link, python3 nel .venv scartato",
          run(venv_first, ["--fail-closed"], commit, {"CLAUDE_PROJECT_DIR": LINK_TO_PROJECT}), 3, stdout=commit)
    check("voce del PATH nel progetto che porta fuori, scartata",
          run(os.pathsep.join([LINK_OUT, FAKE]), ["--fail-closed"], commit, {"CLAUDE_PROJECT_DIR": PROJECT}),
          3, stdout=commit)
    # lanciato dal percorso reale: un link di cartella non sposta dove Python cerca pyvenv.cfg
    check("python3 raggiunto da un link di cartella lanciato dal percorso reale",
          run(os.path.join(LINK_TO_REAL, "bin"), ["--fail-closed"], commit, {"CLAUDE_PROJECT_DIR": PROJECT}),
          3, stdout=commit, stderr="lanciato:" + os.path.join(os.path.realpath(REAL_BIN), "python3"))
# cartelle che la sandbox può scrivere (allowWrite e TMPDIR): un python3 piantato lì non si usa
for folder in SANDBOX_DIRS:
    check(f"python3 in {os.path.relpath(folder, TMP)!r}, scrivibile dalla sandbox, scartato",
          run(os.pathsep.join([folder, FAKE]), ["--fail-closed"], commit,
              {"CLAUDE_PROJECT_DIR": PROJECT, "HOME": SANDBOX_HOME, "TMPDIR": SANDBOX_TMPDIR}), 3, stdout=commit)
for folder in SANDBOX_TMP:
    check(f"python3 in {folder!r}, temporanea della sandbox, scartato",
          run(os.pathsep.join([folder, FAKE]), ["--fail-closed"], commit, {"CLAUDE_PROJECT_DIR": PROJECT}),
          3, stdout=commit)

if failures:
    print("FALLITI:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print(f"OK: {CASES} casi")
