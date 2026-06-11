# Optional DDx Adapter

Use this only when the target repository has `.ddx/` and the `ddx` CLI is
available. Sloptimizer must still work without DDx.

## Useful DDx Checks

```bash
ddx bead lint <id>
ddx bead validate-ready <id>
ddx bead ac-check <id>
ddx bead review <id> --prose
ddx doc prose
```

## Adapter Rules

- Treat DDx bead text as a generic work item plus DDx-specific metadata.
- Never edit `.ddx/beads.jsonl` manually.
- Use DDx commands for tracker mutations.
- Keep sloptimizer findings separate from DDx operator-attention or execution
  state unless the user explicitly asks to file work.
