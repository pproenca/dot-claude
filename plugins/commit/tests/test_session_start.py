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
