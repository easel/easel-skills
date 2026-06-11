#!/usr/bin/env python3
"""Check Markdown table documentation coverage against schema-like JSON."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.$-]*")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Could not read schema: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON schema: {exc}") from exc


def as_name(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, dict):
        for key in ("name", "column_name", "field", "field_name"):
            item = value.get(key)
            if isinstance(item, str) and item.strip():
                return item.strip()
    return None


def column_names(value: Any) -> set[str]:
    columns: set[str] = set()
    if isinstance(value, dict):
        raw_columns = (
            value.get("columns")
            or value.get("fields")
            or value.get("schema")
            or value.get("properties")
            or []
        )
        if isinstance(raw_columns, dict):
            columns.update(str(key) for key in raw_columns)
        elif isinstance(raw_columns, list):
            for item in raw_columns:
                name = as_name(item)
                if name:
                    columns.add(name)
    elif isinstance(value, list):
        for item in value:
            name = as_name(item)
            if name:
                columns.add(name)
    return columns


def table_records(data: Any) -> dict[str, set[str]]:
    records: dict[str, set[str]] = {}

    def add_table(name: str | None, value: Any) -> None:
        if not name:
            return
        records.setdefault(name, set()).update(column_names(value))

    if isinstance(data, dict):
        tables = data.get("tables") or data.get("datasets") or data.get("relations")
        if isinstance(tables, list):
            for item in tables:
                add_table(as_name(item), item)
        elif isinstance(tables, dict):
            for name, value in tables.items():
                add_table(str(name), value)
        elif "name" in data:
            add_table(as_name(data), data)
        else:
            for name, value in data.items():
                if isinstance(value, (dict, list)):
                    add_table(str(name), value)
    elif isinstance(data, list):
        for item in data:
            add_table(as_name(item), item)

    return records


def markdown_identifiers(path: Path) -> set[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Could not read docs: {exc}") from exc

    identifiers = {
        token.strip(".")
        for token in IDENT_RE.findall(text)
        if token.strip(".")
    }
    identifiers.update(match.group(1) for match in re.finditer(r"`([^`]+)`", text))
    return identifiers


def compact(items: set[str]) -> list[str]:
    return sorted(items, key=lambda item: item.lower())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", required=True, help="Path to schema JSON")
    parser.add_argument("--docs", required=True, help="Path to Markdown docs")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of a human-readable report",
    )
    args = parser.parse_args()

    schema_path = Path(args.schema)
    docs_path = Path(args.docs)
    tables = table_records(load_json(schema_path))
    if not tables:
        raise SystemExit("No tables found in schema JSON")

    mentioned = markdown_identifiers(docs_path)
    schema_tables = set(tables)
    schema_columns = {column for columns in tables.values() for column in columns}

    missing_tables = schema_tables - mentioned
    missing_columns = schema_columns - mentioned
    mentioned_identifiers = {
        item for item in mentioned if "." in item or "_" in item or item in schema_columns
    }
    unknown_identifiers = mentioned_identifiers - schema_tables - schema_columns

    report = {
        "schema": str(schema_path),
        "docs": str(docs_path),
        "table_count": len(schema_tables),
        "column_count": len(schema_columns),
        "missing_tables": compact(missing_tables),
        "missing_columns": compact(missing_columns),
        "unknown_identifiers": compact(unknown_identifiers),
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Schema tables: {report['table_count']}")
        print(f"Schema columns: {report['column_count']}")
        for key, label in (
            ("missing_tables", "Tables not mentioned in docs"),
            ("missing_columns", "Columns not mentioned in docs"),
            ("unknown_identifiers", "Doc identifiers not found in schema"),
        ):
            values = report[key]
            print(f"{label}: {len(values)}")
            for value in values[:50]:
                print(f"  - {value}")
            if len(values) > 50:
                print(f"  ... {len(values) - 50} more")

    return 1 if missing_tables or missing_columns else 0


if __name__ == "__main__":
    sys.exit(main())
