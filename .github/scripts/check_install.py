#!/usr/bin/env python3
"""Lancia un installer di Mímir due volte nella HOME corrente e controlla cosa produce.

Uso: python -I .github/scripts/check_install.py <comando dell'installer>
  es.  python -I .github/scripts/check_install.py ./install.sh --yes
       python -I .github/scripts/check_install.py powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1 -Yes

Dopo il primo lancio controlla CLAUDE.md, settings.json, l'exclude di git e i file personali; dopo il
secondo, che nessun file sia cambiato. Il formato delle regole si calcola qui, non con install.py: un
errore di install.py non deve passare perché il controllo lo ripete.
Solo per la CI: va lanciato dalla cartella di Mímir, in una HOME pulita.
"""
import hashlib
import json
import platform
import re
import subprocess
import sys
import types
from pathlib import Path

MIMIR = Path.cwd().resolve()


def load_install():
    path = MIMIR / "install.py"
    module = types.ModuleType("install")
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


def rule(path, windows):
    """Edit(//…): su Windows la lettera del disco diventa /c (doc permissions di Claude Code)."""
    if windows:
        drive = re.match(r"^([A-Za-z]):/(.*)$", path)
        if not drive:
            raise ValueError(f"percorso Windows senza lettera del disco: {path}")
        return f"//{drive.group(1).lower()}/{drive.group(2)}"
    return f"/{path}"


def check_settings(settings, install, mimir_dir, windows):
    problems = []
    permissions = settings.get("permissions") or {}
    ask, deny = permissions.get("ask") or [], permissions.get("deny") or []
    template = json.loads((MIMIR / "settings.template.json").read_text(encoding="utf-8"))["permissions"]
    expected_ask = [f"Edit({rule(f'{mimir_dir}/{name}', windows)}/**)" for name in install.PROTECTED_DIRS]
    expected_ask += [f"Edit({rule(f'{mimir_dir}/{name}', windows)})" for name in install.PROTECTED_FILES]
    problems += [f"ask senza {entry}" for entry in template.get("ask", []) + expected_ask if entry not in ask]
    problems += [f"deny senza {entry}" for entry in template.get("deny", []) if entry not in deny]
    for key, values in (("ask", ask), ("deny", deny)):
        if values != sorted(set(values)):
            problems.append(f"permissions.{key} non ordinato o con duplicati")
    deny_write = ((settings.get("sandbox") or {}).get("filesystem") or {}).get("denyWrite")
    if windows:
        if deny_write is not None:
            problems.append("sandbox.filesystem.denyWrite presente su Windows, dove la sandbox non c'è")
    else:
        expected = [f"{mimir_dir}/{name}" for name in install.PROTECTED_DIRS + install.PROTECTED_FILES]
        problems += [f"denyWrite senza {path}" for path in expected if path not in (deny_write or [])]
    return problems


def check_outputs(install, windows):
    problems = []
    mimir_dir = MIMIR.as_posix()
    claude_md = Path.home() / ".claude" / "CLAUDE.md"
    lines = claude_md.read_text(encoding="utf-8").splitlines() if claude_md.is_file() else []
    if list(zip(lines, lines[1:])).count((install.MARKER, f"@{mimir_dir}/CLAUDE.md")) != 1:
        problems.append(f"{claude_md}: marcatore e import di {mimir_dir}/CLAUDE.md non presenti una volta")
    settings_path = Path.home() / ".claude" / "settings.json"
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        problems.append(f"{settings_path} non leggibile: {exc}")
    else:
        problems += check_settings(settings, install, mimir_dir, windows)
    exclude = MIMIR / ".git" / "info" / "exclude"
    exclude_lines = exclude.read_text(encoding="utf-8").splitlines() if exclude.is_file() else []
    problems += [f"exclude senza {entry}" for entry in [install.EXCLUDE_MARKER] + install.EXCLUDE_ENTRIES
                 if entry not in exclude_lines]
    problems += [f"{name} non creato" for _, name in install.PERSONAL_FILES if not (MIMIR / name).is_file()]
    return problems


def snapshot():
    files = [p for p in (Path.home() / ".claude").rglob("*") if p.is_file()]
    files += [MIMIR / ".git" / "info" / "exclude"] + [MIMIR / name for _, name in load_install().PERSONAL_FILES]
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}


def run_installer(command, round_name):
    print(f"--- {round_name} lancio: {' '.join(command)}", flush=True)
    code = subprocess.run(command).returncode
    if code != 0:
        print(f"FALLITO: l'installer è uscito con {code} al {round_name} lancio")
    return code == 0


def main(argv):
    # niente separatore --: Windows PowerShell 5.1 lo può togliere passando gli argomenti
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    command = argv
    windows = platform.system() == "Windows"
    install = load_install()
    if not run_installer(command, "primo"):
        return 1
    problems = check_outputs(install, windows)
    before = snapshot()
    if not run_installer(command, "secondo"):
        return 1
    after = snapshot()
    problems += [f"cambiato dal secondo lancio: {path}" for path in sorted(set(before) | set(after))
                 if before.get(path) != after.get(path)]
    for problem in problems:
        print(f"FALLITO: {problem}")
    if problems:
        return 1
    print(f"OK: installazione {'Windows' if windows else 'POSIX'} completa e idempotente ({len(after)} file)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
