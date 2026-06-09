#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
vale_assets="${skill_dir}/assets/vale"

if ! command -v vale >/dev/null 2>&1; then
  echo "slop-audit: vale is not installed or not on PATH" >&2
  echo "Install Vale 3.14.2, then rerun this command." >&2
  exit 127
fi

profile="default"
changed=false
args=()
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --changed)
      changed=true
      shift
      ;;
    --profile)
      if [[ -z "${2:-}" ]]; then
        echo "slop-audit: --profile requires default, results, or strict" >&2
        exit 2
      fi
      profile="$2"
      shift 2
      ;;
    --profile=*)
      profile="${1#--profile=}"
      shift
      ;;
    --help|-h)
      echo "usage: slop-audit.sh [--profile default|results|strict] [--changed|PATH ...]"
      exit 0
      ;;
    *)
      args+=("$1")
      shift
      ;;
  esac
done

case "${profile}" in
  default)
    based_on="Sloptimizer"
    ;;
  results)
    based_on="Sloptimizer, SloptimizerResults"
    ;;
  strict)
    based_on="Sloptimizer, SloptimizerResults"
    ;;
  *)
    echo "slop-audit: unknown profile '${profile}' (expected default, results, or strict)" >&2
    exit 2
    ;;
esac

tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

cat > "${tmp_dir}/.vale.ini" <<EOF
StylesPath = ${vale_assets}/styles
MinAlertLevel = suggestion

[*.md]
BasedOnStyles = ${based_on}
TokenIgnores = (\`[^\`]+\`), (\\]\\(<[^>]+>\\)), (\\]\\([^)]+\\))

[*.mdx]
BasedOnStyles = ${based_on}
TokenIgnores = (\`[^\`]+\`), (\\]\\(<[^>]+>\\)), (\\]\\([^)]+\\))

[*.rst]
BasedOnStyles = ${based_on}

[*.txt]
BasedOnStyles = ${based_on}
EOF

if [[ "${changed}" == true ]]; then
  if [[ "${#args[@]}" -gt 0 ]]; then
    echo "slop-audit: --changed cannot be combined with explicit paths" >&2
    exit 2
  fi
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
  echo "usage: slop-audit.sh [--profile default|results|strict] [--changed|PATH ...]" >&2
  exit 2
fi

mapfile -t vale_args < <(python3 "${script_dir}/prepare-vale-inputs.py" "${tmp_dir}/inputs" "${args[@]}")

set +e
vale --no-global --config="${tmp_dir}/.vale.ini" "${vale_args[@]}"
vale_status=$?
set -e

python3 "${script_dir}/raw-profile-audit.py" --profile "${profile}" "${args[@]}"

exit "${vale_status}"
