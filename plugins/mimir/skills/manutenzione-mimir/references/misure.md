# Misure per l'audit

Gli script sono di sola lettura. Regola di `rules/working-style.md`: un controllo improvvisato vale solo dopo averlo visto fallire su un caso con errore noto. Per ognuno c'è il caso con cui provarlo; esegui la prova prima di fidarti di un esito "pulito". Gli script sono stati provati così il 03/10 (Claude Code 2.1.288).

I percorsi presuppongono di lanciare dalla root di Mímir.

## 1. Description: validità YAML, nome, lunghezza

Parsa il frontmatter con un vero parser YAML (richiede PyYAML: `python3 -c "import yaml"`; se manca, segnalalo e non installarlo senza ok). Stampa la lunghezza della description; esce con 1 se un frontmatter non è valido, il `name` non coincide con la cartella o la description manca.

```python
import sys, pathlib, yaml
bad = 0
for p in sorted(pathlib.Path(sys.argv[1]).glob("*/SKILL.md")):
    parts = p.read_text(encoding="utf-8").split("---", 2)
    try:
        fm = yaml.safe_load(parts[1])
        assert isinstance(fm, dict) and fm.get("name") == p.parent.name and fm.get("description")
        print(f"{len(str(fm['description'])):5d}  {p.parent.name}")
    except Exception as e:
        bad += 1
        print(f"ERRORE  {p.parent.name}: {str(e).splitlines()[0]}")
sys.exit(1 if bad else 0)
```

Uso: `python3 controlla.py plugins/mimir/skills | sort -rn | head` (le più lunghe) oppure `| awk '{s+=$1} END {print s, NR}'` (totale caratteri e numero di skill). Le skill con `disable-model-invocation: true` non compaiono nella lista in contesto: non contarle nel peso.

Caso noto: una skill con `description: Usala quando: serve` (due punti seguiti da spazio senza virgolette) deve stampare `ERRORE ... mapping values are not allowed here`. Con `description: "Usala quando: serve"` deve passare.

Riferimento: la lista in contesto taglia description e `when_to_use` a 1.536 caratteri per voce (impostazione `skillListingMaxDescChars`) e la lista complessiva sta nel budget; il limite di Mímir è più stretto (~300 caratteri).

## 2. Riferimenti rotti

Cerca `references/x.md` e `templates/x.md` citati nel SKILL.md e non esistenti; un riferimento nella forma `altra-skill/references/x.md` si cerca nella cartella di quella skill.

```bash
#!/usr/bin/env bash
plugin="$1"
for dir in "$plugin"/skills/*/; do
  skill=$(basename "$dir")
  grep -ohE '([a-z0-9-]+/)?(references|templates)/[A-Za-z0-9_-]+\.md' "$dir/SKILL.md" | sort -u | while read -r ref; do
    case "$ref" in
      references/*|templates/*) path="$dir/$ref" ;;
      *) path="$plugin/skills/$ref"
         # un rimando può puntare a una skill dell'altro plugin (es. brokkr)
         [ -e "$path" ] || path=$(printf '%s\n' "$plugin"/../*/skills/"$ref" | head -n 1) ;;
    esac
    [ -e "$path" ] || echo "ROTTO  $skill: $ref"
  done
done
```

Caso noto: una skill di prova che cita `references/manca.md` senza il file deve stampare `ROTTO`; un rimando a una skill dell'altro plugin passa se il file c'è e stampa `ROTTO` se manca (provato il 10/10). Limiti: non vede i rimandi scritti in prosa ("nella skill `spring-boot`, `references/x.md`") né i file orfani; le segnalazioni ambigue (un percorso senza il nome della skill, scritto in prosa accanto al nome di un'altra) vanno lette a mano. Conferma ogni segnalazione leggendo la riga prima di proporre la modifica.

File orfani: `find plugins/<plugin>/skills -path '*/references/*' -o -path '*/templates/*'` e confronto con i riferimenti citati.

## 3. Sovrapposizioni e regole ripetute

Non c'è uno script che le trovi in modo affidabile: il grep individua i candidati, la lettura decide.
- Una frase caratteristica di una regola, cercata in tutto il repo: `grep -rn "<frase>" rules plugins`. Ripetuta in tre o più skill = candidata alla distillazione.
- Parole d'ordine delle regole sempre attive (`commit`, `push`, `Co-Authored-By`, `verificato`, `haiku`) nelle skill: se ripetono la regola invece di rimandarvi, segnalalo.
- Tabelle dei modelli, limiti di righe, formati di commit: devono comparire in un posto solo e coincidere ovunque siano citati.
- Descriptions con trigger simili: leggi a coppie le description delle skill dello stesso strato (`ticket` e `debugging`, `runbook` e `rilascio`) e chiediti quale richiesta attiva quale delle due.

## 4. Versioni datate

```bash
grep -rnE "Claude Code [0-9]+\.[0-9]+|dalla [0-9]+|[0-9]{2}/[0-9]{2}" plugins rules README.md | head -50
```

Per ogni occorrenza controlla se l'affermazione dipende da una versione (di Claude Code, di un framework, di un linguaggio) e riverificala sulla documentazione ufficiale (`https://code.claude.com/docs/en/<pagina>.md` per Claude Code; Context7 o il sito ufficiale per le altre). Le date di prova ("provato il 03/10") sono evidenze da rinnovare quando cambia la versione.

## 5. Costo e uso (comandi di Claude Code)

- `claude plugin details <plugin>`: always-on in token e riga per componente. Per un plugin non installato: `claude --plugin-dir plugins/<plugin> plugin details <plugin>`. I token sono stime.
- `/doctor`, `/context`, `/skill-doctor`: in sessione (vedi `contesto-e-costi`). `/skill-doctor` con `-p` stampa il report come testo.
- `claude --debug`: l'avviso di budget superato per la lista delle skill finisce nel log di debug.
