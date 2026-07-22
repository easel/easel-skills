# Vale Integration

Sloptimizer owns its Vale dependency and rule pack.

## Expected Version

Use Vale `3.13.0` unless a project pins a newer compatible version. The audit
script checks that `vale` is available before running.

## Rule Pack

The bundled style is `Sloptimizer`, stored in:

```text
assets/vale/styles/Sloptimizer/
```

The script generates a temporary `.vale.ini` that points at the bundled style,
so projects do not need to commit Vale configuration to use the skill.

## Commands

```bash
scripts/slop-audit.sh docs/spec.md
scripts/slop-audit.sh --changed
```

The output is Vale's normal text output. Use the findings as a review aid, not
as an automatic rewrite contract.
