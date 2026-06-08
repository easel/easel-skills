---
name: adversarial-review
description: Pressure-test a plan, spec, prompt, work item, code change, or PR by asking one or more independent model harnesses to find blocking issues, contradictions, missing constraints, and rework risks. Use for high-stakes design review, cross-model critique, or multi-round validation before implementation.
---

# Adversarial Review

Use this skill when ordinary review is not enough and the work needs a critic,
not a validator.

## Workflow

1. Prepare a target prompt containing:
   - the artifact under review;
   - the review question;
   - relevant governing artifacts or constraints;
   - the output contract below.
2. Select independent reviewers:
   - direct `codex`, `claude`, or other local harness commands when available;
   - optional adapters from `references/adapters.md` when DDx or Fizeau is
     available.
3. Run reviewers independently. Prefer different model families when cost is
   justified.
4. Aggregate findings:
   - any `BLOCKING` finding stops the work;
   - matching `WARNING` findings from two reviewers become blocking;
   - disagreements must be shown explicitly;
   - invalid findings lack evidence and should be discarded.
5. Revise the target and rerun until there are no unresolved blocking findings.

## Prompt Contract

Include this instruction in every review prompt:

```text
You are a critic, not a validator. Find implementation rework risks,
contradictions, missing constraints, ambiguous interfaces, hidden assumptions,
and places where two competent implementers would make different choices.
Do not balance criticism with praise.
```

Require this output shape:

```markdown
### Findings

| Severity | Area | Evidence | Finding |
|---|---|---|---|
| BLOCKING | <area> | <line/section/gap> | <specific issue> |
| WARNING | <area> | <line/section/gap> | <specific issue> |
| NOTE | <area> | <line/section/gap> | <specific issue> |

### Verdict: APPROVE | REQUEST_CHANGES | BLOCK

### Summary
<2-4 sentences>
```

## Anti-Patterns

- Asking one model for an "adversarial review" and treating that as quorum.
- Accepting findings with no cited evidence.
- Collapsing disagreement into a blended summary.
- Running expensive multi-harness review on routine work.
- Stopping after the first round when the target changed materially.

