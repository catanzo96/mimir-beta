#!/usr/bin/env bash
# Lancia uno script Python degli hook con il primo interprete che funziona davvero.
# Su Windows python.org e winget creano python.exe e py.exe, non python3.exe, e lo stub
# dello Store esiste nel PATH ma non esegue nulla: ogni candidato si prova prima di usarlo.
# Un hook che non parte è un errore non bloccante per Claude Code: con --fail-closed,
# se manca Python, il wrapper blocca (exit 2) i comandi il cui campo "command" contiene
# "commit" (anche in maiuscolo: PowerShell non distingue) e lascia passare gli altri,
# perché l'hook gira su ogni comando. Il resto dell'input (cwd, transcript_path) non conta.
# Uso: run-python.sh [--fail-closed] <script.py>
set -uo pipefail

fail_closed=0
if [[ "${1:-}" == "--fail-closed" ]]; then
  fail_closed=1
  shift
fi
script="${1:?uso: run-python.sh [--fail-closed] <script.py>}"

for candidate in python3 python "py -3"; do
  read -r -a cmd <<< "$candidate"
  if "${cmd[@]}" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' </dev/null >/dev/null 2>&1; then
    exec "${cmd[@]}" "$script"
  fi
done

if (( fail_closed )); then
  IFS= read -r -d '' input || true
  # valore JSON di "command": caratteri normali o sequenze di escape, fino a "commit"
  command_with_commit='"command"[[:space:]]*:[[:space:]]*"([^"\\]|\\.)*commit'
  shopt -s nocasematch
  if [[ "$input" =~ $command_with_commit ]]; then
    echo "Mímir: Python 3.8+ non trovato, il controllo dei commit non può partire: commit bloccato. Installa Python o rilancia l'installer di Mímir." >&2
    exit 2
  fi
  exit 0
fi
echo "Mímir: Python 3.8+ non trovato, hook ${script##*/} saltato." >&2
exit 0
