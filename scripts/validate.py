#!/usr/bin/env python3
"""Validate the Easel Skills plugin package without external dependencies."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_file(path: Path) -> None:
    if not path.is_file():
        fail(f"missing {path.relative_to(ROOT)}")


def load_json(path: Path) -> dict:
    require_file(path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def require_string(obj: dict, key: str, label: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"{label}.{key} must be a non-empty string")
    return value


def validate_plugin() -> None:
    manifest = load_json(ROOT / ".codex-plugin" / "plugin.json")
    if require_string(manifest, "name", "plugin") != "easel-skills":
        fail("plugin.name must be easel-skills")
    version = require_string(manifest, "version", "plugin")
    if SEMVER_RE.fullmatch(version) is None:
        fail("plugin.version must be semantic version syntax")
    require_string(manifest, "description", "plugin")
    if manifest.get("skills") != "./skills/":
        fail("plugin.skills must be ./skills/")

    author = manifest.get("author")
    if not isinstance(author, dict):
        fail("plugin.author must be an object")
    require_string(author, "name", "plugin.author")

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        fail("plugin.interface must be an object")
    for key in (
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
    ):
        require_string(interface, key, "plugin.interface")
    prompts = interface.get("defaultPrompt")
    if not isinstance(prompts, list) or not prompts or not all(isinstance(p, str) and p for p in prompts):
        fail("plugin.interface.defaultPrompt must be a non-empty string array")
    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not all(isinstance(c, str) and c for c in capabilities):
        fail("plugin.interface.capabilities must be a string array")


def validate_marketplace() -> None:
    marketplace = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    if require_string(marketplace, "name", "marketplace") != "easel":
        fail("marketplace.name must be easel")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        fail("marketplace.plugins must be an array")
    matches = [p for p in plugins if isinstance(p, dict) and p.get("name") == "easel-skills"]
    if len(matches) != 1:
        fail("marketplace must contain exactly one easel-skills entry")
    entry = matches[0]
    source = entry.get("source")
    if (
        not isinstance(source, dict)
        or source.get("source") != "local"
        or source.get("path") != "./plugins/easel-skills"
    ):
        fail("marketplace easel-skills source must be local path ./plugins/easel-skills")
    policy = entry.get("policy")
    if not isinstance(policy, dict):
        fail("marketplace easel-skills policy must be an object")
    if policy.get("installation") != "AVAILABLE":
        fail("marketplace easel-skills policy.installation must be AVAILABLE")
    if policy.get("authentication") != "ON_INSTALL":
        fail("marketplace easel-skills policy.authentication must be ON_INSTALL")
    require_string(entry, "category", "marketplace.plugins[easel-skills]")


def validate_claude_plugin() -> None:
    manifest = load_json(ROOT / ".claude-plugin" / "plugin.json")
    if require_string(manifest, "name", "claude-plugin") != "easel-skills":
        fail("claude-plugin.name must be easel-skills")
    version = require_string(manifest, "version", "claude-plugin")
    if SEMVER_RE.fullmatch(version) is None:
        fail("claude-plugin.version must be semantic version syntax")
    require_string(manifest, "description", "claude-plugin")
    author = manifest.get("author")
    if not isinstance(author, dict):
        fail("claude-plugin.author must be an object")
    require_string(author, "name", "claude-plugin.author")


def validate_claude_marketplace() -> None:
    marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    if require_string(marketplace, "name", "claude-marketplace") != "easel":
        fail("claude-marketplace.name must be easel")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        fail("claude-marketplace.plugins must be an array")
    matches = [p for p in plugins if isinstance(p, dict) and p.get("name") == "easel-skills"]
    if len(matches) != 1:
        fail("claude-marketplace must contain exactly one easel-skills entry")
    entry = matches[0]
    if entry.get("source") != "./":
        fail("claude-marketplace easel-skills source must be ./")
    if entry.get("version") != "0.1.0":
        fail("claude-marketplace easel-skills version must be 0.1.0")
    require_string(entry, "description", "claude-marketplace.plugins[easel-skills]")


def parse_frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)} must start with YAML frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        fail(f"{path.relative_to(ROOT)} frontmatter is not closed")
    return text[4:end]


def frontmatter_has_key(frontmatter: str, key: str) -> bool:
    return re.search(rf"(?m)^{re.escape(key)}:\s*\S+", frontmatter) is not None


def validate_skills() -> None:
    skills_root = ROOT / "skills"
    if not skills_root.is_dir():
        fail("missing skills directory")
    skill_dirs = [p for p in sorted(skills_root.iterdir()) if p.is_dir()]
    if not skill_dirs:
        fail("skills directory must contain at least one skill")
    for skill in skill_dirs:
        skill_md = skill / "SKILL.md"
        require_file(skill_md)
        frontmatter = parse_frontmatter(skill_md)
        if not frontmatter_has_key(frontmatter, "name"):
            fail(f"{skill_md.relative_to(ROOT)} frontmatter must include name")
        if not frontmatter_has_key(frontmatter, "description"):
            fail(f"{skill_md.relative_to(ROOT)} frontmatter must include description")
        agent_yaml = skill / "agents" / "openai.yaml"
        if agent_yaml.is_file():
            text = agent_yaml.read_text(encoding="utf-8")
            for key in ("display_name:", "short_description:", "default_prompt:"):
                if key not in text:
                    fail(f"{agent_yaml.relative_to(ROOT)} missing {key}")


def validate_package_yaml() -> None:
    path = ROOT / "package.yaml"
    require_file(path)
    text = path.read_text(encoding="utf-8")
    for required in (
        "name: easel-skills",
        "type: plugin",
        "source: skills/",
        "target: .agents/skills/",
        "target: .claude/skills/",
    ):
        if required not in text:
            fail(f"package.yaml missing {required}")


def validate_marketplace_wrapper() -> None:
    wrapper = ROOT / "plugins" / "easel-skills"
    if not wrapper.is_dir():
        fail("missing marketplace wrapper plugins/easel-skills")
    for name in (".codex-plugin", "skills"):
        path = wrapper / name
        if not path.exists():
            fail(f"marketplace wrapper missing plugins/easel-skills/{name}")


def main() -> int:
    validate_plugin()
    validate_marketplace()
    validate_claude_plugin()
    validate_claude_marketplace()
    validate_marketplace_wrapper()
    validate_skills()
    validate_package_yaml()
    print("OK: package metadata is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
