#!/usr/bin/env bash
set -euo pipefail

python3 scripts/validate.py
python3 -m py_compile scripts/validate.py skills/sloptimizer/scripts/redundancy-audit.py skills/sloptimizer/scripts/check-vale-fixtures.py skills/sloptimizer/scripts/raw-profile-audit.py skills/sloptimizer/scripts/prepare-vale-inputs.py
bash -n scripts/validate.sh skills/sloptimizer/scripts/install-vale.sh skills/sloptimizer/scripts/slop-audit.sh
python3 skills/sloptimizer/scripts/check-vale-fixtures.py
python3 skills/sloptimizer/scripts/redundancy-audit.py skills --threshold 0.95 --top 5

echo "OK: all validation checks passed"
