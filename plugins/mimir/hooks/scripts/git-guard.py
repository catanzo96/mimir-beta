#!/usr/bin/env python3
"""PreToolUse (Bash e PowerShell): vincoli di Mímir sui comandi git che scrivono, lanciati da Claude Code.

Blocca (exit 2, motivo su stderr):
- i commit con attribuzioni a un'AI: trailer come Co-Authored-By con un nome di AI,
  frasi "Generated with/by" o "Generato con/da" seguite da un'AI, link a Claude Code;
- i commit con intestazione o righe del corpo oltre 72 caratteri (le righe con un URL sono escluse);
- i commit con argomenti fuori dall'elenco chiuso di parse_commit_args;
- il force push: -f anche tra opzioni corte raggruppate, --mirror, refspec +ref, --force,
  --force-with-lease, --force-if-includes e le loro abbreviazioni.

Blocca anche ogni comando git con una regola ask che non sia in forma semplice. La conferma la chiedono
le regole ask di settings (Bash(git commit:*), Bash(git reset:*), PowerShell(git branch -D:*)…), che
riconoscono solo il prefisso: forme come git -C . reset --hard, FOO=1 git push o
cd x && git rebase main nella sandbox partirebbero senza conferma. L'hook non risponde "ask":
verificato l'08/10 con Claude Code 2.1.293 (sandbox e modalità auto), un "ask" dell'hook è stato
ignorato e il commit è partito. Forma semplice: l'intero comando inizia con il prefisso esatto di una
regola ask (ASK_PREFIXES: git commit, git reset, git branch -D, git stash drop…), senza separatori, a
capo, $( o backtick (per PowerShell senza distinguere le maiuscole, come le sue regole). Per branch,
switch, rm, checkout-index, stash, reflog e worktree l'opzione distruttiva (o la parola: drop, remove)
va quindi subito dopo il sottocomando; le loro forme non distruttive (git branch -a, git stash list,
git rm --cached, git worktree list) passano anche nei comandi composti, come git
tag senza argomenti e git tag -l/--list senza opzioni di scrittura. commit-tree, send-pack e git.exe
non hanno una regola ask e sono sempre bloccati.

Come riconosce i comandi: divide il comando in token con shlex (niente regex con backtracking), separa i comandi semplici su ; & | ( ) e a capo, e cerca un token git (anche
/usr/bin/git, git.exe, dopo FOO=1, env, sudo, xargs) seguito, dopo le opzioni globali, dal
sottocomando. Dopo il primo git che scrive, il resto del comando semplice sono suoi argomenti. Un
sottocomando che la shell espande (git $SUB, git {reset,--hard}, git @args, git ($b) su PowerShell) e
una variabile in posizione di comando seguita da un sottocomando ("$GIT" -C x push) sono bloccati.
Entra negli argomenti di sh/bash/zsh -c, eval, iex/Invoke-Expression e cmd /c, non nei messaggi dei
commit. Se il comando non si divide (virgolette sbilanciate), supera MAX_COMMAND o passa da uno
heredoc, una ricerca lineare per comando semplice di git seguito da un sottocomando che scrive decide:
se la trova, blocca. Il corpo dell'heredoc non si guarda solo quando l'intero comando è cat o tee che lo
scrive in un file, con il delimitatore tra virgolette (forma chiusa in writes_heredoc_to_file, solo
bash). Alcuni input costruiti restano lenti (molti << sulla stessa riga, git -c ripetuto, molti commit -F
su un messaggio grande): un'analisi che supera MAX_ANALYSIS_SECONDS blocca qualsiasi comando, anche
innocuo, prima del timeout di hooks.json.

Limiti: è una rete contro errori e injection banali, non contro un avversario determinato. Non vede
alias di git (anche -c alias.x=push, -c remote.x.push=+ref), alias e variabili di PowerShell, funzioni
shell, script, make, hook git, comandi passati a ssh, update-ref e fast-import, un redirect prima del
sottocomando (git 2>/dev/null push), git ricavato da una sostituzione ($(which git) push) e il secondo
git di find -exec … {} + -exec git … {} +. Le forme distruttive senza una regola ask passano: git
branch -C e fetch +ref (recuperabili dalla reflog), stash pop, remote prune, symbolic-ref, read-tree
--reset (senza -u perde solo lo stage) e gc --prune=now (distrugge solo ciò che la reflog non tiene più,
e reflog expire chiede conferma); merge, revert, cherry-pick e pull chiedono conferma ma creano commit
senza il controllo del messaggio; il messaggio di git tag -m/-F non è controllato (un'attribuzione passa
con la sola regola ask); git push origin :ref e --delete cancellano un branch remoto con la sola regola
ask. Su PowerShell la virgola (-m a,b) e lo splatting negli argomenti di -m non sono provati (niente pwsh
nella prova). Accanto restano la sandbox (credenziali negate) e le regole ask, alle quali l'hook lascia
i comandi in forma semplice.

Le parole da sole (un file CLAUDE.md, un percorso, "integra l'API di Anthropic") non bloccano il
commit: conta la forma dell'attribuzione, non l'argomento.

Un errore inatteso blocca (exit 2) solo se il comando sembra un comando git che scrive: per Claude Code
un hook che esce con 1 è un errore non bloccante, e il comando passerebbe senza controllo. Un errore
prima di main (sintassi, import) non passa da qui: Python esce con 1 e il comando passa.
"""
import json
import os
import re
import shlex
import sys
import threading

MAX_LINE = 72
MAX_COMMAND = 100_000
# oltre il timeout di hooks.json (10 s) Claude Code lascia passare il comando: l'analisi che supera questa
# soglia blocca; il margine copre macchine lente e l'avvio di Python e di run-python.sh
MAX_ANALYSIS_SECONDS = 6
MAX_DEPTH = 3

# i nomi dei modelli con il confine di parola: opus non deve prendere opuscolo
AI = (r"(claude|anthropic|openai|chatgpt|gpt-?\d|copilot|gemini|cursor|codeium|tabnine|\bai\b|assistant|assistente"
      r"|llm|\b(?:sonnet|opus|haiku|fable)\b)")
ATTRIBUTION = [
    re.compile(r"^[ \t]*(co-authored-by|co-developed-by|assisted-by|generated-by)\s*:.*" + AI, re.I | re.M),
    re.compile(r"(generated|created|written)\s+(with|by|using)\b[^\n]{0,40}" + AI, re.I),
    re.compile(r"(generat[oa]|creat[oa]|scritt[oa])\s+(con|da|tramite)\b[^\n]{0,40}" + AI, re.I),
    re.compile(r"claude\.(ai|com)/(code|claude-code)", re.I),
]

# i sottocomandi con una regola ask in settings su git <sottocomando>
ASK_SUBCOMMANDS = ("commit", "push", "tag", "reset", "rebase", "merge", "cherry-pick", "revert", "pull", "am",
                   "clean", "restore", "checkout", "update-ref", "filter-branch", "prune")
# i sottocomandi con una regola ask solo sulle forme distruttive (git branch -D, git stash drop…);
# worktree remove intero: anche senza --force cancella i file ignorati (sonda dell'11/10, git 2.43.0)
ASK_FORMS = {
    "branch": ("-D", "-d", "--delete", "-M", "-f", "--force"),
    "switch": ("-f", "--force", "--discard-changes", "-C"),
    "rm": ("-f", "--force"),
    "checkout-index": ("-f", "--force"),
    "stash": ("drop", "clear"),
    "reflog": ("expire", "delete", "drop"),
    "worktree": ("remove",),
}
# le stesse opzioni come le accetta git: corte anche raggruppate (-fD), lunghe anche abbreviate (--del);
# gli altri sottocomandi di ASK_FORMS hanno una parola (drop, remove…)
DESTRUCTIVE_OPTIONS = {
    "branch": ("dDMf", ("--delete", "--force")),
    "switch": ("fC", ("--force", "--discard-changes", "--force-create")),
    "rm": ("f", ("--force",)),
    "checkout-index": ("f", ("--force",)),
}
WRITE_SUBCOMMANDS = set(ASK_SUBCOMMANDS) | set(ASK_FORMS) | {"commit-tree", "send-pack"}
# i prefissi delle regole ask: solo un comando che inizia esattamente così può passare
ASK_PREFIXES = ASK_SUBCOMMANDS + tuple(f"{sub} {form}" for sub, forms in ASK_FORMS.items() for form in forms)
GIT_NAMES = {"git", "git.exe"}
GIT_OPTIONS_WITH_VALUE = {"-c", "-C", "--git-dir", "--work-tree", "--namespace", "--config-env", "--attr-source"}
# le parole che possono stare prima del comando: FOO=1 env -i "$GIT" push, then timeout 10 "$GIT" push
ASSIGNMENT = re.compile(r"\w+=")
REDIRECT = re.compile(r"\d*[<>]")
NUMBER = re.compile(r"\d[\w.]*$")
WRAPPERS = {"env", "sudo", "doas", "command", "exec", "nice", "nohup", "time", "xargs", "timeout", "setsid",
            "stdbuf"}
KEYWORDS = {"if", "then", "elif", "else", "do", "while", "until", "!", "{"}
IFS = re.compile(r"\$\{IFS\}|\$IFS")
# un sottocomando con questi caratteri lo decide la shell: git $SUB, git {reset,--hard}, git @args
EXPANSION = re.compile(r"[\s$`{}@()*?\[~]")
PUSH_OPTIONS_WITH_VALUE = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}
FORCE_OPTIONS = ("--force", "--force-with-lease", "--force-if-includes")
TAG_LIST_OPTIONS = {"-l", "--list"}
TAG_WRITE_OPTIONS = {"-a", "-s", "-u", "-f", "-d", "-m", "-F", "-e", "--annotate", "--sign", "--local-user",
                     "--force", "--delete", "--message", "--file", "--edit"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "su", "sh.exe", "bash.exe"}
POWERSHELLS = {"pwsh", "powershell", "pwsh.exe", "powershell.exe"}
CMDS = {"cmd", "cmd.exe"}
EVALUATORS = {"eval", "iex", "invoke-expression"}
NESTING = SHELLS | POWERSHELLS | CMDS | EVALUATORS
QUOTES = "\"'`"

# segnaposto che prende il posto di ogni heredoc nel comando analizzato
HEREDOC_MARK = "__HEREDOC__"
# << seguito dal delimitatore, ma non <<< (here-string di bash)
HEREDOC_START = re.compile(r"(?<!<)<<(?!<)-?\s*(['\"]?)(\w+)\1")
LOOSE_GIT = re.compile(r"\bgit\b", re.I)
LOOSE_WRITE = re.compile(r"(?<![\w-])(" + "|".join(sorted(WRITE_SUBCOMMANDS)) + r")(?![\w-])", re.I)
LOOSE_COMMIT = re.compile(r"(?<![\w-])commit(?![\w-])", re.I)
# un comando semplice per la ricerca lineare: il testo tra ; & | e a capo
LOOSE_SEGMENT = re.compile(r"[^;&|\n]+")
# le parole che possono rendere distruttivi i sottocomandi di ASK_FORMS (-D, --force, drop, remove…); anche
# attaccate, perché in una parola con espansione seguono } , o $IFS: {git,stash,drop}
LOOSE_MARKER = re.compile(r"(-[\w-]+|drop|clear|expire|delete|remove)(?![\w-])", re.I)
# nomi di file di cat e tee con un heredoc: elenco chiuso, senza # (commento), $ e graffe (espansioni),
# backslash o caratteri jolly, che possono far leggere alla shell il comando in un altro modo
PLAIN_FILE = re.compile(r"[\w./~+-]+")
# redirect di cat verso un file: >f e >>f, oppure > e >> con il file nella parola dopo
FILE_REDIRECT = re.compile(r">>?([\w./~+-]*)")
TEE_APPEND = {"-a", "--append"}

def arithmetic_spans(line):
    """Intervalli di ((…)) e $((…)) nella riga, dove << è uno shift e non un heredoc; uno non chiuso arriva in fondo."""
    spans, start = [], line.find("((")
    while start != -1:
        end = line.find("))", start + 2)
        end = len(line) if end == -1 else end + 2
        spans.append((start, end))
        start = line.find("((", end)
    return spans


def heredoc_starts(line):
    """I << che aprono un heredoc: match e intervalli aritmetici sono in ordine, un solo passaggio."""
    spans, k, starts = arithmetic_spans(line), 0, []
    for m in HEREDOC_START.finditer(line):
        while k < len(spans) and spans[k][1] <= m.start():
            k += 1
        if k == len(spans) or m.start() < spans[k][0]:
            starts.append(m)
    return starts


def heredoc_bodies(cmd):
    """Corpi degli heredoc, per ciascuno se il delimitatore è tutto tra virgolette ('EOF' o "EOF": la shell
    non espande il corpo), e comando senza di essi, riga per riga; un heredoc non chiuso arriva in fondo.

    Quadratico con molti << sulla stessa riga (ogni segnaposto ricostruisce la riga): 1-2,6 s al limite di
    MAX_COMMAND, accettato.
    """
    bodies, quoted, kept, pending, body = [], [], [], [], None
    for line in cmd.split("\n"):
        if body is not None:
            if line.strip() == pending[0][0]:
                bodies.append("\n".join(body))
                quoted.append(pending.pop(0)[1])
                body = [] if pending else None
            else:
                body.append(line)
            continue
        starts = heredoc_starts(line)
        delimiters = [(m.group(2), m.group(1) != "") for m in starts]
        for m in reversed(starts):
            line = line[:m.start()] + f" {HEREDOC_MARK} " + line[m.end():]
        kept.append(line)
        if delimiters:
            pending, body = delimiters, []
    if body is not None:
        bodies.append("\n".join(body))
        quoted.append(pending[0][1])
    return bodies, quoted, "\n".join(kept)


def split_command(text, tool_name):
    """Token del comando con le regole della sua shell; ; & | ( ) e a capo diventano token separati."""
    powershell = tool_name == "PowerShell"
    # continuazione di riga: \ a capo in bash, ` a capo in PowerShell
    text = text.replace("`\n" if powershell else "\\\n", " ")
    # PowerShell non usa il backslash come escape: in modalità POSIX C:\tmp\m.txt diventerebbe C:tmpm.txt
    lexer = shlex.shlex(text, posix=not powershell, punctuation_chars="();|&\n")
    lexer.whitespace_split = True
    lexer.whitespace = " \t\r"
    lexer.commenters = ""
    tokens = list(lexer)
    if powershell:
        tokens = [tok[1:-1] if len(tok) > 1 and tok[0] == tok[-1] and tok[0] in "\"'" else tok for tok in tokens]
    return tokens


def is_separator(tok):
    return tok != "" and all(ch in "();|&\n" for ch in tok)


def simple_commands(tokens):
    current = []
    for tok in tokens:
        if is_separator(tok):
            if current:
                yield current
            current = []
        else:
            current.append(tok)
    if current:
        yield current


def bare(tok):
    """Il token senza redirect attaccato (push>/dev/null), virgolette o backtick ai lati e percorso, in minuscolo."""
    tok = re.split(r"[<>]", tok, maxsplit=1)[0].strip(QUOTES)
    return re.split(r"[\\/]", tok)[-1].lower()


def skip_git_options(words, start):
    """L'indice della prima parola dopo le opzioni globali di git (-C x, --no-pager…)."""
    j = start
    while j < len(words) and words[j].startswith("-"):
        j += 2 if words[j] in GIT_OPTIONS_WITH_VALUE else 1
    return j


def ps_git_expression(tokens):
    """PowerShell passa a git il valore di un'espressione: git ($b) --hard, git -C . @("reset","--hard")."""
    # i token fino a end sono opzioni di un git già guardato: ripassarli costerebbe un tempo quadratico
    end = 0
    for i, tok in enumerate(tokens):
        if i < end or bare(tok) not in GIT_NAMES:
            continue
        end = skip_git_options(tokens, i + 1)
        if end < len(tokens) and tokens[end].startswith(("(", "@")):
            return True
    return False


def git_calls(tokens, tool_name, depth=0):
    """(sottocomando, argomenti) per ogni git con un sottocomando di WRITE_SUBCOMMANDS nei token.

    Un sottocomando che non si conosce prima che la shell lo espanda dà ("dynamic", []).

    Una shell che legge lo script da stdin o da un file (bash <<< …, echo … | sh) dà ("shell", []):
    il chiamante decide con la ricerca lineare su tutto il comando.
    """
    calls = []
    for words in simple_commands(tokens):
        # vero finché le parole sono assegnazioni, wrapper, loro opzioni o il valore dopo un'opzione
        # (sudo -u root): la parola dopo è il comando
        prefix, after_option = True, False
        # dopo il primo git che scrive, il resto del comando semplice sono suoi argomenti (git commit -m git):
        # guardarli di nuovo come git costerebbe anche un tempo quadratico (git branch git branch …); resta
        # quadratico git -c git -c …, dove ogni git è il valore dell'opzione prima (lo ferma il tempo massimo).
        # Limite accettato: find -exec git branch {} + -exec git push {} + non vede il secondo git
        git_args = False
        # le parole fino a qui sono opzioni globali di una variabile già guardata come git ("$GIT" -C x)
        options_end = 0
        for i, word in enumerate(words):
            name, at_command = bare(word), prefix
            prefix = prefix and (ASSIGNMENT.match(word) is not None or name in WRAPPERS or name in KEYWORDS
                                 or word.startswith("-") or REDIRECT.match(word) is not None
                                 or NUMBER.match(word) is not None or after_option)
            after_option = word.startswith("-") or REDIRECT.fullmatch(word) is not None
            if not git_args and name in GIT_NAMES:
                j = skip_git_options(words, i + 1)
                # senza redirect e virgolette, ma con backtick: `echo push` non è un sottocomando
                sub = re.split(r"[<>]", words[j], maxsplit=1)[0].strip("\"'") if j < len(words) else ""
                if bare(sub) in WRITE_SUBCOMMANDS:
                    args = words[j + 1:]
                    # la shell toglie il redirect attaccato (push -f>/dev/null): git riceve -f. Il commit resta
                    # intero perché si controlla il testo di -m, che shlex lascia senza virgolette ("a > b"
                    # tagliato nasconderebbe un'attribuzione); lo protegge parse_commit_args, che ammette solo
                    # forme chiuse e rifiuta un -F con < o >
                    if bare(sub) != "commit":
                        args = [re.split(r"[<>]", arg, maxsplit=1)[0] for arg in args]
                    calls.append((bare(sub), args))
                    git_args = True
                elif EXPANSION.search(re.split(r"[\\/]", sub)[-1]):
                    # il percorso non conta: in grep -rn git plugins/ git è un argomento
                    calls.append(("dynamic", []))
                    git_args = True
                continue
            if depth < MAX_DEPTH and ("$(" in word or "`" in word):
                # sostituzione tra virgolette ("$(git push)", "`git push`"): shlex la lascia in un solo token
                try:
                    calls.extend(git_calls(split_command(word, tool_name), tool_name, depth + 1))
                except ValueError:
                    if loose_git_write(word):
                        calls.append(("shell", []))
            # "$GIT" -C x push, {git,} push solo in posizione di comando (make -C $DIR clean è altro);
            # git${IFS}push e {git,reset} ovunque
            if "$" in word or "{" in word:
                written = False
                if at_command and i >= options_end:
                    options_end = skip_git_options(words, i + 1)
                    written = options_end < len(words) and bare(words[options_end]) in WRITE_SUBCOMMANDS
                # git$IFS"push": senza virgolette la parola è git$IFSpush, e push non sembra una parola intera
                if written or loose_git_write(IFS.sub(" ", word)):
                    calls.append(("dynamic", []))
            if not git_args and depth < MAX_DEPTH and name in NESTING:
                script = nested_script(name, words, i + 1)
                if script is None:
                    calls.append(("shell", []))
                else:
                    calls.extend(git_calls(split_command(script, tool_name), tool_name, depth + 1))
                # il resto del comando semplice sono argomenti della shell: guardarlo di nuovo a ogni parola
                # costerebbe un tempo quadratico (bash bash bash …)
                break
    return calls


def nested_script(name, words, start):
    """Il comando passato a una shell o a un valutatore (sh -c, pwsh -Command, eval, iex, cmd /c), o None."""
    rest = words[start:]
    if name in EVALUATORS:
        return " ".join(rest) if rest else None
    for k, tok in enumerate(rest[:-1]):
        option = tok.lower()
        if name in POWERSHELLS:
            # -c, -com, -command: PowerShell accetta le abbreviazioni dei parametri
            if len(option) >= 2 and "-command".startswith(option):
                return rest[k + 1]
        elif name in CMDS:
            if option == "/c":
                return " ".join(rest[k + 1:])
        elif re.fullmatch(r"-[a-z]*c[a-z]*", option):
            # bash -c -- 'script': -- chiude le opzioni, lo script è dopo
            return rest[k + 2] if rest[k + 1] == "--" and k + 2 < len(rest) else rest[k + 1]
    return None


def is_force_push(args):
    skip = False
    # il backtick di una sostituzione `git push -f` resta attaccato all'ultimo argomento
    for arg in (a.strip("`") for a in args):
        if skip:
            skip = False
            # -o">x" -f, tagliato al redirect, sembra -o -f: un valore che inizia con - si guarda come opzione
            # (fail-closed: blocca anche git push -o -f, dove per git -f è il valore)
            if not arg.startswith("-"):
                continue
        option = arg.split("=", 1)[0].lower()
        if option in PUSH_OPTIONS_WITH_VALUE:
            skip = "=" not in arg
            continue
        if arg.startswith("+") and len(arg) > 1:
            return True
        if option == "--mirror":
            return True
        # git accetta le abbreviazioni univoche delle opzioni lunghe: --force-w vale --force-with-lease
        if len(option) >= 4 and option.startswith("--f") and any(full.startswith(option) for full in FORCE_OPTIONS):
            return True
        if re.fullmatch(r"-[A-Za-z0-9]+", arg) and "f" in arg[1:]:
            return True
    return False


def is_destructive(sub, args):
    """Un sottocomando di ASK_FORMS in una delle forme per cui settings ha una regola ask."""
    args = [a.strip("`") for a in args]
    if sub not in DESTRUCTIVE_OPTIONS:
        return any(arg in ASK_FORMS[sub] for arg in args)
    short, long_options = DESTRUCTIVE_OPTIONS[sub]
    for arg in args:
        if arg == "--":
            break
        if arg.startswith("--"):
            option = arg.split("=", 1)[0]
            if len(option) >= 3 and any(full.startswith(option) for full in long_options):
                return True
        elif re.fullmatch(r"-[A-Za-z]+", arg) and any(c in short for c in arg[1:]):
            return True
    return False


def is_tag_listing(args):
    args = [a.strip("`") for a in args if a.strip("`")]
    if not args:
        return True
    if args[0] not in TAG_LIST_OPTIONS:
        return False
    return not any(arg.split("=", 1)[0] in TAG_WRITE_OPTIONS for arg in args)


class UnreadableMessageFile(Exception):
    """Il file di -F/--file non si legge: il messaggio non si può controllare, quindi si blocca."""

    def __init__(self, path, reason):
        super().__init__(f"{path}: {reason}")
        self.path, self.reason = path, reason


class CommitFormError(Exception):
    """Gli argomenti di git commit non sono tra le forme ammesse: git li leggerebbe in modi che l'hook non vede."""


def read_message_file(value, cwd):
    """Il testo del file di -F/--file. Solleva CommitFormError o UnreadableMessageFile se non si può leggere."""
    if value == "-":
        raise CommitFormError("-F - legge il messaggio da stdin, che l'hook non vede")
    if "<" in value or ">" in value:
        raise CommitFormError("il percorso di -F contiene un redirect")
    # la shell espande variabili, ~ e caratteri jolly, l'hook no: leggerebbe un altro file
    if "$" in value or value.startswith("~") or any(c in value for c in "*?["):
        raise UnreadableMessageFile(value, "contiene variabili, ~ o caratteri jolly")
    path = value if os.path.isabs(value) else os.path.join(cwd, value)
    # solo file regolari e con un limite: -F /dev/zero non finirebbe mai di leggere
    if not os.path.isfile(path):
        raise UnreadableMessageFile(path, "non è un file esistente")
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read(MAX_COMMAND + 1)
    except OSError:
        raise UnreadableMessageFile(path, "non si apre") from None
    if len(text) > MAX_COMMAND:
        raise UnreadableMessageFile(path, f"supera {MAX_COMMAND} caratteri")
    return text


def parse_commit_args(args, cwd):
    """Il messaggio di git commit dalle forme ammesse (elenco chiuso), o None per --amend --no-edit.

    Ammessi: -m/--message, anche ripetuti, oppure un solo -F/--file, con il valore nel token dopo o, per
    le forme lunghe, dopo =; --amend; --no-edit solo come git commit --amend --no-edit. Tutto il resto
    (valori attaccati, abbreviazioni, altre opzioni, file da aggiungere) solleva CommitFormError: git lo
    accetterebbe con effetti che il controllo del messaggio non vede (verificato su git 2.43.0).
    Solleva UnreadableMessageFile se il file del messaggio non è un file regolare leggibile.
    """
    messages, files, flags, i = [], [], set(), 0
    while i < len(args):
        tok = args[i]
        if HEREDOC_MARK in args[i:i + 2]:
            raise CommitFormError("un heredoc non può passare il messaggio")
        if tok in ("-m", "--message", "-F", "--file"):
            if i + 1 == len(args):
                raise CommitFormError(f"{tok} senza valore")
            # git prende il token dopo anche se inizia con -: -m --amend è il messaggio "--amend"
            option, value, i = tok, args[i + 1], i + 2
        elif tok.startswith(("--message=", "--file=")):
            (option, value), i = tok.split("=", 1), i + 1
        elif tok in ("--amend", "--no-edit"):
            if tok in flags:
                raise CommitFormError(f"{tok} è ripetuto")
            flags.add(tok)
            i += 1
            continue
        else:
            raise CommitFormError(f"l'argomento {tok[:40]!r} non è ammesso")
        (files if option in ("-F", "--file") else messages).append(value)

    if messages and files:
        raise CommitFormError("-m e -F insieme")
    # con più -F git usa solo l'ultimo
    if len(files) > 1:
        raise CommitFormError("più di un -F")
    if "--no-edit" in flags:
        if "--amend" not in flags or messages or files:
            raise CommitFormError("--no-edit si usa solo come git commit --amend --no-edit")
        return None
    if files:
        return read_message_file(files[0], cwd)
    if not messages:
        raise CommitFormError("manca il messaggio")
    for value in messages:
        # l'hook vede il valore dopo le virgolette, non sa se la shell lo espanderà: Cl{au,x}de diventa Claude
        if any(c in value for c in "$`{}*?[") or value.startswith("~"):
            raise CommitFormError("il messaggio di -m contiene $, backtick, graffe, caratteri jolly o ~ "
                                  "iniziale, che la shell può espandere")
        # here-string di PowerShell (@" … "@): il tokenizzatore la spezza, il messaggio non è quello passato a git
        if any(line.startswith(("@\"", "@'")) for line in value.split("\n")):
            raise CommitFormError("il messaggio di -m è una here-string di PowerShell")
    return "\n\n".join(m.strip("\n") for m in messages)


def length_problems(message):
    lines = message.splitlines()
    problems = []
    if lines and len(lines[0]) > MAX_LINE:
        problems.append(f"intestazione di {len(lines[0])} caratteri (massimo {MAX_LINE})")
    for n, line in enumerate(lines[1:], start=2):
        # le righe con # contano: senza editor git le tiene nel messaggio (--cleanup=default)
        if len(line) > MAX_LINE and "://" not in line:
            problems.append(f"riga {n} di {len(line)} caratteri (massimo {MAX_LINE})")
    return problems


def has_attribution(text):
    return any(pattern.search(text) for pattern in ATTRIBUTION)


def commit_problem(commit_args, cwd):
    """Il motivo per cui il commit va bloccato, o None se forma e messaggio sono in regola."""
    try:
        message = parse_commit_args(commit_args, cwd)
    except CommitFormError as exc:
        return (f"Commit bloccato: {exc}. Le forme ammesse sono git commit -m \"…\" (anche ripetuto) o "
                "--message=\"…\", oppure un solo -F <file> o --file=<file>, senza altre opzioni né file e "
                "senza redirect, pipe o altri comandi uniti: i file si aggiungono prima, con git add in un "
                "comando a parte. Davanti si può mettere --amend; git commit --amend --no-edit riusa il "
                "messaggio di HEAD. Per un messaggio con $, backtick, graffe, caratteri jolly o su più righe, "
                "scrivilo con lo strumento Write e usa git commit -F con il percorso assoluto che restituisce.")
    except UnreadableMessageFile as exc:
        return (f"Commit bloccato: il file del messaggio {exc.path[:80]!r} {exc.reason}, quindi non si può "
                "controllare. Scrivi il messaggio con lo strumento Write e passa a git commit -F il percorso "
                "assoluto che restituisce (su Windows con le barre, C:/…).")
    # --amend --no-edit: nessun messaggio nel comando, git riusa quello di HEAD
    if message is None:
        return None
    if has_attribution(message):
        return ("Commit bloccato: il messaggio contiene un'attribuzione all'AI "
                "(trailer come Co-Authored-By, 'Generated with…', link a Claude Code). "
                "Rimuovila e riproponi il commit.")
    problems = length_problems(message)
    if problems:
        return ("Commit bloccato: " + "; ".join(problems)
                + ". Vedi la skill commit: intestazione e righe del corpo entro 72 caratteri.")
    return None


def is_destructive_word(word):
    return any(is_destructive(sub, [word]) for sub in ASK_FORMS)


def loose_git_write(text):
    """Ricerca lineare, comando semplice per comando semplice: git seguito più avanti da un sottocomando che
    scrive, come parola intera; quelli di ASK_FORMS (branch, rm, stash…) solo se più avanti, nello stesso
    comando semplice, c'è una parola che può renderli distruttivi (-D, --force, drop, remove…)."""
    # una riga continuata (\ a capo in bash, ` a capo in PowerShell) resta nello stesso comando semplice
    text = text.replace("\\\n", " ").replace("`\n", " ")
    for segment in LOOSE_SEGMENT.finditer(text):
        git = LOOSE_GIT.search(text, segment.start(), segment.end())
        if not git:
            continue
        # la posizione dell'ultima parola distruttiva basta a dire se ce n'è una dopo ogni sottocomando
        last_marker = max((m.start() for m in LOOSE_MARKER.finditer(text, git.end(), segment.end())
                           if is_destructive_word(m.group(1))), default=-1)
        for write in LOOSE_WRITE.finditer(text, git.end(), segment.end()):
            if write.group(1).lower() not in ASK_FORMS or last_marker > write.start():
                return True
    return False


def is_simple_form(cmd, tokens, tool_name):
    """L'intero comando inizia con il prefisso esatto di una regola ask di settings (git commit, git branch -D…)."""
    text = cmd.strip()
    if "\n" in text or "$(" in text or "`" in text or any(is_separator(tok) for tok in tokens):
        return False
    # le regole PowerShell non distinguono le maiuscole, quelle Bash sì
    flags = re.I if tool_name == "PowerShell" else 0
    return re.match(r"git (?:" + "|".join(map(re.escape, ASK_PREFIXES)) + r")(?: |$)", text, flags) is not None


def redirects_to_files(words):
    """Vero se words sono solo redirect > o >> verso un file, almeno uno, attaccati al file o separati."""
    i = 0
    while i < len(words):
        redirect = FILE_REDIRECT.fullmatch(words[i])
        if not redirect:
            return False
        if not redirect.group(1):
            if i + 1 == len(words) or not PLAIN_FILE.fullmatch(words[i + 1]):
                return False
            i += 1
        i += 1
    return bool(words)


def tee_to_files(words):
    """Vero se words sono nomi di file, almeno uno, con al più -a o --append davanti."""
    files = words[1:] if words[:1] and words[0] in TEE_APPEND else words
    return bool(files) and all(PLAIN_FILE.fullmatch(f) and not f.startswith("-") for f in files)


def writes_heredoc_to_file(quoted, flat, tokens, tool_name):
    """Vero se l'intero comando è cat o tee che scrive l'unico heredoc in un file: il corpo è testo, non uno script.

    Forma chiusa di un solo comando semplice di bash: un solo heredoc, con il delimitatore tra virgolette
    (senza, la shell esegue $( ) e backtick del corpo); cat con soli redirect > o >> verso file, tee con soli
    nomi di file e al più -a/--append; nomi di file da PLAIN_FILE. Un separatore (anche la ( di >(…) e
    <(…)), $( o un backtick la escludono, anche tra virgolette, dove la shell li espande ancora; un
    segnaposto tra virgolette, dopo # o dentro ${…} è un << che la shell non legge come heredoc.
    """
    words = list(tokens)
    while words and set(words[-1]) == {"\n"}:
        words.pop()
    if tool_name != "Bash" or quoted != [True] or "$(" in flat or "`" in flat \
            or any(is_separator(word) for word in words) or words.count(HEREDOC_MARK) != 1:
        return False
    command = [word for word in words if word != HEREDOC_MARK]
    if not command:
        return False
    name, args = command[0], command[1:]
    return redirects_to_files(args) if name == "cat" else name == "tee" and tee_to_files(args)


def block_form(reason=""):
    print("Comando git bloccato: i comandi git che chiedono conferma (" + ", ".join(ASK_SUBCOMMANDS)
          + " e le forme distruttive di " + ", ".join(ASK_FORMS) + ") vanno lanciati da soli, in forma "
          "semplice, dalla cartella del repo (git commit -F <file>, git push …, git reset --hard …), così "
          "chiede conferma la regola ask di settings. Niente git -C, opzioni globali, variabili, &&, ;, |, "
          "redirect, heredoc, $( ) o messaggi su più righe: per un commit scrivi il messaggio in un file "
          "con lo strumento Write e usa git commit -F con il percorso assoluto che restituisce. commit-tree e "
          "send-pack non sono ammessi." + reason,
          file=sys.stderr)
    return 2


def check(raw):
    data = json.loads(raw)
    cmd = (data.get("tool_input") or {}).get("command") or ""
    tool_name = data.get("tool_name")

    if len(cmd) > MAX_COMMAND:
        return block_form(" (Comando troppo lungo per l'analisi.)") if loose_git_write(cmd) else 0
    bodies, quoted, flat = heredoc_bodies(cmd)
    try:
        tokens = split_command(flat, tool_name)
        calls = git_calls(tokens, tool_name)
    except ValueError:
        if not loose_git_write(cmd):
            return 0
        # anche senza token un commit con attribuzione si riconosce nel testo (here-string di PowerShell)
        if LOOSE_COMMIT.search(cmd) and has_attribution(cmd):
            print("Commit bloccato: il comando contiene un'attribuzione all'AI. Rimuovila e riproponi il commit.",
                  file=sys.stderr)
            return 2
        return block_form(" (Comando non analizzabile: virgolette sbilanciate.)")

    # il corpo di un heredoc può essere uno script eseguito (bash <<EOF): nel dubbio è una scrittura, tranne
    # quando cat o tee, da soli, lo scrivono in un file
    writes = ["heredoc"] if any(loose_git_write(body) for body in bodies) \
        and not writes_heredoc_to_file(quoted, flat, tokens, tool_name) else []
    if tool_name == "PowerShell" and ps_git_expression(tokens):
        writes.append("dynamic")
    shell_checked = False

    for sub, args in calls:
        if sub == "dynamic":
            writes.append(sub)
            continue
        if sub == "shell":
            # shell che legge lo script da stdin o da un file: non si vede cosa esegue, nel dubbio è una
            # scrittura; la ricerca su tutto il comando si fa una volta sola anche con molte shell
            if not shell_checked:
                shell_checked = True
                if loose_git_write(cmd):
                    writes.append(sub)
            continue
        if sub == "push" and is_force_push(args):
            print("Force push bloccato: Mímir non lo esegue mai. Se serve davvero, lancialo tu a mano "
                  "nel terminale, fuori da Claude Code.", file=sys.stderr)
            return 2
        # commit-tree ha altri argomenti e non ha una regola ask: lo blocca block_form
        if sub == "commit":
            problem = commit_problem(args, data.get("cwd") or os.getcwd())
            if problem:
                print(problem, file=sys.stderr)
                return 2
        if sub == "tag" and is_tag_listing(args):
            continue
        if sub in ASK_FORMS and not is_destructive(sub, args):
            continue
        writes.append(sub)

    if not writes:
        return 0
    if len(calls) == 1 and writes == [calls[0][0]] and (writes[0] in ASK_SUBCOMMANDS or writes[0] in ASK_FORMS) \
            and is_simple_form(cmd, tokens, tool_name):
        return 0  # ci pensa la regola ask di settings
    if any(sub in ASK_FORMS for sub in writes):
        return block_form(" Per " + ", ".join(ASK_FORMS) + " l'opzione distruttiva va subito dopo il "
                          "sottocomando, da sola e non raggruppata: git branch -fD x diventa git branch -D -f x, "
                          "git rm -rf x diventa git rm -f -r x (anche git switch --force main, git stash drop, "
                          "git worktree remove x).")
    return block_form()


def command_of(raw):
    """Il comando dell'input, anche quando il JSON non si riesce a leggere; se non si trova, tutto l'input."""
    try:
        cmd = (json.loads(raw).get("tool_input") or {}).get("command")
        if isinstance(cmd, str):
            return cmd
    except (ValueError, AttributeError):
        pass
    match = re.search(r'"command"\s*:\s*"((?:[^"\\]|\\.)*)', raw)
    return match.group(1) if match else raw


def give_up():
    """Allo scadere di MAX_ANALYSIS_SECONDS: blocca qualsiasi comando, anche uno che sarebbe stato innocuo."""
    print("Comando bloccato: troppo complesso da analizzare nel tempo dell'hook. Spezzalo in comandi più "
          "semplici.", file=sys.stderr)
    sys.stderr.flush()
    # dal thread del timer: sys.exit chiuderebbe solo il thread
    os._exit(2)


def main():
    raw = None
    try:
        # Su Windows la codifica di default della console non è UTF-8: motivi e messaggi si rovinerebbero.
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
        # un thread e non signal.alarm, che su Windows non esiste; scatta tra un'istruzione Python e l'altra,
        # non dentro una sola chiamata C lunga
        timer = threading.Timer(MAX_ANALYSIS_SECONDS, give_up)
        timer.daemon = True
        timer.start()
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        return check(raw)
    except Exception as exc:  # confine dell'hook: nessun errore deve far passare un comando git che scrive
        if raw is None or loose_git_write(command_of(raw)):
            print(f"Comando bloccato: il controllo git di Mímir è fallito ({type(exc).__name__}: {exc}). "
                  "Riprova o segnala il problema dell'hook.", file=sys.stderr)
            return 2
        return 0


if __name__ == "__main__":
    sys.exit(main())
