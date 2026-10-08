#!/usr/bin/env python3
"""Test di install.py e install.sh.

Uso: python3 -I test_install.py
Gli installer girano su copie di Mímir in una cartella temporanea, con HOME temporanea e un claude
finto nel PATH: il repo vero, ~/.claude e la CLI di Claude Code non vengono toccati.
La cartella di Mímir è scrivibile dalla sandbox: con -I non si importano moduli piantati accanto al
test, e install.py si carica dal sorgente, senza sys.path e senza la cache .pyc.
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
PYTHON = Path(sys.executable).resolve()


def load_install():
    path = HERE / "install.py"
    module = types.ModuleType("install")
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


install = load_install()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def make_executable(path, body):
    write(path, "#!/bin/sh\n" + body + "\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def shim_files(folder, name, command):
    """I file di un comando che lancia command (già quotato) con i suoi argomenti: name.cmd su
    Windows, name eseguibile su POSIX. Su Windows PowerShell non lancia uno script #!/bin/sh."""
    if os.name == "nt":
        return {folder / f"{name}.cmd": f"@{command} %*\n"}
    return {folder / name: f'#!/bin/sh\nexec {command} "$@"\n'}


def write_shim(folder, name, command):
    for path, text in shim_files(folder, name, command).items():
        write(path, text)
        path.chmod(path.stat().st_mode | stat.S_IXUSR)


def make_fake(folder, name, code):
    """Un comando finto scritto in Python, così gira uguale su Windows e su POSIX."""
    script = folder / f"{name}_finto.py"
    write(script, "import os, subprocess, sys\n" + code + "\n")
    write_shim(folder, name, f'"{PYTHON}" -I "{script}"')


def fake_logging(log, exit_code=0, label=""):
    """Codice di un finto che aggiunge al log i suoi argomenti, come echo label "$@" >> log."""
    words = f"[{label!r}] + sys.argv[1:]" if label else "sys.argv[1:]"
    return (f"with open({str(log)!r}, 'a', encoding='utf-8') as log:\n"
            f"    log.write(' '.join({words}) + '\\n')\n"
            f"sys.exit({exit_code})")


def is_elevated():
    if os.name != "nt":
        return False
    import ctypes
    return bool(ctypes.windll.shell32.IsUserAnAdmin())


# Sui runner Windows di GitHub i processi girano come amministratore: install.ps1 lì si ferma.
# La CI dichiara l'elevazione, così un test che non gira lo fa per un motivo controllato.
ELEVATED = os.environ.get("MIMIR_TEST_ELEVATED", "0")


class Sandbox:
    """Una cartella temporanea con HOME, copie di Mímir e un PATH con claude finto."""

    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="mimir-install-test-")).resolve()
        self.home = self.root / "home"
        self.home.mkdir()
        self.bin = self.root / "bin"
        make_fake(self.bin, "claude", fake_logging(self.root / "claude.log"))
        if os.name != "nt":  # per install.sh
            for tool in ("dirname", "cat"):
                (self.bin / tool).symlink_to(shutil.which(tool))

    def mimir(self, name="mimir"):
        copy = self.root / name
        copy.mkdir()
        for file in ("install.py", "install.sh", "install.ps1", "settings.template.json"):
            shutil.copy2(str(HERE / file), str(copy / file))
        write(copy / "CLAUDE.md", "# Mímir\n")
        write(copy / "sandbox.settings.json", "{}\n")
        (copy / "plugins").mkdir(exist_ok=True)
        write(copy / "profile" / "profile.example.md", "profilo\n")
        write(copy / "inbox.example.md", "inbox\n")
        (copy / ".git" / "info").mkdir(parents=True, exist_ok=True)
        return copy

    def env(self, with_python=False):
        env = {"HOME": str(self.home), "USERPROFILE": str(self.home), "PATH": str(self.bin), "LANG": "C.UTF-8"}
        for name in ("SystemRoot", "WINDIR", "TEMP", "TMP", "ComSpec", "PATHEXT"):  # senza, su Windows non parte nulla
            if name in os.environ:
                env[name] = os.environ[name]
        if with_python:
            link = self.bin / "python3"
            if not link.exists():
                link.symlink_to(PYTHON)
        return env

    def run_py(self, mimir, *args, isolated=True):
        command = [str(PYTHON)] + (["-I"] if isolated else []) + [str(mimir / "install.py"), "--skip-system"]
        return subprocess.run(command + list(args), env=self.env(), capture_output=True, text=True,
                              encoding="utf-8", stdin=subprocess.DEVNULL)

    def run_sh(self, mimir, with_python=True):
        return subprocess.run([shutil.which("bash"), str(mimir / "install.sh"), "--skip-system"],
                              env=self.env(with_python), capture_output=True, text=True, encoding="utf-8",
                              stdin=subprocess.DEVNULL)

    def settings(self):
        return json.loads((self.home / ".claude" / "settings.json").read_text(encoding="utf-8"))

    def backups(self):
        return sorted(p.name for p in (self.home / ".claude").glob("*.bak-*"))

    def snapshot(self):
        return {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file() and "claude.log" not in p.name}


class PureFunctions(unittest.TestCase):
    def test_deep_merge_unisce_oggetti_e_sostituisce_array(self):
        merged = install.deep_merge({"a": {"x": 1, "y": [1]}, "b": 1}, {"a": {"y": [2], "z": 3}, "c": 4})
        self.assertEqual(merged, {"a": {"x": 1, "y": [2], "z": 3}, "b": 1, "c": 4})

    def test_merge_settings_conserva_chiavi_estranee_di_permissions(self):
        current = {"permissions": {"allow": ["Read"], "ask": ["B"], "disableBypassPermissionsMode": "disable"}}
        template = {"attribution": {"commit": ""}, "permissions": {"ask": ["A", "B"], "deny": ["D"]}}
        merged = install.sort_lists(install.merge_settings(current, template))
        self.assertEqual(merged["permissions"], {"allow": ["Read"], "ask": ["A", "B"],
                                                 "disableBypassPermissionsMode": "disable", "deny": ["D"]})
        self.assertEqual(merged["attribution"], {"commit": ""})
        self.assertEqual(current["permissions"]["ask"], ["B"], "l'input non deve cambiare")

    def test_protezione_toglie_le_voci_della_cartella_precedente(self):
        settings = install.merge_settings({}, {})
        install.apply_protection(settings, "/vecchia/mimir", None, "linux")
        install.apply_protection(settings, "/nuova/mimir", "/vecchia/mimir", "linux")
        text = json.dumps(settings)
        self.assertNotIn("/vecchia/", text)
        self.assertIn("Edit(//nuova/mimir/plugins/**)", settings["permissions"]["ask"])
        self.assertIn("/nuova/mimir/install.py", settings["sandbox"]["filesystem"]["denyWrite"])

    def test_protezione_su_windows_solo_ask_con_lettera_del_disco(self):
        settings = install.apply_protection(install.merge_settings({}, {}), "C:/Users/a/mimir", None, "windows")
        self.assertIn("Edit(//c/Users/a/mimir/rules/**)", settings["permissions"]["ask"])
        self.assertNotIn("sandbox", settings)

    def test_ordinamento_finale_anche_di_deny_write(self):
        settings = {"permissions": {"ask": ["b", "a", "b"], "deny": []},
                    "sandbox": {"filesystem": {"denyWrite": ["/z", "/a", "/z"]}}}
        install.sort_lists(settings)
        self.assertEqual(settings["permissions"]["ask"], ["a", "b"])
        self.assertEqual(settings["sandbox"]["filesystem"]["denyWrite"], ["/a", "/z"])

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO solo su POSIX")
    def test_lettura_dalla_cartella_rifiuta_fifo_e_symlink(self):
        folder = Path(tempfile.mkdtemp(prefix="mimir-read-test-"))
        self.addCleanup(shutil.rmtree, str(folder), ignore_errors=True)
        os.mkfifo(str(folder / "fifo"))
        write(folder / "vero", "ok\r\n")
        (folder / "link").symlink_to(folder / "vero")
        self.assertEqual(install.read_mimir_file(folder / "vero"), "ok\n")
        self.assertIsNone(install.read_mimir_file(folder / "manca"))
        for name in ("fifo", "link"):
            with self.assertRaises(install.InstallError, msg=name):
                install.read_mimir_file(folder / name)

    def test_import_scritto_una_volta_e_sostituito(self):
        first = install.linked_claude_md("riga\n@/a/CLAUDE.md\n", "/a")
        self.assertEqual(first, f"riga\n{install.MARKER}\n@/a/CLAUDE.md\n")
        self.assertEqual(install.linked_claude_md(first, "/a"), first)
        self.assertEqual(install.linked_claude_md(first, "/b"), f"riga\n{install.MARKER}\n@/b/CLAUDE.md\n")
        self.assertEqual(install.imported_dir(first), "/a")
        self.assertIsNone(install.imported_dir("@/a/CLAUDE.md\n"))

    def test_exclude_senza_duplicati(self):
        once = install.updated_exclude("# commento\n")
        self.assertEqual(once.count(install.EXCLUDE_MARKER), 1)
        self.assertEqual(install.updated_exclude(once), once)
        partial = install.updated_exclude("/.bashrc\n")
        self.assertEqual(partial.count("/.bashrc\n"), 1)

    def test_detect_system(self):
        cases = [("Darwin", "", "macos"), ("Windows", "", "windows"), ("Linux", "6.11.0-29-generic", "linux"),
                 ("Linux", "5.15.153.1-microsoft-standard-WSL2", "wsl2"),
                 ("Linux", "4.19.104-microsoft-standard", "wsl2"), ("Linux", "4.4.0-19041-Microsoft", "wsl1")]
        for system, osrelease, expected in cases:
            self.assertEqual(install.detect_system(system, osrelease), expected, osrelease)

    def test_launcher_per_sistema(self):
        mimir = Path("/opt/mimir")
        self.assertEqual(install.launcher_command("linux", mimir), "/opt/mimir/bin/claude-mimir")
        windows = install.launcher_command("windows", mimir)
        self.assertIn(f'-File "{mimir / "bin" / "claude-mimir.ps1"}"', windows)
        self.assertIn("senza sandbox", windows)

    def test_comando_del_gestore_dei_pacchetti(self):
        def which(*present):
            return lambda name: f"/usr/bin/{name}" if name in present else None
        with mock.patch.object(install, "as_root", side_effect=lambda c: ["sudo"] + c):
            self.assertEqual(install.install_command(["bwrap", "socat"], which("dnf", "zypper")),
                             ["sudo", "dnf", "install", "-y", "bubblewrap", "socat"])
            self.assertEqual(install.install_command(["socat"], which("pacman")),
                             ["sudo", "pacman", "-S", "--needed", "--noconfirm", "socat"])
            self.assertIsNone(install.install_command(["socat"], which()))

    def test_conferma_con_eof_vale_no(self):
        with mock.patch("builtins.input", side_effect=EOFError), mock.patch("builtins.print"):
            self.assertFalse(install.confirm("procedo?", assume_yes=False))
        self.assertTrue(install.confirm("procedo?", assume_yes=True))

    def test_installazione_fallita_si_segnala(self):
        calls = []

        def runner(command, **kwargs):
            calls.append(command)
            return False
        with mock.patch.object(install, "needs_apparmor_profile", return_value=False), \
                mock.patch("builtins.print"):
            problems = install.install_sandbox_requirements(
                "linux", True, which=lambda n: "/usr/bin/apt-get" if n == "apt-get" else None, runner=runner)
        self.assertEqual(problems, ["bubblewrap, socat"])
        self.assertEqual(len(calls), 1)


@unittest.skipIf(os.name == "nt", "asserzioni nel formato POSIX: su Windows install.py lo provano InstallPs1 e la CI")
class Installer(unittest.TestCase):
    def setUp(self):
        self.box = Sandbox()
        self.addCleanup(shutil.rmtree, str(self.box.root), ignore_errors=True)

    def test_installazione_e_rilancio_senza_modifiche(self):
        mimir = self.box.mimir()
        result = self.box.run_py(mimir)
        self.assertEqual(result.returncode, 0, result.stderr)
        claude_md = (self.box.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual(claude_md, f"{install.MARKER}\n@{mimir.as_posix()}/CLAUDE.md\n")
        settings = self.box.settings()
        for name in ("install.py", "install.ps1", "test_install.py", "test_claude_mimir.py", "inbox.example.md"):
            self.assertIn(f"Edit(/{mimir}/{name})", settings["permissions"]["ask"])
            self.assertIn(f"{mimir}/{name}", settings["sandbox"]["filesystem"]["denyWrite"])
        self.assertEqual(settings["permissions"]["ask"], sorted(settings["permissions"]["ask"]))
        self.assertIn("/.bashrc", (mimir / ".git" / "info" / "exclude").read_text(encoding="utf-8"))
        self.assertTrue((mimir / "inbox.md").exists())
        self.assertIn(f"plugin marketplace add {mimir}", (self.box.root / "claude.log").read_text())

        before = self.box.snapshot()
        again = self.box.run_py(mimir)
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(self.box.snapshot(), before, "il secondo lancio non deve cambiare file né fare backup")

    def test_json_non_valido_nessuna_modifica(self):
        mimir = self.box.mimir()
        write(self.box.home / ".claude" / "CLAUDE.md", f"{install.MARKER}\n@/vecchia/mimir/CLAUDE.md\n")
        write(self.box.home / ".claude" / "settings.json", '{"permissions": ')
        before = self.box.snapshot()
        result = self.box.run_py(mimir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("nessuna modifica", result.stderr)
        self.assertEqual(self.box.snapshot(), before)

    def test_tipo_sbagliato_nessuna_modifica(self):
        mimir = self.box.mimir()
        write(self.box.home / ".claude" / "settings.json", '{"permissions": {"ask": "Bash"}}')
        before = self.box.snapshot()
        self.assertEqual(self.box.run_py(mimir).returncode, 1)
        self.assertEqual(self.box.snapshot(), before)

    def test_spostamento_toglie_le_voci_vecchie(self):
        old, new = self.box.mimir("vecchia"), self.box.mimir("nuova")
        self.assertEqual(self.box.run_py(old).returncode, 0)
        result = self.box.run_py(new)
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.box.home / ".claude" / "settings.json").read_text(encoding="utf-8")
        self.assertNotIn(str(old), text)
        self.assertIn(f"{new}/plugins", text)
        claude_md = (self.box.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual(claude_md, f"{install.MARKER}\n@{new.as_posix()}/CLAUDE.md\n")

    def test_import_della_stessa_cartella_in_altra_forma_conserva_le_voci(self):
        # regressione: oggi le voci della cartella attuale, se tolte, si riaggiungono subito, quindi
        # questo test non distingue se old_dir sia normalizzato; protegge solo il risultato
        mimir = self.box.mimir()
        link = self.box.root / "collegamento"
        link.symlink_to(mimir)
        self.assertEqual(self.box.run_py(mimir).returncode, 0)
        for other in (f"{link}", f"{mimir}/."):
            write(self.box.home / ".claude" / "CLAUDE.md", f"{install.MARKER}\n@{other}/CLAUDE.md\n")
            self.assertEqual(self.box.run_py(mimir).returncode, 0)
            settings = self.box.settings()
            self.assertIn(f"Edit(/{mimir}/plugins/**)", settings["permissions"]["ask"], other)
            self.assertIn(f"{mimir}/plugins", settings["sandbox"]["filesystem"]["denyWrite"], other)

    def test_destinazione_symlink_pendente_non_scrive_fuori(self):
        mimir = self.box.mimir()
        target = self.box.root / "fuori" / "bersaglio"
        target.parent.mkdir()
        (mimir / "inbox.md").symlink_to(target)
        result = self.box.run_py(mimir)
        self.assertFalse(target.exists(), "l'installer ha seguito il symlink di inbox.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("inbox.md", result.stdout + result.stderr)

    def test_sorgente_symlink_verso_un_segreto_rifiutata(self):
        mimir = self.box.mimir()
        secret = self.box.root / "segreto"
        write(secret, "SEGRETO\n")
        (mimir / "inbox.example.md").unlink()
        (mimir / "inbox.example.md").symlink_to(secret)
        before = self.box.snapshot()
        result = self.box.run_py(mimir)
        self.assertFalse((mimir / "inbox.md").exists(), "il segreto è stato copiato in inbox.md")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.box.snapshot(), before)

    def test_template_symlink_verso_credenziali_rifiutato(self):
        mimir = self.box.mimir()
        secret = self.box.root / "credentials.json"
        write(secret, '{"claudeAiOauth": {"accessToken": "SEGRETO"}}')
        (mimir / "settings.template.json").unlink()
        (mimir / "settings.template.json").symlink_to(secret)
        before = self.box.snapshot()
        result = self.box.run_py(mimir)
        self.assertFalse((self.box.home / ".claude" / "settings.json").exists(), "credenziali unite nei settings")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.box.snapshot(), before)

    def test_exclude_symlink_rifiutato(self):
        mimir = self.box.mimir()
        other = self.box.root / "altro"
        write(other, "SEGRETO\n")
        (mimir / ".git" / "info" / "exclude").symlink_to(other)
        before = self.box.snapshot()
        result = self.box.run_py(mimir)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.box.snapshot(), before)

    def test_claude_md_symlink_scritto_attraverso_il_link(self):
        mimir = self.box.mimir()
        dotfile = self.box.root / "dotfiles" / "CLAUDE.md"
        write(dotfile, "mio\n")
        (self.box.home / ".claude").mkdir()
        (self.box.home / ".claude" / "CLAUDE.md").symlink_to(dotfile)
        result = self.box.run_py(mimir)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.box.home / ".claude" / "CLAUDE.md").is_symlink(), "il symlink è stato sostituito")
        self.assertIn(install.MARKER, dotfile.read_text(encoding="utf-8"))

    def test_install_sh_lancia_python_isolato(self):
        mimir = self.box.mimir()
        spy = self.box.root / "spia"
        write(mimir / "json.py", f"open({str(spy)!r}, 'w').close()\nfrom importlib import import_module\n")
        # controllo del controllo: senza -I il modulo piantato viene importato
        self.box.run_py(mimir, isolated=False)
        self.assertTrue(spy.exists(), "senza -I json.py doveva essere importato: il test non prova nulla")
        spy.unlink()
        result = self.box.run_sh(mimir)
        self.assertFalse(spy.exists(), "install.sh ha importato json.py dalla cartella di Mímir")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_import_precedente_non_assoluto_ignorato(self):
        mimir = self.box.mimir()
        write(self.box.home / ".claude" / "CLAUDE.md", f"{install.MARKER}\n@relativo/CLAUDE.md\n")
        result = self.box.run_py(mimir)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("non valido, ignorato", result.stdout)

    @unittest.skipUnless(sys.platform.startswith("linux"), "requisiti della sandbox solo su Linux")
    def test_requisiti_mancanti_si_prosegue_e_si_esce_con_1(self):
        # nel PATH del test non ci sono bwrap, socat né un gestore dei pacchetti; stdin chiuso = no
        mimir = self.box.mimir()
        result = subprocess.run([str(PYTHON), "-I", str(mimir / "install.py")], env=self.box.env(),
                                capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Requisiti della sandbox mancanti", result.stderr)
        self.assertTrue((self.box.home / ".claude" / "settings.json").exists(), "il resto doveva proseguire")

    def test_install_sh_python_troppo_vecchio(self):
        mimir = self.box.mimir()
        make_executable(self.box.bin / "python3", "exit 1")  # come un Python < 3.8 al controllo di versione
        result = self.box.run_sh(mimir, with_python=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Python 3.8", result.stderr)

    def test_install_sh_senza_python(self):
        mimir = self.box.mimir()
        result = self.box.run_sh(mimir, with_python=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Python 3.8", result.stderr)
        self.assertFalse((self.box.home / ".claude").exists())


PWSH = os.environ.get("MIMIR_TEST_PWSH") or shutil.which("pwsh") or shutil.which("powershell")


class ElevazioneDichiarata(unittest.TestCase):
    def test_coincide_con_quella_reale(self):
        self.assertIn(ELEVATED, ("0", "1"), "MIMIR_TEST_ELEVATED vale 0 o 1")
        self.assertEqual(ELEVATED == "1", is_elevated(), "MIMIR_TEST_ELEVATED non corrisponde all'elevazione reale")


class Ps1Case(unittest.TestCase):
    """install.ps1 con python, git e winget finti nel PATH. Su Linux gira con pwsh 7: la
    compatibilità con Windows PowerShell 5.1 la controlla PSScriptAnalyzer, il resto la CI."""

    def setUp(self):
        self.box = Sandbox()
        self.addCleanup(shutil.rmtree, str(self.box.root), ignore_errors=True)
        self.mimir = self.box.mimir()
        self.log = self.box.root / "comandi.log"
        make_fake(self.box.bin, "git", "sys.exit(0)")

    def link_python(self):
        write_shim(self.box.bin, "python", f'"{PYTHON}"')

    def fake_winget_installing_python(self):
        """Un winget finto che registra gli argomenti e "installa" python nel PATH del test."""
        files = {str(path): text for path, text in shim_files(self.box.bin, "python", f'"{PYTHON}"').items()}
        make_fake(self.box.bin, "winget",
                  f"for path, text in {files!r}.items():\n"
                  "    with open(path, 'w', encoding='utf-8', newline='\\n') as file:\n"
                  "        file.write(text)\n"
                  "    os.chmod(path, 0o755)\n" + fake_logging(self.log))

    def fake_linux_requirements(self):
        """Senza -SkipSystem, su Linux install.py controlla bwrap e socat (finti qui) e può usare sudo
        per il profilo AppArmor: nel PATH del test c'è solo un sudo finto che fallisce. I test si
        lanciano anche fuori dalla sandbox: il vero sudo non deve mai essere raggiungibile."""
        for tool in ("bwrap", "socat"):
            make_fake(self.box.bin, tool, "sys.exit(0)")
        make_fake(self.box.bin, "sudo", fake_logging(self.log, exit_code=1, label="sudo"))
        self.assertEqual(Path(shutil.which("sudo", path=self.box.env()["PATH"])).parent, self.box.bin,
                         "nel PATH del test deve esserci solo il sudo finto")

    def run_ps1(self, *args, stdin_text=None, env=None):
        command = [PWSH, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                   "-File", str(self.mimir / "install.ps1")] + list(args)
        stdin = {"input": stdin_text} if stdin_text is not None else {"stdin": subprocess.DEVNULL}
        # su Windows l'output rediretto è nella code page OEM: le asserzioni usano testo ASCII
        return subprocess.run(command, env=env or self.box.env(), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", **stdin)


@unittest.skipUnless(PWSH and ELEVATED == "1", "solo come amministratore (MIMIR_TEST_ELEVATED=1)")
class InstallPs1Amministratore(Ps1Case):
    def test_amministratore_si_ferma(self):
        self.link_python()
        # install.ps1 controlla l'elevazione solo con OS=Windows_NT. Gli altri test non lo passano:
        # con OS, Update-SessionPath rileggerebbe il PATH vero dal registro
        result = self.run_ps1("-Yes", "-SkipSystem", env=dict(self.box.env(), OS=os.environ["OS"]))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("in esecuzione come amministratore", result.stdout)
        self.assertFalse((self.box.home / ".claude").exists(), "install.py è partito da amministratore")


@unittest.skipUnless(PWSH, "PowerShell non trovato (MIMIR_TEST_PWSH, pwsh o powershell)")
@unittest.skipIf(ELEVATED == "1", "da amministratore install.ps1 si ferma: lo prova InstallPs1Amministratore")
class InstallPs1(Ps1Case):
    def test_file_in_utf8_con_bom(self):
        # Windows PowerShell 5.1 legge un .ps1 senza BOM come ANSI e rompe gli accenti
        self.assertEqual((HERE / "install.ps1").read_bytes()[:3], b"\xef\xbb\xbf")

    def test_candidato_py_con_prefisso(self):
        make_fake(self.box.bin, "py", "if sys.argv[1:2] != ['-3']:\n    sys.exit(2)\n"
                                      f"sys.exit(subprocess.run([{str(PYTHON)!r}] + sys.argv[2:]).returncode)")
        result = self.run_ps1("-Yes", "-SkipSystem")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.box.home / ".claude" / "settings.json").exists())

    def test_risposta_si_da_input(self):
        self.fake_linux_requirements()
        self.fake_winget_installing_python()
        result = self.run_ps1(stdin_text="s\n")
        self.assertIn("install --id Python.Python.3.13 -e --source winget", self.log.read_text(),
                      result.stdout + result.stderr)
        self.assertNotIn("--accept-package-agreements", self.log.read_text(), "accordi accettati senza -Yes")
        self.assertTrue((self.box.home / ".claude" / "settings.json").exists())

    def test_output_di_winget_visibile_e_fallimento_riconosciuto(self):
        make_fake(self.box.bin, "winget", "print('RIGA-DI-WINGET')\nsys.exit(1)")
        result = self.run_ps1("-Yes")
        self.assertIn("RIGA-DI-WINGET", result.stdout, "l'output di winget è stato catturato")
        self.assertIn("installazione di Python 3 non riuscita", result.stdout)
        self.assertEqual(result.returncode, 1)

    def test_lancia_install_py_isolato_con_gli_stessi_flag(self):
        self.link_python()
        spy = self.box.root / "spia"
        write(self.mimir / "json.py", f"open({str(spy)!r}, 'w').close()\nraise ImportError\n")
        result = self.run_ps1("-Yes", "-SkipSystem")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(spy.exists(), "install.ps1 ha importato json.py dalla cartella di Mímir")
        self.assertTrue((self.box.home / ".claude" / "settings.json").exists())

    def test_stub_dello_store_scartato(self):
        make_fake(self.box.bin, "python", "sys.exit(9009)")  # su POSIX il codice di uscita vale 49
        result = self.run_ps1("-Yes", "-SkipSystem")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Python 3.8+ non trovato", result.stdout)
        self.assertFalse((self.box.home / ".claude").exists())

    def test_python_da_winget_poi_trovato(self):
        self.fake_linux_requirements()
        self.fake_winget_installing_python()
        result = self.run_ps1("-Yes")
        self.assertIn("install --id Python.Python.3.13 -e --source winget", self.log.read_text())
        self.assertTrue((self.box.home / ".claude" / "settings.json").exists(), result.stdout + result.stderr)

    def test_conferma_con_input_chiuso_vale_no(self):
        make_fake(self.box.bin, "winget", fake_logging(self.log))
        result = self.run_ps1()
        self.assertFalse(self.log.exists(), "winget lanciato senza conferma")
        self.assertEqual(result.returncode, 1)

    def test_senza_git_si_prosegue_e_si_esce_con_1(self):
        self.link_python()
        for path in self.box.bin.glob("git*"):
            path.unlink()
        result = self.run_ps1("-Yes", "-SkipSystem")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Git for Windows", result.stdout)
        self.assertTrue((self.box.home / ".claude" / "settings.json").exists(), "install.py doveva girare")

    def test_wsl_mai_con_yes(self):
        # senza -SkipSystem l'uscita può valere 1 per i requisiti di Linux (AppArmor con il sudo
        # finto): conta che wsl non parta e che lo script non si rompa
        self.link_python()
        self.fake_linux_requirements()
        make_fake(self.box.bin, "wsl.exe", fake_logging(self.log, label="wsl"))
        result = self.run_ps1("-Yes")
        self.assertNotIn("wsl", self.log.read_text() if self.log.exists() else "", "wsl lanciato con -Yes")
        self.assertNotIn("install.ps1:", result.stderr, "errore di PowerShell")
        self.assertNotIn("WSL2", result.stdout)
        self.assertTrue((self.box.home / ".claude" / "settings.json").exists())


if __name__ == "__main__":
    unittest.main()
