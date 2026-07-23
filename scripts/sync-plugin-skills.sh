#!/usr/bin/env bash
# Sync canonical skills/ into marketplace plugin wrappers.
#
# skills/ is the source of truth. Do not edit plugins/*/skills/ by hand.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

skills=()
while IFS= read -r -d '' skill_dir; do
  skills+=("$(basename "$skill_dir")")
done < <(find skills -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

if [[ ${#skills[@]} -eq 0 ]]; then
  echo "FAIL: no skills found under skills/" >&2
  exit 1
fi

RSYNC_EXCLUDES=(
  --exclude '__pycache__/'
  --exclude '*.pyc'
  --exclude '.DS_Store'
)

for name in "${skills[@]}"; do
  if [[ -d "plugins/$name" ]]; then
    mkdir -p "plugins/$name/skills"
    rsync -a --delete "${RSYNC_EXCLUDES[@]}" "skills/$name/" "plugins/$name/skills/$name/"
  fi
  if [[ -d "plugins/all" ]]; then
    mkdir -p "plugins/all/skills"
    rsync -a --delete "${RSYNC_EXCLUDES[@]}" "skills/$name/" "plugins/all/skills/$name/"
  fi
done

if [[ -d "plugins/all/skills" ]]; then
  while IFS= read -r -d '' wrapper_skill; do
    name="$(basename "$wrapper_skill")"
    if [[ ! -d "skills/$name" ]]; then
      rm -rf "$wrapper_skill"
      echo "removed stale plugins/all/skills/$name"
    fi
  done < <(find plugins/all/skills -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null || true)
fi

echo "OK: synced ${#skills[@]} skills into plugin wrappers"
