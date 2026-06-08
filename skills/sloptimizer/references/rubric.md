# Sloptimizer Rubric

## Remove Or Repair

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
- Repeated paragraph openings that make prose sound templated.

## Replacement Standard

Every retained sentence should do at least one job:

- Name a decision, risk, constraint, actor, or artifact.
- State an input, output, command, test, interface, or observable behavior.
- Explain why a choice follows from evidence.
- Delimit scope or non-scope.

## Rewrite Pattern

1. Delete claims that add no testable information.
2. Replace adjectives with specifics.
3. Name the actor and operation.
4. Add evidence when a claim matters.
5. Split overloaded sentences.

Example:

```text
Before: This provides a robust and seamless workflow for managing tasks.
After: The workflow lists ready tasks, shows blocked tasks with blocker names,
and lets the operator start a worker from the queue view.
```

