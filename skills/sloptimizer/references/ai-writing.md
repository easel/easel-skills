# AI-Writing Cleanup

This reference folds useful AI-writing cleanup patterns into Sloptimizer so the
skill can handle both deterministic checks and editorial rewrites. It adapts
patterns from field skills such as Peter Yang's `no-ai-slop`, Hardik Pandya's
`stop-slop`, and from Easel work on HELIX, Lucebox, and 7th Sense prose. Keep
this provenance visible when editing or extending the pattern set.

## Modes

- `detect`: flag AI-writing patterns by **name**, quote the line, and give a
  short fix. Do not rewrite. Do not claim the text was written by AI.
- `rewrite`: revise the prose, preserve claims and evidence, and summarize the
  changes.
- `validate`: run deterministic file checks such as Vale and redundancy audits.

## Check Profiles

- `default`: conservative prose checks for unsupported claims, vague capability
  verbs, filler transitions, token-cost phrases, repeated openings, and
  reader-steering phrases.
- `results`: default checks plus benchmark and comparison verbs that need
  dataset, metric, run, or time-window scope.
- `strict`: results checks plus source-level AI-tell checks for em dashes, bold
  inline-header bullets, and negation-reversal constructions.

## Rewrite Boundary

Do not silently change numbers, legal claims, benchmark results, commands,
paths, acceptance criteria, citations, product names, or named evidence. If a
claim lacks backing evidence, flag it or scope it rather than inventing
evidence.

**Minimum effective edit for prose.** Fix AI patterns, errors, repetition, and
unclear passages. Leave strong human sentences alone. Do not invent opinions,
jokes, rough edges, or a synthetic "human voice." Preserve the writer's real
cadence, bluntness, humor, uncertainty, and digressions when present.

## Named Patterns

Use these names in `detect` findings and in the **What changed** summary after
rewrites. Prefer quoting the exact line.

### Throat-clearing openers

"Here's the thing," "Here's what I mean," "Let me be clear," "I'll be honest,"
"The uncomfortable truth is," "It turns out." Cut the opener and state the
point.

### Faux-insight setups

"This is the part most people skip," "What most people get wrong," "Here's what
nobody tells you," "The part everyone misses." Drop the flattery setup. Make the
claim stand alone.

### Binary contrasts

"This is not X. It's Y." / "The question isn't X, it's Y." / "Not because X.
Because Y." State Y directly.

### Negative listing

"Not a X. Not a Y. A Z." State Z without the runway.

### Colon reveals

Noun phrase, colon, then a dramatic lowercase reveal: "The best part: it
learns." Rewrite as a plain sentence. Keep colons for lists, labels, and quotes.

### Superficial analysis

Trailing `-ing` clauses that fake explanation: "highlighting," "underscoring,"
"reflecting," "showcasing," "demonstrating." Replace with the concrete
consequence or mechanism.

### Importance puffery

"Stands as a testament," "marks a pivotal moment," "plays a vital role,"
"solidifies its position," "game-changer," "transformative," "watershed." State
the fact and let the reader judge significance.

### Weasel attribution

"Experts agree," "industry reports suggest," "many argue," "studies show,"
"widely regarded as." Name the source or cut the claim. Ask instead of inventing
a citation.

### Fake-strong verbs / copula avoidance

"Serves as," "acts as," "functions as," "represents a," when a plain "is" or a
concrete verb is clearer. "The app serves as a centralized hub" becomes what the
app actually tracks or does.

### Synonym cycling

Rotating agent/assistant/tool, platform/solution/offering, or other labels for
style. Repeat the clear word.

### Dramatic fragmentation

"X. And Y. And Z." / "That's it. That's the whole thing." / "[Noun]. That's it.
That's the [thing]." Prefer complete sentences unless the fragment is clearly
the writer's voice.

### Rhetorical setups

"What if I told you," "Think about it," "Plot twist," self-answered
"Question? Answer." pairs. Drop the setup; make the point.

### Fake-profound kickers

Closing aphorisms or mic-drop metaphors that restate the point cute. Delete
them. End on the last concrete takeaway or next action already in the draft.

### Summary-recap endings

"In conclusion," "Ultimately," "Overall," or a final paragraph that only
restates earlier points. End on the last new concrete point or next action.

### Forced groups of three

"A, B, and C" packaging used for rhythm rather than meaning. Use the number of
items the point needs.

### False ranges

"From X to Y" when the poles are marketing extremes rather than a real span
("from startups to enterprises," "from idea to production" with no mechanism).
Name the actual range or drop it.

### False agency

Inanimate subjects doing human verbs: "the decision emerges," "the data tells
us," "the market rewards," "the culture shifts." Name the actor.

### Chatbot residue

"I hope this helps," "Let me know if you have questions," "As an AI,"
"Certainly!" "Great question!" Cut assistant chrome from shipped prose.

### Formatting slop

Emoji headings, bold mid-sentence for emphasis, bullets that should be two
sentences of prose, headers over two-sentence sections. Format follows content.

### Reader-steering labels

"Worth noting," "what stands out," "here's what's interesting," "the real
answer." State the reason or consequence directly.

### Hollow intensifiers

Truly, genuinely, really, quite, clearly, obviously, simply, actually. Delete
unless they carry a named contrast or the writer's spoken rhythm.

### Hedge stacks

Could potentially, may eventually, might ultimately. Pick one uncertainty
marker and state the condition that would make the claim true.

### Compulsive rule of three / over-structure

Repeated "A, B, and C" packaging, bold inline labels, TL;DR badges, and section
formulas that make every paragraph look generated. Use normal headings, prose,
or real lists.

## Rubric-Only Signals

These are judgment calls, not stable Vale rules:

- Paragraphs could be reordered without the reader noticing.
- Every paragraph has the same length and cadence (robotic rhythm).
- The opening gives broad context before the actual point.
- The voice is sanded flat enough to remove useful human judgment.
- The conclusion summarizes instead of landing a decision, caveat, or next
  action.
- Most sentences restate one point at different levels of abstraction, so a
  summary loses nothing.
- Synonym cycling across paragraphs for the same referent.

## Data-Bearing Prose

Numeric and comparative claims need scope. Name the relevant dataset, sample
size, run, metric, seed, quantization, source, engine, time window, or
comparability boundary.

Weak:

```text
Model A beats Model B and is much faster.
```

Better:

```text
On ds4-eval-92, Model A scored 84% versus Model B's 81% and decoded 4.9x
faster on the 3090 Ti run from 2026-06-02.
```

## Second Pass

After rewriting, load `references/eval.md` and run the pass/fail checks. Fix
failures before returning. Rewrites often introduce fresh filler, unsupported
broad claims, or reader-steering labels while fixing the first set of issues.
