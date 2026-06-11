#!/usr/bin/env python3
"""Find near-duplicate paragraphs in prose files.

Usage:
    redundancy-audit.py [--threshold 0.25] [--top 25] PATH ...
    redundancy-audit.py --changed [--threshold 0.25] [--top 25]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

MIN_WORDS = 15
SHINGLE_N = 3
PROSE_SUFFIXES = {".md", ".mdx", ".rst", ".txt"}


def normalize(text: str) -> list[str]:
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\W+", " ", text.lower())
    return [w for w in text.split() if len(w) > 2]


def shingles(words: list[str], n: int = SHINGLE_N) -> set[tuple[str, ...]]:
    if len(words) < n:
        return set()
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(
                p for p in sorted(path.rglob("*")) if p.is_file() and p.suffix in PROSE_SUFFIXES
            )
        elif path.is_file() and path.suffix in PROSE_SUFFIXES:
            files.append(path)
    return files


def changed_files() -> list[Path]:
    try:
        raw = subprocess.check_output(
            ["git", "diff", "--name-only", "--diff-filter=ACMR"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        print("redundancy-audit: --changed requires git inside a work tree", file=sys.stderr)
        raise SystemExit(2)
    return [Path(line) for line in raw.splitlines() if Path(line).suffix in PROSE_SUFFIXES]


def paragraphs(path: Path) -> list[tuple[str, set[tuple[str, ...]]]]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :]

    out: list[tuple[str, set[tuple[str, ...]]]] = []
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block or block.startswith(("#", "|", "-", "*", ">", "```", "{{")):
            continue
        words = normalize(block)
        if len(words) < MIN_WORDS:
            continue
        sh = shingles(words)
        if sh:
            out.append((" ".join(block.split())[:120], sh))
    return out


def jaccard(a: set[tuple[str, ...]], b: set[tuple[str, ...]]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--changed", action="store_true")
    parser.add_argument("--threshold", type=float, default=0.25)
    parser.add_argument("--top", type=int, default=25)
    args = parser.parse_args()

    paths = changed_files() if args.changed else args.paths
    if not paths:
        print("usage: redundancy-audit.py [--changed|PATH ...]", file=sys.stderr)
        return 2

    files = iter_files(paths)
    if not files:
        print("redundancy-audit: no prose files")
        return 0

    items: list[tuple[Path, str, set[tuple[str, ...]]]] = []
    for path in files:
        for preview, sh in paragraphs(path):
            items.append((path, preview, sh))

    pairs: list[tuple[float, Path, str, Path, str]] = []
    for i, (fa, pa, sa) in enumerate(items):
        for fb, pb, sb in items[i + 1 :]:
            if fa == fb:
                continue
            score = jaccard(sa, sb)
            if score >= args.threshold:
                pairs.append((score, fa, pa, fb, pb))
    pairs.sort(reverse=True, key=lambda x: x[0])

    if not pairs:
        print(
            f"OK: no cross-file paragraph pairs >= {args.threshold} similarity "
            f"({len(items)} paragraphs scanned)"
        )
        return 0

    print(
        f"FAIL: {len(pairs)} cross-file paragraph pair(s) >= {args.threshold} "
        f"similarity (top {args.top}):"
    )
    for score, fa, pa, fb, pb in pairs[: args.top]:
        print(f"\n  similarity={score:.2f}")
        print(f"  {fa}")
        print(f"    {pa}")
        print(f"  {fb}")
        print(f"    {pb}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
