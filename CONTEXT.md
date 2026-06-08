# Easel Skills

Easel is the upstream home for reusable agent skills that should work across
Codex, Claude, DDx, Fizeau, and plain local repositories.

## Design Rules

- Core skills are dependency-light and product-neutral.
- Optional adapters can use local tools when present.
- Deterministic tooling is preferred for repeatable checks.
- Skills should make execution artifacts more specific without requiring a
  work tracker, methodology, or agent harness.

## Initial Skills

- `sloptimizer`: removes AI slop from prose, plans, specs, and work items.
- `adversarial-review`: runs structured pressure tests across one or more
  model harnesses and aggregates findings.

## Integration Model

DDx may depend on Easel skills, ship pinned copies, or add adapters. Easel does
not depend on DDx. If a DDx-specific change is useful generally, upstream it
here; if it is product-specific, keep it in DDx.
