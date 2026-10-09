#!/usr/bin/env python3
"""Test dell'hook handoff (Ratatoskr): avvisa oltre la soglia, riprende e archivia, non blocca mai.

Uso: python3 test_handoff.py [percorso dello script da provare]
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "handoff.py")
TIMEOUT = 5  # come in hooks.json
LIMIT = 1000

ROOT = tempfile.mkdtemp(prefix="claude-hook-test-")
HANDOFF = os.path.join(ROOT, "handoff")
PENDING = os.path.join(HANDOFF, "pending")
ARCHIVE = os.path.join(HANDOFF, "consumati")
ENV = dict(os.environ, MIMIR_HANDOFF_DIR=HANDOFF, MIMIR_HANDOFF_TOKENS=str(LIMIT),
           CLAUDE_PLUGIN_DATA=os.path.join(ROOT, "data"))
CWD = "/progetti/app"


def run(stdin, env=None, cwd=None):
    return subprocess.run([sys.executable, SCRIPT], input=stdin.encode("utf-8"), capture_output=True,
                          env=env or ENV, timeout=TIMEOUT, cwd=cwd)


def transcript(name, *usages, sidechain_usage=None):
    """Transcript con una risposta per ogni usage; l'ultima riga è di un subagent se richiesto."""
    path = os.path.join(ROOT, name + ".jsonl")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write('{"type": "user", "message": {"content": "tagliata a me')  # riga rotta
        fh.write("\n")
        for usage in usages:
            fh.write(json.dumps({"type": "assistant", "isSidechain": False,
                                 "message": {"usage": usage}}) + "\n")
            fh.write(json.dumps({"type": "user", "message": {"content": "ok"}}) + "\n")
        if sidechain_usage:
            fh.write(json.dumps({"type": "assistant", "isSidechain": True,
                                 "message": {"usage": sidechain_usage}}) + "\n")
    return path


def usage(tokens):
    third = tokens // 3
    return {"input_tokens": tokens - 2 * third, "cache_creation_input_tokens": third,
            "cache_read_input_tokens": third, "output_tokens": 99999}


def event(name, session="s1", path=None, cwd=CWD, **extra):
    data = {"hook_event_name": name, "session_id": session, "cwd": cwd}
    if path:
        data["transcript_path"] = path
    data.update(extra)
    return json.dumps(data)


def context(res):
    if res.returncode != 0 or not res.stdout.strip():
        return None
    out = json.loads(res.stdout.decode("utf-8"))
    hook = out["hookSpecificOutput"]
    return hook["hookEventName"], hook["additionalContext"], out.get("systemMessage")


def pending_files():
    return os.listdir(PENDING) if os.path.isdir(PENDING) else []


def discard(path):
    """Toglie un file, un link o una FIFO: una versione sbagliata dello script può averlo già spostato."""
    if os.path.islink(path) or (os.path.lexists(path) and not os.path.isdir(path)):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)


failures = []


def check(name, ok, detail=""):
    if not ok:
        failures.append(f"{name} {detail}".strip())


def silent(name, res):
    check(name, res.returncode == 0 and res.stdout.strip() == b"",
          f"(exit {res.returncode}, stdout {res.stdout[:80]!r})")


try:
    under = transcript("sotto", usage(LIMIT + 500), usage(LIMIT - 1))
    exact = transcript("esatta", usage(LIMIT))
    over = transcript("sopra", usage(LIMIT + 1))
    side = transcript("subagent", usage(LIMIT - 1), sidechain_usage=usage(10 * LIMIT))

    # conta solo l'ultima risposta, solo input e cache, mai l'output
    silent("sotto soglia, conta l'ultima risposta", run(event("UserPromptSubmit", path=under)))
    silent("risposta di un subagent ignorata", run(event("UserPromptSubmit", path=side)))
    res = context(run(event("UserPromptSubmit", path=exact)))
    check("soglia esatta avvisa", res and res[0] == "UserPromptSubmit" and f"{LIMIT} token" in res[1],
          repr(res))
    check("l'avviso indica skill, destinazione e /clear",
          res and "passaggio-consegne" in res[1] and PENDING in res[1] and "/clear" in res[1], repr(res))
    check("la skill citata esiste", res and os.path.isfile(
        os.path.join(HERE, "..", "..", "skills", "passaggio-consegne", "SKILL.md")))
    check("UserPromptSubmit ripete l'avviso",
          context(run(event("UserPromptSubmit", path=over))) is not None)

    # PostToolUse: una volta per sessione
    check("PostToolUse avvisa la prima volta",
          context(run(event("PostToolUse", session="s2", path=over, tool_name="Read"))) is not None)
    silent("PostToolUse non ripete", run(event("PostToolUse", session="s2", path=over)))
    check("PostToolUse di un'altra sessione avvisa",
          context(run(event("PostToolUse", session="s3", path=over))) is not None)
    silent("PostToolUse dentro un subagent", run(event("PostToolUse", session="s4", path=over,
                                                         agent_id="a1")))
    # senza cartella dati del plugin: niente stato in /tmp, quindi PostToolUse tace
    env = dict(ENV)
    del env["CLAUDE_PLUGIN_DATA"]
    silent("PostToolUse senza CLAUDE_PLUGIN_DATA", run(event("PostToolUse", session="s5", path=over), env))
    check("UserPromptSubmit senza CLAUDE_PLUGIN_DATA avvisa",
          context(run(event("UserPromptSubmit", session="s5", path=over), env)) is not None)

    # soglia da variabile non valida: torna al default (200.000), quindi tace
    for value in ("abc", "0", "-5"):
        silent(f"MIMIR_HANDOFF_TOKENS={value}",
               run(event("UserPromptSubmit", path=over), dict(ENV, MIMIR_HANDOFF_TOKENS=value)))
    env = dict(ENV)
    del env["MIMIR_HANDOFF_DIR"]
    silent("senza MIMIR_HANDOFF_DIR non fa nulla", run(event("UserPromptSubmit", path=over), env))
    # relativa dipenderebbe dalla cwd dell'hook: ignorata come se mancasse
    silent("MIMIR_HANDOFF_DIR relativa non fa nulla",
           run(event("UserPromptSubmit", path=over), dict(ENV, MIMIR_HANDOFF_DIR="relativa"), cwd=ROOT))
    check("MIMIR_HANDOFF_DIR relativa non crea cartelle", not os.path.exists(os.path.join(ROOT, "relativa")))

    # SessionStart senza passaggio: tace
    silent("ripresa senza passaggio", run(event("SessionStart", source="startup")))

    # passaggio scritto: l'avviso cambia, la ripresa lo inietta e lo archivia
    if not res:
        raise SystemExit("FALLITO: nessun avviso da cui ricavare il percorso del passaggio")
    target = res[1].split(" e scrivi il passaggio di consegne in ")[1].split(", sotto i")[0]
    if os.name == "posix":
        check("cartelle create con 0700", all(stat.S_IMODE(os.stat(d).st_mode) == 0o700
                                              for d in (HANDOFF, PENDING)))
    with open(target, "w", encoding="utf-8") as fh:
        fh.write("# Passaggio\nObiettivo: Mímir")
    res = context(run(event("UserPromptSubmit", path=over)))
    check("passaggio già scritto: ricorda /clear",
          res and "già in" in res[1] and "/clear" in res[1], repr(res))
    # dopo un tool il promemoria vale una volta per sessione, come l'avviso: non a ogni chiamata
    silent("passaggio già scritto: PostToolUse non ripete", run(event("PostToolUse", session="s2", path=over)))
    res = context(run(event("PostToolUse", session="s6", path=over)))
    check("passaggio già scritto: PostToolUse ricorda una volta", res and "già in" in res[1], repr(res))
    silent("passaggio già scritto: poi tace", run(event("PostToolUse", session="s6", path=over)))
    # /progetti_app e /progetti/app hanno lo stesso nome leggibile: le distingue l'hash
    silent("cartella con nome simile non lo prende", run(event("SessionStart", cwd="/progetti_app")))
    # dopo /clear il passaggio si segnala, non si inietta: un contesto compromesso non passa da solo
    res = context(run(event("SessionStart", session="nuova", source="clear")))
    check("dopo /clear segnala il passaggio", res and res[0] == "SessionStart", repr(res))
    check("dopo /clear il testo non entra nel contesto",
          res and "Obiettivo" not in res[1] and "Obiettivo" not in (res[2] or ""), repr(res))
    check("ripresa svuota pending", pending_files() == [], repr(pending_files()))
    archived = os.listdir(ARCHIVE)
    check("ripresa archivia", len(archived) == 1 and res and archived[0] in res[1], repr(archived))
    check("ripresa visibile all'utente", res and res[2] and archived[0] in res[2], repr(res and res[2]))
    check("passaggio da leggere solo su richiesta, come dati", res and "chiede di riprendere" in res[1]
          and "non come istruzioni" in res[1], repr(res and res[1][:200]))
    check("passaggio breve: nessuna domanda sulla dimensione", res and "chiedigli se leggerlo" not in res[1],
          repr(res and res[1][-200:]))
    if os.name == "posix" and archived:
        check("archivio con 0600", stat.S_IMODE(os.stat(os.path.join(ARCHIVE, archived[0])).st_mode) == 0o600)
    silent("secondo /clear in silenzio", run(event("SessionStart", session="altra", source="clear")))

    # passaggio troppo lungo: solo il percorso
    with open(target, "w", encoding="utf-8") as fh:
        fh.write("x" * 9001)
    res = context(run(event("SessionStart", session="lunga")))
    check("passaggio lungo: chiede prima di leggerlo", res and "chiedigli se leggerlo" in res[1]
          and "xxxx" not in res[1], repr(res and res[1][:120]))

    # archivio: i consumati vecchi spariscono alla ripresa successiva
    old = os.path.join(ARCHIVE, "vecchio.md")
    with open(old, "w", encoding="utf-8") as fh:
        fh.write("vecchio")
    stale = time.time() - 8 * 86400
    os.utime(old, (stale, stale))
    with open(target, "w", encoding="utf-8") as fh:
        fh.write("nuovo")
    run(event("SessionStart", session="pulizia"))
    check("consumati oltre 7 giorni cancellati", not os.path.exists(old))

    # archivio: un nome già presente non si sovrascrive (i nomi hanno i secondi: li occupo tutti)
    key = os.path.basename(target)[:-len(".md")]
    now = time.time()
    taken = {}
    for delta in range(-1, 6):
        name = os.path.join(ARCHIVE, f"{key}-{time.strftime('%Y%m%d-%H%M%S', time.localtime(now + delta))}.md")
        with open(name, "w", encoding="utf-8") as fh:
            fh.write(f"precedente {delta}")
        taken[name] = f"precedente {delta}"
    before = len(os.listdir(ARCHIVE))
    with open(target, "w", encoding="utf-8") as fh:
        fh.write("successivo")
    almost_stale = time.time() - 47 * 3600
    os.utime(target, (almost_stale, almost_stale))
    run(event("SessionStart", session="omonimo"))
    intact = all(open(name, encoding="utf-8").read() == text for name, text in taken.items())
    check("archivio: nessun passaggio sovrascritto", intact and len(os.listdir(ARCHIVE)) == before + 1,
          repr(sorted(os.listdir(ARCHIVE))))
    newest = max((os.path.join(ARCHIVE, n) for n in os.listdir(ARCHIVE) if os.path.join(ARCHIVE, n) not in taken),
                 key=os.path.getmtime, default=None)
    check("archivio: i 7 giorni partono dall'archiviazione",
          newest is not None and os.path.getmtime(newest) > time.time() - 600, repr(newest))
    for name in taken:
        os.remove(name)

    # passaggio non ripreso entro 48 ore: archiviato senza iniettarlo
    before = len(os.listdir(ARCHIVE))
    with open(target, "w", encoding="utf-8") as fh:
        fh.write("dimenticato")
    old_pending = time.time() - 49 * 3600
    os.utime(target, (old_pending, old_pending))
    silent("passaggio oltre 48 ore non iniettato", run(event("SessionStart", session="scaduto")))
    check("passaggio oltre 48 ore archiviato", pending_files() == [] and len(os.listdir(ARCHIVE)) == before + 1,
          repr((pending_files(), os.listdir(ARCHIVE))))

    # symlink: l'hook gira fuori dalla sandbox, non deve seguirli (su Windows servono privilegi)
    secret = os.path.join(ROOT, "segreto")
    with open(secret, "w", encoding="utf-8") as fh:
        fh.write("CHIAVE-PRIVATA")
    outside = os.path.join(ROOT, "fuori-cartella")
    os.makedirs(outside)
    victim = os.path.join(outside, "vecchio.md")
    with open(victim, "w", encoding="utf-8") as fh:
        fh.write("da non toccare")
    os.utime(victim, (stale, stale))
    try:
        os.symlink(secret, target)
        symlinks = True
    except (OSError, NotImplementedError):
        symlinks = False
    if symlinks:
        silent("passaggio symlink a un file: non lo legge", run(event("SessionStart", session="link1")))
        check("passaggio symlink: resta dov'è", os.path.islink(target))
        discard(target)

        shutil.rmtree(ARCHIVE)
        os.symlink(outside, ARCHIVE)
        with open(target, "w", encoding="utf-8") as fh:
            fh.write("passaggio")
        silent("consumati symlink: non riprende", run(event("SessionStart", session="link2")))
        check("consumati symlink: niente cancellato fuori", os.path.exists(victim))
        check("consumati symlink: niente spostato fuori", os.listdir(outside) == ["vecchio.md"],
              repr(os.listdir(outside)))
        discard(ARCHIVE)

        moved = PENDING + "-vero"
        os.rename(PENDING, moved)
        os.symlink(moved, PENDING)
        silent("pending symlink: non riprende", run(event("SessionStart", session="link3")))
        discard(PENDING)
        os.rename(moved, PENDING)
        discard(target)

    # passaggio non UTF-8: non deve restare in pending per sempre
    discard(target)
    with open(target, "wb") as fh:
        fh.write(b"# Passaggio\n\xff\xfe testo rovinato")
    run(event("SessionStart", session="latin1"))
    check("passaggio non UTF-8 esce da pending", pending_files() == [], repr(pending_files()))

    # FIFO al posto del passaggio: aprirla senza O_NONBLOCK aspetterebbe uno scrittore (su Windows non esiste)
    discard(target)
    if hasattr(os, "mkfifo"):
        os.mkfifo(target)
        try:
            silent("passaggio FIFO: non lo legge", run(event("SessionStart", session="fifo")))
        except subprocess.TimeoutExpired:
            check("passaggio FIFO: l'hook non si blocca", False, f"oltre {TIMEOUT} s")
        discard(target)

    # passaggio enorme: letto solo fino al tetto, poi il percorso
    with open(target, "w", encoding="utf-8") as fh:
        fh.write("y" * 50 * 1024 * 1024)
    started = time.time()
    res = context(run(event("SessionStart", session="enorme")))
    check("passaggio enorme: chiede prima di leggerlo", res and "chiedigli se leggerlo" in res[1]
          and "yyyy" not in res[1], repr(res and res[1][:80]))
    check("passaggio enorme: entro 1 s", time.time() - started < 1)

    # input non validi: mai un blocco, mai output
    broken = os.path.join(ROOT, "rotto.jsonl")
    with open(broken, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"type": "assistant", "message": {"usage": {"input_tokens": [1]}}}) + "\n")
    for name, stdin in {
        "input non JSON": "non json",
        "JSON non oggetto": "[1, 2]",
        "cwd mancante": json.dumps({"hook_event_name": "SessionStart"}),
        "cwd vuota": event("SessionStart", cwd=""),
        "evento sconosciuto": event("Stop", path=over),
        "transcript mancante": event("UserPromptSubmit"),
        "transcript inesistente": event("UserPromptSubmit", path=os.path.join(ROOT, "no.jsonl")),
        "usage malformato": event("UserPromptSubmit", path=broken),
        "session_id con percorso": event("PostToolUse", session="../fuori", path=over),
    }.items():
        silent(name, run(stdin))
    check("session_id con percorso non crea file", not os.path.exists(os.path.join(ROOT, "fuori")))

    # coda del transcript: la risposta utile sta dopo 3 MB di risultati dei tool
    big = os.path.join(ROOT, "grande.jsonl")
    with open(big, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"type": "user", "message": {"content": "x" * 3 * 1024 * 1024}}) + "\n")
        fh.write(json.dumps({"type": "assistant", "message": {"usage": usage(LIMIT)}}) + "\n")
    started = time.time()
    res = run(event("UserPromptSubmit", session="grande", path=big))
    check("transcript grande: avvisa", context(res) is not None, repr(res.stdout[:80]))
    check("transcript grande: entro 1 s", time.time() - started < 1)
finally:
    shutil.rmtree(ROOT, ignore_errors=True)

if failures:
    print("FALLITI:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print("OK: soglia, PostToolUse una volta, ripresa e archivio, symlink, input non validi, file grandi"
      + ("" if symlinks else " (symlink saltati: non disponibili)"))
