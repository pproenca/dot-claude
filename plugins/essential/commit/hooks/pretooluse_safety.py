#!/usr/bin/env python3 -S
"""
PreToolUse hook for commit plugin.

Validates:
1. Commit messages follow Conventional Commits specification
2. Destructive git commands have proper safety measures
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

# Valid Conventional Commit types
VALID_TYPES = ("feat", "fix", "docs", "chore", "refactor", "perf", "test", "build", "ci")
VALID_TYPES_PATTERN = "|".join(VALID_TYPES)

# Vague description patterns (case-insensitive)
VAGUE_PATTERNS = [
    r"^bug$", r"^build$", r"^fix$", r"^stuff$", r"^things$",
    r"^update$", r"^updates$", r"^changes$", r"^misc$",
    r"^wip$", r"^work in progress$", r"^done$", r"^ready$",
    r"^final$", r"^initial$", r"^first$", r"^test$"
]

MAX_STDIN_SIZE = 256 * 1024  # 256KB


def output_deny(message: str) -> dict:
    """Create a deny response for the hook."""
    return {
        "hookSpecificOutput": {
            "permissionDecision": "deny"
        },
        "systemMessage": message
    }


def validate_commit_message(commit_msg: str) -> str | None:
    """
    Validate commit message follows Conventional Commits format.

    Returns None if valid, or error message string if invalid.
    """
    subject = commit_msg.split('\n')[0]

    # Check for valid Conventional Commits format: type[!]: description
    pattern = rf"^({VALID_TYPES_PATTERN})(!)?:\s+.+"
    if not re.match(pattern, subject):
        # Check if it starts with valid type but missing format
        if re.match(rf"^({VALID_TYPES_PATTERN})", subject):
            if not re.search(r":\s", subject):
                return "Missing colon and space after type. Format: 'type: description'"
            if not re.search(r":\s+.+", subject):
                return "Empty description after type. Format: 'type: description'"
        else:
            return "Missing type prefix. Must start with: feat, fix, docs, chore, refactor, perf, test, build, or ci"

    # Extract description (part after "type: " or "type!: ")
    description_match = re.match(rf"^({VALID_TYPES_PATTERN})(!)?:\s+(.+)", subject)
    description = description_match.group(3) if description_match else ""

    # Check for vague descriptions
    if description:
        for pattern in VAGUE_PATTERNS:
            if re.match(pattern, description, re.IGNORECASE):
                return f"Vague description '{description}' - be specific about WHAT changed"

    # Check subject length
    if len(subject) > 100:
        return f"Subject too long ({len(subject)} chars) - max 100"

    # Check imperative mood in description
    if description:
        first_word = description.split()[0]
        if re.match(r"^[A-Z]?[a-z]+ing$", first_word):
            return "Use imperative mood: 'add' not 'adding'"
        if re.match(r"^[A-Z]?[a-z]+ed$", first_word):
            return "Use imperative mood: 'add' not 'added'"
        if re.match(r"^[A-Z][a-z]+s$", first_word):
            return "Use imperative mood: 'add' not 'adds'"

    # Check for period at end
    if subject.endswith('.'):
        return "Subject must not end with period"

    return None


def check_destructive_command(command: str) -> str | None:
    """
    Check for destructive git commands without proper safeguards.

    Returns None if safe, or error message string if blocked.
    """
    # git reset --hard (dangerous without backup)
    if re.search(r"git\s+reset\s+--hard", command):
        try:
            result = subprocess.run(
                ["git", "branch", "--list", "backup/*"],
                capture_output=True, text=True, timeout=5
            )
            if not result.stdout.strip():
                return "git reset --hard without backup branch"
        except (subprocess.TimeoutExpired, OSError):
            return "git reset --hard without backup branch"

    # git push --force or -f (always warn)
    if re.search(r"git\s+push\s+(--force|-f)", command):
        return "git push --force is dangerous"

    # git branch -D (delete branch permanently)
    if re.search(r"git\s+branch\s+-D", command):
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, timeout=5
            )
            current_branch = result.stdout.strip()
            if current_branch and current_branch in command:
                return "Cannot delete current branch"
        except (subprocess.TimeoutExpired, OSError):
            pass

    # git clean -fd (remove untracked files)
    if re.search(r"git\s+clean\s+-[a-zA-Z]*f", command):
        return "git clean removes untracked files permanently"

    return None


def extract_commit_message(command: str) -> str | None:
    """Extract commit message from git commit command."""
    # Try -m flag with various quote patterns
    patterns = [
        r'-m\s+["\']([^"\']+)["\']',  # -m "msg" or -m 'msg'
        r'-m\s+"([^"]+)"',             # -m "msg"
        r"-m\s+'([^']+)'",             # -m 'msg'
        r'-m\s+(\S+)',                 # -m msg (no quotes)
    ]

    for pattern in patterns:
        match = re.search(pattern, command)
        if match:
            return match.group(1)

    # Handle printf '%b' pattern: printf '%b' 'message' | git commit -F -
    if re.search(r"git\s+commit\s+-F\s+-\s*$", command):
        # Match printf '%b' with single-quoted message
        match = re.search(r"printf\s+'%b'\s+'([^']+)'", command)
        if match:
            # Convert \n escape sequences to actual newlines
            msg = match.group(1).replace('\\n', '\n')
            return msg

        # Legacy: printf '%s...' patterns
        match = re.search(r"printf\s+'%s[^']*'\s+'([^']+)'", command)
        if match:
            return match.group(1)

        match = re.search(r'printf\s+"%s[^"]*"\s+"([^"]+)"', command)
        if match:
            return match.group(1)

    return None


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


def main() -> dict:
    """Process hook event from stdin."""
    try:
        raw_input = sys.stdin.read(MAX_STDIN_SIZE)
        if not raw_input:
            return {}

        # Fast-path: exit immediately if input doesn't contain git
        if '"git ' not in raw_input and '| git ' not in raw_input:
            return {}

        try:
            data = json.loads(raw_input)
        except json.JSONDecodeError:
            return {}

        # Skip validation on WIP/temp branches
        current_branch = get_current_branch()
        if re.match(r"^(wip|temp|backup)/", current_branch):
            return {}

        # Extract command from tool_input
        command = data.get("tool_input", {}).get("command", "")

        # Quick exit if not a git command
        if not re.search(r"(^git|\|\s*git)", command):
            return {}

        # === COMMIT MESSAGE VALIDATION ===
        if re.search(r"git\s+commit", command):
            commit_msg = extract_commit_message(command)
            if commit_msg:
                error = validate_commit_message(commit_msg)
                if error:
                    return output_deny(
                        f"BLOCKED: {error}\n\n"
                        "Conventional Commits format: type: description\n"
                        "Types: feat, fix, docs, chore, refactor, perf, test, build, ci\n"
                        "Example: 'feat: add rate limiting to auth endpoint'"
                    )

        # === DESTRUCTIVE COMMAND CHECKS ===
        error = check_destructive_command(command)
        if error:
            return output_deny(
                f"BLOCKED: {error}. Create a backup branch first: "
                "git branch backup/$(git branch --show-current)-$(date +%Y%m%d-%H%M%S)"
            )

        return {}

    except Exception:
        return {}


if __name__ == "__main__":
    result = main()
    print(json.dumps(result))
