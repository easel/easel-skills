#!/usr/bin/env bash
set -euo pipefail

# Ensure marketplace wrappers and plugin-index match skills/.
bash scripts/check-generated.sh

python3 scripts/validate.py
find scripts skills -name '*.py' -print0 | xargs -0 python3 -m py_compile
while IFS= read -r -d '' script; do
  bash -n "$script"
done < <(find scripts skills -name '*.sh' -print0)
python3 skills/sloptimizer/scripts/check-vale-fixtures.py
python3 skills/sloptimizer/scripts/redundancy-audit.py skills --threshold 0.95 --top 5

echo "OK: all validation checks passed"
