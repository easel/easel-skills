---
name: sloptimizer
description: Audit and rewrite AI-generated prose, plans, specs, prompts, and work items by removing AI-isms, vague claims, filler, generic phrasing, missing actors, weak acceptance criteria, and unsupported implementation promises. Use when asked to reduce AI slop, make text sound less like AI, tighten writing, make a task executable, harden a spec, audit only, rewrite, or run Vale-backed prose checks.
---

# Sloptimizer

Use this skill to turn vague AI-shaped output into specific, evidence-bearing
writing and executable work.

## Operating Stance

Act as a strict editor and spec hardener. Remove filler, unsupported certainty,
and vague promises; preserve real domain terms; and make the resulting text
usable by a reader, reviewer, or executor without hidden context.

## Workflow

1. Choose the mode:
   - `detect`: flag issues only; do not rewrite.
   - `rewrite`: edit the text and summarize what changed.
   - `validate`: run deterministic checks against available files.
   If the requested mode, audience, or authority to rewrite is unclear, ask a
   concise clarifying question or state the assumed mode.
2. Classify the target:
   - `prose`: docs, posts, summaries, PR descriptions.
   - `work-item`: tasks, tickets, implementation prompts.
   - `plan`: staged technical plans or specs.
   - `review`: completed output being checked against intent.
3. Run deterministic checks when files are available:
   - Use `scripts/slop-audit.sh <paths...>` for Vale-backed prose findings.
   - Use `scripts/slop-audit.sh --profile results <paths...>` for benchmark or
     comparison prose.
   - Use `scripts/slop-audit.sh --profile strict <paths...>` for house-style
     AI-tell checks, including source-level Markdown structure.
   - Use `scripts/slop-audit.sh --changed` when the user asks about changed
     files in a git repo.
   - Use `scripts/redundancy-audit.py <paths...>` when the draft set may repeat
     the same point across files or sections.
4. Apply the rubric:
   - Load `references/rubric.md` for prose and specificity checks.
   - Load `references/ai-writing.md` for AI-ism cleanup, "make this sound less
     like AI", or human-voice rewrites.
   - Load `references/work-items.md` for task or acceptance-criteria cleanup.
   - Load `references/vale.md` when installing, pinning, or debugging Vale.
5. Rewrite only when the edit adds clarity or executability. Preserve correct domain
   terms, headings, commands, paths, identifiers, tables, and legitimate lists.
6. After rewriting, re-audit the changed text or files when practical. Check for
   survivor patterns introduced by the rewrite before returning the result.
7. When local tools are present, optionally use adapters:
   - `references/adapters-ddx.md` for DDx repositories.
   - `references/adapters-helix.md` for HELIX-governed artifacts.

## Output Rules

- Prefer concrete edits over commentary.
- Prefer the exact domain noun, field, artifact, command, status, metric, or
  constraint over a broad synonym.
- Replace broad adjectives with observable facts or delete them.
- State actors, actions, inputs, outputs, evidence, and non-scope.
- Flag unsupported claims instead of inventing justification.
- Preserve cited sources, paths, commands, dates, and constraints that support
  claims; remove only background text that does not affect meaning.
- For work items, make the task executable by a competent agent using only the
  item text.
- For data-bearing prose, scope numbers and comparisons to the dataset, sample,
  run, metric, seed, quantization, source, or other comparability boundary.

## Dependency Policy

The core skill requires no DDx, Fizeau, HELIX, Node, or Python dependency.
Vale is the supported deterministic checker and is owned by this skill. Git is
used only for `--changed` mode. Product tools are optional adapters.
