#!/usr/bin/env python3
"""Mine local agent sessions for recurring workflows that may deserve skills."""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "reports" / "session-skill-candidates.md"
DEFAULT_STATE_DIR = ROOT / ".session-analysis"


EXPLORATORY_INTENTS: dict[str, dict[str, Any]] = {
    "data-quality-rule-generation": {
        "title": "Data quality rule and expectation generation",
        "patterns": [
            r"\bgreat expectations\b",
            r"\bvalidation rules?\b",
            r"\bvalidation constraints?\b",
            r"\bexpect column\b",
            r"\bcolumn values\b",
            r"\btable-level\b",
        ],
        "portable_read": "strong templated signal; possible data-quality skill for schema-aware validation rules and expectation JSON",
    },
    "data-doc-generation": {
        "title": "Data table documentation generation",
        "patterns": [
            r"\bdocumentation generation prompt\b",
            r"\btable information\b",
            r"\bhealthcare data table\b",
            r"\btable specification\b",
            r"\bgenerate comprehensive documentation\b",
        ],
        "portable_read": "strong templated signal; likely a data documentation skill with domain adapters",
    },
    "data-mapping-and-survivorship": {
        "title": "Data mapping, filename extraction, and survivorship workflows",
        "patterns": [
            r"\bsurvivorship mapping\b",
            r"\bderive columns\b",
            r"\bfilename pattern extraction\b",
            r"\bcanonical table names?\b",
            r"\bdisposition\b",
            r"\bmapping\b",
        ],
        "portable_read": "strong templated signal; possible ETL mapping skill, probably with healthcare-specific references",
    },
    "strict-json-output-contracts": {
        "title": "Strict JSON output contracts and hash-tracked prompts",
        "patterns": [
            r"\bcritical: json\b",
            r"\bjson object output with hash tracking\b",
            r"\bno comments allowed\b",
            r"\bmust output (?:a )?json\b",
            r"\brequired output format\b",
            r"\bjson schema\b",
        ],
        "portable_read": "covered partly by adversarial-review output contracts; may deserve reusable prompt-contract fixtures",
    },
    "github-pr-comment-handling": {
        "title": "GitHub PR review comment handling",
        "patterns": [
            r"\breview comments?\b",
            r"\bPR comments?\b",
            r"\bpull request comments?\b",
            r"\baddress .*comments?\b",
            r"\bresolve .*comments?\b",
            r"\bgh pr\b",
        ],
        "portable_read": "portable; likely covered by installed GitHub comment skills, not currently in this repo",
    },
    "ci-repair": {
        "title": "CI failure investigation and repair",
        "patterns": [
            r"\bfix CI\b",
            r"\bCI (?:is )?(?:failing|failed|red|blocked)\b",
            r"\bfailing tests?\b",
            r"\bgithub actions?\b",
            r"\bworkflow run\b",
            r"\brerun failed\b",
        ],
        "portable_read": "portable; covered by installed agent-ci/gh-fix-ci style skills, not currently in this repo",
    },
    "cloud-deploy": {
        "title": "Cloud deployment and hosting workflow",
        "patterns": [
            r"\bcloudflare\b",
            r"\bwrangler\b",
            r"\bworkers?\b",
            r"\bpages deploy\b",
            r"\bdeploy(?:ment)?\b",
            r"\bpreview URL\b",
        ],
        "portable_read": "portable but provider-specific; likely belongs in provider deploy skills",
    },
    "docs-maintenance": {
        "title": "Documentation maintenance and stale-doc repair",
        "patterns": [
            r"\bstale docs?\b",
            r"\bupdate docs?\b",
            r"\bdocumentation assistant\b",
            r"\bdoc[- ]dag\b",
            r"\btechnical document\b",
            r"\bwrite .*docs?\b",
        ],
        "portable_read": "portable; possible new skill if scoped to doc freshness, references, and evidence-backed updates",
    },
    "dependency-upgrade": {
        "title": "Dependency upgrade and migration workflow",
        "patterns": [
            r"\bupgrade\b",
            r"\bmigration\b",
            r"\bmigrate\b",
            r"\bdependency\b",
            r"\bdependencies\b",
            r"\bnext 15\b",
            r"\bpackage upgrade\b",
        ],
        "portable_read": "portable; possible skill for upgrade planning, compatibility checks, tests, and rollback notes",
    },
    "agent-telemetry-costs": {
        "title": "Agent telemetry, token accounting, and quota reasoning",
        "patterns": [
            r"\botel\b",
            r"\bopentelemetry\b",
            r"\btoken costs?\b",
            r"\bcached tokens?\b",
            r"\bquota\b",
            r"\brate limits?\b",
            r"\btool calls?\b",
            r"\busage metrics?\b",
        ],
        "portable_read": "emerging; likely a reference skill for agent observability and cost instrumentation",
    },
    "agent-orchestration": {
        "title": "Sub-agent orchestration and worker coordination",
        "patterns": [
            r"\bsub-?agents?\b",
            r"\bbackground workers?\b",
            r"\bworker queue\b",
            r"\bparallel workers?\b",
            r"\bdelegate\b",
            r"\bpreserve context\b",
        ],
        "portable_read": "partly covered by adversarial-review; possible reference content for multi-agent execution hygiene",
    },
}


INTENTS: dict[str, dict[str, Any]] = {
    "release-and-publish": {
        "title": "Release, version, commit, tag, and push workflow",
        "patterns": [
            r"\bcommit\b",
            r"\bpush\b",
            r"\brelease\b",
            r"\btag\b",
            r"\bpoint release\b",
            r"\bversion\b",
            r"\bmarketplace\b",
        ],
        "baseline": "extension",
        "covered_by": "plugin-creator partly covers plugin metadata; no dedicated release skill found",
    },
    "cross-agent-review": {
        "title": "Cross-agent review and feedback incorporation",
        "patterns": [
            r"\breview (?:this )?(?:plan|work|change|diff)\b",
            r"\breview .* with claude\b",
            r"\bask claude\b",
            r"\bwith claude\b",
            r"\bsub-?agents?\b",
            r"\bincorporate .*feedback\b",
        ],
        "baseline": "covered-or-extension",
        "covered_by": "adversarial-review covers critical review; may need lighter cross-agent plan-review workflow",
    },
    "plan-then-execute": {
        "title": "Plan, review, adjust, then execute loop",
        "patterns": [
            r"\bmake a plan\b",
            r"\bplan first\b",
            r"\breview this plan\b",
            r"\bexecute (?:the|this) plan\b",
            r"\bfold .* in\b",
            r"\bmake the adjustments\b",
        ],
        "baseline": "new-or-extension",
        "covered_by": "adversarial-review covers review; no general plan-execution operating skill found",
    },
    "validation-and-docker": {
        "title": "Local validation, Docker verification, and CI parity",
        "patterns": [
            r"\bdocker\b",
            r"\bvalidate\b",
            r"\btest everything\b",
            r"\bCI\b",
            r"\bgithub actions\b",
            r"\brun tests?\b",
        ],
        "baseline": "covered-or-extension",
        "covered_by": "agent-ci covers GitHub Actions; repo-specific Docker validation may be a release-skill component",
    },
    "skill-and-plugin-authoring": {
        "title": "Skill and plugin authoring or marketplace packaging",
        "patterns": [
            r"\bskill\b",
            r"\bSKILL\.md\b",
            r"\bplugin\b",
            r"\bmarketplace\b",
            r"\bclaude plugin\b",
            r"\bcodex plugin\b",
        ],
        "baseline": "covered",
        "covered_by": "skill-creator and plugin-creator",
    },
    "prompt-or-harness-engineering": {
        "title": "Agent prompt, harness, and command design",
        "patterns": [
            r"\bharness\b",
            r"\bsubagent\b",
            r"\bsub-agent\b",
            r"\bprompt contract\b",
            r"\bslash command\b",
            r"\bmode:\s",
            r"\breturn exactly\b",
        ],
        "baseline": "new-or-extension",
        "covered_by": "adversarial-review and skill-creator overlap; recurring harness prompt design may deserve its own reference skill",
    },
    "prose-quality": {
        "title": "Prose cleanup, AI-writing, voice, and slop reduction",
        "patterns": [
            r"\bslop(?:timizer)?\b",
            r"\bAI[- ]writing\b",
            r"\bvoice\b",
            r"\bprose\b",
            r"\brewrite\b",
            r"\bprompt\b",
        ],
        "baseline": "covered-or-extension",
        "covered_by": "sloptimizer",
    },
    "repo-triage": {
        "title": "Repository status, branch, diff, and PR/issue triage",
        "patterns": [
            r"\bcurrent state of this branch\b",
            r"\bvs\.? master\b",
            r"\bstatus\b",
            r"\bPR\b",
            r"\bissue\b",
            r"\bdiff\b",
        ],
        "baseline": "new-or-extension",
        "covered_by": "GitHub plugin helps with PRs; no portable repo-triage skill found",
    },
    "ddx-bead-workflow": {
        "title": "DDx bead intake, execution, and tracker hygiene",
        "patterns": [
            r"\bddx\b",
            r"\bbead\b",
            r"\bacceptance\b",
            r"\bmeasure-results\b",
            r"\btracker\b",
        ],
        "baseline": "not-portable-core",
        "covered_by": "product-specific; should be an adapter or external product skill, not core Easel",
    },
    "frontend-design": {
        "title": "Frontend, UI, and design-system work",
        "patterns": [
            r"\bfrontend\b",
            r"\bUI\b",
            r"\bdesign\b",
            r"\bStitch\b",
            r"\bReact\b",
            r"\bCSS\b",
        ],
        "baseline": "covered",
        "covered_by": "frontend-design, stitch-design, design-md",
    },
}


INJECTED_MARKERS = (
    "system-reminder",
    "<system-reminder>",
    "<local-command-stdout>",
    "<command-name>",
    "<command-args>",
    "<tool_result",
    "This session is being continued",
    "Caveat: The messages below",
)

AUTOMATION_MARKERS = (
    "<execute-bead",
    "<bead-review",
    "MODE:",
    "Base directory for this skill:",
    "Work slung:",
    "You are executing one bead",
    "You are evaluating whether this bead",
    "# HELIX Execution Context",
    "Execute the following HELIX fresh-eyes review action",
    "# Execute Bead",
    "# Dun Prompt",
    "Check-ID:",
    "Use the HELIX skill",
    "Use the helix skill",
    "You are reviewing a technical document",
    "You are an expert software engineer reviewing a plan",
    "You are the lead reviewer",
)

TEMPLATE_MARKERS = (
    "CRITICAL: JSON OBJECT OUTPUT WITH HASH TRACKING",
    "CRITICAL: JSON OUTPUT FORMAT",
    "REQUIRED OUTPUT FORMAT",
    "Healthcare Data Table Relationship Analysis",
    "Validation Rules:",
    "Documentation Generation Prompt",
    "Survivorship Mapping:",
    "Filename Pattern Extraction",
)


@dataclass
class Prompt:
    source: str
    session_id: str
    project: str
    timestamp: str
    text: str


@dataclass
class CorpusStats:
    root: str
    real_root: str
    files: int = 0
    bytes: int = 0
    oldest: float | None = None
    newest: float | None = None
    suffixes: collections.Counter[str] = field(default_factory=collections.Counter)
    record_types: collections.Counter[str] = field(default_factory=collections.Counter)


def iso(ts: float | None) -> str:
    if ts is None:
        return "n/a"
    return dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc).date().isoformat()


def read_jsonl(path: Path):
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line_no, line in enumerate(handle, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield line_no, json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def safe_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        chunks: list[str] = []
        for item in value:
            if isinstance(item, str):
                chunks.append(item)
            elif isinstance(item, dict):
                if item.get("type") in {"text", "input_text"} and isinstance(item.get("text"), str):
                    chunks.append(item["text"])
                elif item.get("type") == "tool_result":
                    continue
        return "\n".join(chunks)
    if isinstance(value, dict):
        return safe_text(value.get("text") or value.get("content") or "")
    return ""


def is_probably_injected(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    return any(marker in stripped for marker in INJECTED_MARKERS)


def is_automation_like(text: str) -> bool:
    stripped = text.strip()
    return any(stripped.startswith(marker) or marker in stripped[:500] for marker in AUTOMATION_MARKERS)


def is_template_like(text: str) -> bool:
    stripped = text.strip()
    return any(marker in stripped[:1000] for marker in TEMPLATE_MARKERS)


def normalize_space(text: str, limit: int = 5000) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def is_assistant_workflow_signal(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < 40:
        return False
    patterns = (
        r"\bI(?:'ll| will| am|’ll)\b",
        r"\bI(?:'m| am|’m) going to\b",
        r"\bNext,? I\b",
        r"\bI need to\b",
        r"\bI found\b",
        r"\bI(?:'ve| have|’ve) got\b",
    )
    return any(re.search(pattern, stripped, re.IGNORECASE) for pattern in patterns)


def command_family(cmd: str) -> str:
    cmd = cmd.strip()
    if not cmd:
        return "cmd:<empty>"
    try:
        parts = shlex.split(cmd, posix=True)
    except ValueError:
        parts = cmd.split()
    if not parts:
        return "cmd:<empty>"
    while parts and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", parts[0]):
        parts.pop(0)
    if parts and parts[0] in {"sudo", "env", "command"}:
        parts.pop(0)
    if not parts:
        return "cmd:<env>"
    head = Path(parts[0]).name
    if head == "git" and len(parts) > 1:
        return f"cmd:git {parts[1]}"
    if head in {"python", "python3"} and len(parts) > 1:
        script = Path(parts[1]).name
        return f"cmd:python {script}" if script.endswith(".py") else "cmd:python"
    if head == "docker" and len(parts) > 1:
        return f"cmd:docker {parts[1]}"
    if head in {"npm", "pnpm", "yarn"} and len(parts) > 1:
        return f"cmd:{head} {parts[1]}"
    if head == "go" and len(parts) > 1:
        return f"cmd:go {parts[1]}"
    if head == "bash" and len(parts) > 1:
        return f"cmd:bash {Path(parts[1]).name}"
    return f"cmd:{head}"


def parse_json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def project_from_path(path: Path) -> str:
    parts = path.parts
    if "projects" in parts:
        idx = parts.index("projects")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    if "sessions" in parts:
        return "codex"
    return path.parent.name


def unique_paths(paths: list[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        try:
            key = str(path.expanduser().resolve())
        except OSError:
            key = str(path.expanduser())
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def user_home_candidates() -> list[Path]:
    user = os.environ.get("USER", "")
    candidates = [Path.home()]
    if user:
        candidates.extend([Path("/Users") / user, Path("/home") / user])
    return unique_paths([path for path in candidates if path.exists()])


def candidate_roots() -> tuple[list[Path], list[Path], list[Path]]:
    codex_roots: list[Path] = []
    claude_roots: list[Path] = []
    claude_aux_roots: list[Path] = []
    for home in user_home_candidates():
        codex_roots.append(home / ".codex" / "sessions")
        claude_roots.append(home / ".claude" / "projects")
        claude_aux_roots.extend([home / ".claude" / "sessions", home / ".claude" / "tasks"])
    claude_roots = unique_paths([root for root in claude_roots if root.exists()])
    if any(str(root.expanduser().resolve()).startswith("/Users/") for root in claude_roots):
        claude_roots = [root for root in claude_roots if not str(root.expanduser().resolve()).startswith("/tank/")]
    return (
        unique_paths([root for root in codex_roots if root.exists()]),
        claude_roots,
        unique_paths([root for root in claude_aux_roots if root.exists()]),
    )


def inventory_root(root: Path, limit_records: int = 20000) -> CorpusStats:
    real = root.expanduser().resolve()
    stats = CorpusStats(str(root), str(real))
    seen: set[tuple[int, int]] = set()
    if not real.exists():
        return stats
    iterable = [real] if real.is_file() else real.rglob("*")
    for path in iterable:
        try:
            st = path.stat()
        except OSError:
            continue
        if not path.is_file():
            continue
        inode = (st.st_dev, st.st_ino)
        if inode in seen:
            continue
        seen.add(inode)
        stats.files += 1
        stats.bytes += st.st_size
        stats.oldest = st.st_mtime if stats.oldest is None else min(stats.oldest, st.st_mtime)
        stats.newest = st.st_mtime if stats.newest is None else max(stats.newest, st.st_mtime)
        stats.suffixes[path.suffix or "<none>"] += 1
        if path.suffix == ".jsonl" and sum(stats.record_types.values()) < limit_records:
            for _, obj in read_jsonl(path):
                stats.record_types[str(obj.get("type") or obj.get("role") or "<none>")] += 1
                if sum(stats.record_types.values()) >= limit_records:
                    break
    return stats


def collect_jsonl_files(roots: list[Path], max_per_root: int = 0) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        real = root.expanduser().resolve()
        if not real.exists():
            continue
        try:
            result = subprocess.run(
                ["find", str(real), "-type", "f", "-name", "*.jsonl"],
                check=False,
                text=True,
                capture_output=True,
                timeout=30,
            )
            found = [Path(line) for line in result.stdout.splitlines() if line]
        except subprocess.TimeoutExpired:
            print(f"warning: timed out discovering {real}; skipping", file=sys.stderr)
            found = []
        except OSError:
            iterator = real.glob("**/*.jsonl")
            found = [path for path in iterator if path.is_file()]
        if max_per_root:
            found = found[:max_per_root]
        files.extend(found)
    return unique_paths(files)


def collect_json_files(roots: list[Path], max_per_root: int = 0) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        real = root.expanduser().resolve()
        if not real.exists():
            continue
        try:
            result = subprocess.run(
                ["find", str(real), "-type", "f", "-name", "*.json"],
                check=False,
                text=True,
                capture_output=True,
                timeout=30,
            )
            found = [Path(line) for line in result.stdout.splitlines() if line]
        except subprocess.TimeoutExpired:
            print(f"warning: timed out discovering {real}; skipping", file=sys.stderr)
            found = []
        except OSError:
            found = [path for path in real.glob("**/*.json") if path.is_file()]
        if max_per_root:
            found = found[:max_per_root]
        files.extend(found)
    return unique_paths(files)


def inventory_files(
    label: str,
    roots: list[Path],
    files: list[Path],
    limit_records: int = 0,
) -> CorpusStats:
    stats = CorpusStats(label, ", ".join(str(root.expanduser().resolve()) for root in roots))
    seen: set[tuple[int, int]] = set()
    for path in files:
        try:
            st = path.stat()
        except OSError:
            continue
        inode = (st.st_dev, st.st_ino)
        if inode in seen:
            continue
        seen.add(inode)
        stats.files += 1
        stats.bytes += st.st_size
        stats.oldest = st.st_mtime if stats.oldest is None else min(stats.oldest, st.st_mtime)
        stats.newest = st.st_mtime if stats.newest is None else max(stats.newest, st.st_mtime)
        stats.suffixes[path.suffix or "<none>"] += 1
        if limit_records and sum(stats.record_types.values()) < limit_records:
            for _, obj in read_jsonl(path):
                stats.record_types[str(obj.get("type") or obj.get("role") or "<none>")] += 1
                if sum(stats.record_types.values()) >= limit_records:
                    break
    return stats


def extract_codex_history(path: Path) -> list[Prompt]:
    prompts: list[Prompt] = []
    if not path.exists():
        return prompts
    for _, obj in read_jsonl(path):
        text = safe_text(obj.get("text"))
        if is_probably_injected(text):
            continue
        ts = obj.get("ts")
        timestamp = ""
        if isinstance(ts, (int, float)):
            timestamp = dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc).isoformat()
        prompts.append(
            Prompt(
                source="codex-history",
                session_id=str(obj.get("session_id") or ""),
                project="codex-history",
                timestamp=timestamp,
                text=normalize_space(text),
            )
        )
    return prompts


def extract_codex_session(path: Path) -> tuple[list[Prompt], list[str], list[Prompt]]:
    prompts: list[Prompt] = []
    tools: list[str] = []
    assistant_signals: list[Prompt] = []
    session_id = path.stem
    project = "codex"
    timestamp = ""
    for _, obj in read_jsonl(path):
        typ = obj.get("type")
        payload = obj.get("payload") if isinstance(obj.get("payload"), dict) else {}
        if typ == "session_meta":
            session_id = str(payload.get("id") or session_id)
            project = str(payload.get("cwd") or project)
            timestamp = str(payload.get("timestamp") or timestamp)
            continue
        if typ == "event_msg" and payload.get("type") == "user_message":
            text = safe_text(payload.get("message") or payload.get("text_elements") or "")
            if not is_probably_injected(text):
                prompts.append(
                    Prompt(
                        "codex-session",
                        session_id,
                        project,
                        str(obj.get("timestamp") or timestamp),
                        normalize_space(text),
                    )
                )
            continue
        item = payload.get("item") if isinstance(payload.get("item"), dict) else payload
        name = item.get("name") or payload.get("name") or payload.get("tool_name")
        event_type = payload.get("type")
        if typ == "response_item" and payload.get("type") == "message" and payload.get("role") == "assistant":
            text = safe_text(payload.get("content"))
            if is_assistant_workflow_signal(text):
                assistant_signals.append(
                    Prompt(
                        "codex-assistant",
                        session_id,
                        project,
                        str(obj.get("timestamp") or timestamp),
                        normalize_space(text),
                    )
                )
        if typ == "event_msg" and isinstance(event_type, str):
            if event_type in {"exec_command_begin", "patch_apply_begin", "tool_call_begin"}:
                tools.append(event_type)
        if typ and ("tool" in str(typ) or "function" in str(typ)) and name:
            tools.append(str(name))
        if item.get("type") in {"function_call", "tool_call"} and name:
            tools.append(str(name))
            if name == "exec_command":
                args = parse_json_object(item.get("arguments"))
                if isinstance(args.get("cmd"), str):
                    tools.append(command_family(args["cmd"]))
    return prompts, tools, assistant_signals


def extract_claude_session(path: Path) -> tuple[list[Prompt], list[str], list[Prompt]]:
    prompts: list[Prompt] = []
    tools: list[str] = []
    assistant_signals: list[Prompt] = []
    project = project_from_path(path)
    session_id = path.stem
    for _, obj in read_jsonl(path):
        session_id = str(obj.get("sessionId") or obj.get("session_id") or session_id)
        timestamp = str(obj.get("timestamp") or "")
        typ = str(obj.get("type") or "")
        if obj.get("isSidechain") is True or "subagents" in path.parts:
            continue
        message = obj.get("message") if isinstance(obj.get("message"), dict) else obj
        role = message.get("role") or obj.get("role")
        content = message.get("content") or obj.get("content")
        has_tool_result = False
        if isinstance(content, list):
            has_tool_result = any(isinstance(part, dict) and part.get("type") == "tool_result" for part in content)
        if (
            typ == "user"
            and role == "user"
            and not has_tool_result
            and "sourceToolAssistantUUID" not in obj
            and "toolUseResult" not in obj
        ):
            text = safe_text(message.get("content") or obj.get("content"))
            if not is_probably_injected(text):
                prompts.append(Prompt("claude-message", session_id, project, timestamp, normalize_space(text)))
        if typ == "assistant" and role == "assistant":
            text = safe_text(message.get("content") or obj.get("content"))
            if is_assistant_workflow_signal(text):
                assistant_signals.append(Prompt("claude-assistant", session_id, project, timestamp, normalize_space(text)))
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "tool_use":
                    tools.append(str(part.get("name") or "tool_use"))
                    if part.get("name") == "Bash":
                        command = part.get("input", {}).get("command") if isinstance(part.get("input"), dict) else ""
                        if isinstance(command, str):
                            tools.append(command_family(command))
        if typ in {"tool_use", "tool-call"} and obj.get("name"):
            tools.append(str(obj.get("name")))
    return prompts, tools, assistant_signals


def classify_prompt(text: str) -> set[str]:
    hits: set[str] = set()
    for key, meta in INTENTS.items():
        for pattern in meta["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                hits.add(key)
                break
    return hits


def classify_exploratory(text: str) -> set[str]:
    hits: set[str] = set()
    for key, meta in EXPLORATORY_INTENTS.items():
        for pattern in meta["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                hits.add(key)
                break
    return hits


def prompt_opening(text: str) -> str:
    text = summarize_shape(text)
    text = re.sub(r"^#+\s*", "", text)
    words = text.split()
    return " ".join(words[:10])


STOPWORDS = {
    "the",
    "and",
    "that",
    "this",
    "with",
    "from",
    "have",
    "there",
    "what",
    "about",
    "should",
    "would",
    "could",
    "then",
    "into",
    "need",
    "needs",
    "using",
    "make",
    "review",
    "plan",
    "work",
    "please",
    "okay",
    "good",
    "let",
    "lets",
}


def tokens_for_ngrams(text: str) -> list[str]:
    text = re.sub(r"`[^`]+`", " ", text.lower())
    text = re.sub(r"/[a-z0-9._~/-]+", " ", text)
    text = re.sub(r"[^a-z0-9+.#-]+", " ", text)
    tokens = [token.strip("-") for token in text.split()]
    return [token for token in tokens if len(token) > 2 and token not in STOPWORDS and not token.isdigit()]


def interesting_ngrams(text: str) -> list[str]:
    tokens = tokens_for_ngrams(text)
    phrases: list[str] = []
    for n in (2, 3, 4):
        for index in range(0, max(0, len(tokens) - n + 1)):
            phrase = " ".join(tokens[index : index + n])
            if len(phrase) >= 8:
                phrases.append(phrase)
    return phrases


def load_existing_skills() -> list[dict[str, str]]:
    roots = [
        ROOT / "skills",
    ]
    for home in user_home_candidates():
        roots.extend([home / ".codex" / "skills", home / ".agents" / "skills", home / ".claude" / "skills"])
    skills: dict[str, dict[str, str]] = {}
    for root in roots:
        if not root.exists():
            continue
        for skill_md in root.glob("*/SKILL.md"):
            text = skill_md.read_text(encoding="utf-8", errors="replace")
            name = ""
            desc = ""
            match = re.match(r"---\n(.*?)\n---", text, re.S)
            if match:
                for line in match.group(1).splitlines():
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip().strip('"')
                    if line.startswith("description:"):
                        desc = line.split(":", 1)[1].strip().strip('"')
            if name:
                skills[name] = {"name": name, "description": desc, "path": str(skill_md)}
    return sorted(skills.values(), key=lambda item: item["name"])


def write_manifest(paths: list[Path], output: Path) -> None:
    records = []
    for path in paths:
        real = path.expanduser().resolve()
        if not real.exists():
            continue
        if not real.is_file():
            continue
        try:
            st = real.stat()
        except OSError:
            continue
        records.append(
            {
                "path": str(path),
                "realpath": str(real),
                "bytes": st.st_size,
                "mtime": st.st_mtime,
            }
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(records, indent=2), encoding="utf-8")

def generate_report(
    stats: list[CorpusStats],
    prompts: list[Prompt],
    assistant_signals: list[Prompt],
    tool_sequences: dict[str, list[str]],
    existing_skills: list[dict[str, str]],
    output: Path,
) -> None:
    by_intent: dict[str, list[Prompt]] = collections.defaultdict(list)
    for prompt in prompts:
        for intent in classify_prompt(prompt.text):
            by_intent[intent].append(prompt)

    lines: list[str] = []
    lines.append("# Session Skill Candidate Analysis")
    lines.append("")
    lines.append(f"Generated: {dt.datetime.now(dt.timezone.utc).isoformat()}")
    lines.append("")
    lines.append("## Corpus Inventory")
    lines.append("")
    for stat in stats:
        lines.append(f"- `{stat.root}` -> `{stat.real_root}`")
        lines.append(
            f"  files={stat.files}, bytes={stat.bytes:,}, date_range={iso(stat.oldest)}..{iso(stat.newest)}"
        )
        if stat.suffixes:
            suffixes = ", ".join(f"{k}:{v}" for k, v in stat.suffixes.most_common(8))
            lines.append(f"  suffixes: {suffixes}")
        if stat.record_types:
            types = ", ".join(f"{k}:{v}" for k, v in stat.record_types.most_common(10))
            lines.append(f"  sampled record types: {types}")
    lines.append("")
    lines.append("## Extraction Assumptions")
    lines.append("")
    lines.append("- Codex `history.jsonl` is treated as the highest-confidence Codex human-prompt source.")
    lines.append("- Codex session JSONL is mined for `event_msg.payload.type == user_message` records.")
    lines.append("- Claude JSONL is mined only for main-session `type == user`, `message.role == user` records without tool-result linkage.")
    lines.append("- Assistant workflow signals are mined separately from assistant messages and never counted as direct user demand.")
    lines.append("- Automation-like harness prompts are retained but counted separately from direct human-ish prompts.")
    lines.append("- Repeated generated prompt templates are counted separately from manual direct prompts.")
    lines.append("- Counts are distinct sessions/projects where possible; raw occurrence counts are shown as secondary evidence.")
    lines.append("")
    lines.append("## Existing Skill Baseline")
    lines.append("")
    for skill in existing_skills:
        lines.append(f"- `{skill['name']}`: {skill['description']}")
    lines.append("")
    lines.append("## Candidate Ranking")
    lines.append("")
    lines.append("Primary ranking is based on direct human-ish prompt matches. Automation-like")
    lines.append("harness prompts are retained as evidence but do not drive the score.")
    lines.append("")

    ranked = []
    for intent, matches in by_intent.items():
        sessions = {m.session_id for m in matches if m.session_id}
        projects = {m.project for m in matches if m.project}
        non_easel = [m for m in matches if "easel-skills" not in m.project]
        direct = [m for m in matches if not is_automation_like(m.text) and not is_template_like(m.text)]
        automation = [m for m in matches if is_automation_like(m.text)]
        templated = [m for m in matches if not is_automation_like(m.text) and is_template_like(m.text)]
        direct_sessions = {m.session_id for m in direct if m.session_id}
        direct_projects = {m.project for m in direct if m.project}
        score = len(direct_sessions) * 3 + len(direct_projects) * 2 + len(direct)
        ranked.append((score, intent, matches, sessions, projects, non_easel, direct, automation, templated))
    ranked.sort(reverse=True)

    for score, intent, matches, sessions, projects, non_easel, direct, automation, templated in ranked:
        meta = INTENTS[intent]
        lines.append(f"### {meta['title']}")
        lines.append("")
        lines.append(f"- Intent key: `{intent}`")
        lines.append(f"- Score: {score}")
        lines.append(f"- Occurrences: {len(matches)}")
        lines.append(f"- Manual direct occurrences: {len(direct)}")
        lines.append(f"- Templated prompt occurrences: {len(templated)}")
        lines.append(f"- Automation-like occurrences: {len(automation)}")
        lines.append(f"- Distinct sessions: {len(sessions)}")
        lines.append(f"- Distinct projects: {len(projects)}")
        lines.append(f"- Non-easel occurrences: {len(non_easel)}")
        lines.append(f"- Baseline classification: `{meta['baseline']}`")
        lines.append(f"- Existing coverage: {meta['covered_by']}")
        lines.append("- Representative direct prompt shapes:")
        shape_counts = collections.Counter()
        for match in direct:
            shape = summarize_shape(match.text)
            shape_counts[shape] += 1
        if shape_counts:
            for shape, count in shape_counts.most_common(5):
                lines.append(f"  - ({count}) {shape}")
        else:
            lines.append("  - None detected.")
        if automation:
            lines.append("- Representative automation-like prompt shapes:")
            auto_counts = collections.Counter(summarize_shape(match.text) for match in automation)
            for shape, count in auto_counts.most_common(3):
                lines.append(f"  - ({count}) {shape}")
        if templated:
            lines.append("- Representative templated prompt shapes:")
            template_counts = collections.Counter(summarize_shape(match.text) for match in templated)
            for shape, count in template_counts.most_common(3):
                lines.append(f"  - ({count}) {shape}")
        lines.append("")

    lines.append("## Exploratory Candidate Signals")
    lines.append("")
    lines.append("These are broader pattern matches added after the first full-corpus pass.")
    lines.append("They separate manual direct prompts from repeated generated templates.")
    lines.append("Assistant workflow signals and automation prompts are not counted here.")
    lines.append("")
    exploratory: dict[str, list[Prompt]] = collections.defaultdict(list)
    for prompt in prompts:
        if is_automation_like(prompt.text):
            continue
        for intent in classify_exploratory(prompt.text):
            exploratory[intent].append(prompt)
    exploratory_ranked = []
    for intent, matches in exploratory.items():
        manual = [m for m in matches if not is_template_like(m.text)]
        templated = [m for m in matches if is_template_like(m.text)]
        sessions = {m.session_id for m in matches if m.session_id}
        projects = {m.project for m in matches if m.project}
        score = len(manual) * 3 + min(len(templated), 2000) + len(sessions) * 2 + len(projects)
        exploratory_ranked.append((score, intent, matches, manual, templated, sessions, projects))
    exploratory_ranked.sort(reverse=True)
    for score, intent, matches, manual, templated, sessions, projects in exploratory_ranked:
        meta = EXPLORATORY_INTENTS[intent]
        lines.append(f"### {meta['title']}")
        lines.append("")
        lines.append(f"- Intent key: `{intent}`")
        lines.append(f"- Score: {score}")
        lines.append(f"- Manual direct occurrences: {len(manual)}")
        lines.append(f"- Templated prompt occurrences: {len(templated)}")
        lines.append(f"- Distinct sessions: {len(sessions)}")
        lines.append(f"- Distinct projects: {len(projects)}")
        lines.append(f"- Portability read: {meta['portable_read']}")
        lines.append("- Representative manual prompt shapes:")
        shape_counts = collections.Counter(summarize_shape(match.text) for match in manual)
        for shape, count in shape_counts.most_common(5):
            lines.append(f"  - ({count}) {shape}")
        if not shape_counts:
            lines.append("  - None detected.")
        if templated:
            lines.append("- Representative templated prompt shapes:")
            template_counts = collections.Counter(summarize_shape(match.text) for match in templated)
            for shape, count in template_counts.most_common(5):
                lines.append(f"  - ({count}) {shape}")
        lines.append("")

    lines.append("## Emergent Prompt Shapes")
    lines.append("")
    direct_prompts = [prompt for prompt in prompts if not is_automation_like(prompt.text) and not is_template_like(prompt.text)]
    templated_prompts = [prompt for prompt in prompts if not is_automation_like(prompt.text) and is_template_like(prompt.text)]
    opening_counts = collections.Counter(prompt_opening(prompt.text) for prompt in direct_prompts)
    for opening, count in opening_counts.most_common(40):
        if count >= 3 and opening:
            lines.append(f"- {count}: {opening}")
    lines.append("")

    lines.append("## Templated Prompt Shapes")
    lines.append("")
    template_opening_counts = collections.Counter(prompt_opening(prompt.text) for prompt in templated_prompts)
    for opening, count in template_opening_counts.most_common(40):
        if count >= 3 and opening:
            lines.append(f"- {count}: {opening}")
    lines.append("")

    lines.append("## Emergent Prompt N-Grams")
    lines.append("")
    ngram_counts = collections.Counter()
    for prompt in direct_prompts:
        for phrase in set(interesting_ngrams(prompt.text)):
            ngram_counts[phrase] += 1
    for phrase, count in ngram_counts.most_common(50):
        if count >= 5:
            lines.append(f"- {count}: {phrase}")
    lines.append("")

    lines.append("## Assistant Workflow Signals")
    lines.append("")
    assistant_openings = collections.Counter(prompt_opening(signal.text) for signal in assistant_signals)
    if assistant_openings:
        for opening, count in assistant_openings.most_common(30):
            if count >= 2 and opening:
                lines.append(f"- {count}: {opening}")
    else:
        lines.append("- No repeated assistant workflow signals extracted.")
    lines.append("")

    lines.append("## Frequent Prompt Phrases")
    lines.append("")
    phrase_counts = collections.Counter()
    for prompt in prompts:
        for phrase in extract_phrases(prompt.text):
            phrase_counts[phrase] += 1
    for phrase, count in phrase_counts.most_common(40):
        lines.append(f"- {count}: {phrase}")
    lines.append("")

    lines.append("## Tool Sequence Signals")
    lines.append("")
    seq_counts = collections.Counter()
    for tools in tool_sequences.values():
        if len(tools) >= 2:
            seq_counts[" -> ".join(tools[:8])] += 1
    if seq_counts:
        for seq, count in seq_counts.most_common(30):
            lines.append(f"- {count}: `{seq}`")
    else:
        lines.append("- No repeated tool sequences extracted from sampled schemas.")
    lines.append("")

    lines.append("## Command Family Signals")
    lines.append("")
    command_counts = collections.Counter()
    for tools in tool_sequences.values():
        for tool in tools:
            if tool.startswith("cmd:"):
                command_counts[tool] += 1
    if command_counts:
        for command, count in command_counts.most_common(40):
            lines.append(f"- {count}: `{command}`")
    else:
        lines.append("- No command families extracted.")
    lines.append("")

    lines.append("## Suggested Next Skill Work")
    lines.append("")
    lines.append("1. The already-built `repo-triage`, `release-management`, and `adversarial-review` extensions still match strong manual-request signals.")
    lines.append("2. Consider a new data-quality skill for Great Expectations-style validation rule generation and JSON expectation output.")
    lines.append("3. Consider a data-documentation skill for schema/table documentation generation, with healthcare as an optional adapter rather than core vocabulary.")
    lines.append("4. Consider a data-mapping skill for survivorship mappings, filename pattern extraction, and source-to-target derivation workflows.")
    lines.append("5. Keep strict JSON/hash output contract material as an `adversarial-review` reference extension unless it grows beyond review/prompt contracts.")
    lines.append("6. Treat cloud deploy, CI repair, and PR comment handling as already covered by installed external skills unless Easel should vendor them.")
    lines.append("7. Keep DDx/bead/HELIX specifics out of core Easel skills unless implemented as optional adapters.")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def summarize_shape(text: str) -> str:
    text = normalize_space(text, 220)
    replacements = [
        (r"\b[0-9a-f]{7,40}\b", "<sha>"),
        (r"/[A-Za-z0-9._~/-]+", "<path>"),
        (r"\b\d+(?:\.\d+)?\b", "<n>"),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    return text


def extract_phrases(text: str) -> list[str]:
    lower = text.lower()
    phrases = [
        "commit and push",
        "review this plan",
        "review with claude",
        "make a plan",
        "execute the plan",
        "fold in",
        "docker",
        "marketplace",
        "point release",
        "test everything",
        "install",
        "validate",
        "sloptimizer",
        "skill",
        "plugin",
        "sub-agent",
    ]
    return [phrase for phrase in phrases if phrase in lower]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR))
    parser.add_argument("--max-session-files", type=int, default=0, help="0 means all")
    parser.add_argument("--discovery-only", action="store_true")
    parser.add_argument("--progress-every", type=int, default=1000)
    args = parser.parse_args()

    codex_roots, claude_roots, claude_aux_roots = candidate_roots()
    codex_history_files = unique_paths(
        [home / ".codex" / "history.jsonl" for home in user_home_candidates() if (home / ".codex" / "history.jsonl").exists()]
    )
    codex_files = collect_jsonl_files(codex_roots, args.max_session_files)
    claude_files = collect_jsonl_files(claude_roots, args.max_session_files)
    claude_aux_files = collect_json_files(claude_aux_roots, args.max_session_files)
    stats = [
        inventory_files("codex sessions", codex_roots, codex_files),
        inventory_files("claude projects", claude_roots, claude_files),
        inventory_files("claude auxiliary json", claude_aux_roots, claude_aux_files),
    ]
    for codex_history in codex_history_files:
        stats.append(inventory_root(codex_history))

    state_dir = Path(args.state_dir)
    write_manifest(codex_files + claude_files + claude_aux_files + codex_history_files, state_dir / "corpus-manifest.json")

    prompts: list[Prompt] = []
    assistant_signals: list[Prompt] = []
    tool_sequences: dict[str, list[str]] = {}
    for codex_history in codex_history_files:
        prompts.extend(extract_codex_history(codex_history))

    for index, path in enumerate(codex_files, 1):
        if args.progress_every and index % args.progress_every == 0:
            print(f"progress: codex {index}/{len(codex_files)} files", file=sys.stderr)
        found, tools, assistant = extract_codex_session(path)
        prompts.extend(found)
        assistant_signals.extend(assistant)
        if tools:
            tool_sequences[str(path)] = tools
    for index, path in enumerate(claude_files, 1):
        if args.progress_every and index % args.progress_every == 0:
            print(f"progress: claude {index}/{len(claude_files)} files", file=sys.stderr)
        found, tools, assistant = extract_claude_session(path)
        prompts.extend(found)
        assistant_signals.extend(assistant)
        if tools:
            tool_sequences[str(path)] = tools

    existing_skills = load_existing_skills()
    output = Path(args.output)
    generate_report(stats, prompts, assistant_signals, tool_sequences, existing_skills, output)

    summary = {
        "prompts": len(prompts),
        "assistant_workflow_signals": len(assistant_signals),
        "codex_session_files": len(codex_files),
        "claude_session_files": len(claude_files),
        "claude_aux_json_files": len(claude_aux_files),
        "codex_history_files": len(codex_history_files),
        "tool_sequence_sessions": len(tool_sequences),
        "report": str(output),
        "manifest": str(state_dir / "corpus-manifest.json"),
    }
    (state_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
