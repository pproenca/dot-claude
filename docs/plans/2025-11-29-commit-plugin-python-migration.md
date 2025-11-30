# Commit Plugin Python Migration - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use super:executing-plans to implement this plan task-by-task.

**Goal:** Convert all bash scripts in `plugins/commit/` to Python with unittest test coverage, making the codebase reliable and testable.

**Architecture:** Each bash script becomes a Python module with a `main()` entry point. Tests use standard `unittest` library with mocking for subprocess/stdin. The blackbox plugin pattern (`python3 -S`) serves as the reference implementation.

**Tech Stack:** Python 3, unittest, subprocess, json (stdlib only - no external dependencies)

---

## Summary of Changes

| Current File | New Python File | Test File |
|--------------|-----------------|-----------|
| `hooks/pretooluse-safety.sh` | `hooks/pretooluse_safety.py` | `tests/test_pretooluse_safety.py` |
| `hooks/posttooluse-validate.sh` | `hooks/posttooluse_validate.py` | `tests/test_posttooluse_validate.py` |
| `hooks/session-start.sh` | `hooks/session_start.py` | `tests/test_session_start.py` |
| `scripts/analyze-branch.sh` | `scripts/analyze_branch.py` | `tests/test_analyze_branch.py` |

## Why Python Over Bash

1. **Testability**: Bash requires complex mocking of external commands; Python allows proper unit testing
2. **Reliability**: Bash regex parsing is fragile; Python has robust regex and string handling
3. **Maintainability**: Python is easier to read, debug, and extend
4. **Consistency**: Matches blackbox plugin pattern already in use

---

### Task 1: Create Test Directory Structure

**Files:**
- Create: `plugins/commit/tests/__init__.py`
- Create: `plugins/commit/tests/fixtures/sample_input.json`

**Step 1: Create tests directory and __init__.py**

```bash
mkdir -p plugins/commit/tests
```

**Step 2: Create __init__.py**

```python
# plugins/commit/tests/__init__.py
"""Tests for commit plugin hooks and scripts."""
```

Write to `plugins/commit/tests/__init__.py`.

**Step 3: Create sample fixture for hook input**

```json
{
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "git commit -m 'feat: add new feature'"
  }
}
```

Write to `plugins/commit/tests/fixtures/sample_input.json`.

**Step 4: Verify structure**

Run: `ls -la plugins/commit/tests/`
Expected: Shows `__init__.py` and `fixtures/` directory

**Step 5: Commit**

```bash
git add plugins/commit/tests/
git commit -m "chore: add test directory structure for commit plugin"
```

---

### Task 2: Write Failing Tests for pretooluse_safety.py

**Files:**
- Create: `plugins/commit/tests/test_pretooluse_safety.py`

**Step 1: Write the failing tests**

```python
#!/usr/bin/env python3
"""Tests for pretooluse_safety hook."""
import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add hooks directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hooks'))


class TestValidateCommitMessage(unittest.TestCase):
    """Tests for commit message validation."""

    def setUp(self):
        import pretooluse_safety
        self.module = pretooluse_safety

    def test_valid_feat_commit(self):
        """Valid feat commit should pass."""
        error = self.module.validate_commit_message("feat: add new feature")
        self.assertIsNone(error)

    def test_valid_fix_commit(self):
        """Valid fix commit should pass."""
        error = self.module.validate_commit_message("fix: resolve null pointer")
        self.assertIsNone(error)

    def test_valid_breaking_change(self):
        """Breaking change with ! should pass."""
        error = self.module.validate_commit_message("feat!: remove deprecated API")
        self.assertIsNone(error)

    def test_missing_type_prefix(self):
        """Missing type prefix should fail."""
        error = self.module.validate_commit_message("add new feature")
        self.assertIsNotNone(error)
        self.assertIn("type prefix", error.lower())

    def test_missing_colon_space(self):
        """Missing colon and space should fail."""
        error = self.module.validate_commit_message("feat add new feature")
        self.assertIsNotNone(error)
        self.assertIn("colon", error.lower())

    def test_empty_description(self):
        """Empty description should fail."""
        error = self.module.validate_commit_message("feat: ")
        self.assertIsNotNone(error)
        self.assertIn("description", error.lower())

    def test_vague_description_bug(self):
        """Vague description 'bug' should fail."""
        error = self.module.validate_commit_message("fix: bug")
        self.assertIsNotNone(error)
        self.assertIn("vague", error.lower())

    def test_vague_description_update(self):
        """Vague description 'update' should fail."""
        error = self.module.validate_commit_message("chore: update")
        self.assertIsNotNone(error)
        self.assertIn("vague", error.lower())

    def test_subject_too_long(self):
        """Subject over 100 chars should fail."""
        long_msg = "feat: " + "a" * 100
        error = self.module.validate_commit_message(long_msg)
        self.assertIsNotNone(error)
        self.assertIn("too long", error.lower())

    def test_imperative_mood_adding(self):
        """Non-imperative 'adding' should fail."""
        error = self.module.validate_commit_message("feat: adding new feature")
        self.assertIsNotNone(error)
        self.assertIn("imperative", error.lower())

    def test_imperative_mood_added(self):
        """Non-imperative 'added' should fail."""
        error = self.module.validate_commit_message("feat: added new feature")
        self.assertIsNotNone(error)
        self.assertIn("imperative", error.lower())

    def test_imperative_mood_adds(self):
        """Non-imperative 'Adds' should fail."""
        error = self.module.validate_commit_message("feat: Adds new feature")
        self.assertIsNotNone(error)
        self.assertIn("imperative", error.lower())

    def test_subject_ends_with_period(self):
        """Subject ending with period should fail."""
        error = self.module.validate_commit_message("feat: add new feature.")
        self.assertIsNotNone(error)
        self.assertIn("period", error.lower())

    def test_all_valid_types(self):
        """All valid types should pass."""
        valid_types = ["feat", "fix", "docs", "chore", "refactor", "perf", "test", "build", "ci"]
        for t in valid_types:
            error = self.module.validate_commit_message(f"{t}: valid description here")
            self.assertIsNone(error, f"Type '{t}' should be valid")


class TestCheckDestructiveCommand(unittest.TestCase):
    """Tests for destructive command checking."""

    def setUp(self):
        import pretooluse_safety
        self.module = pretooluse_safety

    def test_normal_git_commit_allowed(self):
        """Normal git commit should be allowed."""
        error = self.module.check_destructive_command("git commit -m 'feat: test'")
        self.assertIsNone(error)

    def test_git_push_force_blocked(self):
        """git push --force should be blocked."""
        error = self.module.check_destructive_command("git push --force")
        self.assertIsNotNone(error)
        self.assertIn("force", error.lower())

    def test_git_push_f_blocked(self):
        """git push -f should be blocked."""
        error = self.module.check_destructive_command("git push -f origin main")
        self.assertIsNotNone(error)
        self.assertIn("force", error.lower())

    def test_git_clean_fd_blocked(self):
        """git clean -fd should be blocked."""
        error = self.module.check_destructive_command("git clean -fd")
        self.assertIsNotNone(error)
        self.assertIn("clean", error.lower())

    @patch('subprocess.run')
    def test_git_reset_hard_without_backup_blocked(self, mock_run):
        """git reset --hard without backup should be blocked."""
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        error = self.module.check_destructive_command("git reset --hard HEAD~1")
        self.assertIsNotNone(error)
        self.assertIn("backup", error.lower())

    @patch('subprocess.run')
    def test_git_reset_hard_with_backup_allowed(self, mock_run):
        """git reset --hard with backup branch should be allowed."""
        mock_run.return_value = MagicMock(stdout="backup/main-20231201", returncode=0)
        error = self.module.check_destructive_command("git reset --hard HEAD~1")
        self.assertIsNone(error)


class TestMain(unittest.TestCase):
    """Tests for main hook processing."""

    def setUp(self):
        import pretooluse_safety
        self.module = pretooluse_safety

    @patch('sys.stdin')
    @patch('subprocess.run')
    def test_non_git_command_passes(self, mock_run, mock_stdin):
        """Non-git commands should pass through."""
        mock_run.return_value = MagicMock(stdout="main", returncode=0)
        event = {
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la"}
        }
        mock_stdin.read.return_value = json.dumps(event)

        result = self.module.main()
        self.assertEqual(result, {})

    @patch('sys.stdin')
    @patch('subprocess.run')
    def test_valid_commit_passes(self, mock_run, mock_stdin):
        """Valid commit should pass."""
        mock_run.return_value = MagicMock(stdout="main", returncode=0)
        event = {
            "tool_name": "Bash",
            "tool_input": {"command": "git commit -m 'feat: add feature'"}
        }
        mock_stdin.read.return_value = json.dumps(event)

        result = self.module.main()
        self.assertEqual(result, {})

    @patch('sys.stdin')
    @patch('subprocess.run')
    def test_invalid_commit_blocked(self, mock_run, mock_stdin):
        """Invalid commit should be blocked."""
        mock_run.return_value = MagicMock(stdout="main", returncode=0)
        event = {
            "tool_name": "Bash",
            "tool_input": {"command": "git commit -m 'bad commit'"}
        }
        mock_stdin.read.return_value = json.dumps(event)

        result = self.module.main()
        self.assertIn("hookSpecificOutput", result)
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")

    @patch('sys.stdin')
    @patch('subprocess.run')
    def test_wip_branch_skips_validation(self, mock_run, mock_stdin):
        """WIP branches should skip validation."""
        mock_run.return_value = MagicMock(stdout="wip/feature", returncode=0)
        event = {
            "tool_name": "Bash",
            "tool_input": {"command": "git commit -m 'wip stuff'"}
        }
        mock_stdin.read.return_value = json.dumps(event)

        result = self.module.main()
        self.assertEqual(result, {})

    @patch('sys.stdin')
    @patch('subprocess.run')
    def test_printf_heredoc_pattern(self, mock_run, mock_stdin):
        """printf '%b' pattern for multiline commits should be validated."""
        mock_run.return_value = MagicMock(stdout="main", returncode=0)
        event = {
            "tool_name": "Bash",
            "tool_input": {"command": "printf '%b' 'feat: add feature\\n\\nBody text' | git commit -F -"}
        }
        mock_stdin.read.return_value = json.dumps(event)

        result = self.module.main()
        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
```

Write to `plugins/commit/tests/test_pretooluse_safety.py`.

**Step 2: Run tests to verify they fail**

Run: `python3 -m pytest plugins/commit/tests/test_pretooluse_safety.py -v 2>/dev/null || python3 -m unittest plugins/commit/tests/test_pretooluse_safety -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'pretooluse_safety'"

**Step 3: Commit failing tests**

```bash
git add plugins/commit/tests/test_pretooluse_safety.py
git commit -m "test: add failing tests for pretooluse_safety hook"
```

---

### Task 3: Implement pretooluse_safety.py

**Files:**
- Create: `plugins/commit/hooks/pretooluse_safety.py`

**Step 1: Write the implementation**

```python
#!/usr/bin/env python3 -S
"""
PreToolUse hook for commit plugin.

Validates:
1. Commit messages follow Conventional Commits specification
2. Destructive git commands have proper safety measures
"""
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
```

Write to `plugins/commit/hooks/pretooluse_safety.py`.

**Step 2: Make executable**

```bash
chmod +x plugins/commit/hooks/pretooluse_safety.py
```

**Step 3: Run tests to verify they pass**

Run: `python3 -m unittest plugins/commit/tests/test_pretooluse_safety -v`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add plugins/commit/hooks/pretooluse_safety.py
git commit -m "feat: implement pretooluse_safety hook in Python"
```

---

### Task 4: Write Failing Tests for posttooluse_validate.py

**Files:**
- Create: `plugins/commit/tests/test_posttooluse_validate.py`

**Step 1: Write the failing tests**

```python
#!/usr/bin/env python3
"""Tests for posttooluse_validate hook."""
import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hooks'))


class TestCheckBreakingChanges(unittest.TestCase):
    """Tests for breaking change detection."""

    def setUp(self):
        import posttooluse_validate
        self.module = posttooluse_validate

    @patch('subprocess.run')
    def test_no_breaking_changes(self, mock_run):
        """Normal commits should not flag breaking changes."""
        mock_run.return_value = MagicMock(
            stdout="+ new line\n+ another line",
            returncode=0
        )
        result = self.module.check_breaking_changes("feat: add feature", "body text")
        self.assertEqual(result, "")

    @patch('subprocess.run')
    def test_already_marked_breaking_exclamation(self, mock_run):
        """Commits marked with ! should skip detection."""
        mock_run.return_value = MagicMock(
            stdout="-def removed_func():",
            returncode=0
        )
        result = self.module.check_breaking_changes("feat!: remove API", "body")
        self.assertEqual(result, "")

    @patch('subprocess.run')
    def test_already_marked_breaking_footer(self, mock_run):
        """Commits with BREAKING CHANGE footer should skip detection."""
        mock_run.return_value = MagicMock(
            stdout="-def removed_func():",
            returncode=0
        )
        result = self.module.check_breaking_changes(
            "feat: remove API",
            "BREAKING CHANGE: removed old endpoint"
        )
        self.assertEqual(result, "")

    @patch('subprocess.run')
    def test_detect_removed_function(self, mock_run):
        """Should detect removed function definitions."""
        mock_run.return_value = MagicMock(
            stdout="-def old_function():\n-    pass",
            returncode=0
        )
        result = self.module.check_breaking_changes("feat: update code", "body")
        self.assertIn("function", result.lower())

    @patch('subprocess.run')
    def test_detect_removed_export(self, mock_run):
        """Should detect removed exports."""
        mock_run.return_value = MagicMock(
            stdout="-export const API_KEY = 'xxx'",
            returncode=0
        )
        result = self.module.check_breaking_changes("feat: update code", "body")
        self.assertIn("export", result.lower())


class TestMain(unittest.TestCase):
    """Tests for main hook processing."""

    def setUp(self):
        import posttooluse_validate
        self.module = posttooluse_validate

    @patch('sys.stdin')
    @patch('subprocess.run')
    def test_non_commit_command_passes(self, mock_run, mock_stdin):
        """Non-commit commands should pass through."""
        mock_run.return_value = MagicMock(stdout="main", returncode=0)
        event = {
            "tool_input": {"command": "git status"}
        }
        mock_stdin.read.return_value = json.dumps(event)

        result = self.module.main()
        self.assertEqual(result, {})

    @patch('sys.stdin')
    @patch('subprocess.run')
    def test_wip_branch_skips_validation(self, mock_run, mock_stdin):
        """WIP branches should skip validation."""
        mock_run.return_value = MagicMock(stdout="wip/feature", returncode=0)
        event = {
            "tool_input": {"command": "git commit -m 'wip'"}
        }
        mock_stdin.read.return_value = json.dumps(event)

        result = self.module.main()
        self.assertEqual(result, {})

    @patch('sys.stdin')
    @patch('subprocess.run')
    def test_large_commit_warning(self, mock_run, mock_stdin):
        """Large commits should produce warning."""
        def run_side_effect(cmd, **kwargs):
            if cmd[1] == "branch":
                return MagicMock(stdout="main", returncode=0)
            if cmd[1] == "log":
                return MagicMock(stdout="feat: add feature\n", returncode=0)
            if "--numstat" in cmd:
                return MagicMock(stdout="500\t100\tfile.py", returncode=0)
            if "--name-only" in cmd:
                return MagicMock(stdout="file.py\nfile2.py", returncode=0)
            return MagicMock(stdout="", returncode=0)

        mock_run.side_effect = run_side_effect
        event = {
            "tool_input": {"command": "git commit -m 'feat: big change'"}
        }
        mock_stdin.read.return_value = json.dumps(event)

        result = self.module.main()
        self.assertIn("systemMessage", result)
        self.assertIn("large", result["systemMessage"].lower())

    @patch('sys.stdin')
    @patch('subprocess.run')
    def test_missing_body_warning(self, mock_run, mock_stdin):
        """Non-trivial commits without body should warn."""
        def run_side_effect(cmd, **kwargs):
            if cmd[1] == "branch":
                return MagicMock(stdout="main", returncode=0)
            if cmd[1] == "log":
                return MagicMock(stdout="feat: add feature", returncode=0)
            if "--numstat" in cmd:
                return MagicMock(stdout="50\t10\tfile.py", returncode=0)
            if "--name-only" in cmd:
                return MagicMock(stdout="file.py\nfile2.py\nfile3.py", returncode=0)
            return MagicMock(stdout="", returncode=0)

        mock_run.side_effect = run_side_effect
        event = {
            "tool_input": {"command": "git commit -m 'feat: add feature'"}
        }
        mock_stdin.read.return_value = json.dumps(event)

        result = self.module.main()
        self.assertIn("systemMessage", result)
        self.assertIn("body", result["systemMessage"].lower())


if __name__ == '__main__':
    unittest.main()
```

Write to `plugins/commit/tests/test_posttooluse_validate.py`.

**Step 2: Run tests to verify they fail**

Run: `python3 -m unittest plugins/commit/tests/test_posttooluse_validate -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'posttooluse_validate'"

**Step 3: Commit failing tests**

```bash
git add plugins/commit/tests/test_posttooluse_validate.py
git commit -m "test: add failing tests for posttooluse_validate hook"
```

---

### Task 5: Implement posttooluse_validate.py

**Files:**
- Create: `plugins/commit/hooks/posttooluse_validate.py`

**Step 1: Write the implementation**

```python
#!/usr/bin/env python3 -S
"""
PostToolUse hook for commit plugin.

Handles post-commit checks that can't be done before execution:
- Commit size warnings (requires actual commit stats)
- Non-trivial commit body requirement (requires file count)
- Breaking change detection (warns if potential breaking change lacks marker)
"""
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
```

Write to `plugins/commit/hooks/posttooluse_validate.py`.

**Step 2: Make executable**

```bash
chmod +x plugins/commit/hooks/posttooluse_validate.py
```

**Step 3: Run tests to verify they pass**

Run: `python3 -m unittest plugins/commit/tests/test_posttooluse_validate -v`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add plugins/commit/hooks/posttooluse_validate.py
git commit -m "feat: implement posttooluse_validate hook in Python"
```

---

### Task 6: Write Failing Tests for session_start.py

**Files:**
- Create: `plugins/commit/tests/test_session_start.py`

**Step 1: Write the failing tests**

```python
#!/usr/bin/env python3
"""Tests for session_start hook."""
import json
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hooks'))


class TestMain(unittest.TestCase):
    """Tests for session_start hook."""

    def setUp(self):
        import session_start
        self.module = session_start

    def test_returns_empty_dict(self):
        """Session start should return empty dict (no context injection)."""
        result = self.module.main()
        self.assertEqual(result, {})

    @patch('sys.stdin')
    def test_ignores_stdin(self, mock_stdin):
        """Session start should work regardless of stdin."""
        mock_stdin.read.return_value = '{"some": "data"}'
        result = self.module.main()
        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
```

Write to `plugins/commit/tests/test_session_start.py`.

**Step 2: Run tests to verify they fail**

Run: `python3 -m unittest plugins/commit/tests/test_session_start -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'session_start'"

**Step 3: Commit failing tests**

```bash
git add plugins/commit/tests/test_session_start.py
git commit -m "test: add failing tests for session_start hook"
```

---

### Task 7: Implement session_start.py

**Files:**
- Create: `plugins/commit/hooks/session_start.py`

**Step 1: Write the implementation**

```python
#!/usr/bin/env python3 -S
"""
SessionStart hook for commit plugin.

Context injection removed - guidelines available via skill lookup when needed.
This reduces SessionStart context pollution per Claude Code best practices.
"""
import json


def main() -> dict:
    """Return empty response - no context injection."""
    return {}


if __name__ == "__main__":
    result = main()
    print(json.dumps(result))
```

Write to `plugins/commit/hooks/session_start.py`.

**Step 2: Make executable**

```bash
chmod +x plugins/commit/hooks/session_start.py
```

**Step 3: Run tests to verify they pass**

Run: `python3 -m unittest plugins/commit/tests/test_session_start -v`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add plugins/commit/hooks/session_start.py
git commit -m "feat: implement session_start hook in Python"
```

---

### Task 8: Write Failing Tests for analyze_branch.py

**Files:**
- Create: `plugins/commit/tests/test_analyze_branch.py`

**Step 1: Write the failing tests**

```python
#!/usr/bin/env python3
"""Tests for analyze_branch script."""
import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class TestAnalyzeBranch(unittest.TestCase):
    """Tests for branch analysis."""

    def setUp(self):
        import analyze_branch
        self.module = analyze_branch

    @patch('subprocess.run')
    def test_not_git_repo_returns_error(self, mock_run):
        """Should return error when not in git repo."""
        mock_run.side_effect = Exception("Not a git repo")
        result = self.module.main()
        self.assertIn("error", result)

    @patch('subprocess.run')
    def test_returns_branch_info(self, mock_run):
        """Should return branch information."""
        def run_side_effect(cmd, **kwargs):
            if "rev-parse" in cmd and "--git-dir" in cmd:
                return MagicMock(stdout=".git", returncode=0)
            if cmd == ["git", "branch", "--show-current"]:
                return MagicMock(stdout="feature-branch\n", returncode=0)
            if "show-ref" in cmd:
                return MagicMock(returncode=0)
            if "merge-base" in cmd:
                return MagicMock(stdout="abc123\n", returncode=0)
            if "rev-parse" in cmd and "--short" in cmd:
                return MagicMock(stdout="abc123\n", returncode=0)
            if cmd[1] == "log" and "--format=%s" in cmd:
                return MagicMock(stdout="initial commit\n", returncode=0)
            if "--name-only" in cmd:
                return MagicMock(stdout="file1.py\nfile2.py\n", returncode=0)
            if "--numstat" in cmd:
                return MagicMock(stdout="10\t5\tfile1.py\n20\t3\tfile2.py\n", returncode=0)
            if cmd[1] == "diff":
                return MagicMock(stdout="+added\n-removed", returncode=0)
            return MagicMock(stdout="", returncode=0)

        mock_run.side_effect = run_side_effect
        result = self.module.main()

        self.assertIn("branch", result)
        self.assertEqual(result["branch"]["current"], "feature-branch")

    @patch('subprocess.run')
    def test_returns_file_stats(self, mock_run):
        """Should return file statistics."""
        def run_side_effect(cmd, **kwargs):
            if "rev-parse" in cmd and "--git-dir" in cmd:
                return MagicMock(stdout=".git", returncode=0)
            if cmd == ["git", "branch", "--show-current"]:
                return MagicMock(stdout="main\n", returncode=0)
            if "show-ref" in cmd:
                return MagicMock(returncode=0)
            if "merge-base" in cmd:
                return MagicMock(stdout="abc123\n", returncode=0)
            if "rev-parse" in cmd and "--short" in cmd:
                return MagicMock(stdout="abc123\n", returncode=0)
            if cmd[1] == "log" and "--format=%s" in cmd:
                return MagicMock(stdout="initial\n", returncode=0)
            if "--name-only" in cmd:
                return MagicMock(stdout="file.py\n", returncode=0)
            if "--numstat" in cmd:
                return MagicMock(stdout="10\t5\tfile.py\n", returncode=0)
            if cmd[1] == "diff":
                return MagicMock(stdout="+line", returncode=0)
            return MagicMock(stdout="", returncode=0)

        mock_run.side_effect = run_side_effect
        result = self.module.main()

        self.assertIn("stats", result)
        self.assertIn("total", result)
        self.assertEqual(result["total"]["additions"], 10)
        self.assertEqual(result["total"]["deletions"], 5)

    @patch('subprocess.run')
    def test_handles_no_changes(self, mock_run):
        """Should handle branches with no changes."""
        def run_side_effect(cmd, **kwargs):
            if "rev-parse" in cmd and "--git-dir" in cmd:
                return MagicMock(stdout=".git", returncode=0)
            if cmd == ["git", "branch", "--show-current"]:
                return MagicMock(stdout="main\n", returncode=0)
            if "show-ref" in cmd:
                return MagicMock(returncode=0)
            if "merge-base" in cmd:
                return MagicMock(stdout="abc123\n", returncode=0)
            if "rev-parse" in cmd and "--short" in cmd:
                return MagicMock(stdout="abc123\n", returncode=0)
            if cmd[1] == "log" and "--format=%s" in cmd:
                return MagicMock(stdout="initial\n", returncode=0)
            if "--name-only" in cmd:
                return MagicMock(stdout="", returncode=0)
            return MagicMock(stdout="", returncode=0)

        mock_run.side_effect = run_side_effect
        result = self.module.main()

        self.assertEqual(result["files"], [])
        self.assertEqual(result["total"]["files"], 0)


if __name__ == '__main__':
    unittest.main()
```

Write to `plugins/commit/tests/test_analyze_branch.py`.

**Step 2: Run tests to verify they fail**

Run: `python3 -m unittest plugins/commit/tests/test_analyze_branch -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'analyze_branch'"

**Step 3: Commit failing tests**

```bash
git add plugins/commit/tests/test_analyze_branch.py
git commit -m "test: add failing tests for analyze_branch script"
```

---

### Task 9: Implement analyze_branch.py

**Files:**
- Create: `plugins/commit/scripts/analyze_branch.py`

**Step 1: Write the implementation**

```python
#!/usr/bin/env python3 -S
"""
Minimal branch analysis for commit-organizer.

Outputs JSON with branch point, file list, line counts, and diffs.
"""
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
```

Write to `plugins/commit/scripts/analyze_branch.py`.

**Step 2: Make executable**

```bash
chmod +x plugins/commit/scripts/analyze_branch.py
```

**Step 3: Run tests to verify they pass**

Run: `python3 -m unittest plugins/commit/tests/test_analyze_branch -v`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add plugins/commit/scripts/analyze_branch.py
git commit -m "feat: implement analyze_branch script in Python"
```

---

### Task 10: Update hooks.json to Use Python Scripts

**Files:**
- Modify: `plugins/commit/hooks/hooks.json`

**Step 1: Read current hooks.json**

Already read above.

**Step 2: Update to use Python**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 -S ${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py",
            "timeout": 5
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -S ${CLAUDE_PLUGIN_ROOT}/hooks/pretooluse_safety.py",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -S ${CLAUDE_PLUGIN_ROOT}/hooks/posttooluse_validate.py",
            "timeout": 10
          },
          {
            "type": "prompt",
            "prompt": "Review the commit that was just created. Run: git log -1 --format='%B' && git diff --stat HEAD~1..HEAD\n\nEvaluate the commit against Conventional Commits standards:\n\n1. **Subject line**: Is it imperative mood? Specific about WHAT changed? 50-72 chars?\n\n2. **Body (if present)**: Does it explain WHY, not just repeat WHAT the code shows?\n\n3. **Scope**: Is this ONE logical change? Are tests included with their feature/fix?\n\n4. **Separation**: Is refactoring mixed with features/fixes? (violation)\n\nIf ANY issue found, output 'ISSUE: [description]' and suggest amending.\n\nIf the commit is good, output 'VALIDATED: Commit follows Conventional Commits standards.'"
          }
        ]
      }
    ]
  }
}
```

Write to `plugins/commit/hooks/hooks.json`.

**Step 3: Commit**

```bash
git add plugins/commit/hooks/hooks.json
git commit -m "feat: update hooks.json to use Python scripts"
```

---

### Task 11: Update analyze-branch Reference in Agent

**Files:**
- Modify: `plugins/commit/agents/commit-organizer.md`

**Step 1: Update the script reference**

Change line 33-34 from:
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/analyze-branch.sh
```
to:
```bash
python3 -S ${CLAUDE_PLUGIN_ROOT}/scripts/analyze_branch.py
```

**Step 2: Commit**

```bash
git add plugins/commit/agents/commit-organizer.md
git commit -m "docs: update commit-organizer to use Python analyze_branch"
```

---

### Task 12: Run All Tests and Verify

**Files:**
- Test: `plugins/commit/tests/`

**Step 1: Run all commit plugin tests**

Run: `python3 -m unittest discover plugins/commit/tests -v`
Expected: All tests PASS

**Step 2: Manual verification - test hooks work**

Run: `cd plugins/commit && python3 -S hooks/pretooluse_safety.py < tests/fixtures/sample_input.json`
Expected: Returns `{}`

**Step 3: Verify Python runs with -S flag (no site-packages)**

Run: `python3 -S -c "import sys; print('site-packages' not in str(sys.path))"`
Expected: `True`

---

### Task 13: Remove Old Bash Scripts

**Files:**
- Delete: `plugins/commit/hooks/pretooluse-safety.sh`
- Delete: `plugins/commit/hooks/posttooluse-validate.sh`
- Delete: `plugins/commit/hooks/session-start.sh`
- Delete: `plugins/commit/scripts/analyze-branch.sh`

**Step 1: Remove bash scripts**

```bash
git rm plugins/commit/hooks/pretooluse-safety.sh
git rm plugins/commit/hooks/posttooluse-validate.sh
git rm plugins/commit/hooks/session-start.sh
git rm plugins/commit/scripts/analyze-branch.sh
```

**Step 2: Commit**

```bash
git commit -m "chore: remove deprecated bash scripts, replaced by Python"
```

---

### Task 14: Final Verification

**Step 1: Run full test suite**

Run: `python3 -m unittest discover plugins/commit/tests -v`
Expected: All tests PASS (should be 20+ tests)

**Step 2: Verify hooks.json syntax**

Run: `python3 -c "import json; json.load(open('plugins/commit/hooks/hooks.json'))"`
Expected: No errors

**Step 3: Test a real hook invocation**

Run:
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git commit -m '\''feat: test feature'\''"}}' | python3 -S plugins/commit/hooks/pretooluse_safety.py
```
Expected: `{}`

Run:
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git commit -m '\''bad commit'\''"}}' | python3 -S plugins/commit/hooks/pretooluse_safety.py
```
Expected: JSON with `permissionDecision: deny`

---

## Test Coverage Summary

| Module | Test Count | Coverage |
|--------|------------|----------|
| `pretooluse_safety.py` | 18 tests | Commit validation, destructive commands, main processing |
| `posttooluse_validate.py` | 8 tests | Breaking changes, warnings, main processing |
| `session_start.py` | 2 tests | Returns empty dict |
| `analyze_branch.py` | 4 tests | Git repo check, branch info, file stats, edge cases |
| **Total** | **32 tests** | |

## Running Tests

```bash
# Run all tests
python3 -m unittest discover plugins/commit/tests -v

# Run specific module tests
python3 -m unittest plugins/commit/tests/test_pretooluse_safety -v

# Run with coverage (if coverage.py installed)
python3 -m coverage run -m unittest discover plugins/commit/tests
python3 -m coverage report
```
