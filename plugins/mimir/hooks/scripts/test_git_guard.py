#!/usr/bin/env python3
"""Test dell'hook git-guard: casi da bloccare (contenuto o forma) e casi da lasciare alle regole ask.

Uso: python3 test_git_guard.py [percorso dello script da provare]
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "git-guard.py")

# come il timeout dell'hook in hooks.json: oltre, Claude Code lascia passare il comando
HOOK_TIMEOUT = 10

TMP = tempfile.mkdtemp(prefix="claude-hook-test-")
CLEAN_FILE = os.path.join(TMP, "msg-pulito.txt")
DIRTY_FILE = os.path.join(TMP, "msg-attribuito.txt")
with open(CLEAN_FILE, "w", encoding="utf-8") as fh:
    fh.write("feat(core): aggiungi una skill\n\nCorpo breve.\n")
with open(DIRTY_FILE, "w", encoding="utf-8") as fh:
    fh.write("feat: aggiungi una skill\n\nCo-Authored-By: GitHub Copilot <copilot@github.com>\n")
# Esche nella cwd con i nomi letterali che la shell invece espanderebbe: l'hook non deve leggerle
for decoy in ("$TMPDIR", "~"):
    os.makedirs(os.path.join(TMP, decoy), exist_ok=True)
    shutil.copyfile(CLEAN_FILE, os.path.join(TMP, decoy, "msg-pulito.txt"))
if os.name != "nt":  # su Windows * non può stare nel nome di un file
    shutil.copyfile(CLEAN_FILE, os.path.join(TMP, "msg-pul*.txt"))
# Un messaggio più lungo di quanto l'hook legge, con l'attribuzione in fondo
LONG_FILE = os.path.join(TMP, "msg-lungo.txt")
with open(LONG_FILE, "w", encoding="utf-8") as fh:
    fh.write("feat: x\n\n" + "y\n" * 60000 + "Co-Authored-By: Claude <noreply@anthropic.com>\n")
# Percorso Windows relativo alla cwd del test: su POSIX è un file con il backslash nel nome
WIN_REL = "attr\\msg.txt"
WIN_FILE = os.path.join(TMP, "attr", "msg.txt") if os.name == "nt" else os.path.join(TMP, WIN_REL)
os.makedirs(os.path.dirname(WIN_FILE), exist_ok=True)
shutil.copyfile(DIRTY_FILE, WIN_FILE)

LONG = "feat(core): " + "x" * 70
HEREDOC = "git commit -F - <<'EOF'\n{}\nEOF"

# Bloccati per il contenuto: attribuzioni, righe oltre 72, force push (exit 2)
CONTENT_BLOCK = {
    "Generated with Claude Code": 'git commit -m "feat: x" -m "🤖 Generated with [Claude Code](https://claude.com/claude-code)"',
    # con le barre: un percorso Windows con i backslash e senza virgolette bash lo rompe (anche Git Bash)
    "attribuzione in un file -F": f"git commit -F {Path(DIRTY_FILE).as_posix()}",
    # fail-closed: un messaggio che l'hook non può leggere non si può controllare
    "file -F inesistente": f"git commit -F {Path(TMP, 'manca.txt').as_posix()}",
    "--file= inesistente": f"git commit --file={Path(TMP, 'manca.txt').as_posix()}",
    "file -F che è una cartella": f"git commit -F {Path(TMP).as_posix()}",
    # la shell espande, l'hook no: una cartella letterale "$TMPDIR" o "~" nella cwd farebbe leggere un altro file
    "-F con una variabile": "git commit -F $TMPDIR/msg-pulito.txt",
    "-F con ~": "git commit -F ~/msg-pulito.txt",
    "-F con un glob": f"git commit -F {Path(TMP).as_posix()}/msg-pul*.txt",
    "attribuzione oltre il limite di lettura": f"git commit -F {Path(LONG_FILE).as_posix()}",
    "intestazione oltre 72": f'git commit -m "{LONG}"',
    "intestazione accentata di 73 caratteri": 'git commit -m "feat: ' + "è" * 67 + '"',
    "opzione globale -c con intestazione lunga": f'git -c user.name=x commit -m "{LONG}"',
    "force push -f": "git push -f",
    "-f dopo il remote": "git push origin -f",
    "opzioni corte raggruppate": "git push -uf origin feature",
    "--force-with-lease": "git push --force-with-lease origin main",
    "--force-if-includes": "git push --force-if-includes",
    "refspec +ref": "git push origin +main",
    "--mirror": "git push --mirror origin",
    "abbreviazione --force-w": "git push --force-w origin main",
    "-C prima di push --force": "git -C . push --force",
    "force push dopo un commit": 'git commit -m "feat: x" && git push -f',
    "variabile d'ambiente davanti": "FOO=1 git push -f",
    "-C con percorso tra virgolette": 'git -C "my dir" push --force',
    "continuazione di riga": "git push origin main \\\n  --force",
    "tra parentesi": "(git push -f)",
    "sostituzione $( )": "echo $(git push -f)",
    "sostituzione con backtick": "echo `git push -f`",
    "dentro sh -c": "sh -c 'git push -f'",
    "percorso assoluto": "/usr/bin/git push --force",
    "dopo un heredoc che non c'entra": "cat <<'EOF'\nnota\nEOF\ngit push -f",
    "dopo una here-string <<<": "cat <<<parola\ngit push -f",
    "dopo uno shift aritmetico": "echo $((1<<2))\ngit push -f",
    "dentro pwsh -c": "pwsh -c 'git push -f'",
    "dentro powershell -Command con opzioni": 'powershell -NoProfile -ExecutionPolicy Bypass -Command "git push -f"',
    "dentro bash -o pipefail -c": "bash -o pipefail -c 'git push -f'",
    "sostituzione tra virgolette in un'assegnazione": 'X="$(git push -f)"',
}

# Bloccati per la forma: commit, push e tag che la regola ask a prefisso non riconoscerebbe (exit 2)
FORM_BLOCK = {
    "-C prima di commit": 'git -C . commit -m "feat: x"',
    "commit-tree, senza regola ask": 'git commit-tree abc -m "feat: x"',
    "send-pack, senza regola ask": "git send-pack origin main",
    "push dopo un commit": 'git commit -m "feat: x" && git push',
    "git add e commit nello stesso comando": 'git add a.txt && git commit -m "feat: x"',
    "-C con percorso tra virgolette": 'git -C "my dir" push',
    "-c con valore tra virgolette": "git -c user.name='A B' commit -m \"feat: x\"",
    "--no-pager prima di commit": 'git --no-pager commit -m "feat: x"',
    "commit dentro un gruppo { }": '{ git commit -m "feat: x"; }',
    "commit dopo then": 'if true; then git commit -m "feat: x"; fi',
    "variabile d'ambiente davanti": "FOO=1 git push",
    "env": "env GIT_TRACE=1 git push",
    "sudo": "sudo git push",
    "command": 'command git commit -m "feat: x"',
    "percorso assoluto": "/usr/bin/git push origin main",
    "sh -c": "sh -c 'git push origin main'",
    "bash -lc": 'bash -lc "git commit -m \\"feat: x\\""',
    "bash -c --": "bash -c -- 'git push origin main'",
    "eval": 'eval "git push"',
    "xargs": "echo main | xargs git push origin",
    "su -c": "su -c 'git push origin main' utente",
    "bash <<< con git push": "bash <<< 'git push'",
    "echo | sh con git push": "echo 'git push' | sh",
    "messaggio su più righe": 'git commit -m "feat: x\n\nCorpo breve."',
    "push nel corpo di bash <<EOF": "bash <<'EOF'\ngit push\nEOF",
    "commit citato nel corpo di un heredoc": "python3 - <<'X'\nnota = 'dopo `git commit` il trailer'\nX",
    "sostituzione $( ) tra virgolette": 'echo "$(git push)"',
    "backtick tra virgolette": 'echo "`git push`"',
    "redirect 2>&1": "git push 2>&1",
    "redirect attaccato a commit": 'git commit>/dev/null -m "feat: x"',
    "variabile tra git e il sottocomando": "git${IFS}push",
    "git in una variabile": '"$GIT" push origin main',
    "sottocomando in una variabile": "git $SUB origin main",
    "sottocomando con valore di default": "git ${X:-push}",
    "echo git push": "echo git push",
    "virgolette sbilanciate": 'git push "origin',
    "due spazi dopo git": "git  push origin main",
    # i sottocomandi distruttivi con una regola ask: stessa forma semplice di commit, push e tag
    "-C prima di reset": "git -C . reset --hard",
    "rebase dopo cd": "cd x && git rebase main",
    "variabile davanti a merge": "FOO=1 git merge x",
    "cherry-pick dopo un fetch": "git fetch && git cherry-pick abc",
    "revert dentro sh -c": "sh -c 'git revert HEAD'",
    "--no-pager prima di pull": "git --no-pager pull",
    "am in una pipe": "cat p.patch | git am",
    "clean dopo ;": "true; git clean -fdx",
    "restore con redirect": "git restore . 2>&1",
    "checkout dopo status": "git status && git checkout main",
    "update-ref con -c": "git -c x=y update-ref -d refs/heads/x",
    "filter-branch in eval": 'eval "git filter-branch --force"',
    "prune con env": "env X=1 git prune",
    "reset nel corpo di bash <<EOF": "bash <<'EOF'\ngit reset --hard\nEOF",
    "reset in una variabile": '"$GIT" reset --hard',
    "reset in una variabile dopo sudo -u": 'sudo -u root "$GIT" reset --hard',
    # branch, switch, stash e reflog: la regola ask riconosce l'opzione distruttiva solo subito dopo
    "branch -D dopo -q": "git branch -q -D x",
    "branch -fD raggruppato": "git branch -fD x",
    "branch --delete dopo cd": "cd x && git branch --delete y",
    "branch --del abbreviato": "git branch --del x",
    "switch --force dopo -q": "git switch -q --force main",
    "switch -C dopo un fetch": "git fetch && git switch -C x",
    "switch --discard abbreviato": "git switch --discard main",
    "stash drop con -C": "git -C . stash drop",
    "stash clear dopo ;": "true; git stash clear",
    "reflog expire con env": "env X=1 git reflog expire --all",
    "reflog delete dentro bash -c": "bash -c 'git reflog delete HEAD@{1}'",
    "variabile come comando dopo un'assegnazione": 'FOO=1 "$GIT" reset --hard',
    # git 2.43 accetta --attr-source con il valore separato
    "--attr-source prima di reset": "git --attr-source HEAD reset --hard",
    "brace expansion del sottocomando": "git {reset,--hard}",
    "brace expansion di git": "{git,reset} --hard",
    # variabile come git dopo parole riservate, wrapper e redirect
    "variabile come git dopo then": 'if true; then "$GIT" push; fi',
    "variabile come git dopo do": 'for r in a b; do "$GIT" push $r; done',
    "variabile come git in un gruppo": '{ "$GIT" push; }',
    "variabile come git dopo !": '! "$GIT" push',
    "variabile come git dopo timeout": 'timeout 10 "$GIT" push',
    "variabile come git dopo un redirect": '>/dev/null "$GIT" push',
    # variabile come git seguita da opzioni globali
    "variabile come git con -C": '"$GIT" -C repo reset --hard',
    "variabile come git con --no-pager": "$GIT --no-pager branch -D x",
    # espansioni che portano l'opzione distruttiva nella stessa parola
    "branch -D con $IFS": "git${IFS}branch${IFS}-D${IFS}x",
    "branch -D con $IFS e virgolette": 'git$IFS"branch"$IFS-D$IFS"x"',
    "push con $IFS e virgolette": 'git$IFS"push"',
    "stash drop con brace expansion": "{git,stash,drop}",
    "switch --force con brace expansion": "{git,switch,--force,main}",
    "reflog expire con brace expansion": "{git,reflog,expire,--all}",
    # riga continuata con \ nel corpo di un heredoc eseguito
    "push continuato nel corpo di bash <<EOF": "bash <<EOF\ngit \\\npush origin main\nEOF",
    # falsi positivi accettati: un comando in una variabile seguito da clean non si distingue da git
    "make in una variabile e clean": "$MAKE clean",
    # -committerdate contiene una d: senza = sembra un'opzione distruttiva raggruppata
    "branch --sort senza =": "git branch --sort -committerdate",
}

# Bloccati perché gli argomenti di git commit non sono tra le forme ammesse (elenco chiuso): exit 2
COMMIT_FORM_BLOCK = {
    # git accetta valori attaccati e abbreviazioni delle opzioni lunghe
    "-F attaccato al file": "git commit -Fmsg-pulito.txt",
    "-m attaccato al messaggio": 'git commit -m"feat: x"',
    "abbreviazione --fil=": "git commit --fil=msg-pulito.txt",
    "abbreviazione --mess=": 'git commit --mess="feat: x"',
    "-am": 'git commit -am "feat: x"',
    # opzioni che cambiano autore, contenuto o messaggio senza passare dal controllo
    "--author con un'AI": 'git commit -m "feat: x" --author="Claude <noreply@anthropic.com>"',
    "--trailer pulito": 'git commit -m "feat: x" --trailer "Signed-off-by: Mario <m@x.it>"',
    "-C riusa un messaggio": "git commit -C HEAD",
    "-c riusa un messaggio": "git commit -c HEAD",
    "--fixup": "git commit --fixup=HEAD",
    "--squash": "git commit --squash=HEAD",
    "--template": "git commit --template=msg-pulito.txt",
    "--no-verify": 'git commit --no-verify -m "feat: x"',
    "-a": 'git commit -a -m "feat: x"',
    "-s": 'git commit -s -m "feat: x"',
    "-q": 'git commit -q -m "feat: x"',
    "--dry-run": 'git commit --dry-run -m "feat: x"',
    "file posizionale": 'git commit -m "feat: x" a.txt',
    "--": 'git commit -m "feat: x" -- a.txt',
    "senza messaggio": "git commit",
    "--no-edit senza --amend": "git commit --no-edit",
    # combinazioni che git rifiuta o risolve in modo diverso dall'hook
    "-m insieme a -F": 'git commit -m "feat: x" -F msg-pulito.txt',
    "due -F: vince l'ultimo": "git commit -F msg-pulito.txt -F msg-pulito.txt",
    # messaggi che la shell espande o che l'hook non vede
    "-m con una variabile": 'git commit -m "feat: $X"',
    "-m con un backtick": 'git commit -m "feat: `id`"',
    # la shell espande graffe, caratteri jolly e ~: git riceverebbe un altro messaggio o altri file
    "-m con le graffe": "git commit --message=Co-Authored-By:\\ Cl{au,x}de",
    "-m con un glob": "git commit -m *",
    "-m con ~ iniziale": "git commit -m ~/x",
    "-m con [ ]: falso positivo accettato": 'git commit -m "[skip ci] feat: x"',
    "-m senza valore": "git commit -m",
    "--amend da solo": "git commit --amend",
    "messaggio con $(cat <<EOF)": "git commit -m \"$(cat <<'EOF'\nfeat: x\n\nCorpo breve.\nEOF\n)\"",
    "-F - da stdin": "git commit -F - < msg-pulito.txt",
    "-F con redirect": "git commit -F msg-pulito.txt > out.txt",
}
COMMIT_FORM_REASON = "forme ammesse"

# Bloccati con un motivo preciso: (comando, testo che deve comparire nel motivo)
REASON_BLOCK = {
    # il messaggio si controlla tutto, non solo l'ultimo -m
    "attribuzione in un -m che non è l'ultimo": (
        'git commit -m "feat: x" -m "Co-Authored-By: Claude <noreply@anthropic.com>" -m "Corpo breve."',
        "attribuzione"),
    "riga del corpo oltre 72 in un -m che non è l'ultimo": (
        'git commit -m "feat: x" -m "' + "y" * 80 + '" -m "Corpo breve."', "riga 3 di 80"),
    # senza editor git pulisce solo gli spazi e tiene le righe con # (--cleanup=default in git-commit(1))
    "riga del corpo oltre 72 che inizia con #": ('git commit -m "feat: x" -m "#' + "y" * 80 + '"', "riga 3 di 81"),
    "intestazione oltre 72 con --message=": (f'git commit --message="{LONG}"', "intestazione di 82"),
    # il motivo non deve mostrare il segnaposto interno degli heredoc
    "heredoc come messaggio": (HEREDOC.format("feat: x\n\nCorpo breve."), "heredoc"),
    "redirect dopo il messaggio": ('git commit -m "feat: x" 2>&1', "redirect"),
    "--amend ripetuto": ('git commit --amend --amend -m "feat: x"', "--amend è ripetuto"),
    "branch -D dopo -q: indica come riscriverlo": ("git branch -q -D x", "Per branch, switch, stash e reflog"),
}

# Lasciati alle regole ask di settings (forma semplice) o senza nulla da controllare: exit 0, nessun output
ALLOW = {
    "push semplice": "git push origin main",
    "push -u": "git push -u origin feature",
    "push --dry-run": "git push --dry-run",
    "push -o con valore che inizia con +": "git push -o +x origin main",
    "tag leggero": "git tag v1",
    "tag annotato": 'git tag -a v1 -m "rilascio"',
    "tag cancellato": "git tag -d v1",
    "commit con -m": 'git commit -m "feat: x"',
    "commit con -m ripetuti": 'git commit -m "feat: x" -m "Corpo breve."',
    "commit con -F su un file pulito": f"git commit -F {Path(CLEAN_FILE).as_posix()}",
    "commit con -F relativo alla cwd": "git commit -F msg-pulito.txt",
    "argomento AI": 'git commit -m "feat(api): integra l\'API di Anthropic"',
    "messaggio che descrive l'hook": 'git commit -m "fix(core): l\'hook ignora i nomi di file come CLAUDE.md"',
    "commit che cita un force push nel messaggio": 'git commit -m "docs: git push --force resta vietato"',
    "intestazione di 72 esatti": 'git commit -m "' + "feat: " + "z" * 66 + '"',
    # 72 caratteri ma 138 byte: la lunghezza si conta sul testo decodificato in UTF-8
    "intestazione accentata di 72 caratteri": 'git commit -m "feat: ' + "è" * 66 + '"',
    "amend senza messaggio": "git commit --amend --no-edit",
    "commit con --message=": 'git commit --message="feat: x"',
    "commit con --file=": "git commit --file=msg-pulito.txt",
    "amend con -m": 'git commit --amend -m "feat: x"',
    "amend con -F": "git commit --amend -F msg-pulito.txt",
    # git prende il token dopo -m anche se inizia con -: il messaggio è "--amend"
    "-m con valore che inizia con -": "git commit -m --amend",
    "tag senza argomenti": "git tag",
    "tag -l": "git tag -l 'v*'",
    "tag --list in una pipe": "git tag --list | grep v1",
    "fetch --tags": "git fetch --tags",
    "log con push nel filtro": "git log --grep push",
    "push citato tra virgolette": 'echo "git push --force"',
    "attribuzione in un comando che non è un commit": 'echo "Co-Authored-By: Claude"',
    "docker tag": "docker tag img:1 img:latest",
    "status": "git status",
    "cancelletto dentro una parola": "git log --grep issue#12",
    "git come argomento": "cd git && make",
    # sottocomandi distruttivi in forma semplice: chiede conferma la regola ask
    "reset": "git reset --hard HEAD~1",
    "rebase": "git rebase main",
    "merge": "git merge feature",
    "cherry-pick": "git cherry-pick abc",
    "revert": "git revert HEAD",
    "pull": "git pull --rebase",
    "am": "git am p.patch",
    "clean": "git clean -fdx",
    "restore": "git restore .",
    "checkout": "git checkout main",
    "update-ref": "git update-ref -d refs/heads/x",
    "filter-branch": "git filter-branch --force",
    "prune": "git prune",
    "branch -D": "git branch -D x",
    "branch -d": "git branch -d x",
    "branch --delete": "git branch --delete x",
    "branch -M": "git branch -M x",
    "branch -f": "git branch -f x main",
    "branch --force": "git branch --force x main",
    "switch -f": "git switch -f main",
    "switch --force": "git switch --force main",
    "switch --discard-changes": "git switch --discard-changes main",
    "switch -C": "git switch -C x",
    "stash drop": "git stash drop",
    "stash clear": "git stash clear",
    "reflog expire": "git reflog expire --expire=now --all",
    "reflog delete": "git reflog delete HEAD@{1}",
    # letture e forme non distruttive: libere anche in un comando composto
    "branch in un comando composto": "git branch && git status",
    "branch -a in una pipe": "git branch -a | grep x",
    "branch -m, rinomina senza forzare": "git -C . branch -m nuovo",
    "stash list": "git stash list && git log",
    "stash e stash pop": "git stash && git stash pop",
    "reflog in una pipe": "git reflog | head",
    "switch con -C globale": "git -C . switch main",
    "switch -c dopo un fetch": "git fetch && git switch -c x",
    "merge-base non è merge": "git merge-base main HEAD && git log",
    # parole come clean o branch dopo una variabile, in comandi che non sono git o sono letture
    "make con una variabile e clean": "make -C $DIR clean",
    "mvn con una variabile e clean": "mvn -f $POM clean verify",
    "stash list con -C e una variabile": 'git -C "$REPO" stash list',
    "branch -a con -C e una variabile": "git -C $DIR branch -a",
    # uno script lanciato con bash non si vede, ma git branch -a e echo clean non scrivono
    "bash script e branch -a": "bash build.sh && git branch -a",
    "bash script e clean in un altro comando": "bash build.sh; git status; echo clean",
    "git e commit come messaggi": "git commit -m git -m commit",
    # git come argomento di un altro comando, seguito da un percorso
    "grep di git in una cartella": "grep -rn git plugins/mimir/",
    "rg di git in più cartelle": "rg -n git skills/ agents/",
    "apt install git": "apt install -y git libssl-dev:amd64",
    "comando PowerShell con backtick nel tool Bash": "Get-ChildItem -Path C:\\repo `\n  -Filter *.md | Select-Object Name",
}

# comandi del tool PowerShell
PS_CONTENT_BLOCK = {
    "maiuscole con intestazione lunga": f'Git COMMIT -m "{LONG}"',
    "-F con percorso Windows e attribuzione nel file": f"git commit -F {WIN_REL}",
    "here-string con attribuzione": 'git commit -m @"\nfeat: x\n\nCo-Authored-By: Claude <noreply@anthropic.com>\n"@',
    "powershell -Command": 'powershell -Command "git push -f"',
    "git.exe push --FORCE": "git.exe push --FORCE",
    "& 'git' push --force": "& 'git' push --force",
    "git.exe con intestazione lunga": f'git.exe commit -m "{LONG}"',
}
PS_FORM_BLOCK = {
    "git.exe, senza regola ask": "git.exe push origin main",
    "& git push": "& git push origin main",
    "iex": 'iex "git push origin main"',
    "continuazione con backtick": "git push `\n  origin main",
    "git.exe reset": "git.exe reset --hard",
    "& git branch -D": "& git branch -D x",
    "splat dopo git": "git @args",
    "array dopo git": 'git @("reset","--hard")',
    "sottocomando tra parentesi": "git ($b) --hard",
    "sottocomando tra parentesi dopo -C": "git -C . ($sub) --hard",
    "sottocomando tra parentesi dopo --no-pager": "git --no-pager ($sub) --hard",
    # su più righe il tokenizzatore trova virgolette sbilanciate: non arriva al controllo degli argomenti
    "here-string pulita": 'git commit -m @"\nfeat: x\n\nCorpo breve.\n"@',
}
PS_COMMIT_FORM_BLOCK = {
    "here-string su una riga": "git commit -m @'feat: x'@",
    # falso positivo accettato: il tokenizzatore spezza --message="a b" in due token
    "--message= con uno spazio": 'git commit --message="feat: x"',
}
PS_ALLOW = {
    "maiuscole: le regole PowerShell non le distinguono": 'Git COMMIT -m "feat: x"',
    "push semplice": "git push origin main",
    "reset in maiuscolo": "Git RESET --hard",
    "branch -d": "git branch -d x",
    "comando non git": "Get-ChildItem -Path C:\\repo -Filter *.md",
}

# input che fa fallire il controllo: blocca solo se sembra un commit, un push o un tag
BROKEN = {
    "JSON rotto con git commit": ('{"tool_input": {"command": "git commit -m x"', 2),
    "JSON rotto senza commit": ('{"tool_input": {"command": "ls"', 0),
    "JSON rotto, commit solo nella cwd": ('{"cwd": "/home/x/git-commit-tools", "tool_input": {"command": "ls"', 0),
    "JSON rotto, commit in maiuscolo": ('{"tool_input": {"command": "Git COMMIT -m x"', 2),
    "JSON rotto con git push": ('{"tool_input": {"command": "git push origin main"', 2),
    "JSON rotto con fetch --tags": ('{"tool_input": {"command": "git fetch --tags"', 0),
}


def run_raw(payload):
    """(exit, stdout, stderr) dell'hook; exit "timeout" oltre HOOK_TIMEOUT."""
    # byte UTF-8 come li manda Claude Code, indipendenti dalla codifica di default del sistema
    try:
        res = subprocess.run([sys.executable, SCRIPT], input=payload.encode("utf-8"), capture_output=True,
                             timeout=HOOK_TIMEOUT)
    except subprocess.TimeoutExpired:
        return "timeout", "", ""
    return res.returncode, res.stdout.decode("utf-8").strip(), res.stderr.decode("utf-8")


def run(command, tool="Bash"):
    return run_raw(json.dumps({"tool_name": tool, "tool_input": {"command": command}, "cwd": TMP},
                              ensure_ascii=False))


failures = 0
FORM_REASON = "forma semplice"


def expect(label, name, result, code, reason=None):
    """L'hook non scrive mai su stdout; reason, se dato, deve comparire nel motivo su stderr."""
    global failures
    exit_code, stdout, stderr = result
    if exit_code != code or stdout or (reason is not None and reason not in stderr):
        failures += 1
        print(f"FALLITO ({label}: atteso exit {code}{'' if reason is None else ' con ' + repr(reason)}, "
              f"ottenuto exit {exit_code}, stdout {stdout[:60]!r}, stderr {stderr[:80]!r}): {name}")


for tool, groups in (
    ("Bash", [(CONTENT_BLOCK, 2, None), (FORM_BLOCK, 2, FORM_REASON),
              (COMMIT_FORM_BLOCK, 2, COMMIT_FORM_REASON), (ALLOW, 0, None)]),
    ("PowerShell", [(PS_CONTENT_BLOCK, 2, None), (PS_FORM_BLOCK, 2, FORM_REASON),
                    (PS_COMMIT_FORM_BLOCK, 2, COMMIT_FORM_REASON), (PS_ALLOW, 0, None)]),
):
    for cases, code, reason in groups:
        for name, cmd in cases.items():
            expect(tool, name, run(cmd, tool), code, reason)
for name, (cmd, reason) in REASON_BLOCK.items():
    expect("Bash", name, run(cmd), 2, reason)
for name, (payload, code) in BROKEN.items():
    expect("input rotto", name, run_raw(payload), code)

# Input costruiti dalle review per far andare in timeout le versioni precedenti (oltre il timeout l'hook
# non blocca): devono dare l'esito giusto entro MAX_SECONDS.
MAX_SECONDS = 3
SLOW = {
    "opzioni -C ripetute prima di un push": ("git" + " -C" * 28 + " x; git push", 2),
    "opzioni -C e -c alternate": ("git" + " -C -c" * 20 + " x; git push", 2),
    "heredoc mai chiusi e attribuzione": (
        "git commit -m 'feat: x\n\nCo-Authored-By: Claude <a@b.c>'\n" + "<<a x\n" * 12000, 2),
    "git ripetuto": ("git " * 20000, 0),
    "oltre il limite di lunghezza con un push": ("echo " + "x" * 100_001 + "; git push", 2),
    "eval annidati": ("eval " * 80 + "git push", 2),
    "bash ripetuto": ("bash " * 20000, 0),
    "git commit ripetuto senza messaggio": ("git commit\n" * 8000, 2),
    "aritmetica e heredoc ripetuti": ("(()) <<A " * 8000, 0),
    "shell ripetute come comandi separati": ("bash; " * 15000 + "git push", 2),
    "eval annidati, 160": ("eval " * 160 + "git push", 2),
    "cmd ripetuto": ("cmd " * 10000, 0),
    "heredoc e aritmetica alternati": ("<<a (()) " * 10000, 0),
    "messaggio con 20000 righe vuote": ('git commit -m "feat: x' + "\n" * 20000 + 'y"', 2),
    # non è un file regolare: bloccato senza leggerlo (e senza restare appeso)
    "commit -F su un file che non finisce": ("git commit -F /dev/zero", 2),
    # un solo git: gli altri sono suoi argomenti, da leggere una volta sola
    "git branch ripetuto": ("git branch " * 6500 + "-D x", 2),
    "git push ripetuto": ("git push " * 6500 + "origin", 0),
}
for name, (cmd, code) in SLOW.items():
    start = time.monotonic()
    result = run(cmd)
    elapsed = time.monotonic() - start
    expect("tempo", name, result, code)
    if elapsed > MAX_SECONDS:
        failures += 1
        print(f"FALLITO (tempo: {elapsed:.1f} s, massimo {MAX_SECONDS}): {name}")

# Le forme semplici dell'hook devono essere i prefissi delle regole ask di settings: se divergono, un
# comando passa senza conferma o viene bloccato anche in forma semplice.
spec = importlib.util.spec_from_file_location("git_guard", SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
ROOT = Path(HERE).parents[3]
ALIGNMENT = [(settings, tool) for settings in ("settings.template.json", "sandbox.settings.json")
             for tool in ("Bash", "PowerShell")]
for settings, tool in ALIGNMENT:
    rules = json.loads(Path(ROOT, settings).read_text(encoding="utf-8"))["permissions"]["ask"]
    prefixes = {m.group(1) for m in (re.fullmatch(tool + r"\(git (.+):\*\)", rule) for rule in rules) if m}
    if prefixes != set(guard.ASK_PREFIXES):
        failures += 1
        print(f"FALLITO (allineamento {settings}, {tool}): solo nelle regole {sorted(prefixes - set(guard.ASK_PREFIXES))}, "
              f"solo nell'hook {sorted(set(guard.ASK_PREFIXES) - prefixes)}")
FORMS = [(sub, form) for sub, forms in guard.ASK_FORMS.items() for form in forms]
for sub, form in FORMS:
    if not guard.is_destructive(sub, [form, "x"]):
        failures += 1
        print(f"FALLITO (forma distruttiva non riconosciuta): git {sub} {form}")

shutil.rmtree(TMP, ignore_errors=True)
total = sum(len(c) for c in (CONTENT_BLOCK, FORM_BLOCK, COMMIT_FORM_BLOCK, ALLOW, PS_CONTENT_BLOCK,
                             PS_FORM_BLOCK, PS_COMMIT_FORM_BLOCK, PS_ALLOW, REASON_BLOCK, BROKEN, SLOW,
                             ALIGNMENT, FORMS))
print(f"{total - failures}/{total} casi corretti")
sys.exit(1 if failures else 0)
