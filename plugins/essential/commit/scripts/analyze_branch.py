#!/usr/bin/env python3 -S
"""
Minimal branch analysis for commit-organizer.

Outputs JSON with branch point, file list, line counts, and diffs.
"""
from __future__ import annotations

import json
import subprocess
import sys


def run_git(*args, timeout: int = 10) -> tuple[str, int]:
    """Run a git command and return (stdout, returncode)."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip(), result.returncode
    except (subprocess.TimeoutExpired, OSError):
        return "", 1


def check_git_repo() -> bool:
    """Check if current directory is a git repository."""
    stdout, code = run_git("rev-parse", "--git-dir")
    return code == 0


def get_current_branch() -> str:
    """Get current branch name."""
    stdout, _ = run_git("branch", "--show-current")
    return stdout or "HEAD"


def detect_main_branch() -> str:
    """Detect the main branch (main or master)."""
    for candidate in ["main", "master"]:
        _, code = run_git("show-ref", "--verify", "--quiet",
                         f"refs/remotes/origin/{candidate}")
        if code == 0:
            return candidate

    # Try symbolic ref
    stdout, code = run_git("symbolic-ref", "refs/remotes/origin/HEAD")
    if code == 0 and stdout:
        return stdout.replace("refs/remotes/origin/", "")

    return "main"


def get_branch_point(main_branch: str) -> tuple[str, str, str]:
    """
    Get branch point info.

    Returns: (short_hash, full_hash, commit_message)
    """
    full_hash, code = run_git("merge-base", "HEAD", f"origin/{main_branch}")
    if code != 0 or not full_hash:
        return "", "", ""

    short_hash, _ = run_git("rev-parse", "--short", full_hash)
    msg, _ = run_git("log", "-1", "--format=%s", full_hash)

    return short_hash, full_hash, msg


def get_changed_files(branch_point: str) -> list[str]:
    """Get list of files changed since branch point."""
    stdout, _ = run_git("diff", "--name-only", branch_point, "HEAD")
    return [f for f in stdout.split('\n') if f]


def get_file_stats(branch_point: str, files: list[str]) -> tuple[list[dict], int, int]:
    """
    Get statistics for changed files.

    Returns: (stats_list, total_additions, total_deletions)
    """
    stats = []
    total_add = 0
    total_del = 0

    for file in files:
        stdout, _ = run_git("diff", "--numstat", branch_point, "HEAD", "--", file)
        if not stdout:
            continue

        parts = stdout.split('\t')
        if len(parts) >= 2:
            add = int(parts[0]) if parts[0] != '-' else 0
            delete = int(parts[1]) if parts[1] != '-' else 0
            total_add += add
            total_del += delete
            stats.append({
                "file": file,
                "additions": add,
                "deletions": delete
            })

    return stats, total_add, total_del


def get_file_diffs(branch_point: str, files: list[str]) -> list[dict]:
    """Get diff content for each file."""
    diffs = []

    for file in files:
        stdout, _ = run_git("diff", branch_point, "HEAD", "--", file)
        diffs.append({
            "file": file,
            "diff": stdout
        })

    return diffs


def main() -> dict:
    """Analyze current branch and return JSON report."""
    # Check if in git repo
    if not check_git_repo():
        return {"error": "Not a git repository"}

    current_branch = get_current_branch()
    main_branch = detect_main_branch()

    short_hash, full_hash, msg = get_branch_point(main_branch)
    if not full_hash:
        return {
            "error": f"Could not find branch point. Ensure origin/{main_branch} exists."
        }

    files = get_changed_files(full_hash)
    stats, total_add, total_del = get_file_stats(full_hash, files)
    diffs = get_file_diffs(full_hash, files)

    return {
        "branch": {
            "current": current_branch,
            "main": main_branch,
            "branch_point": short_hash,
            "branch_point_full": full_hash,
            "branch_point_message": msg
        },
        "files": files,
        "stats": stats,
        "diffs": diffs,
        "total": {
            "files": len(files),
            "additions": total_add,
            "deletions": total_del
        }
    }


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
