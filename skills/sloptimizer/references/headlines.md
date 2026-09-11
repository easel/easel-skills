# Headlines

Use this reference when the target is a `headline`: a deck or slide title, a
section heading, a one-line claim, or a titles-only outline. A headline is
read on its own, out loud, and in sequence with its neighbors, so the tells
that pass in a paragraph stand out in a title, and the sentence-level checks
in the Vale pack never see it (they exclude headings, and a headline has no
terminal punctuation for a sentence splitter to work with).

## Detect

`scripts/headline-audit.py` owns these rules (`SloptimizerHeadline.*`). Each
runs on every Markdown heading in `slop-audit.sh`, and on every line with
`--all-lines` or `slop-audit.sh --target headline`. Name the rule in detect
findings.

| Rule | Tell | Example |
|---|---|---|
| `ContrastiveReversal` | The claim is made by denying its opposite: a trailing `, and Y is not`; `X, not a Y`; `Not a X, a Y`; `not just X but Y`; `isn't X; it's Y`; `Less X, more Y`. | "a methodology you adopt, not a platform you join" |
| `ColonList` | Label, colon, then two or more comma-separated items. The list is the body, not the title. | "Three failures repeat: drift, local decisions, lost context" |
| `ColonReveal` | Label, colon, then a reveal. Clock times and ratios (`10:30`, `3:1`) are exempt. | "The best part: it learns" |
| `ImperativeChain` | Three or more comma-separated clauses that each open with an imperative verb. | "Write the brief, check alignment, plan the work, run it" |
| `Listicle` | A count of a generic container noun (`things`, `reasons`, `ways`, `lessons`, `signs`). A count of a concrete noun (`3 findings`, `two conditions`) is fine. | "Five things change once the catalog is in place" |
| `StackedNegation` | Two or more of `no`, `not`, `never`, `nothing`, `without`, `n't`. | "no runtime, no tracker, and no technology choice" |
| `Triplet` | `A, B, and C` (or `or`) packaging in one line. | "no runtime, no tracker, and no technology choice" |
| `Flattery` | A compliment to the reader in place of a fact: `your best teams`, `teams like yours`, `we hold ourselves to`, `you already know`, `world-class`. | "the discipline your best teams already use" |
| `Aphorism` | A slogan shape: `X is the new Y`, `the only X that matters`, a trailing `wins` or `matters`, `at scale`, `done right`, `changes everything`. | "Documentation is the new code review" |
| `UniversalClaim` | A bare group noun as subject with a behavior verb (`Teams switch`, `Users want`), or `every`/`all` + a group noun, with no scope or number. | "Teams switch when every change traces back" |
| `Length` | More than 12 words (`--max-words`). The target is under 10. | any 13-word title |

The audit is a suggestion, not proof. A title can pass every rule and still be
a label; a title can trip `Triplet` on a legitimate three-item subject. Read
the findings against the rewrite procedure below before editing.

## Rewrite

A headline is one sentence with a subject, a verb, and an object, under 10
words if it can be, and it answers "so what" for the audience named in the
brief. Rewrite in this order:

1. **Find the claim.** Ask what the slide or section proves. If the body
   holds a number, the number goes in the title (`under 3 findings per run`,
   `$180M is reachable`). If the body holds no number and no checkable fact,
   the problem is the body, not the title.
2. **Name one concrete noun as the subject.** The artifact, the metric, the
   actor, the cost. Not `things`, `failures`, `the practice`, `teams` in
   general. Drop the reader-compliment and the group generalization; keep
   the fact the reader can check.
3. **Pick one plain verb.** Catches, costs, traces, ships, averages, fails.
   One imperative is fine for an ask (`Approve the pilot budget`); two joined
   by `and` are fine when the ask really has two decisions; three is a
   process slide pretending to be a title.
4. **Delete the reversal.** State the positive half. `X, not Y` becomes the
   claim about X with the number or mechanism that makes it true. If the
   contrast is the point, put it in the body as two rows.
5. **Delete the colon and the list.** Keep the one item the unit proves; the
   other items are bullets, a table, or their own units.
6. **Say what it does, never what it is not.** `no runtime, no tracker`
   becomes `runs on the runtime and tracker you own`.
7. **Read the titles in sequence.** Each title should share a word or an
   idea with the one before it, and the sequence alone should carry the
   story spine (situation, complication, resolution, proof, ask). A title
   that does not connect to its neighbor is in the wrong place or makes the
   wrong claim.
8. **Re-run the audit** on the rewritten set with `--target headline` and
   fix what it still flags before touching bodies.

Before and after, from one deck:

```text
Before: HELIX takes no runtime, no tracker, and no technology choice away from you
After:  HELIX runs on the runtime and tracker you own

Before: Five things change once the catalog and the alignment skill are in place
After:  Alignment reviews audit documents instead of chat transcripts

Before: Fewer than 3 alignment findings per run is the health bar we hold ourselves to
After:  A healthy document set averages under 3 findings per run
```

## Validate

The pass is `detect`, `rewrite`, `validate`, on the titles alone and before
the bodies are written or edited:

```bash
scripts/slop-audit.sh --target headline titles.md   # or the deck script itself
```

On a deck script whose unit titles are Markdown headings, the default
`slop-audit.sh <script>` already runs the headline rules on every heading.
