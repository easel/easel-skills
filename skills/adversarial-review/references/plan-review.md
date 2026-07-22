# Lightweight Plan Review

Use this reference when a plan, prompt, work item, or output contract needs a
fresh critique before execution. This is a review workflow, not an execution
workflow.

## Review Boundary

The reviewer may:

- identify contradictions, missing constraints, ambiguous interfaces, hidden
  assumptions, and likely rework;
- cite evidence from the artifact, governing constraints, repository context, or
  reproducible reasoning;
- recommend targeted edits.

The reviewer must not:

- implement the plan;
- rewrite the artifact as a substitute for review;
- run destructive commands or perform the proposed work;
- treat lack of evidence as approval.

## Single-Reviewer Plan Review

Use one reviewer when the artifact is small, the risk is bounded, or the user
asked for a quick fresh pass.

Prompt shape:

```text
Review the plan below before execution. Do not implement it.

Focus on blocking rework risks, contradictions, missing constraints, ambiguous
interfaces, hidden assumptions, and places where two competent implementers
would make different choices.

Only report findings grounded in evidence from the plan, supplied constraints,
repository context, or reproducible reasoning. If the plan is acceptable, say so
with a concise verdict.

Artifact:
<plan, prompt, work item, or contract>

Constraints:
<governing instructions, non-scope, acceptance criteria, files, commands>

Output contract:
<JSON or Markdown contract from output-contracts.md>
```

One reviewer is not quorum. Treat the result as a focused critique unless the
user explicitly asked for a multi-harness review.

## Fresh-Eyes Review With Claude

Use Claude, or another different model family, when the authoring model may have
anchored on its own assumptions. Keep the fresh-eyes reviewer isolated:

- provide the same review brief and constraints;
- do not include the author's private reasoning, previous failed attempts, or
  another reviewer's findings;
- write the result to a separate file or transcript;
- aggregate only after the independent pass is complete.

Example direct harness commands:

```bash
grok -p "$(cat review-target.md)" > findings-grok.md
claude -p "$(cat review-target.md)" > findings-claude.md
```

Adjust flags to the local harness. The required property is independence, not a
specific tool.

## Evidence-Gated Incorporation

Before changing the target, classify each finding:

- `accept`: cites concrete evidence and identifies a real rework risk.
- `reject`: conflicts with a stronger constraint, misreads the artifact, or
  lacks evidence.
- `defer`: valid concern but outside current scope.

Incorporate accepted feedback as explicit edits to the plan, prompt, work item,
or code. Keep the execution decision separate from the review record. If a
finding changes scope, dependencies, schedule, safety posture, or acceptance
criteria, ask for owner confirmation before executing.

## Re-Review Stopping Criteria

Run another review only when one of these is true:

- the artifact changed materially after feedback;
- a blocking finding was accepted and needs verification;
- two reviewers disagree on a blocking issue;
- new governing constraints were added.

Stop when all are true:

- no unresolved `BLOCKING` findings remain;
- accepted findings are reflected in the artifact or explicitly deferred;
- rejected findings have evidence-backed rationale;
- the last review round produced no new material issue;
- further review would repeat the same evidence.
