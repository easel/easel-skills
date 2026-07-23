#!/usr/bin/env bash
# Regenerate derived packaging artifacts from canonical skills/.
#
# Refreshes:
#   - plugins/*/skills/** marketplace skill copies
#   - .grok-plugin/plugin-index.json marketplace catalog
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

bash scripts/sync-plugin-skills.sh
python3 scripts/generate-plugin-index.py

echo "OK: prepared generated packaging artifacts"
