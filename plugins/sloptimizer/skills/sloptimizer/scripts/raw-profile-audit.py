#!/usr/bin/env python3
"""Run source-level Sloptimizer profile checks that Vale should not own."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


REPEATED_OPENING = "SloptimizerRaw.RepeatedOpening"
ENUMERATED_PARADE = "SloptimizerRaw.EnumeratedParade"
FORMULAIC_HEADING = "SloptimizerRaw.FormulaicHeading"
FORMULAIC_HEADING_PATTERNS = (
    re.compile(r"^where .+ breaks?(?: down)?$", re.IGNORECASE),
    re.compile(r"^why .+$", re.IGNORECASE),
    re.compile(r"^what .+ (?:gets? wrong|misses|means)$", re.IGNORECASE),
    re.compile(r"^(?:\w+ ){1,3}that (?:forces?|makes?|breaks?|changes?|shapes?|drives?|matters?) .+$", re.IGNORECASE),
    re.compile(r"^(?:why this matters|what i learned|key takeaways?|final thoughts|the bottom line|lessons learned|closing thoughts)$", re.IGNORECASE),
)
ENUMERATED_OPENER = re.compile(
    r"^\s*(?:the |a )?(?:first|second|third|fourth|fifth)(?: \w+){0,2} (?:is|was|comes)\b",
    re.IGNORECASE,
)

# Patterns Vale existence rules cannot match reliably (trailing punctuation,
# clause structure). Run on every profile as suggestions.
DEFAULT_CHECKS = (
    (
        "SloptimizerRaw.TruthIsFiller",
        re.compile(r"\bthe truth is[,:]", re.IGNORECASE),
        "Throat-clearing 'the truth is,'. State the claim directly.",
    ),
    (
        "SloptimizerRaw.GreatQuestionChrome",
        re.compile(r"\bgreat question[.!]", re.IGNORECASE),
        "Chatbot residue 'Great question!'. Delete assistant chrome.",
    ),
)

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
        "SloptimizerStrict.CommaAndChain",
        re.compile(
            r"\b\w+, and (?:it|its|this|that|they|their|there) "
            r"(?:is|are|was|were|has|have|had|belongs?|holds?|forms?|becomes?|means?|makes?|gives?|keeps?|needs?)\b",
            re.IGNORECASE,
        ),
        "Comma-and clause chain. Split into two sentences or subordinate one clause.",
    ),
    (
        "SloptimizerStrict.NegationReversal",
        re.compile(
            r"\b(?:(?:it|this|that)(?:'|\u2019)?s|(?:it|this|that)\s+is) "
            r"not (?:just |only )?[^.!?]{1,80}[,;.]\s+"
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


def iter_headings(path: Path):
    in_fence = False
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        match = re.match(r"^\s*#{1,6}\s+(.*?)\s*#*\s*$", line)
        if in_fence or not match:
            continue
        yield line_number, scrub_inline(match.group(1)).strip()


def audit_formulaic_heading(path: Path) -> None:
    for line_number, heading in iter_headings(path):
        for pattern in FORMULAIC_HEADING_PATTERNS:
            if pattern.match(heading):
                print(
                    f"{path}:{line_number}: suggestion {FORMULAIC_HEADING}: "
                    "Formulaic heading. Name the subject of the section instead of a template. "
                    f"Match: {heading!r}"
                )
                break


def audit_enumerated_parade(path: Path, lines: list[tuple[int, str]]) -> None:
    """Flag the second and later paragraphs that open 'The first is / The second is'."""
    seen = 0
    for line_number, line in lines:
        if not ENUMERATED_OPENER.match(line):
            continue
        seen += 1
        if seen < 2:
            continue
        print(
            f"{path}:{line_number}: suggestion {ENUMERATED_PARADE}: "
            "Enumerated parade. Lead each paragraph with the item itself, or fold the items into one list. "
            f"Match: {ENUMERATED_OPENER.match(line).group(0)!r}"
        )


def audit_checks(path: Path, line_number: int, line: str, checks: tuple) -> None:
    for check, pattern, message in checks:
        match = pattern.search(line)
        if not match:
            continue
        print(
            f"{path}:{line_number}: suggestion {check}: {message} "
            f"Match: {match.group(0)!r}"
        )


def audit_profile(profile: str, paths: list[Path]) -> None:
    for path in paths:
        if not path.is_file():
            continue
        lines = list(iter_audited_lines(path))
        audit_formulaic_heading(path)
        audit_enumerated_parade(path, lines)
        for line_number, line in lines:
            audit_repeated_opening(path, line_number, line)
            audit_checks(path, line_number, line, DEFAULT_CHECKS)
            if profile != "strict":
                continue
            audit_checks(path, line_number, line, STRICT_CHECKS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("default", "results", "strict"), required=True)
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    audit_profile(args.profile, [Path(path) for path in args.paths])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
