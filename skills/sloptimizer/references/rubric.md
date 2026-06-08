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
