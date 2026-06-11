#!/usr/bin/env python3
"""Emit a read-only JSON snapshot of local Git repository state."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Any


def git(args: list[str], cwd: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def git_out(args: list[str], cwd: str) -> str | None:
    code, out, _err = git(args, cwd)
    if code != 0:
        return None
    return out


def split_lines(value: str | None) -> list[str]:
    if not value:
        return []
    return [line for line in value.splitlines() if line]


def short_sha(ref: str | None, cwd: str) -> str | None:
    if not ref:
        return None
    return git_out(["rev-parse", "--short", ref], cwd)


def ref_exists(ref: str, cwd: str) -> bool:
    code, _out, _err = git(["rev-parse", "--verify", "--quiet", ref], cwd)
    return code == 0


def choose_base(explicit: str | None, upstream: str | None, cwd: str) -> str | None:
    if explicit:
        return explicit
    if upstream:
        return upstream
    for ref in ("origin/HEAD", "main", "master", "origin/main", "origin/master"):
        if ref_exists(ref, cwd):
            return ref
    return None


def ahead_behind(left: str, right: str, cwd: str) -> dict[str, int] | None:
    out = git_out(["rev-list", "--left-right", "--count", f"{left}...{right}"], cwd)
    if not out:
        return None
    parts = out.split()
    if len(parts) != 2:
        return None
    return {"left": int(parts[0]), "right": int(parts[1])}


def parse_status(lines: list[str]) -> dict[str, Any]:
    branch = None
    upstream = None
    ahead = 0
    behind = 0
    entries = []

    for line in lines:
        if line.startswith("## "):
            branch_text = line[3:]
            if "..." in branch_text:
                branch, tracking = branch_text.split("...", 1)
                upstream = tracking.split(" [", 1)[0]
            else:
                branch = branch_text
            if "[ahead " in line:
                ahead = int(line.split("[ahead ", 1)[1].split("]", 1)[0].split(",", 1)[0])
            if "behind " in line:
                behind = int(line.split("behind ", 1)[1].split("]", 1)[0].split(",", 1)[0])
            continue

        if not line:
            continue
        xy = line[:2]
        path = line[3:]
        entries.append({"index": xy[0], "worktree": xy[1], "path": path})

    staged = [item for item in entries if item["index"] not in (" ", "?")]
    unstaged = [item for item in entries if item["worktree"] not in (" ", "?")]
    untracked = [item for item in entries if item["index"] == "?" and item["worktree"] == "?"]

    return {
        "branch_line": branch,
        "upstream_from_status": upstream,
        "ahead_from_status": ahead,
        "behind_from_status": behind,
        "entries": entries,
        "counts": {
            "staged": len(staged),
            "unstaged": len(unstaged),
            "untracked": len(untracked),
            "total": len(entries),
        },
        "paths": {
            "staged": [item["path"] for item in staged],
            "unstaged": [item["path"] for item in unstaged],
            "untracked": [item["path"] for item in untracked],
        },
    }


def recent_commits(limit: int, cwd: str) -> list[dict[str, str]]:
    fmt = "%h%x00%H%x00%an%x00%ad%x00%s"
    out = git_out(["log", f"--max-count={limit}", "--date=short", f"--format={fmt}"], cwd)
    commits = []
    for line in split_lines(out):
        parts = line.split("\x00")
        if len(parts) == 5:
            commits.append(
                {
                    "short_sha": parts[0],
                    "sha": parts[1],
                    "author": parts[2],
                    "date": parts[3],
                    "subject": parts[4],
                }
            )
    return commits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Local ref to compare against")
    parser.add_argument("--limit", type=int, default=8, help="Recent commit limit")
    parser.add_argument("--cwd", default=os.getcwd(), help="Repository directory")
    args = parser.parse_args()

    cwd = os.path.abspath(args.cwd)
    repo_root = git_out(["rev-parse", "--show-toplevel"], cwd)
    if not repo_root:
        print(json.dumps({"error": "not a git repository", "cwd": cwd}, indent=2))
        return 1

    status_lines = split_lines(git_out(["status", "--porcelain=v1", "-b"], repo_root))
    status = parse_status(status_lines)
    branch = git_out(["branch", "--show-current"], repo_root)
    head_sha = git_out(["rev-parse", "HEAD"], repo_root)
    upstream = git_out(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"], repo_root)
    base = choose_base(args.base, upstream, repo_root)

    branch_compare = None
    if base and ref_exists(base, repo_root):
        ahead_behind_counts = ahead_behind("HEAD", base, repo_root)
        merge_base = git_out(["merge-base", "HEAD", base], repo_root)
        diff_files = split_lines(git_out(["diff", "--name-status", f"{base}...HEAD"], repo_root))
        ahead_commits = split_lines(
            git_out(["log", "--oneline", "--decorate=no", f"{base}..HEAD", f"--max-count={args.limit}"], repo_root)
        )
        branch_compare = {
            "base": base,
            "base_short_sha": short_sha(base, repo_root),
            "merge_base": merge_base,
            "merge_base_short_sha": short_sha(merge_base, repo_root),
            "ahead": ahead_behind_counts["left"] if ahead_behind_counts else None,
            "behind": ahead_behind_counts["right"] if ahead_behind_counts else None,
            "files_changed_vs_base": diff_files,
            "ahead_commits": ahead_commits,
        }
    elif base:
        branch_compare = {"base": base, "error": "base ref not found locally"}

    snapshot = {
        "repo_root": repo_root,
        "branch": branch or status["branch_line"],
        "head_sha": head_sha,
        "head_short_sha": short_sha("HEAD", repo_root),
        "upstream": upstream or status["upstream_from_status"],
        "upstream_ahead": status["ahead_from_status"],
        "upstream_behind": status["behind_from_status"],
        "worktree": status,
        "branch_compare": branch_compare,
        "recent_commits": recent_commits(args.limit, repo_root),
        "local_only": True,
        "mutates_worktree": False,
    }
    print(json.dumps(snapshot, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
