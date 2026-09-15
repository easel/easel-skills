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
    headline-audit.py [--all-lines | --slide] [--audience internal|external]
                      [--max-words N] [--format text|json] PATH...

Two independent axes:

Layout (how the file is cut into units). By default every Markdown heading
(`#` to `######`) is a headline (a leading unit number, `### 3. Title`, is
stripped), every standalone short line with no terminal punctuation is a
label (a web eyebrow, a card title, a caption), and every other blank-line
separated block is a paragraph. Headings start a new section. With
`--all-lines` every non-blank line is a headline (a titles-only outline).
With `--slide` the file is a deck: `---` separates slides, each heading is a
slide title, and every other non-blank line is a text shape.
`scripts/pptx-text.py` produces that layout from a .pptx.

Audience (which register rules apply). `--audience external` adds the
`SloptimizerExternal` phrase lists (invented status vocabulary, internal
taxonomy codes, marketing register) to headlines, and turns on the container
and self-justifying checks for Markdown headings, which stay off for
internal documents because `## Overview` and `## Rationale` are conventions
there. `--slide` and `--all-lines` imply `external` unless `--audience
internal` is given.

Rules by unit: headlines get `SloptimizerHeadline.*`; labels and slide shapes
get `SloptimizerShape.*` (shouting label, container title, self-justifying
section, closer shapes, trailing commentary); and within one section or
slide, any two units that restate each other lexically get
`SloptimizerShape.Restatement`. Vale owns the phrase lists on body text, so
labels do not repeat them here.

Exit 1 when any unit has a finding, 0 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PREFIX = "SloptimizerHeadline"
SHAPE_PREFIX = "SloptimizerShape"
LABEL_MAX_WORDS = 8
DEFAULT_MAX_WORDS = 10
TARGET_WORDS = 8
STYLES = Path(__file__).resolve().parent.parent / "assets/vale/styles"
MANNERED_RULE = STYLES / "Sloptimizer/ManneredProse.yml"
# External-audience phrase lists live in the SloptimizerExternal Vale style;
# headings are outside those rules' scope, so titles get the same tokens here.
EXTERNAL_TOKEN_RULES = (
    ("StatusJargon", STYLES / "SloptimizerExternal/StatusJargon.yml",
     "Invented status. Use a state the reader already knows: in use, built, specified, idea, not adopted, retired."),
    ("Taxonomy", STYLES / "SloptimizerExternal/InternalTaxonomy.yml",
     "Internal taxonomy code. The reader does not have the map; name the thing or drop the code."),
    ("Marketing", STYLES / "SloptimizerExternal/MarketingRegister.yml",
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
    if len(letters) < 6 or letters != letters.upper():
        return None
    n = words(h)
    starts_question = re.match(r"^(?:WHAT|WHY|HOW|WHERE|WHEN|WHO)\b", h.strip())
    # "WHAT WE DO" is the web eyebrow; "IN USE" and "API SDK CLI" are labels and pass.
    if (n >= 4 and len(letters) >= 12) or (n >= 2 and starts_question):
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


EXTERNAL_TOKENS = tuple((rule, _vale_tokens(path), message) for rule, path, message in EXTERNAL_TOKEN_RULES)


def audit_label(h: str, *, container: bool = True) -> list[tuple[str, str, str]]:
    """Rules for a title or label that stands alone: slide title, web eyebrow, card label.

    `container` gates the container-title and self-justifying checks, which are
    off for Markdown headings in internal documents (`## Overview` is a convention).
    """
    out: list[tuple[str, str, str]] = []
    if container:
        m = _container_title(h)
        if m:
            out.append(("ContainerTitle", "Container title. Name what the slide or section shows, not the category it belongs to.", m))
        m = _self_justifying(h)
        if m:
            out.append(("SelfJustifying", "Self-justifying section. The text is arguing for itself; delete it or move the one load-bearing fact into the subtitle.", m))
    m = _shouting_label(h)
    if m:
        out.append(("ShoutingLabel", "All-caps label telling the reader what to think. Shorten to a plain noun or delete.", m))
    return out


def audit_external_tokens(h: str) -> list[tuple[str, str, str]]:
    """The SloptimizerExternal Vale phrase lists, for headings Vale never sees."""
    out: list[tuple[str, str, str]] = []
    for rule, tokens, message in EXTERNAL_TOKENS:
        m = _first(h, tokens)
        if m:
            out.append((rule, message, m))
    return out


def audit_shape(h: str) -> list[tuple[str, str, str]]:
    """Rules for a standalone non-title unit: a slide shape, a web label, a caption."""
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
                   external: bool = False, slide_tokens: bool | None = None) -> list[tuple[str, str, str]]:
    """Return (rule, message, match) findings for one headline.

    `label_rules` turns on the container and self-justifying checks (slide
    titles, titles-only outlines, external documents); the shouting-label check
    always runs. `external` adds the SloptimizerExternal phrase lists.
    `slide_tokens` is the pre-rename spelling of `external`.
    """
    if slide_tokens is not None:
        external = slide_tokens
    h = h.strip()
    out: list[tuple[str, str, str]] = []
    out.extend(audit_label(h, container=label_rules))
    if external:
        out.extend(audit_external_tokens(h))
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


SKIP_PREFIXES = ("|", "<!--", "**", "![", "<", ">", "{{", "[^")
LIST_MARKER = re.compile(r"^(?:[-*+]|\d+[.)])\s+")
SHAPE_MARKER = re.compile(r'^<!--\s*(slide \d+: (?:shape \S+(?: "[^"]*")?|table))\s*-->$')


def is_label(text: str) -> bool:
    """A standalone short line with no terminal punctuation: a title-shaped unit that is not a heading."""
    if words(text) > LABEL_MAX_WORDS or not re.search(r"[A-Za-z]", text):
        return False
    return not re.search(r"[.!?;:,]$", text)


def iter_units(path: Path, all_lines: bool = False, slide: bool = False):
    """Yield (line_number, text, kind, section, shape_marker) for one file.

    kind is "headline" for a heading (or every line under --all-lines),
    "shape" for a slide text shape or a document label, and "paragraph" for a
    blank-line separated prose block (used for restatement only). section
    increments at each heading in a document and at each `---` separator or
    `<!-- slide N -->` marker in a deck, so restatement is checked within one
    section or slide only. shape_marker is the last `<!-- slide N: shape ID
    "Name" -->` comment written by pptx-text.py, or "".
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    in_fence = False
    in_frontmatter = False
    section = 1
    shape = ""
    para: list[tuple[int, str]] = []

    def flush():
        nonlocal para
        if not para:
            return
        first_line, first_text = para[0]
        if len(para) == 1 and is_label(first_text):
            yield first_line, first_text, "shape", section, shape
        else:
            yield first_line, " ".join(t for _, t in para), "paragraph", section, shape
        para = []

    for line_number, line in enumerate(lines, 1):
        stripped = line.strip()
        if line_number == 1 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
            continue
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            yield from flush()
            continue
        if in_fence:
            continue
        if not stripped:
            yield from flush()
            continue
        if slide and (re.fullmatch(r"-{3,}|\*{3,}", stripped) or re.match(r"^<!--\s*slide \d+\s*-->$", stripped)):
            yield from flush()
            section += 1
            shape = ""
            continue
        marker = SHAPE_MARKER.match(stripped)
        if marker:
            yield from flush()
            if slide:
                shape = marker.group(1)
            continue
        heading = re.match(r"^\s*#{1,6}\s+(.*?)\s*#*\s*$", line)
        if heading:
            yield from flush()
            if not slide and not all_lines:
                section += 1
            text = re.sub(r"^\d+\.\s+", "", scrub_inline(heading.group(1))).strip()
            if text:
                yield line_number, text, "headline", section, shape
            continue
        if stripped.startswith(SKIP_PREFIXES) or re.fullmatch(r"-{3,}|\*{3,}|_{3,}", stripped):
            yield from flush()
            continue
        if all_lines:
            text = scrub_inline(LIST_MARKER.sub("", stripped)).strip()
            text = re.sub(r"^\d+\.\s+", "", text)
            if text:
                yield line_number, text, "headline", section, shape
            continue
        if slide:
            text = scrub_inline(LIST_MARKER.sub("", stripped)).strip()
            if text:
                yield line_number, text, "shape", section, shape
            continue
        if LIST_MARKER.match(stripped):
            # List items are parallel by design; not labels, not restatement candidates.
            yield from flush()
            continue
        para.append((line_number, scrub_inline(stripped)))
    yield from flush()


def iter_headlines(path: Path, all_lines: bool, slide: bool = False):
    """Headline units only; kept for callers of the pre-refactor name."""
    for line_number, text, kind, section, shape in iter_units(path, all_lines, slide):
        if kind == "headline":
            yield line_number, text, kind, section, shape


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--all-lines", action="store_true", help="treat every non-blank line as a headline")
    mode.add_argument("--slide", action="store_true",
                      help="deck layout: headings are slide titles, other lines are text shapes, --- separates slides")
    parser.add_argument("--audience", choices=("internal", "external"), default=None,
                        help="external adds the SloptimizerExternal phrase lists and the container checks on headings; "
                             "--slide and --all-lines default to external")
    parser.add_argument("--max-words", type=int, default=DEFAULT_MAX_WORDS)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    external = args.audience == "external" or (args.audience is None and (args.slide or args.all_lines))
    label_rules = args.slide or args.all_lines or external

    findings: list[dict] = []
    for raw in args.paths:
        path = Path(raw)
        if not path.is_file():
            continue
        pool: dict[int, list[tuple[int, str]]] = {}
        shape_at: dict[int, str] = {}
        for line_number, text, kind, section, shape in iter_units(path, args.all_lines, args.slide):
            if kind == "headline":
                prefix = PREFIX
                hits = audit_headline(text, args.max_words, label_rules=label_rules, external=external)
            elif kind == "shape":
                prefix = SHAPE_PREFIX
                hits = audit_shape(text)
            else:
                prefix = SHAPE_PREFIX
                hits = []
            for rule, message, match in hits:
                findings.append({"path": str(path), "line": line_number, "rule": f"{prefix}.{rule}",
                                 "message": message, "match": match, "headline": text, "shape": shape})
            pool.setdefault(section, []).append((line_number, text))
            shape_at[line_number] = shape
        for units in pool.values():
            for line_number, text, other_line in restatements(units):
                where = "slide" if args.slide else "section"
                findings.append({"path": str(path), "line": line_number, "rule": f"{SHAPE_PREFIX}.Restatement",
                                 "message": f"Restates line {other_line} in the same {where}. Keep one and delete the other.",
                                 "match": text[:120], "headline": text, "shape": shape_at.get(line_number, "")})
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
