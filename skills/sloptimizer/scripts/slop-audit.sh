#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
vale_assets="${skill_dir}/assets/vale"

usage="usage: slop-audit.sh [--profile default|results|strict] [--target prose|headline|slide] [--changed|PATH ...]
       PATH may be a .pptx deck; it is converted with scripts/pptx-text.py and audited as a slide target."

profile="default"
target="prose"
target_explicit=false
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
        echo "slop-audit: --target requires prose, headline, or slide" >&2
        exit 2
      fi
      target="$2"
      target_explicit=true
      shift 2
      ;;
    --target=*)
      target="${1#--target=}"
      target_explicit=true
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
  prose|headline|slide) ;;
  *)
    echo "slop-audit: unknown target '${target}' (expected prose, headline, or slide)" >&2
    exit 2
    ;;
esac

tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

# A .pptx is a deck: extract its text with pptx-text.py and audit it as slides.
# Without an explicit --target, a deck switches the target to slide.
has_pptx=false
path_map="${tmp_dir}/paths.sed"
: > "${path_map}"
for index in "${!args[@]}"; do
  path="${args[$index]}"
  if [[ "${path}" == *.pptx ]]; then
    has_pptx=true
    if [[ ! -f "${path}" ]]; then
      echo "slop-audit: ${path} not found" >&2
      exit 2
    fi
    mkdir -p "${tmp_dir}/pptx/${index}"
    out="${tmp_dir}/pptx/${index}/$(basename "${path%.pptx}").md"
    python3 "${script_dir}/pptx-text.py" "${path}" "${out}"
    slides="$(grep -c '^<!-- slide [0-9]*: shape' "${out}" || true)"
    echo "slop-audit: ${path}: ${slides} text shapes extracted; line numbers refer to 'scripts/pptx-text.py ${path}', findings name the slide and shape" >&2
    printf 's|%s|%s|g\n' "${out}" "${path}" >> "${path_map}"
    args[$index]="${out}"
  fi
done
if [[ "${has_pptx}" == true && "${target_explicit}" == false ]]; then
  target="slide"
fi

# Findings on extracted deck text are reported against the .pptx path.
report() {
  if [[ -s "${path_map}" ]]; then
    sed -f "${path_map}" "$1"
  else
    cat "$1"
  fi
}

vale_available=true
if ! command -v vale >/dev/null 2>&1; then
  vale_available=false
  if [[ "${target}" == prose ]]; then
    echo "slop-audit: vale is not installed or not on PATH" >&2
    echo "Install Vale 3.14.2, then rerun this command." >&2
    exit 127
  elif [[ "${target}" == slide ]]; then
    echo "slop-audit: vale is not installed; body-text checks skipped, slide and title checks still run" >&2
  fi
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

# Slide text is short and label-heavy, so it also gets the slide-register rules
# (invented status vocabulary, internal taxonomy codes, marketing adjectives).
if [[ "${target}" == slide ]]; then
  based_on="${based_on}, SloptimizerSlide"
fi

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

vale_status=0
if [[ "${vale_available}" == true ]]; then
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
  vale --no-global --config="${tmp_dir}/.vale.ini" "${vale_args[@]}" > "${tmp_dir}/vale.out"
  vale_status=$?
  set -e
  report "${tmp_dir}/vale.out"
fi

set +e
python3 "${script_dir}/raw-profile-audit.py" --profile "${profile}" "${args[@]}" > "${tmp_dir}/raw.out"
raw_status=$?
set -e
report "${tmp_dir}/raw.out"

# 2 from the raw audit means a path could not be read; that is a usage error.
if [[ "${raw_status}" -eq 2 ]]; then
  exit 2
fi

set +e
if [[ "${target}" == slide ]]; then
  # Titles get the headline rules; every other text shape gets the slide rules.
  python3 "${script_dir}/headline-audit.py" --slide "${args[@]}" > "${tmp_dir}/headline.out"
else
  # Section headings are headlines too; Vale rules skip them, so audit them here.
  python3 "${script_dir}/headline-audit.py" "${args[@]}" > "${tmp_dir}/headline.out"
fi
headline_status=$?
set -e
report "${tmp_dir}/headline.out"

if [[ "${vale_status}" -ne 0 || "${raw_status}" -ne 0 || "${headline_status}" -ne 0 ]]; then
  exit 1
fi
exit 0
