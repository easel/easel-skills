# AI-Writing Cleanup

This reference folds useful AI-writing cleanup patterns into Sloptimizer so the
skill can handle both deterministic checks and editorial rewrites. It adapts
patterns from the locally installed `avoid-ai-writing` skill and from Easel
work on HELIX, Lucebox, and 7th Sense prose. Keep this provenance visible when
editing or extending the pattern set.

## Modes

- `detect`: flag AI-writing patterns and explain which ones matter in context.
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

## Remove Or Repair

<!-- vale off -->

- Reader-steering labels: "worth noting", "what stands out", "here's what's
  interesting", "the real answer". State the reason or consequence directly.
- Hollow intensifiers: truly, genuinely, really, quite, clearly, obviously.
  Delete them unless they carry a contrast that the sentence names.
- Significance inflation: pivotal moment, game-changer, transformative,
  watershed, future looks bright. Replace with the specific change or delete.
- Hedge stacks: could potentially, may eventually, might ultimately. Pick one
  uncertainty marker and state the condition that would make the claim true.
- Generic future-narrative closers: "may become one of the most important..."
  Replace with a falsifiable prediction or a concrete next step.
- Compulsive rule of three: repeated "A, B, and C" packaging that adds rhythm
  without meaning. Use the number of items the point actually needs.
- Over-structured presentation: bold inline labels, TL;DR badges, and section
  formulas that make every paragraph look generated. Use normal headings,
  prose, or real lists.

<!-- vale on -->

## Rubric-Only Signals

These are judgment calls, not stable Vale rules:

- Paragraphs could be reordered without the reader noticing.
- Every paragraph has the same length and cadence.
- The opening gives broad context before the actual point.
- The voice is sanded flat enough to remove useful human judgment.
- The conclusion summarizes instead of landing a decision, caveat, or next
  action.

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

After rewriting, scan again. Rewrites often introduce fresh filler,
unsupported broad claims, or reader-steering labels while fixing the first set
of issues.
