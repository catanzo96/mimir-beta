#!/usr/bin/env bash
# Collega Mímir alla configurazione di Claude Code su questa macchina.
set -euo pipefail

MIMIR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${HOME}/.claude"
STAMP="$(date +%Y%m%d-%H%M%S)"
mkdir -p "$CLAUDE_DIR"

# 0. File personali (profilo, inbox): si creano dagli esempi solo se mancano, poi restano fuori da git.
for pair in "profile/profile.example.md:profile/profile.md" "inbox.example.md:inbox.md"; do
  src="$MIMIR_DIR/${pair%%:*}" dst="$MIMIR_DIR/${pair##*:}"
  if [ -f "$dst" ]; then
    echo "✓ ${pair##*:} già presente"
  else
    cp "$src" "$dst"
    echo "✓ ${pair##*:} creato: personalizzalo"
  fi
done

# 1. Regole globali: ~/.claude/CLAUDE.md importa il CLAUDE.md di Mímir.
#    L'import sta sotto un marcatore: se Mímir si sposta, rilanciando lo script la riga si sostituisce invece di duplicarsi.
TARGET="$CLAUDE_DIR/CLAUDE.md"
MARKER="<!-- mimir: la riga sotto la gestisce install.sh -->"
IMPORT_LINE="@${MIMIR_DIR}/CLAUDE.md"
if [ -f "$TARGET" ] && grep -qxF "$MARKER" "$TARGET" && grep -A1 -xF "$MARKER" "$TARGET" | grep -qxF "$IMPORT_LINE"; then
  echo "✓ CLAUDE.md già collegato"
else
  if [ -f "$TARGET" ]; then
    cp "$TARGET" "$TARGET.bak-$STAMP" && echo "  backup: $TARGET.bak-$STAMP"
    # toglie il vecchio import (marcatore e riga seguente) e quello scritto senza marcatore dalle versioni precedenti
    awk -v m="$MARKER" -v imp="$IMPORT_LINE" \
      '$0 == m { skip = 1; next } skip { skip = 0; next } $0 != imp' \
      "$TARGET.bak-$STAMP" > "$TARGET"
  fi
  printf '%s\n%s\n' "$MARKER" "$IMPORT_LINE" >> "$TARGET"
  echo "✓ CLAUDE.md collegato a $MIMIR_DIR"
fi

# 2. Impostazioni base (attribuzione, permessi): merge di settings.template.json in ~/.claude/settings.json
SETTINGS="$CLAUDE_DIR/settings.json"
if command -v jq >/dev/null; then
  [ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
  cp "$SETTINGS" "$SETTINGS.bak-$STAMP"
  jq -s '
    .[0] as $cur | .[1] as $tpl
    | $cur * ($tpl | del(.permissions)) * {permissions: (($cur.permissions // {}) as $p
        | {ask:  ((($p.ask  // []) + ($tpl.permissions.ask  // [])) | unique),
           deny: ((($p.deny // []) + ($tpl.permissions.deny // [])) | unique)})}
  ' "$SETTINGS" "$MIMIR_DIR/settings.template.json" > "$SETTINGS.tmp" && mv "$SETTINGS.tmp" "$SETTINGS"
  echo "✓ impostazioni unite in settings.json (backup: $SETTINGS.bak-$STAMP)"
else
  echo "! jq non trovato: unisci a mano settings.template.json in $SETTINGS"
fi

# 3. Marketplace: registrato (o spostato sulla cartella attuale) con la CLI.
#    Aggiorna extraKnownMarketplaces in settings.json e known_marketplaces.json; i plugin già installati seguono il nuovo percorso.
if command -v claude >/dev/null && claude plugin marketplace add "$MIMIR_DIR" >/dev/null; then
  echo "✓ marketplace mimir registrato su $MIMIR_DIR"
else
  echo "! marketplace non registrato: dentro Claude Code lancia /plugin marketplace add $MIMIR_DIR"
fi

cat <<MSG

Sessioni con Mímir: $MIMIR_DIR/bin/claude-mimir (carica i plugin dalla cartella, niente da installare).
Per averli anche nelle sessioni normali, dentro Claude Code:
  /plugin install mimir@mimir
  /plugin install brokkr@mimir   (solo dove si lavora)
Se sposti la cartella, rilancia install.sh.
Host privati per la sandbox (azienda, clienti): aggiungili a sandbox.network.allowedDomains in $CLAUDE_DIR/settings.json.
MSG
