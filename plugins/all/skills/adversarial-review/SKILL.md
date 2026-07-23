---
name: adversarial-review
description: Pressure-test a plan, spec, prompt, output contract, work item, code change, or PR by asking one or more independent model harnesses to find blocking issues, contradictions, missing constraints, and rework risks. Use for lightweight plan review, fresh-eyes critique, high-stakes design review, cross-model critique, or multi-round validation before implementation.
when-to-use: pressure-test a plan, fresh-eyes critique, high-stakes design review, cross-model critique, or multi-round validation before implementation
metadata:
  short-description: "Pressure-test plans with independent critics"
  author: Easel
---

# Adversarial Review

Use this skill when ordinary review is not enough and the work needs a critic,
not a validator. Keep review separate from execution: reviewers identify risks
and evidence; implementers decide and make changes.

## Operating Stance

Act as a critical reviewer. Prioritize defects, contradictions, missing
constraints, ambiguous interfaces, and rework risk. Do not soften findings with
general praise, and do not become the implementer unless the user starts a
separate execution step.

## Workflow

1. Choose the review depth:
   - `single-reviewer`: one critic reviews a plan, prompt, or work item before
     execution.
   - `fresh-eyes`: a different model family reviews the same brief without
     seeing the author's reasoning.
   - `multi-harness`: multiple independent reviewers validate high-risk work.
   Keep the reviewer count proportional to risk, cost, and time.
2. Prepare a review brief containing:
   - the artifact under review;
   - the review question;
   - relevant governing artifacts or constraints;
   - explicit non-scope and the instruction not to implement;
   - an output contract from `references/output-contracts.md`.
   If the review question, artifact boundary, or acceptance bar is unclear, ask
   a concise clarifying question or state the assumed boundary before review.
3. Select independent reviewers:
   - direct local harness commands when available;
   - optional adapters from `references/adapters.md`.
4. Run reviewers independently. Prefer different model families when cost is
   justified.
5. Aggregate findings:
   - any `BLOCKING` finding stops the work;
   - matching `WARNING` findings from two reviewers become blocking;
   - disagreements must be shown explicitly;
   - findings without artifact evidence, constraint evidence, or reproducible
     reasoning are discarded.
   Keep only evidence that changes the verdict, severity, or required action.
6. Incorporate feedback only when evidence-gated. The implementer edits the
   plan, prompt, or code; the reviewer does not execute the plan.
7. Re-review only material changes or unresolved blocking findings. Stop when
   the artifact is unchanged, all blocking findings are resolved or rejected
   with evidence, and another round would only restate prior concerns.

## References

- `references/plan-review.md`: lightweight plan review, fresh-eyes review,
  evidence gates, and stopping criteria.
- `references/output-contracts.md`: exact JSON and Markdown verdict prompt
  contracts.
- `references/adapters.md`: optional local harness and product adapters.

## Core Prompt

Include this instruction in every review prompt:

```text
You are a critic, not a validator. Find implementation rework risks,
contradictions, missing constraints, ambiguous interfaces, hidden assumptions,
and places where two competent implementers would make different choices.
Do not implement the plan or rewrite the artifact unless explicitly asked for a
separate execution step. Do not balance criticism with praise.
```

## Anti-Patterns

- Asking one model for an "adversarial review" and treating that as quorum.
- Accepting findings with no cited evidence.
- Collapsing disagreement into a blended summary.
- Letting the reviewer execute the plan, edit the target, or hide the decision
  boundary between review and implementation.
- Running expensive multi-harness review on routine work.
- Stopping after the first round when the target changed materially.
