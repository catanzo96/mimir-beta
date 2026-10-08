#!/usr/bin/env python3
"""Test di bin/claude-mimir.ps1, il launcher per Windows nativo.

Uso: python3 -I test_claude_mimir.py
Il launcher gira su una copia di Mímir in una cartella temporanea, con un claude finto nel PATH che
registra argomenti e variabili d'ambiente: il repo vero e la CLI di Claude Code non vengono toccati.
Su Linux gira con pwsh 7: la compatibilità con Windows PowerShell 5.1 la controlla PSScriptAnalyzer,
il resto la CI su Windows.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYTHON = Path(sys.executable).resolve()
PWSH = os.environ.get("MIMIR_TEST_PWSH") or shutil.which("pwsh") or shutil.which("powershell")
GENERATED = Path("sandbox", "windows.settings.json")
WARNING = "Windows nativo: comandi senza sandbox"

FAKE_CLAUDE = """import json, os, sys
with open(os.environ["FAKE_CLAUDE_LOG"], "w", encoding="utf-8") as log:
    json.dump({"args": sys.argv[1:],
               "env": {name: os.environ.get(name) for name in
                       ("CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD", "MIMIR_MAVEN_SETTINGS")}}, log)
sys.exit(int(os.environ.get("FAKE_CLAUDE_EXIT", "0")))
"""


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


@unittest.skipUnless(PWSH, "PowerShell non trovato (MIMIR_TEST_PWSH, pwsh o powershell)")
class ClaudeMimirPs1(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="mimir-launcher-test-")).resolve()
        self.addCleanup(shutil.rmtree, str(self.root), ignore_errors=True)
        self.mimir = self.root / "mimir"
        (self.mimir / "bin").mkdir(parents=True)
        shutil.copy2(str(HERE / "bin" / "claude-mimir.ps1"), str(self.mimir / "bin" / "claude-mimir.ps1"))
        shutil.copy2(str(HERE / "sandbox.settings.json"), str(self.mimir / "sandbox.settings.json"))
        (self.mimir / "sandbox").mkdir()
        self.generated = self.mimir / GENERATED
        self.bin = self.root / "fake-bin"
        self.log = self.root / "claude.json"
        self.install_fake_claude()

    def install_fake_claude(self):
        script = self.root / "fake_claude.py"
        write(script, FAKE_CLAUDE)
        if os.name == "nt":
            write(self.bin / "claude.cmd", f'@"{PYTHON}" -I "{script}" %*\n')
        else:
            write(self.bin / "claude", f'#!/bin/sh\nexec "{PYTHON}" -I "{script}" "$@"\n')
            (self.bin / "claude").chmod(0o755)

    def env(self, **extra):
        env = {"PATH": str(self.bin), "HOME": str(self.root), "USERPROFILE": str(self.root),
               "LANG": "C.UTF-8", "FAKE_CLAUDE_LOG": str(self.log)}
        for name in ("SystemRoot", "WINDIR", "TEMP", "TMP"):  # senza, powershell.exe non parte
            if name in os.environ:
                env[name] = os.environ[name]
        env.update(extra)
        return env

    def run_ps1(self, *args, **env):
        command = [PWSH, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                   "-File", str(self.mimir / "bin" / "claude-mimir.ps1")] + list(args)
        return subprocess.run(command, env=self.env(**env), capture_output=True, text=True, encoding="utf-8",
                              stdin=subprocess.DEVNULL)

    def received(self):
        return json.loads(self.log.read_text(encoding="utf-8"))

    def mimir_args(self):
        return ["--settings", str(self.generated), "--add-dir", str(self.mimir),
                "--plugin-dir", str(self.mimir / "plugins")]

    def expected_settings(self):
        settings = json.loads((self.mimir / "sandbox.settings.json").read_text(encoding="utf-8"))
        settings["sandbox"] = {"enabled": False}
        return settings

    def test_file_in_utf8_con_bom(self):
        # Windows PowerShell 5.1 legge un .ps1 senza BOM come ANSI e rompe gli accenti
        self.assertEqual((HERE / "bin" / "claude-mimir.ps1").read_bytes()[:3], b"\xef\xbb\xbf")

    def test_argomenti_dopo_quelli_di_mimir_e_avviso(self):
        result = self.run_ps1("-p", "a b", "--model", "opus")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.received()["args"], self.mimir_args() + ["-p", "a b", "--model", "opus"])
        self.assertIn(WARNING, result.stderr)
        for remaining in ("ask/deny", "hook"):
            self.assertIn(remaining, result.stderr)
        for lost in ("rete", "credenziali"):
            self.assertIn(lost, result.stderr)
        self.assertNotIn(WARNING, result.stdout, "l'avviso deve andare su stderr")

    def test_sottocomando_agents(self):
        result = self.run_ps1("agents", "--add-dir", "altro")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.received()["args"], ["agents"] + self.mimir_args() + ["--add-dir", "altro"])

    def test_variabili_d_ambiente(self):
        # senza MIMIR_MAVEN_SETTINGS: l'hook di Maven farebbe lanciare le build offline come nella sandbox
        self.run_ps1()
        self.assertEqual(self.received()["env"], {
            "CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD": "1", "MIMIR_MAVEN_SETTINGS": None})

    def test_file_generato_con_sandbox_spenta(self):
        result = self.run_ps1()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        content = self.generated.read_bytes()
        self.assertNotEqual(content[:3], b"\xef\xbb\xbf", "il file generato deve essere senza BOM")
        self.assertEqual(json.loads(content.decode("utf-8")), self.expected_settings())

    def test_accenti_e_array_corti_conservati(self):
        # ConvertFrom-Json/ConvertTo-Json: accenti, array con un solo elemento o vuoti
        write(self.mimir / "sandbox.settings.json", json.dumps({
            "sandbox": {"enabled": True, "failIfUnavailable": True},
            "permissions": {"ask": ["Bash(git commit:*)"], "deny": []},
            "nota": "Mímir"}, ensure_ascii=False))
        result = self.run_ps1()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(self.generated.read_text(encoding="utf-8")), self.expected_settings())

    def test_codice_di_uscita_di_claude(self):
        result = self.run_ps1(FAKE_CLAUDE_EXIT="3")
        self.assertEqual(result.returncode, 3)

    def test_rilancio_senza_modifiche_non_riscrive(self):
        self.run_ps1()
        old = 1_000_000_000
        os.utime(str(self.generated), ns=(old, old))
        result = self.run_ps1()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.generated.stat().st_mtime_ns, old, "file riscritto senza modifiche")

    def test_file_generato_manomesso_si_rigenera(self):
        self.run_ps1()
        good = self.generated.read_bytes()
        tampered = {
            "sandbox riaccesa": json.dumps({"sandbox": {"enabled": True}}).encode("utf-8"),
            "deny tolte": good.replace(b"Read(~/.ssh/**)", b"Read(~/.nulla)"),
            "BOM aggiunto": b"\xef\xbb\xbf" + good,
        }
        for case, content in tampered.items():
            with self.subTest(case):
                self.assertNotEqual(content, good)
                self.generated.write_bytes(content)
                result = self.run_ps1()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(self.generated.read_bytes(), good)

    def test_sorgente_non_valida_claude_non_parte(self):
        for case, source in {"JSON rotto": "{", "non un oggetto": "[]", "array di oggetti": "[{}]", "assente": None}.items():
            with self.subTest(case):
                path = self.mimir / "sandbox.settings.json"
                if source is None:
                    path.unlink()
                else:
                    write(path, source)
                result = self.run_ps1()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("impossibile preparare", result.stderr)
                self.assertFalse(self.log.exists(), "claude lanciato senza settings")
                self.assertFalse(self.generated.exists())

    def test_claude_assente(self):
        shutil.rmtree(str(self.bin))
        result = self.run_ps1()
        self.assertEqual(result.returncode, 1)
        self.assertIn("claude non trovato", result.stderr)


if __name__ == "__main__":
    unittest.main()
