# Sloptimizer Rubric

## Remove Or Repair

<!-- vale off -->
- Unsupported quality claims: robust, comprehensive, seamless, powerful,
  production-ready, intuitive, world-class.
- Filler transitions: in conclusion, to be clear, it is important to note,
  moreover, furthermore, at its core, let's dive in.
- Generic substitutes: simply, easily, quickly, efficiently, effectively,
  intelligently.
- Missing actor/action phrasing: enables, supports, streamlines, improves,
  facilitates, provides.
- Token-cost padding: in order to, due to the fact that, at this point in time,
  first and foremost.
- Phrase-level AI slop: unlock value, pivotal moment, game-changer, delve into
  (see `references/ai-writing.md` for structural patterns Vale does not own).
- Mannered prose: a stock metaphor or flourish where a plain statement was
  available: earns its keep, a dial worth turning, does the heavy lifting,
  under the hood, moves the needle. Say what you mean.
- Evaluative frames that announce value instead of stating it: a point worth
  making, a parameter worth varying, it is worth noting.
- On slides, invented status vocabulary (portability reference, working
  hypothesis, fit unproven) where a plain state (in use, built, not built)
  was available, and internal taxonomy codes (Zone 6, P3) the audience
  cannot decode.
<!-- vale on -->
- Repeated paragraph openings that make prose sound templated.
- Structural AI tells named in `references/ai-writing.md` (binary contrasts,
  colon reveals, faux-insight setups, dramatic fragments, chatbot residue,
  meta-narration, enumerated parades, count previews, formulaic headings, comma-and clause chains, framing openers,
  unscoped tool behavior, real names in examples).
- Slide tells named in `references/slides.md` (container titles,
  self-justifying sections, aphoristic closers, restatement stacks, trailing
  commentary, shouting labels).

## Replacement Standard

Every retained sentence should do at least one job:

- Name a decision, risk, constraint, actor, or artifact.
- State an input, output, command, test, interface, or observable behavior.
- Explain why a choice follows from evidence.
- Delimit scope or non-scope.

## High-Density Prose

All prose rewrites should optimize for consequence per word rather than
shortness by itself. Requests to make writing tight, dense, compressed, or
"unsummarizable" intensify the density pass but do not change the basic
standard. Treat "unsummarizable" as a direction: the rewrite should be hard to
summarize without losing meaning, not stripped to the minimum.

Target 3 on the verbosity scale in `references/density-voice.md`, which owns
that calibration and states what survives at 3. Keep headroom for flow,
rhythm, and voice; do not drive to the terse minimum unless the user asks.

Keep words that:

- Add an idea, example, mechanism, evidence, image, contrast, or consequence.
- Preserve a distinction a summary would flatten.
- Make the writer's judgment more specific.
- Help a reader infer what is new, disputed, surprising, or costly.
- Carry voice, rhythm, or meter that a flat rewrite would lose.

Cut or rewrite words that:

- Announce the point before making it.
- Repeat a nearby idea with weaker nouns or broader verbs.
- Add politeness or transition that changes no meaning and carries no rhythm.
- Summarize what the next sentence already proves.

Do not compress away useful texture. Dense prose can be longer than a terse
summary when each added word carries information, tension, evidence, or voice.

## Precise Vocabulary

Tight vocabulary preserves context for every downstream reader, reviewer, and
agent. Prefer the exact noun that the surrounding system already uses.

- Use the real artifact, file, command, field, status, metric, role, or
  constraint name when it exists.
- Avoid swapping in broad synonyms for variety. If the source says "acceptance
  criterion", do not rewrite it as "requirement", "check", or "quality bar"
  unless that is the intended meaning.
- Replace value language with consequences: what changes, what is blocked, what
  is measured, or what evidence proves the claim.
- Use the plain phrase when one exists. A metaphor stands in for a literal
  claim only when the writer chose it to draw a distinction the plain phrase
  cannot; the stock metaphor any model reaches for ("does the heavy
  lifting") is mannered prose, and its literal gloss ("a parameter worth
  varying") is not the target either. Write the action, the thing, or the
  number a person would write.
- Name uncertainty as an open question, assumption, risk, or blocker. Do not
  hide it behind hedges.

## Unsupported Claims

Flag claims as unsupported when they assert evidence without naming it:

<!-- vale off -->
- Tests, metrics, coverage, audits, benchmarks, or validation exist.
- A feature is production-ready, scalable, reliable, secure, or complete.
- A change preserves compatibility, behavior, performance, or user experience.
- A process is automated or enforced.
<!-- vale on -->

Do not invent backing evidence. Either add the cited command, test, artifact,
metric, or log line from the available context, or weaken/delete the claim.

## Rewrite Pattern

1. Delete claims that add no testable information.
2. Replace adjectives with specifics.
3. Name the actor and operation.
4. Add evidence when a claim matters.
5. Split overloaded sentences.

Example:

<!-- vale off -->
```text
Before: This provides a robust and seamless workflow for managing tasks.
After: The workflow lists ready tasks, shows blocked tasks with blocker names,
and lets the operator start a worker from the queue view.
```
<!-- vale on -->
