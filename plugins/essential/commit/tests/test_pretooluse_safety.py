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
