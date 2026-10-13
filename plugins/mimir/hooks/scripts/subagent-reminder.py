#!/usr/bin/env python3
"""SubagentStart: aggiunge un richiamo alle regole di Mímir ai subagent Explore e Plan.

Explore e Plan non ricevono il CLAUDE.md, quindi non vedono le regole; general-purpose
e gli agent di Mímir sì. Il matcher di hooks.json limita già l'evento ai due tipi: il
controllo qui lo ripete perché il test dello script non prova il matcher.
SubagentStart non può bloccare: con un input non leggibile l'hook esce con 0 senza
output, e il subagent parte senza richiamo.
"""
import json
import sys

AGENT_TYPES = {"Explore", "Plan"}
REMINDER = (
    "Regole di Mímir per questo subagent: rispondi in italiano; separa ciò che hai "
    "accertato dalle ipotesi e per ogni fatto indica l'evidenza (file:riga o comando); "
    "per dire che qualcosa non c'è serve una ricerca che non salti file; resta nel "
    "perimetro della richiesta e segnala il resto senza farlo."
)


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (json.JSONDecodeError, ValueError):
        return
    agent_type = data.get("agent_type") if isinstance(data, dict) else None
    if not isinstance(agent_type, str) or agent_type not in AGENT_TYPES:
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SubagentStart",
        "additionalContext": REMINDER,
    }}, ensure_ascii=False))


if __name__ == "__main__":
    # Su Windows la codifica di default della console non è UTF-8: il richiamo accentato si rovinerebbe.
    sys.stdout.reconfigure(encoding="utf-8")
    main()
