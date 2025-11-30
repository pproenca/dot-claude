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
