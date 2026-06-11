#!/usr/bin/env python3
"""Prepare temporary Vale inputs while preserving line numbers."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


MARKDOWN_SUFFIXES = {".md", ".mdx"}


def blank_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    lines = text.splitlines(keepends=True)
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            frontmatter = lines[: index + 1]
            rest = lines[index + 1 :]
            blanked = ["\n" if line.endswith("\n") else "" for line in frontmatter]
            return "".join(blanked + rest)
    return text


def prepare_path(path: Path, output_root: Path, index: int) -> Path:
    if not path.is_file() or path.suffix.lower() not in MARKDOWN_SUFFIXES:
        return path
    text = path.read_text(encoding="utf-8")
    prepared = blank_frontmatter(text)
    if prepared == text:
        return path
    target_dir = output_root / str(index)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / path.name
    target.write_text(prepared, encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_root")
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    output_root = Path(args.output_root)
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)

    for index, raw_path in enumerate(args.paths):
        print(prepare_path(Path(raw_path), output_root, index))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
