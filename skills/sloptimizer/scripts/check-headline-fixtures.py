#!/usr/bin/env python3
"""Run Sloptimizer headline fixture checks against scripts/headline-audit.py."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "skills/sloptimizer/tests/fixtures/headline-cases.json"
HEADLINE_AUDIT = ROOT / "skills/sloptimizer/scripts/headline-audit.py"


def load_audit():
    spec = importlib.util.spec_from_file_location("headline_audit", HEADLINE_AUDIT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_script(text: str, all_lines: bool) -> set[str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "case.md"
        path.write_text(text, encoding="utf-8")
        cmd = ["python3", str(HEADLINE_AUDIT), "--format", "json"]
        if all_lines:
            cmd.append("--all-lines")
        result = subprocess.run(cmd + [str(path)], check=False, text=True, capture_output=True)
    findings = json.loads(result.stdout or "[]")
    rules = {f["rule"].split(".", 1)[1] for f in findings}
    if bool(findings) != (result.returncode == 1):
        raise AssertionError(f"exit code {result.returncode} does not match {len(findings)} findings")
    return rules


def main() -> int:
    audit = load_audit()
    cases = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failures: list[str] = []
    for case in cases:
        expected = set(case["expected_rules"])
        mode = case.get("mode", "headline")
        if mode == "headline":
            actual = {rule for rule, _, _ in audit.audit_headline(case["headline"])}
        else:
            try:
                actual = run_script(case["text"], all_lines=(mode == "all-lines"))
            except AssertionError as exc:
                failures.append(f"{case['name']}: {exc}")
                continue
        if actual != expected:
            failures.append(f"{case['name']}: expected {sorted(expected)}, got {sorted(actual)}")
    if failures:
        print("Headline fixture validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"OK: {len(cases)} Sloptimizer headline fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
