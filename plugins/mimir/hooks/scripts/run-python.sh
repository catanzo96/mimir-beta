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

# La cartella reale, senza link; vuota se non esiste o se l'argomento è vuoto (cd "" in alcuni bash resta
# nella cartella corrente, e HOME vuota diventerebbe la cwd). Solo dentro $( ): il cd cambierebbe la cwd,
# e un subshell in più costa un fork, caro in Git Bash.
physical_dir() { [[ -n "$1" ]] && cd -P -- "$1" 2>/dev/null && pwd -P; }

# Un interprete in una cartella che la sandbox può scrivere lo può piantare un comando nella sandbox, e
# l'hook gira fuori: si scarta. Sono il progetto (.venv/bin attivato, node_modules/.bin, .), le cartelle
# di allowWrite in sandbox.settings.json (un test le tiene allineate) e le temporanee della sandbox
# (l'hook non vede il suo TMPDIR, /tmp/claude-<uid>). Le cartelle aggiunte nel settings.json dell'utente
# non sono coperte. Ogni cartella vale sia come è scritta sia senza link (cd -P).
# Un progetto uguale alla home o a un suo antenato (/home, /) non si scarta: conterrebbe ogni interprete
# installato nella home, e tutti i comandi git che scrivono resterebbero bloccati.
roots=()
add_root() {
  [[ "$1" == /* ]] && roots+=("${1%/}")
  local physical
  physical="$(physical_dir "$1")"
  [[ -n "$physical" ]] && roots+=("$physical")
}
in_roots() {
  local root
  for root in "${roots[@]}"; do
    [[ -n "$root" && ( "$1" == "$root" || "$1" == "$root"/* ) ]] && return 0
  done
  return 1
}

project_dir="${CLAUDE_PROJECT_DIR:-}"
[[ -n "$(physical_dir "$project_dir")" ]] || project_dir="$PWD"
project="$(physical_dir "$project_dir")"
home="$(physical_dir "${HOME:-}")"
if [[ "$project" != / && ! ( -n "$home" && ( "$home" == "$project" || "$home" == "$project"/* ) ) ]]; then
  add_root "$project_dir"
fi
for sandbox_dir in .m2/repository .m2/wrapper .npm/_cacache .npm/_logs .cache/yarn .local/share/pnpm \
    .gradle/caches .gradle/wrapper; do
  [[ -n "$home" ]] && add_root "$home/$sandbox_dir"
done
add_root "${TMPDIR:-}"
add_root /tmp/claude
add_root "/tmp/claude-$UID"

# ogni voce del PATH, non solo la prima: con un venv attivato python3 di sistema viene dopo quello del venv
excluded=()
for candidate in python3 python "py -3"; do
  read -r -a cmd <<< "$candidate"
  # l'elenco arriva sul descrittore 3: lo stdin resta l'input dell'hook, per lo script lanciato con exec
  while IFS= read -r found <&3; do
    dir="$(physical_dir "${found%/*}")"
    # una voce relativa del PATH (., bin, vuota) segue i cd di Claude: scartata ovunque; conta sia dove il
    # PATH trova l'interprete sia dove porta un link di cartella, e si lancia il percorso reale: Python cerca
    # pyvenv.cfg accanto al percorso con cui parte
    if [[ "$found" != /* || -z "$dir" ]] || in_roots "${found%/*}" || in_roots "$dir"; then
      excluded+=("$found")
      continue
    fi
    # il percorso reale al posto del nome, con gli stessi argomenti (py -3); niente ${cmd[@]:1}, che vuoto con
    # set -u fallisce nel bash 3.2 di macOS
    run=("${cmd[@]}")
    run[0]="$dir/${found##*/}"
    # -I anche nel controllo della versione: senza, PYTHONPATH, le altre variabili PYTHON* e lo user site
    # caricano codice all'avvio, prima dello script
    run+=(-I)
    if "${run[@]}" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' </dev/null >/dev/null 2>&1; then
      exec "${run[@]}" "$script" 3<&-
    fi
  done 3< <(type -aP -- "${cmd[0]}")
done

if (( ${#excluded[@]} )); then
  # i percorsi arrivano a Claude nel motivo del blocco: al massimo 5, senza caratteri non stampabili
  list=""
  for found in "${excluded[@]:0:5}"; do
    list+="${list:+, }${found//[^[:print:]]/?}"
  done
  missing="nessun Python 3.8+ utilizzabile (scartati perché dentro il progetto, in una cartella scrivibile dalla sandbox o da una voce relativa del PATH: $list)"
  remedy="Metti nel PATH un Python 3.8+ fuori da queste cartelle."
else
  missing="Python 3.8+ non trovato"
  remedy="Installa Python o rilancia l'installer di Mímir."
fi

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
    echo "Mímir: $missing, il controllo dei comandi git che scrivono non può partire: comando bloccato. $remedy" >&2
    exit 2
  fi
  exit 0
fi
echo "Mímir: $missing, hook ${script##*/} saltato." >&2
exit 0
