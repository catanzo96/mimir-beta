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
    "/.bash_profile", "/.bashrc", "/.gitconfig", "/.gitmodules", "/.idea", "/.mcp.json", "/.profile",
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

# Le regole Edit seguono la sintassi gitignore e Claude Code non escapa quelle scritte a mano; su Linux e
# WSL2 una voce di denyWrite con * ? [ viene saltata (doc permissions e settings-reference, 10/10).
# ] e \ per prudenza: \ è l'escape di gitignore, ] chiude [. Le parentesi sono letterali.
PATTERN_CHARS = "*?[]\\"

# Prima della prima installazione la sandbox può scrivere il template, che l'installer unisce fuori:
# ammesse solo le chiavi che non allentano nulla. Non protegge da un install.py modificato.
TEMPLATE_KEYS = {"attribution", "skillListingBudgetFraction", "permissions"}
TEMPLATE_PERMISSION_KEYS = {"ask", "deny"}

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
# senza systemd come PID 1 systemctl non funziona: lì si carica il solo profilo con apparmor_parser
SYSTEMD_RUNTIME_DIR = "/run/systemd/system"
SANDBOX_PACKAGES = {"bwrap": "bubblewrap", "socat": "socat"}
# (gestore, aggiornamento degli indici da lanciare prima, comando di installazione). Con indici vecchi
# apt-get install non trova i pacchetti; dnf e zypper aggiornano i metadati da soli, pacman -Sy
# aggiornerebbe a metà. Tentativi e timeout: un mirror che non rispondeva ha tenuto fermo apt per
# 14 minuti in CI (run 37809319638).
PACKAGE_MANAGERS = [
    ("apt-get", [["apt-get", "-o", "Acquire::Retries=3", "-o", "Acquire::http::Timeout=30", "update"]],
     ["apt-get", "install", "-y"]),
    ("dnf", [], ["dnf", "install", "-y"]),
    ("pacman", [], ["pacman", "-S", "--needed", "--noconfirm"]),
    ("zypper", [], ["zypper", "install", "-y"]),
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

def is_control_char(c):
    """C0, DEL e C1: alcuni terminali interpretano anche questi ultimi."""
    return ord(c) < 32 or 0x7f <= ord(c) <= 0x9f


def check_mimir_dir(mimir_dir):
    """Un percorso con caratteri di pattern renderebbe la protezione inefficace senza avviso. Anche i
    caratteri di controllo: gitignore va a righe e un a capo spezzerebbe la regola."""
    try:
        mimir_dir.encode("utf-8")
    except UnicodeEncodeError as exc:
        # su Linux un byte non UTF-8 del nome arriva come surrogato, che CLAUDE.md non potrebbe contenere
        raise InstallError(f"il percorso {mimir_dir!r} non è UTF-8 valido: rinomina la cartella") from exc
    found = sorted(set(PATTERN_CHARS) & set(mimir_dir))
    if any(is_control_char(c) for c in mimir_dir):
        found.append("caratteri di controllo")
    if found:
        raise InstallError(f"il percorso {mimir_dir!r} contiene {' '.join(found)}: Claude Code lo leggerebbe "
                           "come un pattern e i file di Mímir resterebbero senza protezione. Sposta la cartella "
                           f"in un percorso senza {' '.join(PATTERN_CHARS)} né caratteri di controllo")


def in_expected_dir(mimir_path, relative):
    """La cartella di relative, risolta, è esattamente quella attesa sotto Mímir? O_NOFOLLOW copre solo
    l'ultimo componente: una cartella intermedia come profile/ sostituita con un symlink porterebbe
    fuori, o in una cartella protetta come bin/. In un worktree .git è un file e l'exclude non si scrive."""
    root = os.path.realpath(str(mimir_path))
    expected = os.path.normpath(os.path.join(root, os.path.dirname(relative)))
    actual = os.path.realpath(os.path.join(str(mimir_path), os.path.dirname(relative)))
    return os.path.normcase(actual) == os.path.normcase(expected)


def check_expected_dir(mimir_path, relative):
    if not in_expected_dir(mimir_path, relative):
        raise InstallError(f"la cartella di {relative!r} non è quella attesa: punta fuori dalla cartella di Mímir "
                           "o altrove al suo interno")


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
    # json accetta NaN, Infinity e numeri fuori scala come 1e999 (letti come infinito), ma li riscriverebbe
    # tali e quali: settings.json non sarebbe più JSON. Rifiutarli qui, come i caratteri sotto
    try:
        encoded = json.dumps(data, ensure_ascii=False, allow_nan=False)
    except ValueError as exc:
        raise InstallError(f"{path} contiene NaN, Infinity o un numero fuori scala, che non sono JSON standard") \
            from exc
    # json accetta un surrogato isolato come escape (\ud800), che poi non si scrive in UTF-8: rifiutarlo qui
    # evita di fermarsi a metà, dopo aver già scritto CLAUDE.md
    try:
        encoded.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise InstallError(f"{path} contiene un carattere non scrivibile in UTF-8 ({exc.reason})") from exc
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


def check_template_keys(template):
    """Solo per settings.template.json: il settings.json dell'utente può avere qualsiasi chiave."""
    extra = sorted(set(template) - TEMPLATE_KEYS)
    extra += sorted(f"permissions.{k}" for k in set(template.get("permissions") or {}) - TEMPLATE_PERMISSION_KEYS)
    if extra:
        # repr: i nomi vengono da un file che la sandbox può scrivere, niente sequenze al terminale
        raise InstallError("settings.template.json contiene chiavi non ammesse, da controllare con git status e "
                           f"git diff HEAD: {', '.join(repr(k) for k in extra)}")


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


def install_commands(missing, which=shutil.which):
    """I comandi, in ordine, per installare i pacchetti mancanti con il gestore della distro, o None.
    L'ultimo installa, quelli prima aggiornano gli indici."""
    for name, before, base in PACKAGE_MANAGERS:
        if which(name):
            return [as_root(c) for c in before] + [as_root(base + [SANDBOX_PACKAGES[tool] for tool in missing])]
    return None


def install_packages(commands, runner):
    """Un aggiornamento degli indici fallito (per esempio un repository di terze parti rotto) non
    ferma l'installazione: i pacchetti possono essere già negli indici che ci sono."""
    for refresh in commands[:-1]:
        if not runner(refresh):
            print(f"! {' '.join(refresh)} non riuscito: installo con gli indici presenti")
    return runner(commands[-1])


def apparmor_reload_commands(systemd_runtime_dir=SYSTEMD_RUNTIME_DIR):
    """I modi di ricaricare AppArmor, da provare in ordine fino al primo che riesce."""
    parser = as_root(["apparmor_parser", "-r", APPARMOR_PROFILE_PATH])
    # la cartella c'è se systemd è il PID 1 (sd_booted), ma in un container può esserci senza che
    # systemd risponda: lì systemctl fallisce e resta il parser
    if os.path.isdir(systemd_runtime_dir):
        return [as_root(["systemctl", "reload", "apparmor"]), parser]
    return [parser]


def needs_apparmor_profile(sysctl_path=APPARMOR_SYSCTL, profile_path=APPARMOR_PROFILE_PATH):
    try:
        restricted = Path(sysctl_path).read_text(encoding="utf-8").strip() == "1"
    except OSError:
        return False
    # lexists: anche un symlink rotto è un profilo esistente, che non si scrive né si toglie
    return restricted and not os.path.lexists(profile_path)


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
        commands = install_commands(missing, which)
        if commands is None:
            print(f"! gestore dei pacchetti non riconosciuto: installa a mano {packages}")
            problems.append(packages)
        elif not confirm(f"La sandbox richiede {packages}. Installo con: "
                         f"{', poi '.join(' '.join(c) for c in commands)}?", assume_yes):
            print(f"! {packages} non installati")
            problems.append(packages)
        elif install_packages(commands, runner):
            print(f"✓ {packages} installati")
        else:
            print(f"! installazione di {packages} non riuscita")
            problems.append(packages)
    if needs_apparmor_profile():
        reloads = apparmor_reload_commands()
        remove = as_root(["rm", "-f", APPARMOR_PROFILE_PATH])
        if not confirm(f"AppArmor blocca bubblewrap: scrivo {APPARMOR_PROFILE_PATH} e ricarico AppArmor con: "
                       f"{' o '.join(' '.join(c) for c in reloads)} (se non riesce, tolgo il profilo con: "
                       f"{' '.join(remove)})?", assume_yes):
            print("! profilo AppArmor non installato: la sandbox non parte")
            problems.append("profilo AppArmor")
        elif not needs_apparmor_profile():
            # la conferma può durare minuti: un profilo comparso nel frattempo non è di questo lancio
            print(f"! {APPARMOR_PROFILE_PATH} comparso durante la conferma: lo lascio com'è")
        elif not runner(as_root(["tee", APPARMOR_PROFILE_PATH]), input=APPARMOR_PROFILE, text=True,
                        stdout=subprocess.DEVNULL):
            print("! profilo AppArmor non installato")
            problems.append("profilo AppArmor")
        elif any(runner(c) for c in reloads):
            print(f"✓ profilo AppArmor installato in {APPARMOR_PROFILE_PATH}")
        else:
            # needs_apparmor_profile l'ha visto assente, quindi l'ha creato questo lancio: lasciato lì, al
            # lancio successivo risulterebbe a posto e il ricarico non si riproverebbe
            if runner(remove):
                print("! profilo AppArmor non ricaricato: tolto, rilancia install.sh dopo aver sistemato AppArmor")
            else:
                print(f"! profilo AppArmor non ricaricato e non tolto: toglilo con {' '.join(remove)}")
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
    check_mimir_dir(mimir_path.as_posix())
    for required in ("CLAUDE.md", "plugins", "sandbox.settings.json"):
        if not (mimir_path / required).exists():
            raise InstallError(f"{mimir_path.as_posix()} non sembra la cartella di Mímir: manca {required}")
    template_text = read_mimir_file(mimir_path / "settings.template.json")
    if template_text is None:
        raise InstallError("manca settings.template.json")
    template = parse_settings(template_text, "settings.template.json")
    check_template_keys(template)
    examples = {}
    for example, personal in PERSONAL_FILES:
        check_expected_dir(mimir_path, example)
        check_expected_dir(mimir_path, personal)
        examples[personal] = read_mimir_file(mimir_path / example)
        if examples[personal] is None:
            raise InstallError(f"manca {example}")
    git = mimir_path / ".git"
    has_git = git.is_dir() and not git.is_symlink()
    git_note = "" if has_git else ("assente" if not os.path.lexists(str(git)) else "non è una cartella (worktree?)")
    if has_git:
        check_expected_dir(mimir_path, ".git/info/exclude")
    claude_md = read_text(claude_md_path)
    settings_text = read_text(settings_path)
    return Inputs(
        claude_md=claude_md,
        settings_text=settings_text,
        current=parse_settings(settings_text, settings_path) if settings_text is not None else {},
        template=template,
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


def write_outputs(inputs, outputs, mimir_path, claude_md_path, settings_path, written, skipped):
    """Scrive solo ciò che cambia; aggiunge a written ogni file scritto (per il messaggio d'errore) e a
    skipped quelli saltati perché la loro cartella non è più quella attesa."""
    stamp = time.strftime("%Y%m%d-%H%M%S")
    # La lettura ha già controllato le cartelle; qui si ricontrolla perché la sandbox può cambiarle nel
    # frattempo. Resta una finestra tra controllo e apertura: chiuderla vorrebbe dir_fd per ogni componente,
    # e il guadagno per chi la sfrutta è un profile.md o un exclude scritti altrove.
    for _, personal in PERSONAL_FILES:
        path = mimir_path / personal
        if not in_expected_dir(mimir_path, personal):
            print(f"! {personal}: la cartella non è quella attesa, non creato")
            skipped.append(personal)
            continue
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
    elif not in_expected_dir(mimir_path, ".git/info/exclude"):
        print("! .git/info/exclude: la cartella non è quella attesa, non scritto")
        skipped.append(".git/info/exclude")
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
    written, skipped = [], []
    try:
        write_outputs(inputs, outputs, mimir_path, claude_md_path, settings_path, written, skipped)
    except (OSError, UnicodeError) as exc:
        skipped_note = (f"File saltati perché la loro cartella non è quella attesa: {', '.join(skipped)}. "
                        if skipped else "")
        print(f"✗ scrittura non riuscita ({exc}). File già scritti: {', '.join(written) or 'nessuno'}. "
              f"{skipped_note}Risolvi e rilancia install.sh.", file=sys.stderr)
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
    if skipped:
        # una cartella cambiata durante l'installazione è un segno di manomissione: con --yes un avviso passerebbe
        print(f"\n✗ File saltati perché la loro cartella non è quella attesa: {', '.join(skipped)}. "
              "Controlla con git status e rilancia install.sh.", file=sys.stderr)
    if problems:
        print(f"\n✗ Requisiti della sandbox mancanti: {', '.join(problems)}. Rilancia install.sh dopo averli sistemati.",
              file=sys.stderr)
    return 1 if skipped or problems else 0


if __name__ == "__main__":
    sys.exit(main())
