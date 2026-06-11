# Optional HELIX Adapter

Use this when the project has HELIX artifacts such as feature, contract,
design, ADR, or migration documents. HELIX is read as methodology context, not
as a runtime dependency.

## Checks

- The implementation plan traces to the governing artifact.
- Acceptance criteria cover the contract or feature behavior.
- Migration work names source and destination artifacts.
- Risks and non-scope are explicit.
- Terminology matches the governing document.
- Claims stay inside the artifact's authority: PRDs state product scope, ADRs
  record decisions, test plans name verification strategy, and work items track
  execution.
- Rewrites preserve IDs, paths, artifact names, commands, metrics, statuses,
  acceptance criteria, trace links, non-scope, risks, assumptions, and open
  questions.
- Unsupported claims about tests, metrics, coverage, validation, or ratchets are
  flagged unless the text names the backing evidence.

## Rewrite Rule

Do not make a HELIX artifact sound more polished at the expense of authority.
Prefer precise traceability, file paths, commands, and acceptance checks over
smooth prose.

If a HELIX work item cannot be made measurable from the governing artifact,
return `NOT_EXECUTION_READY` rather than inventing missing acceptance detail.

## Useful Project Gates

When present, use the project's own gates as evidence:

```bash
just lint-prose
just check-prose-redundancy
just validate-artifact-schemas
just test-website-generated
git diff --check
```

These commands are optional. Sloptimizer must still work when HELIX tooling is
not installed.
