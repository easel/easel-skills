#!/usr/bin/env python3
"""Generate Grok marketplace plugin-index.json from skill and plugin metadata."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_VERSION = "0.5.0"
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)
DESC_RE = re.compile(r"(?m)^description:\s*(.+?)(?=\n[a-zA-Z0-9_-]+:|\Z)", re.DOTALL)
NAME_RE = re.compile(r"(?m)^name:\s*(\S+)\s*$")


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_skill_meta(skill_dir: Path) -> tuple[str, str]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        fail(f"missing {skill_md.relative_to(ROOT)}")
    text = skill_md.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        fail(f"{skill_md.relative_to(ROOT)} missing YAML frontmatter")
    frontmatter = match.group(1)
    name_match = NAME_RE.search(frontmatter)
    desc_match = DESC_RE.search(frontmatter)
    if not name_match or not desc_match:
        fail(f"{skill_md.relative_to(ROOT)} frontmatter must include name and description")
    name = name_match.group(1).strip()
    description = " ".join(desc_match.group(1).strip().split())
    return name, description


def truncate(text: str, limit: int = 140) -> str:
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return cut.rstrip(".,;:") + "…"


def plugin_tree_sha(plugin_name: str) -> str | None:
    """Git tree sha of plugins/<name> as it exists in the working tree.

    Reading `HEAD:<rel>` instead would return the tree of the *previous*
    commit, so every commit touching plugins/ would leave the index stale and
    need a follow-up "refresh shas" commit. Staging into a scratch index makes
    prepare.sh a fixed point within a single commit.
    """
    rel = f"plugins/{plugin_name}"
    if not (ROOT / rel).is_dir():
        return None
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}
        try:
            for args in (
                ["git", "add", "-A", "--", rel],
                ["git", "write-tree", f"--prefix={rel}"],
            ):
                result = subprocess.run(
                    args, cwd=ROOT, env=env, check=False,
                    capture_output=True, text=True,
                )
                if result.returncode != 0:
                    return None
        except OSError:
            return None
    sha = result.stdout.strip()
    return sha or None


def skill_component(skill_dir: Path) -> dict[str, str]:
    name, description = parse_skill_meta(skill_dir)
    return {"name": name, "description": truncate(description)}


def build_index() -> dict:
    marketplace = json.loads(
        (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8")
    )
    plugins_meta = marketplace.get("plugins")
    if not isinstance(plugins_meta, list):
        fail("marketplace.plugins must be an array")

    all_skills = sorted(
        p for p in (ROOT / "skills").iterdir() if p.is_dir() and (p / "SKILL.md").is_file()
    )
    all_skill_components = [skill_component(p) for p in all_skills]
    by_name = {item["name"]: item for item in all_skill_components}

    plugins: dict[str, dict] = {}
    for entry in plugins_meta:
        if not isinstance(entry, dict):
            fail("marketplace plugin entries must be objects")
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            fail("marketplace plugin entry missing name")
        wrapper = ROOT / "plugins" / name
        if not wrapper.is_dir():
            fail(f"missing plugin wrapper plugins/{name}")

        if name == "all":
            components = {"skills": all_skill_components}
        else:
            if name not in by_name:
                fail(f"marketplace plugin {name} has no matching skill")
            components = {"skills": [by_name[name]]}

        plugin_entry: dict = {
            "version": PLUGIN_VERSION,
            "components": components,
        }
        sha = plugin_tree_sha(name)
        if sha:
            plugin_entry["sha"] = sha
        plugins[name] = plugin_entry

    return {"version": 1, "plugins": plugins}


def main() -> int:
    index = build_index()
    out_dir = ROOT / ".grok-plugin"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "plugin-index.json"
    out_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"OK: wrote {out_path.relative_to(ROOT)} ({len(index['plugins'])} plugins)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
