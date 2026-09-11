#!/usr/bin/env python3
"""Audit headlines (deck titles, section headings, one-line claims) for slop.

Sentence-level Vale rules skip headings, and a headline has no terminal
punctuation for the sentence splitters to work with, so the raw profile audit
never sees the constructions that make a title read as generated: the
contrastive reversal, the colon list, the imperative chain, the listicle
count, stacked negation, the forced triplet, flattery, the aphorism, and the
mannered phrase (a stock metaphor standing in for the literal claim).

Usage:
    headline-audit.py [--all-lines] [--max-words N] [--format text|json] PATH...

By default every Markdown heading (`#` to `######`) is a headline; a leading
unit number (`### 3. Title`) is stripped. With `--all-lines` every non-blank
line outside code fences, tables, and frontmatter is a headline, after
stripping list markers, which is the shape of a titles-only outline.

Exit 1 when any headline has a finding, 0 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PREFIX = "SloptimizerHeadline"
DEFAULT_MAX_WORDS = 12
MANNERED_RULE = Path(__file__).resolve().parent.parent / "assets/vale/styles/Sloptimizer/ManneredProse.yml"

NUMBER = r"(?:two|three|four|five|six|seven|eight|nine|ten|\d+)"
LISTICLE_NOUNS = (
    r"(?:things|reasons|ways|lessons|mistakes|signs|secrets|tips|takeaways|truths|myths|"
    r"ideas|insights|principles|habits|rules|questions|shifts|changes|factors|points|"
    r"patterns|steps|keys|pillars|traps)"
)
GROUP_NOUNS = (
    r"(?:teams?|people|leaders|engineers|developers|companies|organi[sz]ations|customers|"
    r"users|buyers|founders|executives|managers|businesses|enterprises|startups)"
)
GROUP_VERBS = (
    r"(?:switch|win|lose|choose|prefer|want|need|trust|buy|adopt|leave|stay|succeed|fail|"
    r"care|love|hate|ignore|struggle|expect|demand|know|forget|resist|deserve)"
)
IMPERATIVE_VERBS = {
    "add", "adopt", "align", "ask", "audit", "build", "buy", "call", "check", "choose",
    "close", "commit", "configure", "count", "cut", "decide", "define", "deploy", "design",
    "document", "draft", "drive", "edit", "find", "fix", "follow", "frame", "get", "give",
    "go", "grow", "hire", "hold", "install", "join", "keep", "launch", "lead", "learn",
    "let", "list", "make", "map", "measure", "merge", "move", "name", "open", "own", "pick",
    "plan", "publish", "push", "put", "read", "release", "remove", "review", "run", "scale",
    "see", "sell", "send", "set", "share", "ship", "show", "sign", "start", "stop", "take",
    "tell", "test", "track", "train", "try", "turn", "use", "validate", "verify", "watch",
    "write",
}

WORD = re.compile(r"[A-Za-z0-9$%][\w$%.,'’-]*")
APOS = r"(?:'|’)"


def words(text: str) -> int:
    return len(WORD.findall(text))


def _reversal(h: str) -> str | None:
    patterns = (
        # "..., and the practice behind it is not"
        rf"\b(?:(?:is|are|was|were|do|does|did|has|have|had|will|can|could|should)\s+not|(?:isn|aren|wasn|weren|doesn|don|hasn|haven){APOS}t)\s*[.!]?$",
        # "a methodology you adopt, not a platform you join"
        r",\s*not\s+(?:a|an|the|your|our|their|just|only|merely|simply|because)\b",
        # "Not a tool. A method."
        r"^not\s+(?:a|an|the|just|only|because)\b",
        # "not just X but Y" / "not X, but Y"
        r"\bnot\s+[^,;.]{1,40}?,?\s+but\s+\w",
        # "isn't X; it's Y"
        rf"\b(?:isn{APOS}t|aren{APOS}t|is not|are not|doesn{APOS}t|don{APOS}t)\b[^,;.]{{1,60}}[,;.]\s*(?:it{APOS}s|it is|they{APOS}re|they are|but)\b",
        # "Less process, more shipping"
        r"^(?:less|fewer|more)\b[^,]{1,40},\s*(?:less|fewer|more)\b",
    )
    return _first(h, patterns)


def _colon(h: str) -> tuple[str, str] | None:
    """Return (rule, match) for a colon list or colon reveal."""
    m = re.search(r"(?<!\d):(?!\d|//)\s*(.+)$", h)
    if not m:
        return None
    tail = m.group(1).strip()
    if not tail:
        return None
    items = [i for i in re.split(r",\s+|\s+(?:and|or)\s+", tail) if i.strip()]
    if len(items) >= 2:
        return ("ColonList", h[m.start():])
    return ("ColonReveal", h[m.start():])


def _imperative_chain(h: str) -> str | None:
    segments = [s.strip() for s in re.split(r"[,;]\s+|\.\s+", h) if s.strip()]
    hits = []
    for seg in segments:
        seg = re.sub(r"^(?:and|then|or)\s+", "", seg, flags=re.IGNORECASE)
        first = re.match(r"[A-Za-z]+", seg)
        if first and first.group(0).lower() in IMPERATIVE_VERBS:
            hits.append(first.group(0))
    if len(hits) >= 3:
        return ", ".join(hits)
    return None


def _listicle(h: str) -> str | None:
    m = re.search(rf"\b{NUMBER}\s+(?:[\w-]+\s+){{0,2}}?{LISTICLE_NOUNS}\b", h, re.IGNORECASE)
    return m.group(0) if m else None


def _stacked_negation(h: str) -> str | None:
    hits = re.findall(rf"\b(?:no|not|never|nothing|none|nor|without)\b|n{APOS}t\b", h, re.IGNORECASE)
    if len(hits) >= 2:
        return ", ".join(hits)
    return None


def _triplet(h: str) -> str | None:
    item = r"[\w$%'’-]+(?: [\w$%'’-]+){0,3}"
    m = re.search(rf"\b{item},\s+{item},?\s+(?:and|or)\s+[\w$%'’-]+", h, re.IGNORECASE)
    return m.group(0) if m else None


FLATTERY = (
    r"\byour best (?:teams?|people|engineers?|work|days?)\b",
    r"\b(?:teams|people|leaders|companies) like yours?\b",
    r"\bhold(?:s|ing)? (?:ourselves|yourself|yourselves|themselves) to\b",
    r"\byou deserve\b",
    r"\bthe (?:smartest|best|brightest) (?:teams|people|minds|engineers)\b",
    r"\byou already (?:know|use|have|do|trust)\b",
    r"\bworld[- ]class\b",
    r"\bbest[- ]in[- ]class\b",
    r"\bindustry[- ]leading\b",
    r"\bthe (?:bar|standard) we (?:set|hold|keep)\b",
)
APHORISM = (
    r"\bis the new\b",
    r"\bthe only \w+ that matters\b",
    r"\bis everything\b",
    r"\bmore than ever\b",
    r"\bdone right\b",
    r"\bis (?:a|the) (?:feature|superpower|multiplier|moat|journey|mindset)\b",
    r"\bis (?:a|an) (?:nice-to-have|luxury)\b",
    r"\b(?:wins|matters|counts)\s*[.!]?$",
    r"\bat scale\s*[.!]?$",
    r"\bthe hard way\b",
    r"\bchanges everything\b",
    r"\bhere to stay\b",
    r"\bthe future of\b",
    r"\bwelcome to\b",
)


def _vale_tokens(path: Path) -> tuple[str, ...]:
    """Read the `tokens:` list of a Vale existence rule so one file owns the phrases."""
    if not path.is_file():
        return ()
    tokens: list[str] = []
    in_tokens = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not raw.startswith((" ", "-")) and line.endswith(":"):
            in_tokens = line == "tokens:"
            continue
        if in_tokens and line.startswith("- "):
            token = line[2:].strip()
            if len(token) >= 2 and token[0] == token[-1] and token[0] in "'\"":
                token = token[1:-1].replace("''", "'") if token[0] == "'" else token[1:-1]
            tokens.append(token)
    return tuple(tokens)


# Sentence prose gets these from Vale (`Sloptimizer.ManneredProse`); headings are
# outside that rule's scope, so the headline audit reuses the same token list.
MANNERED = _vale_tokens(MANNERED_RULE)


def _first(h: str, patterns: tuple[str, ...]) -> str | None:
    for p in patterns:
        m = re.search(p, h, re.IGNORECASE)
        if m:
            return m.group(0)
    return None


def _universal_claim(h: str) -> str | None:
    m = re.search(rf"^{GROUP_NOUNS}\s+{GROUP_VERBS}\b", h, re.IGNORECASE)
    if m:
        return m.group(0)
    m = re.search(rf"\b(?:every|all|any)\s+(?:[\w-]+\s+)?{GROUP_NOUNS}\b", h, re.IGNORECASE)
    return m.group(0) if m else None


def audit_headline(h: str, max_words: int = DEFAULT_MAX_WORDS) -> list[tuple[str, str, str]]:
    """Return (rule, message, match) findings for one headline."""
    h = h.strip()
    out: list[tuple[str, str, str]] = []
    m = _reversal(h)
    if m:
        out.append(("ContrastiveReversal", "Contrastive reversal. State the positive claim and drop the 'not X' half.", m))
    c = _colon(h)
    if c and c[0] == "ColonList":
        out.append(("ColonList", "Colon list. Keep the one item the unit proves; the list is body, not title.", c[1]))
    elif c:
        out.append(("ColonReveal", "Colon reveal. Write one sentence with a subject and a verb instead of label: reveal.", c[1]))
    m = _imperative_chain(h)
    if m:
        out.append(("ImperativeChain", "Imperative chain. One verb per headline; the steps belong in the body.", m))
    m = _listicle(h)
    if m:
        out.append(("Listicle", "Listicle count. Name the item that matters instead of counting generic nouns.", m))
    m = _stacked_negation(h)
    if m:
        out.append(("StackedNegation", "Stacked negation. Say what it does or keeps instead of what it is not.", m))
    m = _triplet(h)
    if m:
        out.append(("Triplet", "Rule-of-three list. Keep one concrete noun; move the others to the body.", m))
    m = _first(h, FLATTERY)
    if m:
        out.append(("Flattery", "Flattery. Replace the compliment with the fact the reader can check.", m))
    m = _first(h, APHORISM)
    if m:
        out.append(("Aphorism", "Pseudo-aphorism. Replace the slogan with the specific claim and its number.", m))
    m = _universal_claim(h)
    if m:
        out.append(("UniversalClaim", "Universal claim. Scope it: which teams, how many, measured where.", m))
    m = _first(h, MANNERED)
    if m:
        out.append(("Mannered", "Mannered prose. Say what you mean in plain words: name the thing, the action, or the number.", m))
    n = words(h)
    if n > max_words:
        out.append(("Length", f"Headline is {n} words; aim under 10, hard stop {max_words}.", h))
    return out


def scrub_inline(text: str) -> str:
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"\*\*([^*]+)\*\*", r"\1", text)


def iter_headlines(path: Path, all_lines: bool):
    in_fence = False
    in_frontmatter = False
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line_number == 1 and line.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
            continue
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = re.match(r"^\s*#{1,6}\s+(.*?)\s*#*\s*$", line)
        if heading:
            text = heading.group(1)
        elif all_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith(("|", "<!--", "---", "**")):
                continue
            text = re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", stripped)
        else:
            continue
        text = re.sub(r"^\d+\.\s+", "", scrub_inline(text)).strip()
        if text:
            yield line_number, text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--all-lines", action="store_true", help="treat every non-blank line as a headline")
    parser.add_argument("--max-words", type=int, default=DEFAULT_MAX_WORDS)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    findings: list[dict] = []
    for raw in args.paths:
        path = Path(raw)
        if not path.is_file():
            continue
        for line_number, headline in iter_headlines(path, args.all_lines):
            for rule, message, match in audit_headline(headline, args.max_words):
                findings.append({"path": str(path), "line": line_number, "rule": f"{PREFIX}.{rule}",
                                 "message": message, "match": match, "headline": headline})
    if args.format == "json":
        print(json.dumps(findings, indent=2))
    else:
        for f in findings:
            print(f"{f['path']}:{f['line']}: suggestion {f['rule']}: {f['message']} Match: {f['match']!r}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
