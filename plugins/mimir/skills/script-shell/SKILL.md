---
name: script-shell
description: Script Bash e sh robusti e portabili. Usala quando scrivi o modifichi script shell, hook, wrapper di build o CI, o in progetti con file .sh, Makefile o bin/
---

# Script shell

Si applica insieme a `clean-code` (nomi, errori, sicurezza) e, per il commit degli script, a `commit`. Le convenzioni del progetto prevalgono: interprete, stile, shellcheck già configurato, eventuale `.editorconfig`.

## Prima di tutto: quale shell
Leggi lo shebang dello script esistente e l'ambiente dove gira (CI, container Alpine, macOS, hook).
- `#!/usr/bin/env bash` quando puoi contare su Bash (array, `[[ ]]`, `local`, `pipefail`). Su macOS `/bin/bash` è la 3.2 del 2007: niente array associativi, `mapfile`, `${var,,}`; se lo script deve girare lì, evitali o dichiara il requisito.
- `#!/bin/sh` solo se serve la portabilità vera (Alpine/BusyBox con `ash`, Debian con `dash`). Allora niente bashismi: `[[ ]]`, array, `<(...)`, `local` dove non garantito, `source`, `==` in `[ ]`, `$'...'`. Vedi `references/portabilita.md`.
- Se la logica richiede strutture dati, parsing di JSON, date o espressioni regolari non banali, o supera circa 100-150 righe: vedi "Quando passare a Python".

## Intestazione
```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'   # solo se lavori su liste di nomi con spazi; altrimenti lascia il default

readonly NOME_SCRIPT="${0##*/}"
```
- `set -e` non è una rete: non scatta in `if`, `&&`/`||`, né dentro funzioni chiamate in quei contesti, e `local x=$(cmd)` ignora l'errore di `cmd` (dichiara `local x` e assegna a parte). Controlla gli esiti che contano in modo esplicito.
- `-u` fa fallire le variabili non definite: per quelle opzionali usa `${VAR:-}` o `${VAR:-default}`. Con Bash più vecchi di 4.4 `"${array[@]}"` vuoto fallisce.
- `pipefail` fa propagare l'errore in una pipeline. Attenzione a `grep -q` e `head` che chiudono la pipe prima e producono SIGPIPE: con `pipefail` la pipeline risulta fallita.
- Nessun `set -x` nei file versionati: stampa i segreti. Per il debug usa `bash -x script` o una variabile `DEBUG`.

## Quoting e variabili
- Quota sempre le espansioni: `"$var"`, `"$(cmd)"`, `"${arr[@]}"`. Senza virgolette: word splitting e globbing sui nomi file.
- `[[ ]]` in Bash (niente splitting, supporta `=~` e `&&`); in `sh` `[ ]` con variabili quotate.
- Usa array per costruire comandi, non stringhe: 
  ```bash
  args=(--verbose --output "$dir")
  [[ -n "${filtro:-}" ]] && args+=(--filter "$filtro")
  comando "${args[@]}"
  ```
- `local` per le variabili delle funzioni; nomi in minuscolo per le locali, maiuscolo per costanti e variabili d'ambiente. `readonly` per le costanti.
- `$(...)` e non i backtick. `printf '%s\n' "$x"` e non `echo` quando il contenuto è variabile (`echo -n`, `-e` e backslash cambiano tra shell).
- Parametri: `${var:?messaggio}` per pretenderli, `${var%suffisso}`, `${var##*/}` al posto di `basename` e `sed` per le cose semplici.
- Un file con nomi arbitrari si scorre con `find ... -print0 | while IFS= read -r -d '' f` o `for f in ./*` (il `./` evita che un nome inizi con `-`). Mai `for f in $(ls)`.
- `read -r` sempre (senza `-r` i backslash vengono mangiati). Una `while read` dopo una pipe gira in una subshell: le variabili assegnate lì non sopravvivono (usa redirezione `< <(...)` in Bash).

## Pulizia e file temporanei
```bash
tmp="$(mktemp -d)"
cleanup() { rm -rf -- "${tmp:?}"; }
trap cleanup EXIT
```
- `mktemp` e non `/tmp/nome-fisso`: evita collisioni e attacchi sui file prevedibili. Su macOS `mktemp -d` va bene; `mktemp -t prefisso` ha semantica diversa tra GNU e BSD.
- `trap ... EXIT` copre l'uscita normale, gli errori con `set -e` e la maggior parte dei segnali gestiti. Aggiungi `trap 'exit 130' INT` e `trap 'exit 143' TERM` se serve rilasciare risorse su Ctrl-C.
- Se lo script scrive un file di destinazione, scrivi su un temporaneo nella **stessa directory** e poi `mv`: il rename è atomico, un file parziale non resta mai.
- Un solo `trap` per segnale: un secondo lo sostituisce. Se servono più azioni, una funzione che le richiama.

## Prerequisiti, argomenti, help
- Controlla gli strumenti all'inizio e fallisci con un messaggio chiaro:
  ```bash
  richiedi() { command -v "$1" >/dev/null 2>&1 || { echo "manca: $1" >&2; exit 127; }; }
  richiedi jq; richiedi curl
  ```
- Controlla anche file e directory attesi e le variabili d'ambiente obbligatorie, prima di iniziare a modificare qualcosa.
- Argomenti: `getopts` per opzioni corte, un `while`/`case` su `$1` per quelle lunghe. Gestisci `-h|--help` (stampa su stdout, esce con 0), un'opzione sconosciuta (messaggio e uscita 2) e `--` per terminare le opzioni. Non iniziare con un parser a mano se bastano due argomenti posizionali.
- Valida gli argomenti ai confini: percorsi, numeri e nomi attesi, con `case` o `[[ =~ ]]`. Nessun argomento diventa mai codice.
- Evita stati interattivi: se serve conferma, offri `--yes` o `--dry-run`, e non chiedere nulla quando stdin non è un terminale (`[[ -t 0 ]]`).

## Output, log e codici di uscita
- Risultati su **stdout**, messaggi e log su **stderr**: lo script resta componibile in pipe.
  ```bash
  log() { printf '%s %s\n' "$(date +%H:%M:%S)" "$*" >&2; }
  die() { log "errore: $*"; exit 1; }
  ```
- Mai segreti nei log, negli argomenti (visibili in `ps`) o nei `set -x`: passali da variabile d'ambiente, file con permessi `600` o stdin.
- Codici di uscita: `0` ok, `1` errore generico, `2` uso errato, `127` comando mancante, `130` interrotto. Documenta quelli che chi chiama deve distinguere.
- Colori solo se stdout/stderr è un terminale e `NO_COLOR` non è impostato.

## Idempotenza
Lo script deve poter essere rilanciato dopo un fallimento senza danni.
- `mkdir -p`, `ln -sfn`, `rm -f`, "crea se manca" invece di "crea".
- Controlla lo stato prima di agire (`[[ -f ... ]] || scarica`), e fai il passo irreversibile per ultimo.
- Per le azioni distruttive: `--dry-run` che stampa cosa farebbe, e conferma esplicita se interattivo.
- Un lock (`mkdir "$lockdir"` è atomico; `flock` se disponibile) per gli script che non devono girare in parallelo.

## Sicurezza
- **Mai `eval`** su dati non tuoi, e quasi mai in generale: array e `printf %q` risolvono la maggior parte dei casi. Anche `bash -c "$stringa"`, `sh -c`, `source` di file non fidati e `xargs sh -c '... {}'` con nomi in ingresso sono esecuzione di codice.
- **`rm` con variabili che possono essere vuote**: `rm -rf "$dir/"` con `dir` vuoto cancella `/`. Usa `"${dir:?}"`, verifica che il percorso stia sotto la radice attesa, e `rm -rf -- "$x"` per i nomi che iniziano con `-`.
- Input non fidato (nomi di file, output di altri comandi, variabili di CI controllate da terzi, titoli di PR o branch): quotalo, mettilo dopo `--`, non interpolarlo in comandi SQL, in `curl` con URL costruiti a mano o in comandi `ssh`.
- `curl | sh` e scaricare ed eseguire senza verificare checksum o firma: no. Scarica, verifica, poi esegui.
- Permessi: `umask 077` o `install -m 600` per i file con segreti; il file dello script non scrivibile da altri.
- `PATH` esplicito negli script che girano con privilegi o da cron; percorsi assoluti per i comandi critici.
- Niente `sudo` dentro lo script se si può evitare: chiedilo a chi lo lancia.

## Differenze GNU/BSD (Linux e macOS)
Dettaglio e alternative portabili in `references/portabilita.md` (leggilo quando lo script deve girare su più sistemi). Le trappole principali: `sed -i` (BSD vuole un argomento suffisso), `date -d` (BSD usa `-v`/`-j -f`), `readlink -f` (assente sui BSD più vecchi), `grep -P`, `xargs -r`, `stat`, `cp -a`, `find -printf`, `sort -V`. Regola pratica: se puoi, usa `perl -pi -e` o `python3` per ciò che non è portabile, oppure dichiara "richiede GNU coreutils" nell'help.

## Quando passare a Python
Passa a Python (o a un altro linguaggio già nel progetto) quando:
- elabori JSON, YAML, CSV, XML o date con fusi orari e non basta un `jq` semplice;
- servono strutture dati (mappe annidate, liste di oggetti) o logica con molti rami;
- il Bash supera il centinaio di righe, o devi testarlo seriamente;
- gestisci errori con tentativi, parallelismo, API HTTP complesse;
- lo script deve girare su Windows.

Il Bash resta la scelta giusta per orchestrare comandi, pipeline di processi, wrapper e hook brevi. Usa solo la libreria standard di Python.

## sh POSIX
Stesse regole di sicurezza e struttura, ma: niente array (usa `"$@"` con `set --`), `[ ]` e `case`, `local` non standard (ma accettato da dash e ash: verifica sul target), niente `pipefail` (in alcune shell POSIX recenti c'è, non contarci), `printf` e non `echo`. Prova con `dash` e, se serve, `busybox sh`.

## PowerShell (nota breve)
Per Windows: `Set-StrictMode -Version Latest` e `$ErrorActionPreference = 'Stop'` sono l'analogo di `set -eu`. Passa gli argomenti come array, non concatenare stringhe, usa `try/finally` per la pulizia, `[CmdletBinding()]` e `param()` per gli argomenti. Attenzione: gli errori dei programmi esterni si controllano con `$LASTEXITCODE`. Analisi statica: `PSScriptAnalyzer`, se già presente.
- PowerShell 5.1 altera le virgolette negli argomenti passati ai programmi nativi: niente JSON inline come argomento, scrivi un file e passa il percorso.
- Dopo un'installazione con winget il PATH della sessione è vecchio: rileggilo dal registro (`Machine` e `User`) o chiedi di riaprire il terminale.
- File scritti per altri programmi: UTF-8 senza BOM (`[IO.File]::WriteAllText(path, text, [Text.UTF8Encoding]::new($false))`), perché `Set-Content` e `Out-File` di PowerShell 5.1 aggiungono il BOM o usano un'altra codifica.
- L'output della 5.1 verso un processo che lo legge usa la code page OEM: chi lo legge decodifica con tolleranza e non confronta i caratteri accentati byte per byte.
- `ConvertTo-Json` della 5.1 formatta in modo diverso da pwsh (spazi dopo i due punti): confronta il JSON come dato, non come stringa.
- In un ambiente costruito da zero (`env=` di un test) mancano variabili come `OS`, `SystemRoot` e `ComSpec`: passale esplicitamente. Nello stesso ambiente `[Environment]::GetFolderPath(...)` della 5.1 può restituire una stringa vuota: per le cartelle dell'utente leggi la variabile (`$env:LOCALAPPDATA`) e gestisci il valore vuoto, invece di passarlo a `Join-Path`.

## Verifica
- `bash -n script.sh` controlla la sintassi (`dash -n` per gli script sh).
- `shellcheck script.sh` se è installato o configurato nel progetto (`.shellcheckrc`, CI): correggi gli avvisi o motiva con `# shellcheck disable=SCxxxx` e il perché. Se non è disponibile, dichiaralo nel resoconto: il controllo non è stato fatto.
- Prova lo script su un caso che funziona e su uno che deve fallire (argomento mancante, file inesistente, variabile vuota), controllando il codice di uscita (`echo $?`). Con `--dry-run` prima di qualsiasi azione distruttiva.
- Se è portabile, provalo sulle shell target (`dash`, `bash`, e macOS se è un requisito).
- Controlla che sia eseguibile (`chmod +x`, bit tracciato da git) e che le fini riga siano LF.
- Nel resoconto: cosa hai lanciato, con quale esito, e cosa non hai potuto provare.
