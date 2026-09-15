#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
vale_assets="${skill_dir}/assets/vale"

usage="usage: slop-audit.sh [--profile default|results|strict] [--target prose|headline] [--changed|PATH ...]"

profile="default"
target="prose"
changed=false
args=()
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --changed)
      changed=true
      shift
      ;;
    --target)
      if [[ -z "${2:-}" ]]; then
        echo "slop-audit: --target requires prose or headline" >&2
        exit 2
      fi
      target="$2"
      shift 2
      ;;
    --target=*)
      target="${1#--target=}"
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
      echo "${usage}"
      exit 0
      ;;
    *)
      args+=("$1")
      shift
      ;;
  esac
done

case "${target}" in
  prose|headline) ;;
  *)
    echo "slop-audit: unknown target '${target}' (expected prose or headline)" >&2
    exit 2
    ;;
esac

if [[ "${target}" == prose ]] && ! command -v vale >/dev/null 2>&1; then
  echo "slop-audit: vale is not installed or not on PATH" >&2
  echo "Install Vale 3.14.2, then rerun this command." >&2
  exit 127
fi

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
  args=()
  while IFS= read -r changed_file; do
    [[ -n "${changed_file}" ]] && args+=("${changed_file}")
  done < <(git diff --name-only --diff-filter=ACMR | grep -E '\.(md|mdx|txt|rst)$' || true)
  if [[ "${#args[@]}" -eq 0 ]]; then
    echo "slop-audit: no changed prose files"
    exit 0
  fi
fi

if [[ "${#args[@]}" -eq 0 ]]; then
  echo "${usage}" >&2
  exit 2
fi

# A titles-only outline or a list of one-line claims: every line is a headline.
if [[ "${target}" == headline ]]; then
  exec python3 "${script_dir}/headline-audit.py" --all-lines "${args[@]}"
fi

# Write to a file first so the exit status is visible; a process substitution
# would hide a failure behind the while-read.
if ! python3 "${script_dir}/prepare-vale-inputs.py" \
    "${tmp_dir}/inputs" "${args[@]}" > "${tmp_dir}/vale-args"; then
  exit 2
fi

vale_args=()
while IFS= read -r vale_input; do
  [[ -n "${vale_input}" ]] && vale_args+=("${vale_input}")
done < "${tmp_dir}/vale-args"

if [[ "${#vale_args[@]}" -eq 0 ]]; then
  echo "slop-audit: no readable input files" >&2
  exit 2
fi

set +e
vale --no-global --config="${tmp_dir}/.vale.ini" "${vale_args[@]}"
vale_status=$?
python3 "${script_dir}/raw-profile-audit.py" --profile "${profile}" "${args[@]}"
raw_status=$?
# Section headings are headlines too; Vale rules skip them, so audit them here.
python3 "${script_dir}/headline-audit.py" "${args[@]}"
headline_status=$?
set -e

# 2 from the raw audit means a path could not be read; that is a usage error.
if [[ "${raw_status}" -eq 2 ]]; then
  exit 2
fi
if [[ "${vale_status}" -ne 0 || "${raw_status}" -ne 0 || "${headline_status}" -ne 0 ]]; then
  exit 1
fi
exit 0
