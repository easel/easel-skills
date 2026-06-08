---
name: sloptimizer
description: Audit AI-generated prose, plans, specs, prompts, and work items by removing vague claims, filler, generic phrasing, missing actors, weak acceptance criteria, and unsupported implementation promises. Use when asked to reduce AI slop, tighten writing, make a task executable, harden a spec, or run Vale-backed prose checks.
---

# Sloptimizer

Use this skill to turn vague AI-shaped output into specific, evidence-bearing
writing and executable work.

## Workflow

1. Classify the target:
   - `prose`: docs, posts, summaries, PR descriptions.
   - `work-item`: tasks, tickets, implementation prompts.
   - `plan`: staged technical plans or specs.
   - `review`: completed output being checked against intent.
2. Run deterministic checks when files are available:
   - Use `scripts/slop-audit.sh <paths...>` for Vale-backed prose findings.
   - Use `scripts/slop-audit.sh --changed` when the user asks about changed
     files in a git repo.
   - Use `scripts/redundancy-audit.py <paths...>` when the draft set may repeat
     the same point across files or sections.
3. Apply the rubric:
   - Load `references/rubric.md` for prose and specificity checks.
   - Load `references/work-items.md` for task or acceptance-criteria cleanup.
   - Load `references/vale.md` when installing, pinning, or debugging Vale.
4. Rewrite only when the edit adds clarity or executability. Preserve correct domain
   terms, headings, commands, paths, identifiers, tables, and legitimate lists.
5. When local tools are present, optionally use adapters:
   - `references/adapters-ddx.md` for DDx repositories.
   - `references/adapters-helix.md` for HELIX-governed artifacts.

## Output Rules

- Prefer concrete edits over commentary.
- Prefer the exact domain noun, field, artifact, command, status, metric, or
  constraint over a broad synonym.
- Replace broad adjectives with observable facts or delete them.
- State actors, actions, inputs, outputs, evidence, and non-scope.
- Flag unsupported claims instead of inventing justification.
- For work items, make the task executable by a competent agent using only the
  item text.

## Dependency Policy

The core skill requires no DDx, Fizeau, HELIX, Node, or Python dependency.
Vale is the supported deterministic checker and is owned by this skill. Git is
used only for `--changed` mode. Product tools are optional adapters.
