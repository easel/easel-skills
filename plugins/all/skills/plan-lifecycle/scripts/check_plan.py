#!/usr/bin/env python3
"""Check that a Markdown plan contains core planning sections."""
from __future__ import annotations

import re
import sys
from pathlib import Path


SECTION_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)

GROUPS = {
    "goal": ("goal", "objective", "release target", "decision"),
    "scope": ("scope", "non-goals", "current state", "risk model", "data contract"),
    "work": ("work breakdown", "tasks", "release steps", "test cases", "chosen approach"),
    "validation": ("validation", "commands", "evidence", "quality gates", "acceptance"),
    "risks": ("risks", "gaps", "rollback", "recovery"),
    "open": ("open questions", "assumptions", "handoff", "follow-ups"),
}


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", value.lower()).strip()


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_plan.py path/to/plan.md", file=sys.stderr)
        return 2

    path = Path(argv[1])
    text = path.read_text(encoding="utf-8")
    headings = {normalize(match.group(1)) for match in SECTION_RE.finditer(text)}

    missing: list[str] = []
    for group, labels in GROUPS.items():
        if not any(label in heading for heading in headings for label in labels):
            missing.append(group)

    if missing:
        print(f"FAIL: missing plan section groups: {', '.join(missing)}", file=sys.stderr)
        print("Headings found:", ", ".join(sorted(headings)) or "(none)", file=sys.stderr)
        return 1

    print("OK: plan has core section groups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
