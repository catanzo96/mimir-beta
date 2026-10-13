#!/usr/bin/env python3
"""Test di bin/claude-mimir.ps1, il launcher per Windows nativo, e del passaggio di consegne in bin/claude-mimir.

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
# Percorso assoluto: su POSIX subprocess cerca il programma nel PATH di env=, che qui è ridotto
PWSH = (shutil.which(os.environ["MIMIR_TEST_PWSH"]) or os.environ["MIMIR_TEST_PWSH"]
        if os.environ.get("MIMIR_TEST_PWSH") else shutil.which("pwsh") or shutil.which("powershell"))
BASH = os.environ.get("MIMIR_TEST_BASH") or shutil.which("bash")
# Verso un .cmd (il claude finto su Windows, e lo shim di npm) gli argomenti passano in modo Legacy:
# nella 5.1 sempre, in pwsh 7.3+ per .bat e .cmd ($PSNativeCommandArgumentPassing = 'Windows')
expected_failure_on_windows = unittest.expectedFailure if os.name == "nt" else (lambda test: test)
GENERATED = Path("sandbox", "windows.settings.json")
WARNING = "Windows nativo: comandi senza sandbox"

FAKE_CLAUDE = """import json, os, sys
with open(os.environ["FAKE_CLAUDE_LOG"], "w", encoding="utf-8") as log:
    json.dump({"args": sys.argv[1:],
               "env": {name: os.environ.get(name) for name in
                       ("CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD", "MIMIR_MAVEN_SETTINGS",
                        "MIMIR_HANDOFF_DIR")}}, log)
sys.exit(int(os.environ.get("FAKE_CLAUDE_EXIT", "0")))
"""


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as file:  # write_text(newline=) è dalla 3.10
        file.write(text)


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
        self.local_app_data = self.root / "localappdata"
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
        # LOCALAPPDATA nella box: il passaggio di consegne si prova senza toccare le cartelle vere
        env = {"PATH": str(self.bin), "HOME": str(self.root), "USERPROFILE": str(self.root),
               "LOCALAPPDATA": str(self.local_app_data), "LANG": "C.UTF-8", "FAKE_CLAUDE_LOG": str(self.log)}
        # senza le prime, powershell.exe non parte; senza la cache dei moduli del runner (ipotesi dai run
        # 37932870634 e 37939365792) ogni avvio di Windows PowerShell 5.1 rianalizza i moduli: ~20 s
        for name in ("SystemRoot", "WINDIR", "TEMP", "TMP", "ComSpec", "PATHEXT", "PSModuleAnalysisCachePath"):
            if name in os.environ:
                env[name] = os.environ[name]
        env.update(extra)
        # None toglie la variabile
        return {name: value for name, value in env.items() if value is not None}

    def run_ps1(self, *args, **env):
        command = [PWSH, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                   "-File", str(self.mimir / "bin" / "claude-mimir.ps1")] + list(args)
        # su Windows l'output rediretto è nella code page OEM: le asserzioni usano testo ASCII
        return subprocess.run(command, env=self.env(**env), capture_output=True, text=True, encoding="utf-8",
                              errors="replace", stdin=subprocess.DEVNULL)

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
        env = self.received()["env"]
        handoff = env.pop("MIMIR_HANDOFF_DIR")
        self.assertEqual(env, {"CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD": "1", "MIMIR_MAVEN_SETTINGS": None})
        # fuori da Mímir: nella cartella dati locale dell'utente
        self.assertEqual(Path(handoff), self.local_app_data / "mimir" / "handoff")
        self.assertNotIn(str(self.mimir), handoff)

    def test_senza_localappdata_passaggio_spento_e_claude_parte(self):
        result = self.run_ps1(LOCALAPPDATA=None)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIsNone(self.received()["env"]["MIMIR_HANDOFF_DIR"])
        self.assertIn("LOCALAPPDATA", result.stderr)

    def test_con_print_passaggio_spento_anche_se_ereditato(self):
        # un -p lanciato da una sessione del launcher eredita la variabile: SessionStart archivierebbe il passaggio
        for flag in ("-p", "--print"):
            with self.subTest(flag=flag):
                result = self.run_ps1(flag, "a b", MIMIR_HANDOFF_DIR=str(self.root / "ereditata"))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIsNone(self.received()["env"]["MIMIR_HANDOFF_DIR"])
                self.assertEqual(self.received()["args"], self.mimir_args() + [flag, "a b"])

    def test_con_print_e_senza_localappdata_nessun_avviso(self):
        result = self.run_ps1("-p", "a b", LOCALAPPDATA=None)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("LOCALAPPDATA", result.stderr)

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

    def test_cultura_italiana_conserva_il_punto_decimale(self):
        script = self.mimir / "bin" / "claude-mimir.ps1"
        command = ("[Threading.Thread]::CurrentThread.CurrentCulture = 'it-IT'; "
                   "Write-Output \"cultura=$([CultureInfo]::CurrentCulture.Name) $((0.5).ToString())\"; "
                   f"& '{script}'; exit $LASTEXITCODE")
        result = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                                 "-Command", command], env=self.env(), capture_output=True, text=True,
                                encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("cultura=it-IT 0,5", result.stdout, "la cultura it-IT non è attiva: il test non prova nulla")
        # la 5.1 scrive due spazi dopo i due punti, pwsh 7 uno
        self.assertRegex(self.generated.read_text(encoding="utf-8"), r'"skillListingBudgetFraction":\s+0\.03\b')
        self.assertEqual(json.loads(self.generated.read_text(encoding="utf-8")), self.expected_settings())

    def test_doppio_trattino_passato_a_claude(self):
        result = self.run_ps1("-p", "--", "--non-un-flag")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.received()["args"], self.mimir_args() + ["-p", "--", "--non-un-flag"])

    @expected_failure_on_windows
    def test_argomento_vuoto_e_con_doppi_apici(self):
        # limite documentato nel launcher: verso claude.cmd si perdono
        result = self.run_ps1("-p", "", 'di "ciao"')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.received()["args"], self.mimir_args() + ["-p", "", 'di "ciao"'])

    def test_shim_ps1_di_npm(self):
        # npm installa claude.ps1 accanto a claude.cmd; senza claude.cmd vale lo shim PowerShell
        for path in self.bin.iterdir():
            path.unlink()
        write(self.bin / "claude.ps1",
              f"& '{PYTHON}' -I '{self.root / 'fake_claude.py'}' $args\nexit $LASTEXITCODE\n")
        result = self.run_ps1("-p", "a b", FAKE_CLAUDE_EXIT="4")
        self.assertEqual(result.returncode, 4, result.stdout + result.stderr)
        self.assertEqual(self.received()["args"], self.mimir_args() + ["-p", "a b"])

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


# Solo POSIX: su Windows il bash di Git non lancerebbe il claude finto, che lì è un .cmd
@unittest.skipUnless(BASH and os.name == "posix", "bash non trovato (MIMIR_TEST_BASH o bash) o non POSIX")
class ClaudeMimirBash(unittest.TestCase):
    """bin/claude-mimir: con -p/--print il passaggio di consegne (MIMIR_HANDOFF_DIR) resta spento."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="mimir-launcher-test-")).resolve()
        self.addCleanup(shutil.rmtree, str(self.root), ignore_errors=True)
        self.mimir = self.root / "mimir"
        (self.mimir / "bin").mkdir(parents=True)
        shutil.copy2(str(HERE / "bin" / "claude-mimir"), str(self.mimir / "bin" / "claude-mimir"))
        self.bin = self.root / "fake-bin"
        self.log = self.root / "claude.json"
        self.state = self.root / "state"
        script = self.root / "fake_claude.py"
        write(script, FAKE_CLAUDE)
        write(self.bin / "claude", f'#!/bin/sh\nexec "{PYTHON}" -I "{script}" "$@"\n')
        (self.bin / "claude").chmod(0o755)

    def run_bash(self, *args, **env):
        # XDG_STATE_HOME nella box: il percorso atteso del passaggio non dipende dalla macchina
        full_env = {"PATH": f"{self.bin}{os.pathsep}{os.defpath}", "HOME": str(self.root),
                    "XDG_STATE_HOME": str(self.state), "FAKE_CLAUDE_LOG": str(self.log)}
        full_env.update(env)
        return subprocess.run([BASH, str(self.mimir / "bin" / "claude-mimir")] + list(args), env=full_env,
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)

    def received(self):
        return json.loads(self.log.read_text(encoding="utf-8"))

    def mimir_args(self):
        return ["--settings", str(self.mimir / "sandbox.settings.json"), "--add-dir", str(self.mimir),
                "--plugin-dir", str(self.mimir / "plugins")]

    def test_senza_print_passaggio_attivo_e_argomenti_invariati(self):
        result = self.run_bash("--add-dir", "altro", "domanda con spazi", "")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.received()["env"]["MIMIR_HANDOFF_DIR"], str(self.state / "mimir" / "handoff"))
        self.assertEqual(self.received()["args"], self.mimir_args() + ["--add-dir", "altro", "domanda con spazi", ""])

    def test_con_print_passaggio_spento_e_argomenti_invariati(self):
        cases = ((["-p", "a b"], self.mimir_args() + ["-p", "a b"]),
                 (["--print", "a b"], self.mimir_args() + ["--print", "a b"]),
                 (["agents", "-p", "x"], ["agents"] + self.mimir_args() + ["-p", "x"]))
        for args, expected in cases:
            with self.subTest(args=args):
                result = self.run_bash(*args)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIsNone(self.received()["env"]["MIMIR_HANDOFF_DIR"])
                self.assertEqual(self.received()["args"], expected)

    def test_con_print_tolta_anche_la_variabile_ereditata(self):
        # un -p lanciato da una sessione del launcher eredita la variabile: SessionStart archivierebbe il passaggio
        result = self.run_bash("-p", "a b", MIMIR_HANDOFF_DIR=str(self.root / "ereditata"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIsNone(self.received()["env"]["MIMIR_HANDOFF_DIR"])


if __name__ == "__main__":
    unittest.main()
