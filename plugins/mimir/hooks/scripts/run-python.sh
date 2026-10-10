#!/usr/bin/env bash
# Lancia uno script Python degli hook con il primo interprete che funziona davvero.
# Su Windows python.org e winget creano python.exe e py.exe, non python3.exe, e lo stub
# dello Store esiste nel PATH ma non esegue nulla: ogni candidato si prova prima di usarlo.
# Un hook che non parte è un errore non bloccante per Claude Code: con --fail-closed,
# se manca Python, il wrapper blocca (exit 2) i comandi il cui campo "command" contiene
# "git" seguito da un sottocomando che scrive (commit, push, tag, reset, branch…) come parole
# intere (anche in maiuscolo: PowerShell non distingue) e lascia passare gli altri, perché
# l'hook gira su ogni comando.
# Il resto dell'input (cwd, transcript_path) non conta.
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
  # valore JSON di "command" (caratteri normali o sequenze di escape) con git e poi un sottocomando di
  # WRITE_SUBCOMMANDS di git-guard.py non attaccato a lettere, cifre, _ o - (così --tags, committer e
  # merge-base non contano); tabulazione, a capo e virgolette nel JSON sono \t, \n e \", e valgono come
  # separatori. Branch, switch, stash e reflog si bloccano anche in lettura: senza Python non si distinguono
  json_char='([^"\\]|\\.)'
  separator='(\\[tn"]|[^[:alnum:]_-])'
  subcommands='commit(-tree)?|push|tag|send-pack|reset|rebase|merge|cherry-pick|revert|pull|am|clean'
  subcommands+='|restore|checkout|update-ref|filter-branch|prune|branch|switch|stash|reflog'
  git_write="\"command\"[[:space:]]*:[[:space:]]*\"${json_char}*git${json_char}*${separator}(${subcommands})([^[:alnum:]_-]|\$)"
  shopt -s nocasematch
  if [[ "$input" =~ $git_write ]]; then
    echo "Mímir: Python 3.8+ non trovato, il controllo dei comandi git che scrivono non può partire: comando bloccato. Installa Python o rilancia l'installer di Mímir." >&2
    exit 2
  fi
  exit 0
fi
echo "Mímir: Python 3.8+ non trovato, hook ${script##*/} saltato." >&2
exit 0
