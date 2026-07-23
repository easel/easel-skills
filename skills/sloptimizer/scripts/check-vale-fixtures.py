#!/usr/bin/env python3
"""Run Sloptimizer Vale-style fixture checks without requiring Vale."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STYLES_ROOT = ROOT / "skills/sloptimizer/assets/vale/styles"
FIXTURES = ROOT / "skills/sloptimizer/tests/fixtures/vale-cases.json"
RAW_AUDIT = ROOT / "skills/sloptimizer/scripts/raw-profile-audit.py"
SLOP_AUDIT = ROOT / "skills/sloptimizer/scripts/slop-audit.sh"

PROFILE_STYLES = {
    "default": ["Sloptimizer"],
    "results": ["Sloptimizer", "SloptimizerResults"],
    "strict": ["Sloptimizer", "SloptimizerResults"],
}


def strip_markdown(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :]
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"(?m)^\s*#{1,6}\s+.*$", " ", text)
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text


def parse_rule(path: Path) -> dict[str, object]:
    rule: dict[str, object] = {"name": path.stem, "tokens": [], "swap": {}}
    section: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not raw_line.startswith(" ") and ":" in stripped:
            key, value = stripped.split(":", 1)
            value = value.strip()
            section = key if key in {"tokens", "swap"} else None
            if key in {"extends", "level", "scope", "token"}:
                rule[key] = unquote(value)
            elif key == "ignorecase":
                rule[key] = value.lower() == "true"
            elif key == "max":
                rule[key] = int(value)
            continue
        if section == "tokens" and stripped.startswith("- "):
            rule["tokens"].append(unquote(stripped[2:].strip()))  # type: ignore[index]
        elif section == "swap" and ":" in stripped:
            key, value = stripped.split(":", 1)
            rule["swap"][unquote(key.strip())] = unquote(value.strip())  # type: ignore[index]
    return rule


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        quote = value[0]
        value = value[1:-1]
        if quote == "'":
            return value.replace("''", "'")
        return value
    return value


def find_rules(text: str, rules: list[dict[str, object]]) -> set[str]:
    clean = strip_markdown(text)
    found: set[str] = set()
    for rule in rules:
        flags = re.IGNORECASE if rule.get("ignorecase") else 0
        kind = rule.get("extends")
        if kind == "existence":
            for token in rule["tokens"]:  # type: ignore[index]
                if re.search(str(token), clean, flags):
                    found.add(str(rule["name"]))
                    break
        elif kind == "substitution":
            for token in rule["swap"]:  # type: ignore[index]
                if re.search(rf"\b{re.escape(str(token))}\b", clean, flags):
                    found.add(str(rule["name"]))
                    break
        elif kind == "occurrence":
            token = str(rule.get("token", ""))
            max_count = int(rule.get("max", 0))
            count = 0
            for sentence in re.split(r"(?<=[.!?])\s+", clean):
                if re.search(token, sentence, flags):
                    count += 1
            if count > max_count:
                found.add(str(rule["name"]))
    return found


def find_raw_rules(text: str, profile: str) -> set[str]:
    clean = strip_markdown(text)
    found: set[str] = set()
    for line in clean.splitlines():
        openings: dict[str, int] = {}
        for sentence in re.split(r"(?<=[.!?])\s+", line):
            match = re.match(r"\s*(This|The|It|By|With|When)\b", sentence, re.IGNORECASE)
            if not match:
                continue
            opening = match.group(1).lower()
            openings[opening] = openings.get(opening, 0) + 1
            if openings[opening] > 1:
                found.add("RepeatedOpening")
                break
        if re.search(r"\bthe truth is[,:]", line, re.IGNORECASE):
            found.add("TruthIsFiller")
        if re.search(r"\bgreat question[.!]", line, re.IGNORECASE):
            found.add("GreatQuestionChrome")
        if profile != "strict":
            continue
        if "\u2014" in line:
            found.add("EmDash")
        if re.search(r"^\s*[-*]\s+\*\*[^*\n]{1,80}:\*\*", line):
            found.add("BoldInlineHeader")
        if re.search(
            r"\b(?:(?:it|this|that)(?:'|\u2019)?s|(?:it|this|that)\s+is) "
            r"not (?:just |only )?[^.!?]{1,80}[,;]\s+"
            r"(?:(?:it|this|that)(?:'|\u2019)?s|(?:it|this|that)\s+is) [^.!?]{1,80}",
            line,
            re.IGNORECASE,
        ):
            found.add("NegationReversal")
    return found


def rules_for_profile(profile: str) -> list[dict[str, object]]:
    rules: list[dict[str, object]] = []
    for style in PROFILE_STYLES[profile]:
        rules.extend(parse_rule(path) for path in sorted((STYLES_ROOT / style).glob("*.yml")))
    return rules


def normalize_audit_checks(raw: str) -> set[str]:
    checks: set[str] = set()
    for match in re.finditer(
        r"\b(?:Sloptimizer|SloptimizerResults|SloptimizerRaw|SloptimizerStrict)\.([A-Za-z]+)\b",
        raw,
    ):
        checks.add(match.group(1))
    return checks


def run_real_vale_cases(cases: list[dict[str, object]]) -> list[str]:
    if shutil.which("vale") is None:
        print("SKIP: Vale not on PATH; real Vale fixture smoke not run")
        return []
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for index, case in enumerate(cases):
            if case.get("profile") == "strict":
                continue
            profile = str(case.get("profile", "default"))
            path = tmp_path / f"case-{index}.md"
            path.write_text(str(case["text"]), encoding="utf-8")
            result = subprocess.run(
                [
                    str(SLOP_AUDIT),
                    "--profile",
                    profile,
                    str(path),
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            actual = normalize_audit_checks(result.stdout)
            expected = set(case["expected_rules"])
            if actual != expected:
                failures.append(
                    f"real slop-audit {case['name']}: expected {sorted(expected)}, got {sorted(actual)}"
                )
    return failures


def run_raw_strict_smoke() -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "strict.md"
        path.write_text(
            "\n".join(
                [
                    "# Robust Framework",
                    "",
                    "This is not just a parser issue; it's a contract issue.",
                    "",
                    "- **Thing:** generated structure.",
                    "",
                    "This sentence uses an em dash \u2014 and keeps going.",
                    "",
                    "```text",
                    "This is not just code; it's code.",
                    "- **Code:** no finding.",
                    "```",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            ["python3", str(RAW_AUDIT), "--profile", "strict", str(path)],
            check=False,
            text=True,
            capture_output=True,
        )
    expected = {
        "SloptimizerStrict.EmDash",
        "SloptimizerStrict.BoldInlineHeader",
        "SloptimizerStrict.NegationReversal",
    }
    actual = {check for check in expected if check in result.stdout}
    if actual != expected:
        return [f"raw strict smoke: expected {sorted(expected)}, got {sorted(actual)}"]
    return []


def main() -> int:
    cases = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failures: list[str] = []
    rule_cache = {profile: rules_for_profile(profile) for profile in PROFILE_STYLES}
    for case in cases:
        profile = str(case.get("profile", "default"))
        rules = rule_cache[profile]
        actual = find_rules(case["text"], rules) | find_raw_rules(case["text"], profile)
        expected = set(case["expected_rules"])
        if actual != expected:
            failures.append(
                f"{case['name']}: expected {sorted(expected)}, got {sorted(actual)}"
            )
    failures.extend(run_real_vale_cases(cases))
    failures.extend(run_raw_strict_smoke())
    if failures:
        print("Fixture validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"OK: {len(cases)} Sloptimizer Vale fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
