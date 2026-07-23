#!/usr/bin/env python3
"""Non-destructive release readiness audit for a repository."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


SEMVER_RE = re.compile(r"\b(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?\b")


def run_git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            text=True,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def text_version(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    match = re.search(r"(?m)^version:\s*([^\s]+)", text)
    if match:
        return match.group(1)
    match = SEMVER_RE.search(text)
    return match.group(0) if match else None


def version_sources(root: Path) -> list[dict[str, str]]:
    candidates = [
        "package.json",
        "package.yaml",
        "pyproject.toml",
        "Cargo.toml",
        ".codex-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        ".grok-plugin/plugin-index.json",
    ]
    records: list[dict[str, str]] = []
    for rel in candidates:
        path = root / rel
        if not path.is_file():
            continue
        version = None
        if path.suffix == ".json":
            data = load_json(path)
            if data and isinstance(data.get("version"), str):
                version = data["version"]
        if version is None:
            version = text_version(path)
        if version:
            records.append({"path": rel, "version": version})
    for manifest in sorted(root.glob("plugins/*/.codex-plugin/plugin.json")):
        data = load_json(manifest)
        if data and isinstance(data.get("version"), str):
            records.append({"path": str(manifest.relative_to(root)), "version": data["version"]})
    for manifest in sorted(root.glob("plugins/*/.claude-plugin/plugin.json")):
        data = load_json(manifest)
        if data and isinstance(data.get("version"), str):
            records.append({"path": str(manifest.relative_to(root)), "version": data["version"]})
    return records


def marketplace_entries(root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for rel in [".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"]:
        data = load_json(root / rel)
        if not data:
            continue
        plugins = data.get("plugins")
        if isinstance(plugins, list):
            for item in plugins:
                if isinstance(item, dict):
                    entries.append({"marketplace": rel, **item})
    return entries


def packaging_artifacts(root: Path) -> dict[str, Any]:
    """Summarize generated packaging inputs for release readiness."""
    plugin_index = load_json(root / ".grok-plugin" / "plugin-index.json")
    index_plugins: list[str] = []
    if plugin_index and isinstance(plugin_index.get("plugins"), dict):
        index_plugins = sorted(plugin_index["plugins"])

    skill_dirs = sorted(
        p.name for p in (root / "skills").iterdir() if p.is_dir()
    ) if (root / "skills").is_dir() else []

    return {
        "prepare_script": (root / "scripts" / "prepare.sh").is_file(),
        "plugin_index": ".grok-plugin/plugin-index.json" if plugin_index else None,
        "plugin_index_plugins": index_plugins,
        "canonical_skills": skill_dirs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()

    status = run_git(root, "status", "--short")
    branch = run_git(root, "branch", "--show-current")
    upstream = run_git(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    tags = run_git(root, "tag", "--sort=-version:refname")
    recent_tags = tags.splitlines()[:5] if tags else []

    versions = version_sources(root)
    version_values = sorted({record["version"] for record in versions})
    packaging = packaging_artifacts(root)
    report = {
        "repo": str(root),
        "branch": branch,
        "upstream": upstream,
        "dirty": bool(status),
        "status": status.splitlines(),
        "version_sources": versions,
        "versions_consistent": len(version_values) <= 1,
        "distinct_versions": version_values,
        "recent_tags": recent_tags,
        "marketplace_entries": marketplace_entries(root),
        "packaging": packaging,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
