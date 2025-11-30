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
        # Return non-zero exit code indicating not a git repo
        mock_run.return_value = MagicMock(stdout="", returncode=128)
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
