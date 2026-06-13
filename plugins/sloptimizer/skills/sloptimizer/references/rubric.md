# Sloptimizer Rubric

## Remove Or Repair

<!-- vale off -->
- Unsupported quality claims: robust, comprehensive, seamless, powerful,
  production-ready, intuitive, world-class.
- Filler transitions: in conclusion, to be clear, it is important to note,
  moreover, furthermore.
- Generic substitutes: simply, easily, quickly, efficiently, effectively,
  intelligently.
- Missing actor/action phrasing: enables, supports, streamlines, improves,
  facilitates, provides.
- Token-cost padding: in order to, due to the fact that, at this point in time,
  first and foremost.
<!-- vale on -->
- Repeated paragraph openings that make prose sound templated.

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

Target dense-but-readable prose: roughly 3 on a 1-10 verbosity scale where 10
is padded, 8 is default assistant prose, and 1 is mechanical telegraph style.
Keep enough headroom for flow, rhythm, and voice; do not drive to the terse
minimum unless the user explicitly asks for that.

At 3/10, prose still has connective tissue, sentence rhythm, and one memorable
detail or contrast when the passage earns it. It drops restatement, hedging,
preface, throat-clearing, and generic summary.

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
