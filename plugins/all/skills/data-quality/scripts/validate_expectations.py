#!/usr/bin/env python3
"""Validate basic Great Expectations-style JSON structure without dependencies."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> tuple[Any | None, list[str]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle), []
    except FileNotFoundError:
        return None, [f"{path}: file not found"]
    except json.JSONDecodeError as exc:
        return None, [f"{path}:{exc.lineno}:{exc.colno}: invalid JSON: {exc.msg}"]
    except OSError as exc:
        return None, [f"{path}: cannot read file: {exc}"]


def _expectations_from_document(document: Any) -> tuple[list[Any], list[str]]:
    if isinstance(document, list):
        return document, []

    if not isinstance(document, dict):
        return [], ["root must be an object or an array of expectations"]

    if "expectations" not in document:
        return [], ["suite object must contain an 'expectations' array"]

    expectations = document["expectations"]
    if not isinstance(expectations, list):
        return [], ["'expectations' must be an array"]

    errors: list[str] = []
    suite_name = document.get("expectation_suite_name")
    if suite_name is not None and not isinstance(suite_name, str):
        errors.append("'expectation_suite_name' must be a string when present")

    meta = document.get("meta")
    if meta is not None and not isinstance(meta, dict):
        errors.append("suite 'meta' must be an object when present")

    return expectations, errors


def _validate_expectation(item: Any, index: int) -> list[str]:
    prefix = f"expectations[{index}]"
    errors: list[str] = []

    if not isinstance(item, dict):
        return [f"{prefix} must be an object"]

    expectation_type = item.get("expectation_type", item.get("type"))
    if not isinstance(expectation_type, str) or not expectation_type.strip():
        errors.append(f"{prefix}.expectation_type must be a non-empty string")

    if "kwargs" not in item:
        errors.append(f"{prefix}.kwargs is required")
    elif not isinstance(item["kwargs"], dict):
        errors.append(f"{prefix}.kwargs must be an object")

    meta = item.get("meta")
    if meta is not None and not isinstance(meta, dict):
        errors.append(f"{prefix}.meta must be an object when present")

    unexpected_keys = sorted(
        key
        for key in item
        if key not in {"expectation_type", "type", "kwargs", "meta", "notes"}
    )
    if unexpected_keys:
        joined = ", ".join(unexpected_keys)
        errors.append(f"{prefix} contains unrecognized key(s): {joined}")

    return errors


def validate_document(document: Any) -> list[str]:
    expectations, errors = _expectations_from_document(document)
    if errors and not expectations:
        return errors

    if not expectations:
        errors.append("expectations array must not be empty")

    for index, item in enumerate(expectations):
        errors.extend(_validate_expectation(item, index))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate basic Great Expectations-style expectation JSON shape."
    )
    parser.add_argument("path", type=Path, help="Path to a JSON expectation suite")
    args = parser.parse_args()

    document, load_errors = _load_json(args.path)
    if load_errors:
        for error in load_errors:
            print(error, file=sys.stderr)
        return 1

    errors = validate_document(document)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"{args.path}: valid expectation JSON structure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
