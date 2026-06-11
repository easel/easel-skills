# Versioning

Use SemVer when the project does not define a different scheme.

## Bump Selection

- Patch: bug fixes, validation fixes, metadata corrections, documentation that
  affects installability, and compatible skill refinements.
- Minor: new skills, new public scripts, new install surfaces, and compatible
  feature additions.
- Major: breaking install changes, removed skills, incompatible command
  contracts, or changed public output contracts.

## Consistency Checks

- Manifest versions should agree across package, plugin, marketplace, and
  wrapper metadata when those files represent the same release.
- Tags should use the repository convention. If no convention is visible, prefer
  `vX.Y.Z`.
- Release notes should describe user-visible changes, validation performed, and
  install impact.
- Do not bump versions after validation without rerunning the relevant
  validation checks.
