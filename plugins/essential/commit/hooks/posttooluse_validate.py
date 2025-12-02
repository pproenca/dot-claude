#!/usr/bin/env python3 -S
"""
PostToolUse hook for commit plugin.

Handles post-commit checks that can't be done before execution:
- Commit size warnings (requires actual commit stats)
- Non-trivial commit body requirement (requires file count)
- Breaking change detection (warns if potential breaking change lacks marker)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

MAX_STDIN_SIZE = 256 * 1024  # 256KB


def get_current_branch() -> str:
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        return ""


def get_commit_message() -> str:
    """Get the most recent commit message."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%B"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        return ""


def get_lines_changed() -> int:
    """Get total lines changed in most recent commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--numstat", "HEAD~1..HEAD"],
            capture_output=True, text=True, timeout=5
        )
        total = 0
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    add = int(parts[0]) if parts[0] != '-' else 0
                    delete = int(parts[1]) if parts[1] != '-' else 0
                    total += add + delete
        return total
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return 0


def get_file_count() -> int:
    """Get count of files changed in most recent commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1..HEAD"],
            capture_output=True, text=True, timeout=5
        )
        return len([f for f in result.stdout.strip().split('\n') if f])
    except (subprocess.TimeoutExpired, OSError):
        return 0


def get_diff_content() -> str:
    """Get diff content for most recent commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1..HEAD"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout
    except (subprocess.TimeoutExpired, OSError):
        return ""


def check_breaking_changes(subject: str, commit_msg: str) -> str:
    """
    Check for potential breaking changes in the diff.

    Returns indicators string if breaking changes detected without proper markers,
    empty string otherwise.
    """
    # Skip if already marked as breaking
    if re.match(r"^[a-z]+!:", subject):
        return ""
    if re.search(r"^BREAKING[ -]CHANGE:", commit_msg, re.MULTILINE):
        return ""

    diff_content = get_diff_content()
    if not diff_content:
        return ""

    indicators = []

    # Check for removed function/method definitions
    if re.search(r"^-\s*(def |function |public |export (function|const|class))",
                 diff_content, re.MULTILINE):
        indicators.append("- Removed function/method definition")

    # Check for removed exports
    if re.search(r"^-\s*export ", diff_content, re.MULTILINE):
        indicators.append("- Removed export")

    # Check for changed function signatures (added required parameter)
    if (re.search(r"^-.*\([^)]*\)", diff_content, re.MULTILINE) and
        re.search(r"^\+.*\([^)]*,[^)]*\)", diff_content, re.MULTILINE)):
        indicators.append("- Modified function signature")

    # Check for removed environment variables or config keys
    if re.search(r"^-\s*(ENV|CONFIG|[A-Z_]+_KEY|[A-Z_]+_URL|[A-Z_]+_SECRET)",
                 diff_content, re.MULTILINE | re.IGNORECASE):
        indicators.append("- Removed environment/config variable")

    return "\n".join(indicators)


def main() -> dict:
    """Process hook event from stdin."""
    try:
        raw_input = sys.stdin.read(MAX_STDIN_SIZE)
        if not raw_input:
            return {}

        try:
            data = json.loads(raw_input)
        except json.JSONDecodeError:
            return {}

        # Skip validation on WIP/temp branches
        current_branch = get_current_branch()
        if re.match(r"^(wip|temp|backup)/", current_branch):
            return {}

        command = data.get("tool_input", {}).get("command", "")

        if not re.search(r"^git\s+commit", command):
            return {}

        commit_msg = get_commit_message()
        if not commit_msg:
            return {}

        lines_changed = get_lines_changed()
        subject = commit_msg.split('\n')[0]
        body = '\n'.join(commit_msg.split('\n')[2:]) if '\n' in commit_msg else ""

        warnings = []

        # Check for missing body on non-trivial commits
        file_count = get_file_count()
        is_trivial = (file_count <= 1 and lines_changed < 20)
        if re.search(r"(typo|version|bump|import)", subject, re.IGNORECASE):
            is_trivial = True

        if not is_trivial and not body:
            warnings.append(
                "Non-trivial commits should have a body explaining WHY. "
                "Consider: git commit --amend"
            )

        # Commit size warnings
        if lines_changed > 1000:
            warnings.append(
                f"VERY LARGE commit ({lines_changed} lines) - strongly consider "
                "splitting. Commits over 1000 lines are difficult to review."
            )
        elif lines_changed > 400:
            warnings.append(
                f"Large commit ({lines_changed} lines) - consider splitting into smaller changes"
            )
        elif lines_changed > 200:
            warnings.append(
                f"Commit is {lines_changed} lines - review if it could be split"
            )

        # Check for potential breaking changes without marker
        breaking_indicators = check_breaking_changes(subject, commit_msg)
        if breaking_indicators:
            warnings.append(
                f"Potential breaking change detected but no '!' marker or "
                f"BREAKING CHANGE footer:\n{breaking_indicators}\n"
                "If breaking, amend with: feat!: or add BREAKING CHANGE: footer"
            )

        if warnings:
            return {
                "systemMessage": "Post-commit review:\n" + "\n".join(warnings)
            }

        return {}

    except Exception:
        return {}


if __name__ == "__main__":
    result = main()
    print(json.dumps(result))
