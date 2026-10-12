#!/usr/bin/env python3
"""Lancia tutte le suite di Mímir con lo stesso Python, ognuna con -I, e fallisce se una fallisce.

Uso: python -I .github/scripts/run_tests.py   (dalla cartella di Mímir)
Le variabili MIMIR_TEST_* arrivano alle suite dall'ambiente.
"""
import os
import subprocess
import sys
from pathlib import Path

SUITES = [
    "plugins/mimir/hooks/scripts/test_git_guard.py",
    "plugins/mimir/hooks/scripts/test_handoff.py",
    "plugins/mimir/hooks/scripts/test_maven_sandbox.py",
    "plugins/mimir/hooks/scripts/test_retro_nudge.py",
    "plugins/mimir/hooks/scripts/test_run_python.py",
    "plugins/mimir/skills/scrivi-skill/scripts/test_somiglianza.py",
    "test_install.py",
    "test_claude_mimir.py",
]


def main():
    # senza PowerShell test_install e test_claude_mimir saltano le classi .ps1 e risultano OK
    if os.environ.get("GITHUB_ACTIONS") == "true" and not os.environ.get("MIMIR_TEST_PWSH"):
        print("In CI serve MIMIR_TEST_PWSH: senza, i test dei .ps1 verrebbero saltati")
        return 1
    failed = []
    for suite in SUITES:
        print(f"::group::{suite}", flush=True)
        code = subprocess.run([sys.executable, "-I", str(Path(suite))]).returncode
        print("::endgroup::", flush=True)
        print(f"{'OK' if code == 0 else 'FALLITO'} ({code}): {suite}", flush=True)
        if code != 0:
            failed.append(suite)
    if failed:
        print(f"Suite fallite: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
