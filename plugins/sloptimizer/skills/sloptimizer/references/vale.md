# Vale Integration

Sloptimizer owns its Vale dependency and rule pack.

## Expected Version

Use Vale `3.14.2` or newer (`scripts/install-vale.sh` pins that version).
The audit script checks that `vale` is available before running.

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

The output is Vale's normal text output followed by the raw-profile and
headline findings. Use the findings as a review aid, not as an automatic
rewrite contract.

## Exit Status

`slop-audit.sh` and the scripts it calls share one contract:

| Code | Meaning |
|---|---|
| `0` | No findings. |
| `1` | At least one finding from Vale, the raw profile, or the headline rules. |
| `2` | Usage error, including a path that does not exist. |
| `127` | Vale is not installed. |

A missing path is an error rather than a skip, so a typo cannot read as a
clean audit. Findings are suggestions, so gate on exit `1` only where the
house style is enforced.

## Compatibility

The scripts run under bash 3.2, the version macOS ships, so they avoid
`mapfile` and other bash 4 builtins.
