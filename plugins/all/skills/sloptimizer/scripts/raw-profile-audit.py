#!/usr/bin/env python3
"""Run source-level Sloptimizer profile checks that Vale should not own."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


REPEATED_OPENING = "SloptimizerRaw.RepeatedOpening"

STRICT_CHECKS = (
    (
        "SloptimizerStrict.EmDash",
        re.compile("\u2014"),
        "Em dash. Use punctuation that matches the target style.",
    ),
    (
        "SloptimizerStrict.BoldInlineHeader",
        re.compile(r"^\s*[-*]\s+\*\*[^*\n]{1,80}:\*\*"),
        "Bold inline-header bullet. Use a normal heading, plain list item, or prose.",
    ),
    (
        "SloptimizerStrict.NegationReversal",
        re.compile(
            r"\b(?:(?:it|this|that)(?:'|\u2019)?s|(?:it|this|that)\s+is) "
            r"not (?:just |only )?[^.!?]{1,80}[,;]\s+"
            r"(?:(?:it|this|that)(?:'|\u2019)?s|(?:it|this|that)\s+is) [^.!?]{1,80}",
            re.IGNORECASE,
        ),
        "Negation-reversal construction. Replace rhetorical reversal with direct contrast.",
    ),
)


def scrub_inline(text: str) -> str:
    text = re.sub(r"`[^`]+`", " ", text)
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)


def iter_audited_lines(path: Path):
    in_fence = False
    in_frontmatter = False
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line_number == 1 and line == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line == "---":
                in_frontmatter = False
            continue
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if in_fence or re.match(r"^\s*#{1,6}\s+", line):
            continue
        yield line_number, scrub_inline(line)


def audit_repeated_opening(path: Path, line_number: int, line: str) -> None:
    openings: dict[str, int] = {}
    for sentence in re.split(r"(?<=[.!?])\s+", line):
        match = re.match(r"\s*(This|The|It|By|With|When)\b", sentence, re.IGNORECASE)
        if not match:
            continue
        opening = match.group(1).lower()
        openings[opening] = openings.get(opening, 0) + 1
        if openings[opening] > 1:
            print(
                f"{path}:{line_number}: suggestion {REPEATED_OPENING}: "
                "Repeated sentence opening. Vary structure only when the sentence earns its place. "
                f"Match: {match.group(1)!r}"
            )
            return


def audit_profile(profile: str, paths: list[Path]) -> None:
    for path in paths:
        if not path.is_file():
            continue
        for line_number, line in iter_audited_lines(path):
            audit_repeated_opening(path, line_number, line)
            if profile != "strict":
                continue
            for check, pattern, message in STRICT_CHECKS:
                match = pattern.search(line)
                if not match:
                    continue
                print(
                    f"{path}:{line_number}: suggestion {check}: {message} "
                    f"Match: {match.group(0)!r}"
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("default", "results", "strict"), required=True)
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    audit_profile(args.profile, [Path(path) for path in args.paths])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
