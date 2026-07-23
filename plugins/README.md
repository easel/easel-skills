# Marketplace plugin wrappers

Installable plugin packages for Codex, Claude, Grok, and compatible
marketplaces.

## Source of truth

Canonical skill content lives in `/skills`. Do not edit files under
`plugins/*/skills/` by hand.

| Path | Purpose |
|------|---------|
| `plugins/<skill>/skills/<skill>/` | Single-skill marketplace package |
| `plugins/all/skills/<skill>/` | Umbrella package with every skill |
| `.grok-plugin/plugin-index.json` | Grok marketplace component catalog |

## Regenerate

After changes under `skills/`:

```bash
bash scripts/prepare.sh
bash scripts/validate.sh
```

`prepare.sh` syncs wrapper skill trees and rewrites the Grok plugin index.
`validate.sh` re-runs prepare and fails if generated paths have unstaged
packaging drift.

## Local development

Load skills from this checkout with the plugin surface:

```bash
grok plugin install "$PWD" --trust
# or process-scoped:
grok --plugin-dir "$PWD" ...
```
