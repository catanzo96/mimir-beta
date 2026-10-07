#!/usr/bin/env python3
"""UserPromptSubmit: ogni EVERY prompt della stessa sessione ricorda a Claude di proporre /retro.

Conta i prompt in un file per sessione nella cartella dati del plugin. Non scrive mai
in Mímir e non blocca mai il prompt: se l'input non è leggibile o il file di stato non
è scrivibile esce con 0 senza output, perché un promemoria mancato costa meno di un
prompt bloccato.
"""
import json
import os
import re
import sys
import tempfile
import time

EVERY = 25
MAX_AGE_DAYS = 7
NUDGE = (
    "Promemoria di Mímir: la sessione è lunga. Se sono emerse correzioni, preferenze "
    "o procedure ripetute, a fine compito proponi all'utente /retro in una riga, senza "
    "interrompere il lavoro in corso. Se non è emerso nulla, non dire niente."
)


def state_dir():
    base = os.environ.get("CLAUDE_PLUGIN_DATA") or tempfile.gettempdir()
    return os.path.join(base, "retro-nudge")


def remove_old(folder):
    """Toglie i contatori delle sessioni più vecchie di MAX_AGE_DAYS."""
    limit = time.time() - MAX_AGE_DAYS * 86400
    for entry in os.scandir(folder):
        if entry.is_file() and entry.stat().st_mtime < limit:
            os.remove(entry.path)


def next_count(session_id):
    folder = state_dir()
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, session_id)
    try:
        with open(path, encoding="utf-8") as fh:
            count = int(fh.read().strip() or 0) + 1
    except (FileNotFoundError, ValueError):
        count = 1
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(str(count))
    if count == 1:
        remove_old(folder)
    return count


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    session_id = str(data.get("session_id", "")) if isinstance(data, dict) else ""
    # il session_id diventa un nome di file: niente separatori di percorso
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", session_id):
        return
    try:
        count = next_count(session_id)
    except OSError:
        return
    if count % EVERY == 0:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": NUDGE,
        }}, ensure_ascii=False))


if __name__ == "__main__":
    main()
