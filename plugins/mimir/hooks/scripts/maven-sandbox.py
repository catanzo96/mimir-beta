#!/usr/bin/env python3
"""SessionStart: nei progetti Maven avviati con il launcher di Mímir dice a Claude come buildare.

Nella sandbox ~/.m2/settings.xml non è leggibile e Maven si ferma; la skill java ha la
soluzione ma non si carica per una richiesta come "compila il progetto". Questo hook la
mette in contesto in modo deterministico, solo se:
- il launcher ha esportato MIMIR_MAVEN_SETTINGS e il file esiste;
- nella cartella del progetto c'è un pom.xml.
Non blocca mai: con input illeggibile o condizioni non soddisfatte esce con 0 senza output.
"""
import json
import os
import sys

CONTEXT = (
    "Progetto Maven in una sessione di Mímir con sandbox: ~/.m2/settings.xml non è leggibile "
    "e senza opzioni Maven si ferma. Lancia sempre i comandi Maven nella sandbox così: "
    'mvn -llr -s "$MIMIR_MAVEN_SETTINGS" <goal> (il file è offline e senza credenziali; '
    "-llr fa accettare gli artefatti già in cache). Con il wrapper: ./mvnw con le stesse opzioni. "
    "Non configurare a mano il proxy della sandbox e non leggere le sue credenziali dalle variabili "
    "d'ambiente. Se mancano dipendenze nella cache, fermati e chiedi all'utente di eseguire la build "
    "fuori dalla sandbox."
)


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (json.JSONDecodeError, ValueError):
        return
    if not isinstance(data, dict):
        return
    settings = os.environ.get("MIMIR_MAVEN_SETTINGS", "")
    if not settings or not os.path.isfile(settings):
        return
    project = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR", "")
    if not project or not os.path.isfile(os.path.join(project, "pom.xml")):
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": CONTEXT,
    }}, ensure_ascii=False))


if __name__ == "__main__":
    # Su Windows la codifica di default della console non è UTF-8: il contesto accentato si rovinerebbe.
    sys.stdout.reconfigure(encoding="utf-8")
    main()
