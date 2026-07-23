---
name: release-management
description: Plan and execute software releases by auditing repository state, version metadata, validation commands, marketplace or package manifests, commits, tags, and pushes. Use when asked to prepare a release, cut a point release, verify release readiness, update marketplace metadata, or commit/tag/push release changes.
when-to-use: prepare a release, cut a point release, verify release readiness, update marketplace metadata, or commit/tag/push release changes
metadata:
  short-description: "Audit and execute deliberate software releases"
  author: Easel
---

# Release Management

Use this skill to make releases deliberate and auditable. Default to an audit
or dry run. Commit, tag, publish, or push only when the user explicitly asks.

## Operating Stance

Act as a release manager. Protect user changes, verify version and marketplace
consistency before publishing steps, prefer dry-run evidence over assumptions,
and treat commits, tags, pushes, and publication as explicit authorization
boundaries.

## Workflow

1. Identify the release target:
   - current branch, upstream, dirty files, and recent commits;
   - version sources such as package manifests, plugin manifests, lockfiles, or
     release notes;
   - install or marketplace metadata that must match the release version.
   Ask for the intended release type or target version when it is ambiguous. If
   the user asks to prepare rather than publish, assume audit-only until told
   otherwise.
2. Run the non-destructive audit helper when useful:

```bash
python3 <skill-dir>/scripts/release_audit.py .
```

3. Determine the release type:
   - patch/point release for fixes and metadata corrections;
   - minor release for new skills or feature-level additions;
   - major release only when existing installs or public contracts break.
4. Validate before committing:
   - prefer repository validation commands already documented in README,
     package manifests, CI files, or agent instructions;
   - run Docker validation when the user asks for install/package confidence;
   - report any validation command that cannot be run.
5. Apply version and metadata updates consistently.
6. Re-run validation after edits.
7. If explicitly requested, commit, tag, and push:
   - inspect `git status` before staging;
   - stage only intended files;
   - use an expected tag name such as `vX.Y.Z`;
   - push branch and tag only after local validation passes or after clearly
     reporting why it was skipped.

## Guardrails

- Never overwrite, revert, or discard unrelated user changes.
- Never infer permission to publish, push, or tag from a request to "prepare" or
  "audit" a release.
- State validation scope, skipped checks, and any release evidence that was not
  inspected.
- Prefer HTTPS clone URLs in marketplace or install metadata unless the project
  explicitly requires SSH.
- Keep product-specific release steps in optional references or adapters, not in
  the core workflow.

## References

- Read `references/versioning.md` when choosing or validating a version bump.
- Read `references/marketplaces.md` when release work includes plugin,
  marketplace, installation, or wrapper metadata.
