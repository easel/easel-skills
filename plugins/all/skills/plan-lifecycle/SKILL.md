---
name: plan-lifecycle
description: Create, refine, review, and evolve implementation plans, release plans, test plans, migration plans, data plans, research plans, and work breakdowns through research, iteration, delegation, adversarial review, execution readiness, and post-implementation review. Use when asked to plan work, review this plan, refine this plan, make a release plan, make a test plan, break down work, turn findings into a plan, or compare implementation results against the original plan.
when-to-use: plan work, review this plan, refine this plan, make a release or test plan, break down work, or compare implementation results against the original plan
metadata:
  short-description: "Plan, refine, review, and hand off work"
  author: Easel
---

# Plan Lifecycle

Use this skill as the planning-work gateway. It coordinates narrower skills
when a plan needs evidence, critique, release discipline, test strategy, data
workflow design, repository context, or prose hardening.

## Operating Stance

Act as a pragmatic planning lead. Turn intent into executable work, expose
assumptions and decision points, delegate specialized checks to the right skill,
and keep the plan lifecycle visible from research through post-implementation
review.

## Workflow

1. Classify the planning request:
   - `create`: draft a plan from a goal, issue, findings, or repo state;
   - `refine`: improve sequencing, scope, acceptance criteria, or handoff;
   - `review`: critique an existing plan before work starts;
   - `breakdown`: split work into milestones, tasks, owners, or agent prompts;
   - `post-review`: compare finished work against the plan and capture gaps.
2. Clarify the plan boundary:
   - goal, non-goals, target artifact, audience, constraints, and deadline;
   - current lifecycle stage and whether the user wants execution or planning
     only;
   - validation evidence required before work is considered ready.
   If the boundary is unclear, ask a concise question or state assumptions and
   continue.
3. Route specialized work:
   - research or external facts: use `research-review`;
   - local repo state or branch scope: use `repo-triage`;
   - release plans: use `release-management`;
   - test plans and acceptance checks: include explicit validation strategy and
     ask `adversarial-review` to critique gaps when risk warrants;
   - data validation, documentation, or mapping plans: use `data-quality`,
     `data-documentation`, or `data-mapping`;
   - plan critique: use `adversarial-review`;
   - wording, acceptance criteria, or task executability: use `sloptimizer`.
4. Build or revise the plan:
   - state objective, scope, assumptions, dependencies, risks, and decisions;
   - sequence work into phases or tasks with clear entry and exit criteria;
   - include validation, rollback or recovery, and handoff expectations;
   - mark optional, deferred, and explicitly out-of-scope work.
5. Review the plan before execution:
   - run lightweight self-review for routine work;
   - use `adversarial-review` for release, migration, test, data, multi-agent,
     irreversible, or high-cost plans;
   - incorporate findings only when they are evidence-backed.
6. Support execution handoff only when the user asks to proceed. Planning does
   not imply permission to mutate files, publish releases, push commits, or run
   destructive operations.
7. After implementation, compare delivered work to the plan:
   - completed, changed, skipped, or newly discovered work;
   - validation evidence and gaps;
   - follow-up tasks, documentation updates, and release notes if needed.

## References

- `references/delegation.md`: routing table for common plan types and related
  skills.
- `references/plan-shapes.md`: concise output formats for implementation,
  release, test, research, data, and post-implementation plans.
- `references/lifecycle.md`: deeper lifecycle guidance, gates, and stopping
  criteria.

## Deterministic Check

When producing a Markdown plan artifact, run:

```bash
python3 scripts/check_plan.py path/to/plan.md
```

The script checks for core plan sections. It does not verify technical
correctness.

## Output Rules

- Distinguish planning, review, and execution permissions.
- Prefer concrete tasks, validation commands, acceptance criteria, owners or
  responsible agents, and dependencies over generic phases.
- When delegating, name the skill and the reason.
- Preserve unresolved questions and assumptions instead of hiding them in the
  plan.
- For "review this plan", lead with findings and use `adversarial-review` when
  risk, release, migration, test, or data consequences justify a critic.
