#!/usr/bin/env python3
"""Check basic Markdown research report structure."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


HEADING_RE = re.compile(r"(?m)^#{1,6}\s+(.+?)\s*$")
LINK_RE = re.compile(
    r"\[[^\]]+\]\([^)]+\)|https?://\S+|(?:^|[\s`])(?:\.{0,2}/)?[\w.-]+(?:/[\w.-]+)+",
    re.MULTILINE,
)
DATE_RE = re.compile(r"\b(?:20\d{2}-\d{2}-\d{2}|20\d{2}|as of)\b", re.IGNORECASE)


def headings(text: str) -> set[str]:
    return {match.group(1).strip().lower() for match in HEADING_RE.finditer(text)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Markdown research report")
    args = parser.parse_args()

    try:
        text = args.path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"{args.path}: cannot read file: {exc}", file=sys.stderr)
        return 2

    found = headings(text)
    errors: list[str] = []

    if not any(name in found for name in {"question", "scope", "research question"}):
        errors.append("missing Question or Scope heading")
    if not any(name in found for name in {"findings", "evidence", "source ledger"}):
        errors.append("missing Findings, Evidence, or Source Ledger heading")
    if not any(name in found for name in {"recommendation", "verdict", "implications"}):
        errors.append("missing Recommendation, Verdict, or Implications heading")
    if len(LINK_RE.findall(text)) < 2:
        errors.append("expected at least two source links or local paths")
    if not DATE_RE.search(text):
        errors.append("missing visible date, year, or 'as of' scope")

    if errors:
        print(f"{args.path}: research report check failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"{args.path}: research report structure looks usable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
