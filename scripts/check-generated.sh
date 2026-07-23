#!/usr/bin/env bash
# Fail when generated packaging artifacts drift from skills/.
#
# Re-runs prepare, then checks marketplace skill copies and the Grok plugin
# index for unstaged or untracked drift (when a git checkout exists). Fully
# staged prepare output is allowed so local validation can pass before commit.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

bash scripts/prepare.sh

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "OK: skipped generated-artifact cleanliness check (not a git checkout)"
  exit 0
fi

paths=(
  .grok-plugin/plugin-index.json
)
while IFS= read -r -d '' dir; do
  paths+=("$dir")
done < <(find plugins -mindepth 2 -maxdepth 2 -type d -name skills -print0 2>/dev/null || true)

dirty_lines=()
while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  # git status --porcelain: XY path
  # X = index, Y = worktree. Allow fully staged changes (Y is space).
  # Reject untracked (??) and any worktree modification (Y not space).
  xy="${line:0:2}"
  if [[ "$xy" == "??" || "${xy:1:1}" != " " ]]; then
    dirty_lines+=("$line")
  fi
done < <(git status --porcelain --untracked-files=normal -- "${paths[@]}")

if [[ ${#dirty_lines[@]} -gt 0 ]]; then
  echo "FAIL: generated packaging artifacts have unstaged or untracked drift." >&2
  echo "Run: bash scripts/prepare.sh && git add plugins/*/skills .grok-plugin" >&2
  echo >&2
  printf '%s\n' "${dirty_lines[@]}" >&2
  exit 1
fi

echo "OK: generated packaging artifacts match skills/"
