#!/usr/bin/env bash
# Collega Mímir alla configurazione di Claude Code su questa macchina: lancia install.py.
# Python con -I: la cartella di Mímir è scrivibile dalla sandbox e l'installer gira fuori,
# quindi i moduli accanto a install.py (un json.py piantato) non devono essere importati.
# Uso: install.sh [--yes] [--skip-system]
set -euo pipefail

MIMIR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for candidate in python3 python; do
  if "$candidate" -I -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' </dev/null >/dev/null 2>&1; then
    exec "$candidate" -I "$MIMIR_DIR/install.py" "$@"
  fi
done

cat >&2 <<'MSG'
Mímir: serve Python 3.8+ (python3 nel PATH). Installalo e rilancia install.sh:
  macOS            brew install python   (oppure xcode-select --install)
  Ubuntu/Debian    sudo apt-get install python3
  Fedora           sudo dnf install python3
  Arch             sudo pacman -S python
  openSUSE         sudo zypper install python3
MSG
exit 1
