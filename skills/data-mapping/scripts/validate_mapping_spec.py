#!/usr/bin/env python3
"""Validate a portable data mapping and survivorship JSON spec."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = {
    "version": str,
    "sources": list,
    "targets": list,
    "mappings": list,
}

OPTIONAL_ARRAYS = {
    "canonical_names",
    "extraction_rules",
    "survivorship",
    "open_questions",
}

VALID_CONFIDENCE = {"high", "medium", "low"}
VALID_CONFLICT_POLICIES = {
    "prefer_first",
    "prefer_first_non_null",
    "prefer_latest",
    "prefer_non_null",
    "aggregate",
    "concatenate",
    "manual_review",
    "reject",
}


def fail(errors: list[str], location: str, message: str) -> None:
    errors.append(f"{location}: {message}")


def require_string(errors: list[str], obj: dict[str, Any], key: str, location: str) -> None:
    if key not in obj:
        fail(errors, location, f"missing required key '{key}'")
    elif not isinstance(obj[key], str) or not obj[key].strip():
        fail(errors, location, f"'{key}' must be a non-empty string")


def require_array(errors: list[str], obj: dict[str, Any], key: str, location: str) -> None:
    if key not in obj:
        fail(errors, location, f"missing required key '{key}'")
    elif not isinstance(obj[key], list):
        fail(errors, location, f"'{key}' must be an array")


def validate_top_level(spec: dict[str, Any], errors: list[str]) -> None:
    for key, expected_type in REQUIRED_TOP_LEVEL.items():
        if key not in spec:
            fail(errors, "$", f"missing required top-level key '{key}'")
            continue
        if not isinstance(spec[key], expected_type):
            fail(errors, f"$.{key}", f"must be {expected_type.__name__}")

    for key in OPTIONAL_ARRAYS:
        if key in spec and not isinstance(spec[key], list):
            fail(errors, f"$.{key}", "must be an array")


def validate_named_items(
    errors: list[str],
    items: list[Any],
    location: str,
    required_name: str = "name",
) -> set[str]:
    seen: set[str] = set()
    for index, item in enumerate(items):
        item_location = f"{location}[{index}]"
        if not isinstance(item, dict):
            fail(errors, item_location, "must be an object")
            continue
        require_string(errors, item, required_name, item_location)
        value = item.get(required_name)
        if isinstance(value, str) and value.strip():
            if value in seen:
                fail(errors, item_location, f"duplicate {required_name} '{value}'")
            seen.add(value)
    return seen


def validate_mappings(spec: dict[str, Any], errors: list[str]) -> None:
    target_counts: dict[str, int] = {}
    for index, mapping in enumerate(spec.get("mappings", [])):
        location = f"$.mappings[{index}]"
        if not isinstance(mapping, dict):
            fail(errors, location, "must be an object")
            continue

        require_string(errors, mapping, "id", location)
        require_string(errors, mapping, "target", location)
        require_array(errors, mapping, "sources", location)
        require_string(errors, mapping, "transform", location)

        sources = mapping.get("sources")
        if isinstance(sources, list):
            transform = mapping.get("transform")
            allow_empty_sources = transform in {"unmapped", "manual_review"}
            if not sources and not allow_empty_sources:
                fail(
                    errors,
                    location,
                    "'sources' must not be empty unless transform is unmapped or manual_review",
                )
            for source_index, source in enumerate(sources):
                if not isinstance(source, str) or not source.strip():
                    fail(errors, f"{location}.sources[{source_index}]", "must be a non-empty string")

        if "required" in mapping and not isinstance(mapping["required"], bool):
            fail(errors, location, "'required' must be boolean when present")

        confidence = mapping.get("confidence")
        if confidence is not None and confidence not in VALID_CONFIDENCE:
            fail(errors, location, f"'confidence' must be one of {sorted(VALID_CONFIDENCE)}")

        target = mapping.get("target")
        if isinstance(target, str) and target.strip():
            target_counts[target] = target_counts.get(target, 0) + 1

    for target, count in sorted(target_counts.items()):
        if count > 1:
            fail(errors, "$.mappings", f"target '{target}' appears in {count} mappings")


def validate_extraction_rules(spec: dict[str, Any], errors: list[str]) -> None:
    for index, rule in enumerate(spec.get("extraction_rules", [])):
        location = f"$.extraction_rules[{index}]"
        if not isinstance(rule, dict):
            fail(errors, location, "must be an object")
            continue

        require_string(errors, rule, "id", location)
        require_string(errors, rule, "input", location)
        require_string(errors, rule, "pattern", location)
        require_array(errors, rule, "outputs", location)

        pattern = rule.get("pattern")
        if isinstance(pattern, str):
            try:
                re.compile(pattern)
            except re.error as exc:
                fail(errors, location, f"'pattern' is not valid regex: {exc}")

        outputs = rule.get("outputs")
        if isinstance(outputs, list):
            for output_index, output in enumerate(outputs):
                if not isinstance(output, str) or not output.strip():
                    fail(errors, f"{location}.outputs[{output_index}]", "must be a non-empty string")


def validate_survivorship(spec: dict[str, Any], errors: list[str]) -> None:
    for index, rule in enumerate(spec.get("survivorship", [])):
        location = f"$.survivorship[{index}]"
        if not isinstance(rule, dict):
            fail(errors, location, "must be an object")
            continue

        require_string(errors, rule, "id", location)
        require_string(errors, rule, "target", location)
        require_array(errors, rule, "priority", location)
        require_string(errors, rule, "conflict_policy", location)

        priority = rule.get("priority")
        if isinstance(priority, list):
            if not priority:
                fail(errors, location, "'priority' must not be empty")
            seen_priority: set[str] = set()
            for priority_index, source in enumerate(priority):
                if not isinstance(source, str) or not source.strip():
                    fail(errors, f"{location}.priority[{priority_index}]", "must be a non-empty string")
                elif source in seen_priority:
                    fail(errors, location, f"duplicate priority source '{source}'")
                else:
                    seen_priority.add(source)

        policy = rule.get("conflict_policy")
        if isinstance(policy, str):
            is_custom = policy.startswith("custom:")
            if policy not in VALID_CONFLICT_POLICIES and not is_custom:
                fail(
                    errors,
                    location,
                    "'conflict_policy' must be a known policy or custom:<name>",
                )

        if "manual_review" in rule and not isinstance(rule["manual_review"], bool):
            fail(errors, location, "'manual_review' must be boolean when present")


def validate_spec(spec: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(spec, dict):
        return ["$: spec must be a JSON object"]

    validate_top_level(spec, errors)
    if isinstance(spec.get("sources"), list):
        validate_named_items(errors, spec["sources"], "$.sources")
    if isinstance(spec.get("targets"), list):
        validate_named_items(errors, spec["targets"], "$.targets")
    if isinstance(spec.get("canonical_names"), list):
        validate_named_items(errors, spec["canonical_names"], "$.canonical_names", "canonical")

    validate_mappings(spec, errors)
    validate_extraction_rules(spec, errors)
    validate_survivorship(spec, errors)
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validate_mapping_spec.py path/to/spec.json", file=sys.stderr)
        return 2

    path = Path(argv[1])
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"Could not read {path}: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in {path}: {exc}", file=sys.stderr)
        return 1

    errors = validate_spec(spec)
    if errors:
        print(f"{path}: invalid mapping spec")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"{path}: valid mapping spec")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
