# AI-Writing Cleanup

This reference folds useful AI-writing cleanup patterns into Sloptimizer so the
skill can handle both deterministic checks and editorial rewrites. It adapts
patterns from field skills such as Peter Yang's `no-ai-slop`, Hardik Pandya's
`stop-slop`, from Anthropic's definition of mannered prose in its Claude
Fable 5.1 prompting guide, and from Easel work on HELIX, Lucebox, and 7th
Sense prose. Keep this provenance visible when editing or extending the
pattern set.

## Modes

- `detect`: flag AI-writing patterns by **name**, quote the line, and give a
  short fix. Do not rewrite. Do not claim the text was written by AI.
- `rewrite`: revise the prose, preserve claims and evidence, and summarize the
  changes.
- `validate`: run deterministic file checks such as Vale and redundancy audits.

## Check Profiles

- `default`: conservative prose checks for unsupported claims, vague capability
  verbs, filler transitions, token-cost phrases, repeated openings,
  reader-steering phrases, and mannered stock metaphors.
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

## Highest-Yield Patterns

Most AI drafts fail on the same eight tells. Clear these first; the rest of
the catalog covers the long tail.

1. Unsupported quality claims (`robust`, `production-ready`, `seamless`).
   Cite the evidence or cut the adjective.
2. Filler transitions and throat-clearing openers (`At its core`,
   `Here's the thing`, `In conclusion`). Delete and open with the claim.
3. Binary contrasts and negation reversal (`This is not X. It's Y.`).
   State Y.
4. Capability verbs with no actor (`enables`, `supports`, `streamlines`).
   Name who does what to what.
5. Importance puffery and mannered prose (`plays a vital role`,
   `earns its keep`). State the fact or the number.
6. Summary-recap endings and fake-profound kickers. Stop on the last concrete
   point already in the draft.
7. Colon reveals (`The best part: it learns`). Write the plain sentence.
8. Forced groups of three. Use the number of items the point needs.

A draft cleared of those eight usually stops reading as generated. Work the
full catalog when the first pass leaves the draft still sounding off, or when
the target is a headline, a work item, or data-bearing prose.

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

### Meta-narration

"This post argues," "the argument here is," "this piece takes the position,"
or a sentence that explains what a name means right after coining it ("The
name says what the table is"). The document narrating itself is filler; state
the claim and let the reader see it. Vale: `MetaNarration.yml`.

### Enumerated parades

Consecutive paragraphs opening "The first is," "The second is," "The third
is." The frame carries no information. Lead each paragraph with the item
itself, or fold the items into one list. Raw check:
`SloptimizerRaw.EnumeratedParade`.

### Count previews

"Four other cases are common enough to test it," "Three arguments place the
table in bronze," "This raises two operational questions." The sentence only
announces how many items follow. Delete it, or name the items in it with a
colon. Vale: `CountPreview.yml`.

### Formulaic headings

"Where X breaks," "Why X is Y," "Why X matters," "What X gets wrong," "Two
things that force Y," "Key takeaways." Templates that could head any section of any post. Name
the section's subject. Raw check: `SloptimizerRaw.FormulaicHeading`.

### Comma-and clause chains

"X is the typed table, and its form is the same for every transport." Two
independent clauses joined with ", and" when a period would do. Split them, or
subordinate one clause. Strict raw check: `SloptimizerStrict.CommaAndChain`.

### Framing openers

"With the boundary placed," "With that settled," "With the groundwork done,"
opening a sentence. The phrase points backward and carries nothing. Delete it
and start with the subject. Vale: `FillerTransition.yml`.

### Unscoped tool behavior

A specific product's behavior stated as a general fact: "snapshot mode replaces
append" when only one tool has a snapshot mode. Name the tool and the case the
behavior applies to ("in tablespec, for untyped sources"). Editorial; a
generated draft drops the scope because the model knows the tool and the reader
does not.

### Real names in examples

A colleague's, customer's, or author's name as an example value ("Jarrett",
"Acme Health"). Use an obvious placeholder ("John Doe") so the example cannot be
read as a record. Editorial.

### Coined-term triplets

A three-adjective definition ("typed, validated, deduplicated") repeated every
time the coined term appears. Define the term once, then use the name. This is
the rule-of-three pattern applied to a single concept, and Vale does not own it
because the same triple can be a legitimate subject ("bronze, silver, and
gold").

### Mannered prose

Metaphor or flourish standing in for a direct statement: "a dial worth
turning" for a parameter to try, "earns its keep" for still matters, "does the
heavy lifting", "under the hood", "moves the needle", "table stakes",
"a first-class citizen". The phrase displays the writer instead of carrying
the idea,
and it is imprecise: the metaphor drags in connotations the writer did not
choose. Say what you mean. Name the thing, the action, or the number.

The rewrite target is what a person would write, not the literal gloss of
the metaphor. "A parameter worth varying" is the gloss of "a dial worth
turning", and no one writes it either; the "X worth Y-ing" frame announces
value instead of stating it (Vale: `ReaderSteeringPhrases.yml`). Write the
action: "Try batch sizes 8 through 64 before the full run."

```text
Mannered: The alignment check earns its keep on every review.
Gloss:    The alignment check is still worth running on every review.
Plain:    The alignment check caught 3 of the 4 drift cases in the last review.
```

Keep a metaphor the writer chose to make a distinction the literal phrase
cannot make, once, in their own voice; see the guardrail in
`references/density-voice.md`. Cut the stock one that any model would reach
for. Related: false agency (the concept doing a human verb), fake-profound
kickers (the metaphor as closing line), importance puffery. Vale:
`ManneredProse.yml` for sentence prose; `SloptimizerHeadline.Mannered` reuses
the same phrase list for titles.

This pattern is model-neutral. To ask any model for the same thing directly,
add to the prompt:

```text
Remove all mannered prose. Mannered prose substitutes metaphor and flourish
for direct statement ("a dial worth turning" for a setting to try, "earns
its keep" for still matters). The phrase exists to display the writer, not
to convey the idea, and it is imprecise because the metaphor carries
connotations the writer did not choose. Say what you mean: when a plain
phrase is available, use it, and prefer the concrete action or number over
an evaluative frame such as "worth varying".
```

### Headline slop

Titles carry the same tells in compressed form: a contrastive reversal ("a
methodology you adopt, not a platform you join"), a colon list ("Three
failures repeat: drift, local decisions, lost context"), an imperative chain
("Write the brief, check alignment, plan the work"), a listicle count ("Five
things change"), stacked negation ("no runtime, no tracker, and no
technology choice"), flattery ("your best teams", "we hold ourselves to"),
the slogan ("X is the new Y"), and the mannered phrase ("Documentation earns
its keep"). Sentence checks skip headings, so these
have their own rules and rewrite procedure in `references/headlines.md`. Raw
check: `SloptimizerHeadline.*` from `scripts/headline-audit.py`.

## When The Pattern Is Fine

Every editorial pattern above has a legitimate twin. Flagging one of these is
a false positive, and rewriting it is the over-editing that the
proportional-cutting principle in `references/eval.md` exists to catch.

| Pattern | Legitimate twin |
|---|---|
| Binary contrast | A real distinction the reader would otherwise get wrong: "The check runs at merge, not at push." |
| Colon reveal | A label, list, quote, ratio, or definition: "Exit code 2: bad arguments." |
| Dramatic fragmentation | The writer's established cadence, or a short answer carrying weight: "Nobody did." |
| Forced group of three | A subject with exactly three members: "bronze, silver, and gold". |
| Repeated sentence opening | A deliberate parallel that makes items comparable: three requirements each opening "The worker must". |
| Hollow intensifier | A named contrast the word works for: "the query is slow, but the write path is genuinely broken". |
| Mannered prose | An image the writer chose to draw a distinction the plain phrase cannot make, used once. |
| Meta-narration | Reference documentation that must orient the reader: "This section describes the retry contract." |
| Count preview | A number the reader needs up front, when the list is long or split across sections. |
| Universal claim | A claim the draft then scopes or proves with a number. |

The test is whether the phrasing does work the plain version cannot. When it
does, leave it alone and say so in the change summary rather than preserving
it silently.

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
