# Easel Skills Agent Instructions

This repository contains reusable agent skills. Keep skills portable unless a
skill explicitly declares an integration dependency.

## Dependency Direction

- Easel skills must not depend on DDx, Fizeau, HELIX, or any product-specific
  runtime by default.
- Product integrations may live as optional adapters inside a skill.
- DDx, Fizeau, Grok, and other tools may depend on, vendor, or wrap Easel
  skills.

## Skill Authoring

- Every skill must have a top-level `SKILL.md` with `name` and `description`
  YAML frontmatter. Prefer also setting `when-to-use` and
  `metadata.short-description` for harness discovery UI.
- Keep `SKILL.md` concise. Move detailed rubrics, adapter instructions, and
  examples into `references/`.
- Put deterministic checks in `scripts/` or `assets/` rather than rewriting
  them in prose.
- Use generic vocabulary in core skill files. Product-specific terms belong in
  adapter references.
- Document script invocations relative to the skill directory
  (`python3 scripts/…`), not monorepo-rooted paths like
  `python3 skills/<name>/scripts/…`.

## Verification

Edit skills only under `skills/`. Marketplace wrappers under `plugins/*/skills/`
are generated copies. After skill edits:

```bash
bash scripts/prepare.sh
bash scripts/validate.sh
```

`scripts/prepare.sh` regenerates marketplace skill copies and
`.grok-plugin/plugin-index.json`. `scripts/validate.sh` re-runs prepare and
fails if those paths have unstaged drift, then runs package, syntax, and
Sloptimizer checks.

Optionally validate Grok plugin manifests:

```bash
grok plugin validate .
grok plugin validate plugins/all
```

See `plugins/README.md` for the packaging model.
