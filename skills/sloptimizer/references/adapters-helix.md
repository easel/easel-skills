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

## Rewrite Rule

Do not make a HELIX artifact sound more polished at the expense of authority.
Prefer precise traceability, file paths, commands, and acceptance checks over
smooth prose.

