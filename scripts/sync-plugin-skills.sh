#!/usr/bin/env bash
# Sync canonical skills/ into marketplace wrappers and local discovery links.
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

# Marketplace wrappers: plugins/<name>/skills/<name> and plugins/all/skills/<name>
for name in "${skills[@]}"; do
  if [[ -d "plugins/$name" ]]; then
    mkdir -p "plugins/$name/skills"
    rsync -a --delete "skills/$name/" "plugins/$name/skills/$name/"
  fi
  if [[ -d "plugins/all" ]]; then
    mkdir -p "plugins/all/skills"
    rsync -a --delete "skills/$name/" "plugins/all/skills/$name/"
  fi
done

# Drop stale skills from the umbrella wrapper
if [[ -d "plugins/all/skills" ]]; then
  while IFS= read -r -d '' wrapper_skill; do
    name="$(basename "$wrapper_skill")"
    if [[ ! -d "skills/$name" ]]; then
      rm -rf "$wrapper_skill"
      echo "removed stale plugins/all/skills/$name"
    fi
  done < <(find plugins/all/skills -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null || true)
fi

# In-repo discovery: relative symlinks under .agents/skills for Grok/Claude/agents
mkdir -p .agents/skills
for name in "${skills[@]}"; do
  link=".agents/skills/$name"
  target="../../skills/$name"
  if [[ -L "$link" || -e "$link" ]]; then
    rm -rf "$link"
  fi
  ln -s "$target" "$link"
done

# Drop stale discovery links
while IFS= read -r -d '' link; do
  name="$(basename "$link")"
  if [[ ! -d "skills/$name" ]]; then
    rm -f "$link"
    echo "removed stale .agents/skills/$name"
  fi
done < <(find .agents/skills -mindepth 1 -maxdepth 1 -print0 2>/dev/null || true)

echo "OK: synced ${#skills[@]} skills into plugin wrappers and .agents/skills"
