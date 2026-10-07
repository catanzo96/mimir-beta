# Portabilità: GNU, BSD e sh POSIX

Leggi questo file quando lo script deve girare su Linux e macOS, su Alpine/BusyBox o con `/bin/sh`.

## Comandi che cambiano
| Esigenza | GNU (Linux) | BSD (macOS) | Soluzione portabile |
|---|---|---|---|
| Modifica sul posto | `sed -i 's/a/b/' f` | `sed -i '' 's/a/b/' f` | `sed 's/a/b/' f > "$tmp" && mv "$tmp" f`, oppure `sed -i.bak ... f && rm f.bak` (vale su entrambi) |
| Percorso assoluto | `readlink -f p` | `readlink -f` assente nelle versioni più vecchie | `cd "$(dirname "$p")" && pwd -P`; o `realpath` se presente |
| Data relativa | `date -d '1 day ago'` | `date -v-1d` | Calcola in Python o `perl`, oppure richiedi GNU `date` |
| Parsing data | `date -d "$s" +%s` | `date -j -f '%Y-%m-%d' "$s" +%s` | idem |
| Regex estese | `grep -E`, `-P` (PCRE) | `-P` assente | `grep -E` e `sed -E`; evita `-P` |
| `xargs` senza input | `-r` evita l'esecuzione | `-r` non necessario (non esegue) | Controlla prima che ci sia input |
| `find` output | `-printf` | assente | `-exec`, o `-print0` |
| Dimensione/permessi | `stat -c %s` | `stat -f %z` | `wc -c < f`; per i permessi usa `ls -l` o `find -perm` |
| Ordinamento versioni | `sort -V` | non sempre presente | evita |
| `mktemp` con prefisso | `mktemp -t nome.XXXXXX` | semantica diversa | `mktemp "${TMPDIR:-/tmp}/nome.XXXXXX"` |
| `echo` con opzioni | dipende dalla shell | | `printf` |

`sed`, `awk` e `grep` BSD non supportano alcune estensioni GNU (`\+`, `\|` in BRE, `\b`, `\s`): usa `-E` e classi POSIX (`[[:space:]]`).

Strumenti GNU su macOS (Homebrew) si chiamano `gsed`, `gdate`, `greadlink`: non dare per scontato che ci siano. Se li usi, rilevali all'avvio e fallisci con un messaggio chiaro.

## Bashismi da evitare in sh
`[[ ]]`, `==` in `[ ]`, array, array associativi, `<(...)`, `${var,,}`, `${var//a/b}` (alcune shell), `source` (usa `.`), `$'...'`, `function f {`, `local` (non POSIX, ma accettato da dash e ash), `set -o pipefail`, `echo -e`, `read -a`, `&>`, `+=`, `$RANDOM`, `$BASH_SOURCE`, `{1..5}`.

Sostituzioni: `case` al posto di `[[ =~ ]]` per i pattern semplici; `printf` per `echo -e`; `command -v` al posto di `which` e `type -P`; `"$@"` al posto degli array.

## Come provare
- `dash script.sh` e, se c'è, `busybox sh script.sh` rivelano i bashismi.
- Shellcheck con `-s sh` (o `# shellcheck shell=sh`) segnala i costrutti non POSIX.
- CI su più sistemi se la portabilità è un requisito reale. Se non lo è, dichiara nell'help: "richiede Bash 4+ e GNU coreutils".
