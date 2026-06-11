---
name: repo-triage
description: Inspect and summarize a source repository's local Git state, including dirty worktree status, changed files, branch versus base comparison, recent commits, upstream tracking, ahead-behind counts, and optional PR or issue context when repository tools are available. Use for repo status reports, branch triage, change summaries, pre-PR checks, or understanding what work is in progress without modifying the worktree.
---

# Repo Triage

Use this skill to answer repository-state questions from local evidence first.
Network and hosting integrations are optional; never require them for basic
triage.

## Operating Stance

Act as an operator doing local triage. Report what is true now, distinguish
committed branch state from dirty worktree state, protect user-owned changes,
and call out blockers or uncertainty without mutating the repository.

## Ground Rules

- Do not overwrite, revert, clean, stash, checkout, reset, merge, rebase, or
  otherwise mutate user changes unless the user explicitly asks.
- Treat dirty worktree changes as user-owned. Report them clearly and work
  around them.
- Prefer local commands: `git status`, `git branch`, `git log`, `git diff`,
  `git rev-parse`, `git merge-base`, and `git for-each-ref`.
- Do not run `git fetch`, contact remotes, or use GitHub/GitLab tools unless
  the user asks for remote context or the request cannot be answered locally.
- If hosting tools are unavailable, say so briefly and continue with local
  facts.

## Workflow

1. Identify the repo root and current branch.
2. Collect local state:
   - dirty worktree and staged changes;
   - changed files, including untracked files;
   - current HEAD and recent commits;
   - upstream tracking branch and ahead-behind counts when configured.
3. For branch-vs-base questions, choose the base in this order:
   - explicit user-provided ref;
   - configured upstream branch;
   - repo default branch if it is known locally;
   - `main`, then `master`, when those refs exist locally.
   If none is available, state that no reliable local base was found instead of
   inventing one.
4. Compare with the selected base using local refs only:
   - merge base;
   - commits ahead and behind;
   - files changed relative to base;
   - notable staged or unstaged changes not included in committed comparison.
5. Add PR or issue context only when appropriate tools are already available.
   Keep that context separate from local Git facts and note whether it came from
   a network-backed source.
6. Return a concise report. For structured report options, load
   `references/report-shapes.md`.

## Deterministic Snapshot

When a repeatable local snapshot is useful, run:

```bash
python3 skills/repo-triage/scripts/repo_snapshot.py [--base <ref>] [--limit 8]
```

The script is read-only and emits JSON for local Git state. Use it as evidence,
then summarize the results for the user instead of dumping raw JSON unless they
ask for machine-readable output.

## Output Rules

- Lead with the repo's current state and any risk to user changes.
- Mention the base ref used for comparisons.
- Separate committed branch differences from dirty worktree changes.
- Use exact paths, refs, and counts where available.
- State the inspection boundary, especially when no fetch or hosting lookup was
  performed.
- If a command fails because refs are missing or the directory is not a Git
  repo, report the limitation instead of guessing.
