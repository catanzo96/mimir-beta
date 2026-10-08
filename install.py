#!/usr/bin/env python3
"""Collega Mímir alla configurazione di Claude Code su questa macchina.

Uso: install.sh [--yes] [--skip-system]   (install.sh lancia questo script con python -I)
  --yes          risponde sì alle conferme (per la CI)
  --skip-system  salta i passi che usano sudo (requisiti della sandbox su Linux e WSL2)

Si può rilanciare senza danni. Prima legge e valida tutti i file, poi calcola il risultato in memoria,
poi scrive solo i file che cambiano, con scrittura atomica e, per settings.json e CLAUDE.md, un backup:
se un file non è valido si ferma prima di aver toccato qualsiasi cosa.

Solo libreria standard, Python 3.8+. Va lanciato con -I: la cartella di Mímir è scrivibile dalla
sandbox e l'installer gira fuori, quindi un modulo piantato accanto a questo file (json.py) non deve
essere importato.
"""
import argparse
import copy
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

MARKER = "<!-- mimir: la riga sotto la gestisce install.sh -->"
EXCLUDE_MARKER = "# mimir: file che la sandbox crea vuoti nel repo (gestiti da install.py)"
# Voci che la sandbox crea vuote (mount di /dev/null) nella cartella di lavoro: viste con git status il 07/10
EXCLUDE_ENTRIES = [
    "/.bash_profile", "/.bashrc", "/.gitconfig", "/.gitmodules", "/.mcp.json", "/.profile",
    "/.ripgreprc", "/.vscode", "/.zprofile", "/.zshrc",
    "/.claude/commands", "/.claude/hooks", "/.claude/launch.json", "/.claude/loop.md",
    "/.claude/output-styles", "/.claude/routines", "/.claude/scheduled_tasks.json",
    "/.claude/skills", "/.claude/workflows",
]
PERSONAL_FILES = [("profile/profile.example.md", "profile/profile.md"), ("inbox.example.md", "inbox.md")]
# Girano fuori dalla sandbox o entrano in ogni sessione: la shell nella sandbox non li deve scrivere,
# Edit e Write chiedono conferma. Solo file versionati: un denyWrite su un percorso che non c'è fa
# creare alla sandbox un file vuoto nel repo.
PROTECTED_DIRS = ["plugins", "bin", ".claude-plugin", ".claude", "sandbox", "rules", "profile", ".github"]
PROTECTED_FILES = ["sandbox.settings.json", "settings.template.json", "inbox.example.md", "install.sh", "install.py",
                   "install.ps1", "test_install.py", "test_claude_mimir.py", "CLAUDE.md"]

# Testo dalla doc di Claude Code, pagina sandboxing (08/10/2026)
APPARMOR_PROFILE_PATH = "/etc/apparmor.d/bwrap"
APPARMOR_PROFILE = """abi <abi/4.0>,
include <tunables/global>

profile bwrap /usr/bin/bwrap flags=(unconfined) {
  userns,
  include if exists <local/bwrap>
}
"""
APPARMOR_SYSCTL = "/proc/sys/kernel/apparmor_restrict_unprivileged_userns"
SANDBOX_PACKAGES = {"bwrap": "bubblewrap", "socat": "socat"}
PACKAGE_MANAGERS = [
    ("apt-get", ["apt-get", "install", "-y"]),
    ("dnf", ["dnf", "install", "-y"]),
    ("pacman", ["pacman", "-S", "--needed", "--noconfirm"]),
    ("zypper", ["zypper", "install", "-y"]),
]


class InstallError(Exception):
    """Un file di partenza non è valido: l'installazione si ferma senza modifiche."""


# --- percorsi e sistema ---------------------------------------------------------------------------

def normalize_dir(path):
    return Path(path).resolve().as_posix()


def detect_system(system=None, osrelease=None):
    system = system if system is not None else platform.system()
    if system == "Darwin":
        return "macos"
    if system == "Windows":
        return "windows"
    if osrelease is None:
        try:
            osrelease = Path("/proc/sys/kernel/osrelease").read_text(encoding="utf-8")
        except OSError:
            osrelease = ""
    osrelease = osrelease.lower()
    # WSL2: ...-microsoft-standard[-WSL2]; WSL1: ...-Microsoft
    if "microsoft-standard" in osrelease or "wsl2" in osrelease:
        return "wsl2"
    if "microsoft" in osrelease:
        return "wsl1"
    return "linux"


def rule_path(posix_path):
    """Percorso per le regole di permesso: su Windows C:/x diventa /c/x (doc permissions)."""
    drive = re.match(r"^([A-Za-z]):/", posix_path)
    if drive:
        return "/" + drive.group(1).lower() + posix_path[2:]
    return posix_path


def protected_entries(mimir_dir):
    deny_write, ask = [], []
    for name in PROTECTED_DIRS:
        path = f"{mimir_dir}/{name}"
        deny_write.append(path)
        ask.append(f"Edit(/{rule_path(path)}/**)")
    for name in PROTECTED_FILES:
        path = f"{mimir_dir}/{name}"
        deny_write.append(path)
        ask.append(f"Edit(/{rule_path(path)})")
    return deny_write, ask


# --- lettura e validazione ------------------------------------------------------------------------

def read_text(path):
    """Legge un file di ~/.claude, che la sandbox non scrive: i symlink si seguono (dotfiles)."""
    try:
        return path.read_text(encoding="utf-8") if path.exists() else None
    except (OSError, UnicodeDecodeError) as exc:
        raise InstallError(f"{path} non leggibile in UTF-8 ({exc})") from exc


def read_mimir_file(path):
    """Legge un file della cartella di Mímir, o None se manca.

    La cartella è scrivibile dalla sandbox e l'installer gira fuori: un symlink verso un segreto ne
    copierebbe il contenuto in un file che la sandbox legge. O_NOFOLLOW e fstat sullo stesso
    descrittore non lasciano una finestra tra controllo e lettura; O_NONBLOCK evita di bloccarsi
    su una FIFO.
    """
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0)
    try:
        fd = os.open(str(path), flags)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise InstallError(f"{path} non leggibile o è un symlink ({exc})") from exc
    with os.fdopen(fd, "rb") as fh:
        if not stat.S_ISREG(os.fstat(fh.fileno()).st_mode):
            raise InstallError(f"{path} non è un file regolare")
        data = fh.read()
    try:
        return data.decode("utf-8").replace("\r\n", "\n")
    except UnicodeDecodeError as exc:
        raise InstallError(f"{path} non è in UTF-8 ({exc})") from exc


def parse_settings(text, path):
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise InstallError(f"{path} non è JSON valido ({exc})") from exc
    if not isinstance(data, dict):
        raise InstallError(f"{path} non contiene un oggetto JSON")
    for keys in (("permissions",), ("sandbox",), ("sandbox", "filesystem")):
        value = data
        for key in keys:
            value = value.get(key) if isinstance(value, dict) else None
        if value is not None and not isinstance(value, dict):
            raise InstallError(f"{path}: {'.'.join(keys)} deve essere un oggetto")
    for keys in (("permissions", "ask"), ("permissions", "deny"), ("sandbox", "filesystem", "denyWrite")):
        value = data
        for key in keys:
            value = value.get(key) if isinstance(value, dict) else None
        if value is not None and not (isinstance(value, list) and all(isinstance(v, str) for v in value)):
            raise InstallError(f"{path}: {'.'.join(keys)} deve essere una lista di stringhe")
    return data


def split_lines(text):
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def imported_dir(claude_md_text):
    """La cartella di Mímir importata sotto il marcatore, o None."""
    lines = split_lines(claude_md_text or "")
    for index, line in enumerate(lines[:-1]):
        following = lines[index + 1]
        if line == MARKER and following.startswith("@") and following.endswith("/CLAUDE.md"):
            return following[1:-len("/CLAUDE.md")]
    return None


# --- calcolo in memoria ---------------------------------------------------------------------------

def deep_merge(base, override):
    """Come * di jq: gli oggetti si uniscono in profondità, il resto lo sostituisce override."""
    result = dict(base)
    for key, value in override.items():
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def merge_settings(current, template):
    """Semantica dell'install.sh con jq; permissions.ask e .deny unite (l'ordinamento è alla fine)."""
    merged = deep_merge(current, {k: v for k, v in template.items() if k != "permissions"})
    permissions = dict(merged.get("permissions") or {})
    tpl_permissions = template.get("permissions") or {}
    for key in ("ask", "deny"):
        permissions[key] = (permissions.get(key) or []) + (tpl_permissions.get(key) or [])
    merged["permissions"] = permissions
    return merged


def apply_protection(settings, mimir_dir, old_dir, system):
    deny_write, ask = protected_entries(mimir_dir)
    # le voci della cartella attuale, tolte qui, si riaggiungono subito sotto
    stale_deny_write, stale_ask = protected_entries(old_dir) if old_dir else ([], [])
    permissions = settings["permissions"]
    permissions["ask"] = [e for e in permissions["ask"] if e not in stale_ask] + ask
    filesystem = (settings.get("sandbox") or {}).get("filesystem") or {}
    if system == "windows" and "denyWrite" not in filesystem:
        return settings
    current = [e for e in (filesystem.get("denyWrite") or []) if e not in stale_deny_write]
    sandbox = dict(settings.get("sandbox") or {})
    sandbox["filesystem"] = dict(filesystem, denyWrite=current + ([] if system == "windows" else deny_write))
    settings["sandbox"] = sandbox
    return settings


def sort_lists(settings):
    permissions = settings["permissions"]
    for key in ("ask", "deny"):
        permissions[key] = sorted(set(permissions[key]))
    filesystem = (settings.get("sandbox") or {}).get("filesystem")
    if filesystem and "denyWrite" in filesystem:
        filesystem["denyWrite"] = sorted(set(filesystem["denyWrite"]))
    return settings


def linked_claude_md(text, mimir_dir):
    """Il nuovo testo di ~/.claude/CLAUDE.md, come l'awk dell'install.sh con jq."""
    import_line = f"@{mimir_dir}/CLAUDE.md"
    lines = split_lines(text or "")
    if any(line == MARKER and following == import_line for line, following in zip(lines, lines[1:])):
        return text
    kept, skip = [], False
    for line in lines:
        if line == MARKER:
            skip = True
        elif skip:
            skip = False
        elif line != import_line:
            kept.append(line)
    return "".join(line + "\n" for line in kept + [MARKER, import_line])


def updated_exclude(text):
    lines = split_lines(text or "")
    missing = [e for e in EXCLUDE_ENTRIES if e not in lines]
    if not missing:
        return text
    if EXCLUDE_MARKER not in lines:
        missing.insert(0, EXCLUDE_MARKER)
    return "".join(line + "\n" for line in lines + missing)


# --- scrittura ------------------------------------------------------------------------------------

def write_atomic(path, text):
    """Scrive con un file temporaneo e os.replace: un symlink al posto di path viene sostituito,
    non seguito. Chi vuole scrivere attraverso un link passa il percorso reale."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".mimir-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        if path.exists():
            shutil.copymode(str(path), tmp)
        os.replace(tmp, str(path))
    except BaseException:
        os.unlink(tmp)
        raise


def create_file(path, text):
    """Crea path solo se non esiste: O_EXCL fallisce su qualunque percorso esistente, anche su un
    symlink pendente piantato dalla sandbox, invece di seguirlo (FileExistsError)."""
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o644)
    with os.fdopen(fd, "wb") as fh:
        fh.write(text.encode("utf-8"))


def backup(path, stamp):
    target = Path(f"{path}.bak-{stamp}")
    shutil.copy2(str(path), str(target))
    return target


# --- requisiti della sandbox ----------------------------------------------------------------------

def confirm(question, assume_yes):
    if assume_yes:
        return True
    try:
        answer = input(f"{question} [s/N] ")
    except EOFError:
        print()
        return False
    return answer.strip().lower() in ("s", "si", "sì", "y", "yes")


def as_root(command):
    return command if hasattr(os, "geteuid") and os.geteuid() == 0 else ["sudo"] + command


def install_command(missing, which=shutil.which):
    """Il comando per installare i pacchetti mancanti con il gestore della distro, o None."""
    for name, base in PACKAGE_MANAGERS:
        if which(name):
            return as_root(base + [SANDBOX_PACKAGES[tool] for tool in missing])
    return None


def needs_apparmor_profile(sysctl_path=APPARMOR_SYSCTL, profile_path=APPARMOR_PROFILE_PATH):
    try:
        restricted = Path(sysctl_path).read_text(encoding="utf-8").strip() == "1"
    except OSError:
        return False
    return restricted and not Path(profile_path).exists()


def run(command, **kwargs):
    try:
        return subprocess.run(command, **kwargs).returncode == 0
    except OSError as exc:
        print(f"! {command[0]} non eseguibile ({exc})")
        return False


def install_sandbox_requirements(system, assume_yes, which=shutil.which, runner=run):
    """Restituisce l'elenco di ciò che manca ancora."""
    if system == "macos":
        return []
    if system == "wsl1":
        print("! WSL1: la sandbox di Claude Code richiede WSL2 (wsl --set-version <distro> 2)")
        return ["WSL2"]
    if system == "windows":
        print("! Windows nativo: la sandbox non esiste; per la protezione completa installa Mímir dentro WSL2 (install.ps1)")
        return []
    problems = []
    missing = [tool for tool in SANDBOX_PACKAGES if not which(tool)]
    if not missing:
        print("✓ bubblewrap e socat presenti")
    else:
        packages = ", ".join(SANDBOX_PACKAGES[t] for t in missing)
        command = install_command(missing, which)
        if command is None:
            print(f"! gestore dei pacchetti non riconosciuto: installa a mano {packages}")
            problems.append(packages)
        elif not confirm(f"La sandbox richiede {packages}. Installo con: {' '.join(command)}?", assume_yes):
            print(f"! {packages} non installati")
            problems.append(packages)
        elif runner(command):
            print(f"✓ {packages} installati")
        else:
            print(f"! installazione di {packages} non riuscita")
            problems.append(packages)
    if needs_apparmor_profile():
        if not confirm(f"AppArmor blocca bubblewrap: scrivo {APPARMOR_PROFILE_PATH} e ricarico AppArmor (sudo)?", assume_yes):
            print("! profilo AppArmor non installato: la sandbox non parte")
            problems.append("profilo AppArmor")
        elif (runner(as_root(["tee", APPARMOR_PROFILE_PATH]), input=APPARMOR_PROFILE, text=True,
                     stdout=subprocess.DEVNULL)
              and runner(as_root(["systemctl", "reload", "apparmor"]))):
            print(f"✓ profilo AppArmor installato in {APPARMOR_PROFILE_PATH}")
        else:
            print("! profilo AppArmor non installato")
            problems.append("profilo AppArmor")
    return problems


# --- orchestrazione -------------------------------------------------------------------------------

@dataclass
class Inputs:
    claude_md: Optional[str]
    settings_text: Optional[str]
    current: dict
    template: dict
    examples: dict
    has_git: bool
    git_note: str
    exclude: Optional[str]
    old_dir: Optional[str]


@dataclass
class Outputs:
    settings: dict
    claude_md: str
    exclude: Optional[str]


def read_old_dir(claude_md):
    raw = imported_dir(claude_md)
    if raw is None:
        return None
    try:
        if Path(raw).is_absolute():
            return normalize_dir(raw)
    except (OSError, ValueError):
        pass
    print(f"! import precedente in CLAUDE.md non valido, ignorato: {raw!r}")
    return None


def read_inputs(mimir_path, claude_md_path, settings_path):
    """Legge e valida tutto prima di qualsiasi scrittura; InstallError se qualcosa non va."""
    for required in ("CLAUDE.md", "plugins", "sandbox.settings.json"):
        if not (mimir_path / required).exists():
            raise InstallError(f"{mimir_path.as_posix()} non sembra la cartella di Mímir: manca {required}")
    template_text = read_mimir_file(mimir_path / "settings.template.json")
    if template_text is None:
        raise InstallError("manca settings.template.json")
    examples = {}
    for example, personal in PERSONAL_FILES:
        examples[personal] = read_mimir_file(mimir_path / example)
        if examples[personal] is None:
            raise InstallError(f"manca {example}")
    git = mimir_path / ".git"
    has_git = git.is_dir() and not git.is_symlink()
    git_note = "" if has_git else ("assente" if not os.path.lexists(str(git)) else "non è una cartella (worktree?)")
    claude_md = read_text(claude_md_path)
    settings_text = read_text(settings_path)
    return Inputs(
        claude_md=claude_md,
        settings_text=settings_text,
        current=parse_settings(settings_text, settings_path) if settings_text is not None else {},
        template=parse_settings(template_text, "settings.template.json"),
        examples=examples,
        has_git=has_git,
        git_note=git_note,
        exclude=read_mimir_file(git / "info" / "exclude") if has_git else None,
        old_dir=read_old_dir(claude_md),
    )


def compute(inputs, mimir_dir, system):
    settings = sort_lists(apply_protection(merge_settings(inputs.current, inputs.template),
                                           mimir_dir, inputs.old_dir, system))
    return Outputs(
        settings=settings,
        claude_md=linked_claude_md(inputs.claude_md, mimir_dir),
        exclude=updated_exclude(inputs.exclude) if inputs.has_git else None,
    )


def write_outputs(inputs, outputs, mimir_path, claude_md_path, settings_path, written):
    """Scrive solo ciò che cambia; aggiunge a written ogni file scritto (per il messaggio d'errore)."""
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for _, personal in PERSONAL_FILES:
        path = mimir_path / personal
        try:
            create_file(path, inputs.examples[personal])
            written.append(personal)
            print(f"✓ {personal} creato: personalizzalo")
        except FileExistsError:
            if path.is_symlink() and not path.exists():
                print(f"! {personal} è un symlink che non punta a nulla: non creato")
            else:
                print(f"✓ {personal} già presente")

    # ~/.claude non è scrivibile dalla sandbox: un symlink lì è dell'utente (dotfiles) e si segue
    if outputs.claude_md == inputs.claude_md:
        print("✓ CLAUDE.md già collegato")
    else:
        if inputs.claude_md is not None:
            print(f"  backup: {backup(claude_md_path, stamp)}")
        write_atomic(Path(os.path.realpath(str(claude_md_path))), outputs.claude_md)
        written.append(str(claude_md_path))
        print(f"✓ CLAUDE.md collegato a {mimir_path.as_posix()}")

    if outputs.settings == inputs.current:
        print("✓ settings.json già aggiornato")
    else:
        note = f" (backup: {backup(settings_path, stamp)})" if inputs.settings_text is not None else ""
        write_atomic(Path(os.path.realpath(str(settings_path))),
                     json.dumps(outputs.settings, indent=2, ensure_ascii=False) + "\n")
        written.append(str(settings_path))
        print(f"✓ impostazioni e protezione dei file di Mímir unite in settings.json{note}")

    if not inputs.has_git:
        print(f"  .git {inputs.git_note}: .git/info/exclude saltato")
    elif outputs.exclude != inputs.exclude:
        write_atomic(mimir_path / ".git" / "info" / "exclude", outputs.exclude)
        written.append(".git/info/exclude")
        print("✓ .git/info/exclude: aggiunti i file che la sandbox crea vuoti")


def launcher_command(system, mimir_path):
    # su Windows nativo il launcher bash non parte: sandbox abilitata con failIfUnavailable
    if system == "windows":
        script = mimir_path / "bin" / "claude-mimir.ps1"
        return f'powershell -NoProfile -ExecutionPolicy Bypass -File "{script}" (senza sandbox: per la protezione completa usa WSL2)'
    return f"{mimir_path.as_posix()}/bin/claude-mimir"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Collega Mímir a Claude Code su questa macchina.")
    parser.add_argument("--yes", action="store_true", help="risponde sì alle conferme")
    parser.add_argument("--skip-system", action="store_true", help="salta i passi con sudo")
    args = parser.parse_args(argv)
    # su Windows, con l'output rediretto, la codifica può non avere ✓: meglio un ? che un errore
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")

    mimir_path = Path(__file__).resolve().parent
    mimir_dir = mimir_path.as_posix()
    claude_md_path = Path.home() / ".claude" / "CLAUDE.md"
    settings_path = Path.home() / ".claude" / "settings.json"
    system = detect_system()

    try:
        inputs = read_inputs(mimir_path, claude_md_path, settings_path)
    except InstallError as exc:
        print(f"✗ {exc}: nessuna modifica fatta", file=sys.stderr)
        return 1
    outputs = compute(inputs, mimir_dir, system)
    written = []
    try:
        write_outputs(inputs, outputs, mimir_path, claude_md_path, settings_path, written)
    except OSError as exc:
        print(f"✗ scrittura non riuscita ({exc}). File già scritti: {', '.join(written) or 'nessuno'}. "
              "Risolvi e rilancia install.sh.", file=sys.stderr)
        return 1

    # Il marketplace (registrato o spostato sulla cartella attuale) aggiorna extraKnownMarketplaces e
    # known_marketplaces.json; i plugin già installati seguono il nuovo percorso.
    claude = shutil.which("claude")
    if claude and run([claude, "plugin", "marketplace", "add", mimir_dir], stdout=subprocess.DEVNULL):
        print(f"✓ marketplace mimir registrato su {mimir_dir}")
    else:
        print(f"! marketplace non registrato: dentro Claude Code lancia /plugin marketplace add {mimir_dir}")

    # Requisiti della sandbox: se qualcosa non va si continua, ma l'uscita segnala l'errore.
    problems = [] if args.skip_system else install_sandbox_requirements(system, args.yes)

    print(f"""
Sessioni con Mímir: {launcher_command(system, mimir_path)} (carica i plugin dalla cartella, niente da installare).
Per averli anche nelle sessioni normali, dentro Claude Code:
  /plugin install mimir@mimir
  /plugin install brokkr@mimir   (solo dove si lavora)
Se sposti la cartella, rilancia install.sh.
Host privati per la sandbox (azienda, clienti): aggiungili a sandbox.network.allowedDomains in {settings_path}.""")
    if problems:
        print(f"\n✗ Requisiti della sandbox mancanti: {', '.join(problems)}. Rilancia install.sh dopo averli sistemati.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
