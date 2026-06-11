# Lifecycle

Planning is a lifecycle, not a single artifact. Choose the entry point that
matches the user's request and move forward only as far as authorized.

## Stages

1. Research: gather local and external evidence needed to make the plan sound.
2. Draft: define goal, scope, work breakdown, dependencies, risks, validation,
   and open questions.
3. Refine: remove ambiguity, split overloaded tasks, tighten acceptance
   criteria, and identify missing decisions.
4. Review: use adversarial review when the plan has release, migration, data,
   security, multi-agent, cost, or schedule risk.
5. Handoff: convert the plan into executable tasks or agent prompts with clear
   inputs, outputs, validation, and non-scope.
6. Execute: only after user authorization. Execution may require other skills
   but should preserve the plan's constraints.
7. Post-review: compare implementation to the plan, record deviations, validate
   outcomes, and create follow-ups.

## Gates

- Research gate: enough evidence exists to choose an approach, or unresolved
  uncertainty is visible.
- Readiness gate: each task has inputs, expected output, validation, and
  non-scope.
- Review gate: blocking findings are resolved, rejected with evidence, or
  explicitly accepted as risk.
- Execution gate: the user has authorized mutation, release, publication, or
  other side-effecting work.
- Completion gate: validation evidence and deviations are documented.

## Stopping Criteria

Stop refining when the next revision would only restate known decisions, all
blocking questions have an owner or assumption, and the plan can be executed by
a competent agent without hidden context.

Continue refining when tasks overlap, validation is missing, risks are vague,
dependencies are implicit, or two competent implementers would make materially
different choices.
