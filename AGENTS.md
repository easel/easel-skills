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
  YAML frontmatter.
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

After editing skills under `skills/`:

```bash
bash scripts/sync-plugin-skills.sh
python3 scripts/generate-plugin-index.py
bash scripts/validate.sh
```

`scripts/sync-plugin-skills.sh` copies canonical skills into marketplace
wrappers and refreshes relative symlinks under `.agents/skills/` so Grok and
compatible agents discover project skills while working in this repo.

`scripts/generate-plugin-index.py` refreshes `.grok-plugin/plugin-index.json`
for Grok marketplace catalog metadata.

Optionally validate Grok plugin manifests:

```bash
grok plugin validate .
grok plugin validate plugins/all
```

Marketplace wrappers under `plugins/*/skills/` must stay byte-identical to
`skills/`. Prefer editing `skills/` then running the sync script rather than
hand-editing wrapper copies.
