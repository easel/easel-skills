# Repo Triage Report Shapes

Use these shapes when a repository report needs consistent structure. Keep the
report as short as the request allows.

## Status Snapshot

```markdown
**Repo Status**
- Branch: `<branch>` at `<short-sha>`
- Upstream: `<upstream or none>` (`<ahead>` ahead, `<behind>` behind)
- Worktree: `<clean | dirty>` (`<staged>` staged, `<unstaged>` unstaged, `<untracked>` untracked)
- Recent commits: `<n>` shown

**Changes**
- Staged: `<paths or count>`
- Unstaged: `<paths or count>`
- Untracked: `<paths or count>`

**Notes**
- `<missing refs, detached HEAD, no upstream, submodules, or command limits>`
```

## Branch Vs Base

```markdown
**Branch Comparison**
- Head: `<branch>` at `<short-sha>`
- Base: `<base-ref>` at `<short-sha if available>`
- Merge base: `<short-sha or unavailable>`
- Ahead/behind: `<ahead>` ahead, `<behind>` behind

**Committed Changes**
- Commits ahead of base: `<subjects or count>`
- Files changed vs base: `<paths or count>`

**Dirty Worktree**
- `<clean | staged/unstaged/untracked paths that are not necessarily in the branch comparison>`

**Caveats**
- `<local-only refs, no fetch performed, hosting context unavailable>`
```

## Pre-PR Triage

```markdown
**Pre-PR Triage**
- Branch/base: `<branch>` -> `<base>`
- Local state: `<clean | dirty summary>`
- Ahead/behind: `<ahead>` ahead, `<behind>` behind
- Files changed: `<count>` across `<areas>`
- Recent commits: `<subjects>`

**Review Focus**
- `<likely code areas or files to inspect>`

**Before Publishing**
- `<tests not run, untracked files, missing upstream, unresolved local changes>`
```

## PR Or Issue Context

Use this only when hosting tools are available.

```markdown
**Hosting Context**
- Source: `<GitHub/GitLab/etc. tool name>`
- PR/Issue: `<id, title, state>`
- Review/CI status: `<summary if available>`
- Comments or blockers: `<brief evidence-backed summary>`

**Local Context**
- `<local branch/worktree facts gathered separately>`
```

## Severity Labels

- `Blocking`: local state prevents an accurate answer or likely endangers user
  changes if ignored.
- `Needs attention`: dirty worktree, missing upstream, unresolved conflicts,
  diverged refs, or failed tests.
- `Informational`: clean status, expected ahead count, recent commits, or
  hosting metadata.
