# Delegation

Use this table to decide when planning should call on another skill. Keep the
plan lifecycle skill as the orchestrator; delegate domain checks to the
narrower skill and bring the result back into the plan.

| Trigger | Delegate To | Planning Use |
| --- | --- | --- |
| The plan depends on current docs, best practices, libraries, standards, APIs, or external facts. | `research-review` | Establish evidence, compare options, and cite sources before sequencing work. |
| The plan depends on dirty worktree state, branch scope, local diffs, recent commits, or PR context. | `repo-triage` | Define implementation scope, affected files, and user-change risk. |
| The user says release plan, point release, cut release, publish, tag, marketplace, or version bump. | `release-management` | Audit release readiness, version metadata, validation, and authorization boundaries. |
| The user says review this plan, pressure-test, critique, red team, identify risks, or validate before implementation. | `adversarial-review` | Find contradictions, missing constraints, acceptance gaps, and rework risk. |
| The user says test plan, validation plan, acceptance checks, QA plan, coverage, rollout validation, or regression strategy. | `adversarial-review` plus local test evidence | Critique missing cases, unclear acceptance criteria, fixture gaps, and risky untested paths. |
| The plan changes dataset contracts, data validation, expectations, quality gates, or profile-driven checks. | `data-quality` | Convert data constraints into validation work and quality gates. |
| The plan changes table, column, lineage, glossary, dataset, or metric documentation. | `data-documentation` | Define documentation scope, evidence sources, and freshness requirements. |
| The plan maps source fields to target schemas, canonical models, transforms, survivorship, or extraction rules. | `data-mapping` | Define mapping decisions, confidence, conflict policies, and review gates. |
| The plan is vague, AI-shaped, too broad, or weak on actors, artifacts, commands, acceptance criteria, or non-scope. | `sloptimizer` | Tighten wording and make the work executable. |

## Routing Notes

- A release plan should usually include `repo-triage`, `release-management`,
  validation strategy, and `adversarial-review` before publishable actions.
- A test plan should emphasize risk model, coverage boundaries, fixture or
  environment needs, commands, expected evidence, and gaps that need review.
- A data plan should make grain, ownership, constraints, lineage, and
  validation responsibilities explicit.
- A multi-agent plan should assign independent research, implementation, and
  review responsibilities without giving reviewers execution authority.
- Do not spawn subagents unless the user explicitly asks for subagent or
  parallel-agent work in the current request.
