# Easel Skills Agent Instructions

This repository contains reusable agent skills. Keep skills portable unless a
skill explicitly declares an integration dependency.

## Dependency Direction

- Easel skills must not depend on DDx, Fizeau, HELIX, or any product-specific
  runtime by default.
- Product integrations may live as optional adapters inside a skill.
- DDx, Fizeau, and other tools may depend on, vendor, or wrap Easel skills.

## Skill Authoring

- Every skill must have a top-level `SKILL.md` with `name` and `description`
  YAML frontmatter.
- Keep `SKILL.md` concise. Move detailed rubrics, adapter instructions, and
  examples into `references/`.
- Put deterministic checks in `scripts/` or `assets/` rather than rewriting
  them in prose.
- Use generic vocabulary in core skill files. Product-specific terms belong in
  adapter references.

## Verification

- Validate syntax after editing skills:

```bash
for skill in skills/*/; do
  python3 /home/erik/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"
done
```
