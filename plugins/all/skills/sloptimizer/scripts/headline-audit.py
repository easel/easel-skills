#!/usr/bin/env python3
"""Audit headlines (deck titles, section headings, one-line claims) for slop.

Sentence-level Vale rules skip headings, and a headline has no terminal
punctuation for the sentence splitters to work with, so the raw profile audit
never sees the constructions that make a title read as generated: the
contrastive reversal, the colon list, the imperative chain, the listicle
count, stacked negation, the forced triplet, flattery, the aphorism, the
mannered phrase (a stock metaphor standing in for the literal claim), the
inventory count (the size of a catalog offered as the claim), and the hedge
word that softens a claim instead of scoping it.

Usage:
    headline-audit.py [--all-lines | --slide] [--max-words N] [--format text|json] PATH...

By default every Markdown heading (`#` to `######`) is a headline; a leading
unit number (`### 3. Title`) is stripped. With `--all-lines` every non-blank
line outside code fences, tables, and frontmatter is a headline, after
stripping list markers, which is the shape of a titles-only outline.

With `--slide` the file is a deck: `---` separates slides, each heading is a
slide title and gets the headline rules, and every other non-blank line is a
text shape (subtitle, card label, banner, closer) and gets the shape rules
that Vale cannot see: the shouting all-caps label, the container title, the
self-justifying section, trailing commentary on the previous sentence, and
lexical restatement of another shape on the same slide. `scripts/pptx-text.py`
produces this layout from a .pptx. Titles-only outlines (`--all-lines`) get
the container and self-justifying checks too, because a slide title that is a
category label is the first slide tell; ordinary document headings do not,
because `## Overview` is a documentation convention.

Exit 1 when any headline or shape has a finding, 0 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PREFIX = "SloptimizerHeadline"
SHAPE_PREFIX = "SloptimizerSlide"
DEFAULT_MAX_WORDS = 10
TARGET_WORDS = 8
STYLES = Path(__file__).resolve().parent.parent / "assets/vale/styles"
MANNERED_RULE = STYLES / "Sloptimizer/ManneredProse.yml"
# Slide-register phrase lists live in the SloptimizerSlide Vale style; headings
# are outside those rules' scope, so slide titles get the same tokens here.
SLIDE_TOKEN_RULES = (
    ("StatusJargon", STYLES / "SloptimizerSlide/StatusJargon.yml",
     "Invented status. Use a state the reader already knows: in use, built, specified, idea, not adopted, retired."),
    ("Taxonomy", STYLES / "SloptimizerSlide/InternalTaxonomy.yml",
     "Internal taxonomy code. The reader does not have the map; name the thing or drop the code."),
    ("Marketing", STYLES / "SloptimizerSlide/MarketingRegister.yml",
     "Marketing register. Say the plain noun or verb, or the fact the reader can check."),
)
RESTATEMENT_THRESHOLD = 0.5
RESTATEMENT_MIN_WORDS = 4
STOPWORDS = frozenset(
    "the a an and or but of to in on for with by from at as is are was were be been being it its this that these those "
    "we our you your they their he she his her not no do does did have has had will can into than then so if when what "
    "which who how all any each every one two three".split()
)
CONTAINER_NOUNS = (
    r"(?:capabilit(?:y|ies)|foundations?|layers?|overview|landscape|ecosystem|frameworks?|pillars?|principles|"
    r"considerations|enablers|building blocks|components|dimensions|themes|elements|areas|aspects|fundamentals|"
    r"essentials|basics|highlights|context|background|approach|philosophy|vision|stack|platform|architecture|"
    r"framing|scope|summary|agenda|introduction|recap|takeaways|learnings|observations|reflections|opportunities|"
    r"challenges|implications|next steps|key points|the ask|deep[- ]dive|overview and context)"
)
SELF_JUSTIFYING = (
    r"^how to read (?:this|the)\b",
    r"^how this (?:slide|page|view|diagram|map) (?:works|is organi[sz]ed|reads)\b",
    r"^what this (?:slide|page|deck|diagram|view|map) (?:shows|means|is saying|tells)\b",
    r"^reading (?:this|the) (?:slide|chart|diagram|map|table)\b",
    r"^(?:a )?note on (?:how to read|reading|method|methodology)\b",
    r"^(?:design |guiding |core |our )?principles? (?:served|applied|honou?red|met|addressed|upheld|in play)\b",
    r"^why (?:we|our|us|the \w+|this|it|that) (?:own|control|built|build|chose|choose|keep|hold|matter|matters|care|need|exist)",
    r"^why (?:this|it|that) (?:matters|is different|is hard|works)\b",
    r"^what (?:stays|remains|does ?n[o'’]t change|we (?:control|own|keep|hold|guarantee))\b",
    r"^(?:the |our |design )?rationale\b",
)
TRAILING_COMMENTARY = (
    r"[.!?]\s+(?:Built|Designed|Intended|Meant|Chosen|Included|Added|Kept|Positioned|Shown|Placed|Retained|Selected)"
    r"\s+(?:as|to|because|for|here|so|since)\b"
)
TRAILING_COMMENTARY += r"|[.!?]\s+(?:Serves|Acts|Exists|Stands|Functions)\s+(?:as|to|because|so)\b"
TRAILING_COMMENTARY += r"|[.!?]\s+(?:This|It|That) (?:is|was) (?:the|our|a) (?:worked example|reference|proof point|test case|first step)\b"

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
COUNT = (
    r"(?:\d[\d,]*|a dozen|dozens|hundreds|thousands|"
    r"(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:-(?:one|two|three|four|five|six|seven|eight|nine))?|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
    r"two|three|four|five|six|seven|eight|nine|ten)"
)
INVENTORY_VERBS = (
    r"(?:with|has|have|had|offers?|ships?|includes?|provides?|contains?|routes?|spans?|across|covers?|"
    r"supports?|brings?|delivers?|packs?|features?|comes with|made (?:up )?of|consists? of|bundles?|"
    r"holds?|carries|carry|adds?|lists?|boasts?|totals?|comprises?)"
)
HEDGES = (
    r"\b(?:also|(?<!not )just|simply|really|actually|basically|essentially|arguably|perhaps|maybe|somewhat|"
    r"quite|very|truly|genuinely|literally|surprisingly|frankly|honestly|fairly|rather|pretty)\b"
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
    r"^that(?:'|’)?s what makes\b",
    r"^that is what makes\b",
    r"^(?:this|that) is (?:what|how|why) \w+ (?:works|matters|wins|scales|holds)\b",
    r"\beverything else is (?:detail|plumbing|noise|downstream)\b",
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


def _inventory_count(h: str) -> str | None:
    m = re.search(
        rf"\b{INVENTORY_VERBS}\s+(?:(?:over|more than|about|nearly|some|up to|around|another)\s+)?{COUNT}\s+(?:[\w-]+\s+){{0,2}}?[A-Za-z][\w-]*s\b",
        h, re.IGNORECASE)
    return m.group(0) if m else None


def _container_title(h: str) -> str | None:
    """A category label where a claim should be: 'Firm capabilities', 'Platform layer'."""
    stripped = re.sub(r"[.!?:]+$", "", h.strip())
    if words(stripped) > 4:
        return None
    m = re.fullmatch(rf"(?:[\w&/'’-]+\s+){{0,3}}{CONTAINER_NOUNS}", stripped, re.IGNORECASE)
    return m.group(0) if m else None


def _self_justifying(h: str) -> str | None:
    return _first(h, SELF_JUSTIFYING)


def _shouting_label(h: str) -> str | None:
    """An all-caps section label long enough to be a sentence telling the reader what to think."""
    letters = re.sub(r"[^A-Za-z]", "", h)
    if len(letters) < 12 or letters != letters.upper():
        return None
    n = words(h)
    starts_question = re.match(r"^(?:WHAT|WHY|HOW|WHERE|WHEN|WHO)\b", h.strip())
    if n >= 4 or (n >= 2 and starts_question):
        return h.strip()
    return None


def _trailing_commentary(h: str) -> str | None:
    m = re.search(TRAILING_COMMENTARY, h)
    return m.group(0) if m else None


def _content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z'’-]+", text.lower()) if w not in STOPWORDS and len(w) > 2}


def restatements(shapes: list[tuple[int, str]]) -> list[tuple[int, str, int]]:
    """(line, text, other_line) for shapes on one slide that restate an earlier shape lexically."""
    out: list[tuple[int, str, int]] = []
    bags = [(line, text, _content_words(text)) for line, text in shapes]
    for i, (line, text, bag) in enumerate(bags):
        if len(bag) < RESTATEMENT_MIN_WORDS:
            continue
        for other_line, _, other in bags[:i]:
            if len(other) < RESTATEMENT_MIN_WORDS:
                continue
            if len(bag & other) / len(bag | other) >= RESTATEMENT_THRESHOLD:
                out.append((line, text, other_line))
                break
    return out


def _hedge(h: str) -> str | None:
    m = re.search(HEDGES, h, re.IGNORECASE)
    return m.group(0) if m else None


SLIDE_TOKENS = tuple((rule, _vale_tokens(path), message) for rule, path, message in SLIDE_TOKEN_RULES)


def audit_label(h: str) -> list[tuple[str, str, str]]:
    """Rules for a title or label that stands alone on a slide or in a titles-only outline."""
    out: list[tuple[str, str, str]] = []
    m = _container_title(h)
    if m:
        out.append(("ContainerTitle", "Container title. Name what the slide shows, not the category it belongs to.", m))
    m = _self_justifying(h)
    if m:
        out.append(("SelfJustifying", "Self-justifying section. The slide is arguing for itself; delete it or move the one load-bearing fact into the subtitle.", m))
    m = _shouting_label(h)
    if m:
        out.append(("ShoutingLabel", "All-caps label telling the reader what to think. Shorten to a plain noun or delete.", m))
    return out


def audit_slide_tokens(h: str) -> list[tuple[str, str, str]]:
    """The SloptimizerSlide Vale phrase lists, for headings Vale never sees."""
    out: list[tuple[str, str, str]] = []
    for rule, tokens, message in SLIDE_TOKENS:
        m = _first(h, tokens)
        if m:
            out.append((rule, message, m))
    return out


def audit_shape(h: str) -> list[tuple[str, str, str]]:
    """Rules for a non-title text shape on a slide: subtitle, card, banner, closer."""
    h = h.strip()
    out = audit_label(h)
    m = _reversal(h)
    if m:
        out.append(("ContrastiveReversal", "Contrastive reversal. State the positive claim and drop the 'not X' half.", m))
    m = _first(h, APHORISM)
    if m:
        out.append(("Aphorism", "Aphoristic closer. Delete it; do not replace it with another aphorism.", m))
    m = _first(h, FLATTERY)
    if m:
        out.append(("Flattery", "Flattery. Replace the compliment with the fact the reader can check.", m))
    m = _trailing_commentary(h)
    if m:
        out.append(("TrailingCommentary", "Second sentence is commentary on the first. Keep the first; move any status into the label.", m))
    return out


def audit_headline(h: str, max_words: int = DEFAULT_MAX_WORDS, *, label_rules: bool = False,
                   slide_tokens: bool = False) -> list[tuple[str, str, str]]:
    """Return (rule, message, match) findings for one headline.

    `label_rules` adds the container/self-justifying/shouting checks (slide titles
    and titles-only outlines); `slide_tokens` adds the SloptimizerSlide phrase lists.
    """
    h = h.strip()
    out: list[tuple[str, str, str]] = []
    if label_rules:
        out.extend(audit_label(h))
    if slide_tokens:
        out.extend(audit_slide_tokens(h))
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
    m = _inventory_count(h)
    if m:
        out.append(("InventoryCount", "Inventory count. The size of the catalog is body; the title says what it does for the reader.", m))
    m = _hedge(h)
    if m:
        out.append(("Hedge", "Hedge or filler word. Delete it; if the claim needs softening, scope it with a number.", m))
    n = words(h)
    if n > max_words:
        out.append(("Length", f"Headline is {n} words; aim for {TARGET_WORDS} or fewer, hard stop {max_words}.", h))
    return out


def scrub_inline(text: str) -> str:
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"\*\*([^*]+)\*\*", r"\1", text)


def iter_headlines(path: Path, all_lines: bool, slide: bool = False):
    """Yield (line_number, text, kind, slide_index, shape).

    kind is "headline" for a heading (or every line under --all-lines) and
    "shape" for a non-heading line under --slide. slide_index increments at
    each `---` separator or `<!-- slide N -->` marker so restatement is checked
    within one slide only. shape is the last `<!-- slide N: shape ID "Name" -->`
    marker written by pptx-text.py, or "" when the file has none.
    """
    in_fence = False
    in_frontmatter = False
    slide_index = 1
    shape = ""
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
        stripped = line.strip()
        if slide and (re.fullmatch(r"-{3,}|\*{3,}", stripped) or re.match(r"^<!--\s*slide \d+\s*-->$", stripped)):
            slide_index += 1
            shape = ""
            continue
        marker = re.match(r'^<!--\s*(slide \d+: (?:shape \S+(?: "[^"]*")?|table))\s*-->$', stripped)
        if slide and marker:
            shape = marker.group(1)
            continue
        heading = re.match(r"^\s*#{1,6}\s+(.*?)\s*#*\s*$", line)
        kind = "headline"
        if heading:
            text = heading.group(1)
        elif all_lines or slide:
            if not stripped or stripped.startswith(("|", "<!--", "---", "**", "![", "<")):
                continue
            text = re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", stripped)
            text = re.sub(r"^>\s+", "", text)
            if slide:
                kind = "shape"
        else:
            continue
        text = re.sub(r"^\d+\.\s+", "", scrub_inline(text)).strip()
        if text:
            yield line_number, text, kind, slide_index, shape


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--all-lines", action="store_true", help="treat every non-blank line as a headline")
    mode.add_argument("--slide", action="store_true",
                      help="deck layout: headings are slide titles, other lines are text shapes, --- separates slides")
    parser.add_argument("--max-words", type=int, default=DEFAULT_MAX_WORDS)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    findings: list[dict] = []
    for raw in args.paths:
        path = Path(raw)
        if not path.is_file():
            continue
        label_rules = args.all_lines or args.slide
        shapes_by_slide: dict[int, list[tuple[int, str]]] = {}
        shape_at: dict[int, str] = {}
        for line_number, text, kind, slide_index, shape in iter_headlines(path, args.all_lines, args.slide):
            if kind == "headline":
                prefix = PREFIX
                hits = audit_headline(text, args.max_words, label_rules=label_rules, slide_tokens=args.slide)
            else:
                prefix = SHAPE_PREFIX
                hits = audit_shape(text)
            for rule, message, match in hits:
                findings.append({"path": str(path), "line": line_number, "rule": f"{prefix}.{rule}",
                                 "message": message, "match": match, "headline": text, "shape": shape})
            if args.slide:
                shapes_by_slide.setdefault(slide_index, []).append((line_number, text))
                shape_at[line_number] = shape
        for shapes in shapes_by_slide.values():
            for line_number, text, other_line in restatements(shapes):
                findings.append({"path": str(path), "line": line_number, "rule": f"{SHAPE_PREFIX}.Restatement",
                                 "message": f"Restates line {other_line} on the same slide. Keep one shape and delete the other.",
                                 "match": text, "headline": text, "shape": shape_at.get(line_number, "")})
        findings.sort(key=lambda f: (f["path"], f["line"]))
    if args.format == "json":
        print(json.dumps(findings, indent=2))
    else:
        for f in findings:
            where = f" [{f['shape']}]" if f.get("shape") else ""
            print(f"{f['path']}:{f['line']}:{where} suggestion {f['rule']}: {f['message']} Match: {f['match']!r}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
