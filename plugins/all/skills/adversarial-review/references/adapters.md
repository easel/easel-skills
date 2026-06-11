# Optional Review Adapters

The core skill does not require DDx, Fizeau, or any specific harness. Use these
adapters only when the tool exists locally.

## Direct Harnesses

Use direct commands when available. Keep each reviewer independent and write
outputs to separate files.

```bash
codex exec "$(cat review-target.md)" > findings-codex.md
claude -p "$(cat review-target.md)" > findings-claude.md
```

Adjust command flags for the local harness. The important constraints are:

- same target prompt;
- independent output files;
- no reviewer sees another reviewer's findings before its own pass.

## DDx Adapter

When `ddx` is available, use it as a router rather than a dependency of the
skill:

```bash
ddx run --harness codex --prompt review-target.md > findings-codex.md
ddx run --harness claude --prompt review-target.md > findings-claude.md
wait
```

If the target is a tracked work item, store the final aggregate through the
project's supported evidence mechanism. Do not edit tracker storage manually.

## Fizeau Adapter

When Fizeau is available, use it for model routing or multi-agent execution if
that is the local project's preferred harness layer. Preserve the same output
contract and aggregation rules.
