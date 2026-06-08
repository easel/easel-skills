#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
vale_assets="${skill_dir}/assets/vale"

if ! command -v vale >/dev/null 2>&1; then
  echo "slop-audit: vale is not installed or not on PATH" >&2
  echo "Install Vale 3.13.0, then rerun this command." >&2
  exit 127
fi

tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

cat > "${tmp_dir}/.vale.ini" <<EOF
StylesPath = ${vale_assets}/styles
MinAlertLevel = suggestion

[*]
BasedOnStyles = Sloptimizer
EOF

args=("$@")
if [[ "${1:-}" == "--changed" ]]; then
  if ! command -v git >/dev/null 2>&1 || ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "slop-audit: --changed requires git inside a work tree" >&2
    exit 2
  fi
  mapfile -t args < <(git diff --name-only --diff-filter=ACMR | grep -E '\.(md|mdx|txt|rst)$' || true)
  if [[ "${#args[@]}" -eq 0 ]]; then
    echo "slop-audit: no changed prose files"
    exit 0
  fi
fi

if [[ "${#args[@]}" -eq 0 ]]; then
  echo "usage: slop-audit.sh [--changed|PATH ...]" >&2
  exit 2
fi

vale --config="${tmp_dir}/.vale.ini" "${args[@]}"

