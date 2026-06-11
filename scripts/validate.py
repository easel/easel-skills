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
PLUGIN_VERSION = "0.2.0"
MARKETPLACE_NAME = "easel-skills"


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


def marketplace_path(name: str) -> str:
    return f"./plugins/{name}"


def plugin_wrapper_dirs() -> set[str]:
    plugins_root = ROOT / "plugins"
    if not plugins_root.is_dir():
        fail("missing plugins directory")
    return {p.name for p in plugins_root.iterdir() if p.is_dir()}


def repo_skill_names() -> set[str]:
    skills_root = ROOT / "skills"
    if not skills_root.is_dir():
        fail("missing skills directory")
    names = {p.name for p in skills_root.iterdir() if p.is_dir()}
    if not names:
        fail("skills directory must contain at least one skill")
    return names


def wrapper_skill_names(name: str) -> set[str]:
    skills_root = ROOT / "plugins" / name / "skills"
    if not skills_root.is_dir():
        fail(f"marketplace wrapper plugins/{name}/skills must be a directory")
    names = {p.name for p in skills_root.iterdir() if p.is_dir()}
    if not names:
        fail(f"marketplace wrapper plugins/{name}/skills must expose at least one skill")
    return names


def skill_file_map(path: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for child in sorted(path.rglob("*")):
        if "__pycache__" in child.parts or child.suffix == ".pyc":
            continue
        if child.is_file():
            files[str(child.relative_to(path))] = child.read_bytes()
    return files


def validate_skill_copy(source: Path, copy: Path) -> None:
    source_files = skill_file_map(source)
    copy_files = skill_file_map(copy)
    if source_files != copy_files:
        missing = sorted(set(source_files) - set(copy_files))
        extra = sorted(set(copy_files) - set(source_files))
        changed = sorted(
            path
            for path in set(source_files) & set(copy_files)
            if source_files[path] != copy_files[path]
        )
        details = []
        if missing:
            details.append(f"missing files: {', '.join(missing[:5])}")
        if extra:
            details.append(f"extra files: {', '.join(extra[:5])}")
        if changed:
            details.append(f"changed files: {', '.join(changed[:5])}")
        fail(
            f"{copy.relative_to(ROOT)} must match {source.relative_to(ROOT)} "
            f"({'; '.join(details)})"
        )


def marketplace_entries(plugins: object, label: str) -> dict[str, dict]:
    if not isinstance(plugins, list):
        fail(f"{label}.plugins must be an array")
    seen: dict[str, dict] = {}
    for index, entry in enumerate(plugins):
        if not isinstance(entry, dict):
            fail(f"{label}.plugins[{index}] must be an object")
        name = require_string(entry, "name", f"{label}.plugins[{index}]")
        if name in seen:
            fail(f"{label}.plugins contains duplicate plugin name {name}")
        seen[name] = entry
    if not seen:
        fail(f"{label}.plugins must contain at least one plugin")
    return seen


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


def validate_marketplace() -> set[str]:
    marketplace = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    if require_string(marketplace, "name", "marketplace") != MARKETPLACE_NAME:
        fail(f"marketplace.name must be {MARKETPLACE_NAME}")
    seen = marketplace_entries(marketplace.get("plugins"), "marketplace")
    for name, entry in seen.items():
        expected_path = marketplace_path(name)
        source = entry.get("source")
        if (
            not isinstance(source, dict)
            or source.get("source") != "local"
            or source.get("path") != expected_path
        ):
            fail(f"marketplace {name} source must be local path {expected_path}")
        policy = entry.get("policy")
        if not isinstance(policy, dict):
            fail(f"marketplace {name} policy must be an object")
        if policy.get("installation") != "AVAILABLE":
            fail(f"marketplace {name} policy.installation must be AVAILABLE")
        if policy.get("authentication") != "ON_INSTALL":
            fail(f"marketplace {name} policy.authentication must be ON_INSTALL")
        require_string(entry, "category", f"marketplace.plugins[{name}]")
    return set(seen)


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


def validate_claude_marketplace() -> set[str]:
    marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    if require_string(marketplace, "name", "claude-marketplace") != MARKETPLACE_NAME:
        fail(f"claude-marketplace.name must be {MARKETPLACE_NAME}")
    seen = marketplace_entries(marketplace.get("plugins"), "claude-marketplace")
    for name, entry in seen.items():
        expected_path = marketplace_path(name)
        if entry.get("source") != expected_path:
            fail(f"claude-marketplace {name} source must be {expected_path}")
        if entry.get("version") != PLUGIN_VERSION:
            fail(f"claude-marketplace {name} version must be {PLUGIN_VERSION}")
        require_string(entry, "description", f"claude-marketplace.plugins[{name}]")
    return set(seen)


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


def validate_marketplace_wrapper(marketplace_plugins: set[str]) -> None:
    wrapper_dirs = plugin_wrapper_dirs()
    if wrapper_dirs != marketplace_plugins:
        missing = marketplace_plugins - wrapper_dirs
        extra = wrapper_dirs - marketplace_plugins
        details = []
        if missing:
            details.append(f"missing wrappers: {', '.join(sorted(missing))}")
        if extra:
            details.append(f"unlisted wrappers: {', '.join(sorted(extra))}")
        fail(f"marketplace plugins must match plugins/ wrappers ({'; '.join(details)})")

    all_skill_names = repo_skill_names()
    for name in sorted(marketplace_plugins):
        wrapper = ROOT / "plugins" / name
        for child in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json", "skills"):
            path = wrapper / child
            if not path.exists():
                fail(f"marketplace wrapper missing plugins/{name}/{child}")
        for manifest_path in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
            manifest = load_json(wrapper / manifest_path)
            if require_string(manifest, "name", f"plugins/{name}/{manifest_path}") != name:
                fail(f"plugins/{name}/{manifest_path} name must be {name}")

        exposed_skills = wrapper_skill_names(name)
        if name == "all":
            if exposed_skills != all_skill_names:
                missing = all_skill_names - exposed_skills
                extra = exposed_skills - all_skill_names
                details = []
                if missing:
                    details.append(f"missing skills: {', '.join(sorted(missing))}")
                if extra:
                    details.append(f"unknown skills: {', '.join(sorted(extra))}")
                fail(f"plugins/all/skills must expose all repo skills ({'; '.join(details)})")
            for skill_name in sorted(all_skill_names):
                validate_skill_copy(
                    ROOT / "skills" / skill_name,
                    wrapper / "skills" / skill_name,
                )
        else:
            if name not in all_skill_names:
                fail(f"plugins/{name} must match a repo skill named {name}")
            if exposed_skills != {name}:
                fail(f"plugins/{name}/skills must expose exactly the {name} skill")
            validate_skill_copy(
                ROOT / "skills" / name,
                wrapper / "skills" / name,
            )


def main() -> int:
    validate_plugin()
    marketplace_plugins = validate_marketplace()
    validate_claude_plugin()
    claude_marketplace_plugins = validate_claude_marketplace()
    if marketplace_plugins != claude_marketplace_plugins:
        fail(
            ".agents and .claude marketplaces must contain the same plugins "
            f"(agents: {', '.join(sorted(marketplace_plugins))}; "
            f"claude: {', '.join(sorted(claude_marketplace_plugins))})"
        )
    validate_marketplace_wrapper(marketplace_plugins)
    validate_skills()
    validate_package_yaml()
    print("OK: package metadata is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
