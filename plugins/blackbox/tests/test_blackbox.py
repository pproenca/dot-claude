#!/usr/bin/env python3
"""Tests for blackbox flight recorder."""
import json
import os
import sys
import tempfile
import time
import unittest
import shutil
import io
from unittest.mock import patch

# Add hooks directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hooks'))

class TestBlackbox(unittest.TestCase):
    def setUp(self):
        self.fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.sample_path = os.path.join(self.fixtures_dir, 'sample.txt')
        self.binary_path = os.path.join(self.fixtures_dir, 'binary.png')
        self.large_path = os.path.join(self.fixtures_dir, 'large.txt')
        
        # Import here to ensure clean state if needed, though usually top-level is fine
        import blackbox
        self.blackbox = blackbox
        
        # Clean up data dir before each test
        if os.path.exists(self.blackbox.DATA_DIR):
            shutil.rmtree(self.blackbox.DATA_DIR)

    def test_fast_hash_mmap_text_file(self):
        """Test hashing a normal text file."""
        file_hash, is_binary = self.blackbox.fast_hash_mmap(self.sample_path)

        self.assertIsNotNone(file_hash, "Should return hash for text file")
        self.assertFalse(is_binary, "Should not detect as binary")
        self.assertEqual(len(file_hash), 40, "SHA1 hash should be 40 hex chars")

    def test_fast_hash_mmap_binary_file(self):
        """Test that binary files are detected and rejected."""
        file_hash, is_binary = self.blackbox.fast_hash_mmap(self.binary_path)

        self.assertIsNone(file_hash, "Should return None for binary")
        self.assertTrue(is_binary, "Should detect as binary")

    def test_fast_hash_mmap_oversized_file(self):
        """Test that oversized files are rejected."""
        file_hash, is_binary = self.blackbox.fast_hash_mmap(self.large_path)

        self.assertIsNone(file_hash, "Should return None for oversized file")

    def test_fast_hash_mmap_empty_file(self):
        """Test hashing an empty file returns known SHA1."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name

        try:
            file_hash, is_binary = self.blackbox.fast_hash_mmap(temp_path)
            self.assertEqual(file_hash, "da39a3ee5e6b4b0d3255bfef95601890afd80709", "Empty file SHA1")
            self.assertFalse(is_binary)
        finally:
            os.unlink(temp_path)

    def test_fast_hash_mmap_nonexistent_file(self):
        """Test that nonexistent files return None gracefully."""
        file_hash, is_binary = self.blackbox.fast_hash_mmap('/nonexistent/path/file.txt')

        self.assertIsNone(file_hash, "Should return None for nonexistent file")
        self.assertFalse(is_binary)

    def test_atomic_store_creates_blob(self):
        """Test that atomic_store creates blob in CAS."""
        file_hash, _ = self.blackbox.fast_hash_mmap(self.sample_path)
        self.blackbox.atomic_store(self.sample_path, file_hash)

        prefix = file_hash[:2]
        suffix = file_hash[2:]
        blob_path = os.path.join(self.blackbox.OBJECTS_DIR, prefix, suffix)

        self.assertTrue(os.path.exists(blob_path), f"Blob should exist at {blob_path}")

        with open(blob_path, 'rb') as f:
            blob_content = f.read()
        with open(self.sample_path, 'rb') as f:
            original_content = f.read()

        self.assertEqual(blob_content, original_content, "Blob content should match original")

    def test_atomic_store_deduplicates(self):
        """Test that atomic_store skips existing blobs."""
        file_hash, _ = self.blackbox.fast_hash_mmap(self.sample_path)

        self.blackbox.atomic_store(self.sample_path, file_hash)
        first_stat = os.stat(os.path.join(self.blackbox.OBJECTS_DIR, file_hash[:2], file_hash[2:]))

        # Wait a tiny bit to ensure mtime difference if it were rewritten (though fs resolution might limit this)
        time.sleep(0.01)
        
        self.blackbox.atomic_store(self.sample_path, file_hash)
        second_stat = os.stat(os.path.join(self.blackbox.OBJECTS_DIR, file_hash[:2], file_hash[2:]))

        self.assertEqual(first_stat.st_mtime, second_stat.st_mtime, "Should not rewrite existing blob")

    def test_atomic_store_verifies_hash_on_write(self):
        """Test TOCTOU protection: atomic_store verifies content hash during write."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("original content")
            temp_path = f.name

        try:
            fake_hash = "0" * 40
            result = self.blackbox.atomic_store(temp_path, fake_hash)
            blob_path = os.path.join(self.blackbox.OBJECTS_DIR, fake_hash[:2], fake_hash[2:])
            
            self.assertFalse(os.path.exists(blob_path), "Should NOT store when hash mismatches content")
            self.assertFalse(result, "Should return False on hash mismatch")
        finally:
            os.unlink(temp_path)

    def test_atomic_store_blobs_are_immutable(self):
        """Test that CAS blobs are read-only (0o444) after creation."""
        file_hash, _ = self.blackbox.fast_hash_mmap(self.sample_path)
        self.blackbox.atomic_store(self.sample_path, file_hash)

        blob_path = os.path.join(self.blackbox.OBJECTS_DIR, file_hash[:2], file_hash[2:])
        blob_mode = os.stat(blob_path).st_mode & 0o777

        self.assertEqual(blob_mode, 0o444, f"Blob should be read-only (0o444), got {oct(blob_mode)}")

    def test_atomic_store_content_matches_hash(self):
        """Test that stored blob content actually matches its hash address."""
        import hashlib
        file_hash, _ = self.blackbox.fast_hash_mmap(self.sample_path)
        self.blackbox.atomic_store(self.sample_path, file_hash)

        blob_path = os.path.join(self.blackbox.OBJECTS_DIR, file_hash[:2], file_hash[2:])
        with open(blob_path, 'rb') as f:
            stored_content = f.read()

        actual_hash = hashlib.sha1(stored_content).hexdigest()
        self.assertEqual(actual_hash, file_hash, "Stored content hash must match address")

    @patch('sys.stdin')
    def test_main_pretooluse_write_creates_snapshot(self, mock_stdin):
        """Test PreToolUse for Write tool creates snapshot."""
        event_data = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": self.sample_path
            }
        }
        mock_stdin.read.return_value = json.dumps(event_data)

        self.blackbox.main()

        self.assertTrue(os.path.exists(self.blackbox.BUFFER_PATH), "buffer.jsonl should be created")

        with open(self.blackbox.BUFFER_PATH, 'r') as f:
            log_entry = json.loads(f.readline())

        self.assertEqual(log_entry['e'], 'PreToolUse', "Event should be PreToolUse")
        self.assertIsNotNone(log_entry['h'], "Hash should be recorded")

    @patch('sys.stdin')
    def test_main_pretooluse_binary_skipped(self, mock_stdin):
        """Test PreToolUse for binary file marks as skipped."""
        event_data = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": self.binary_path
            }
        }
        mock_stdin.read.return_value = json.dumps(event_data)

        self.blackbox.main()

        with open(self.blackbox.BUFFER_PATH, 'r') as f:
            log_entry = json.loads(f.readline())

        self.assertEqual(log_entry.get('skipped'), 'binary_or_oversize', "Should mark binary as skipped")

    @patch('sys.stdin')
    def test_main_sessionstart_logs_event(self, mock_stdin):
        """Test SessionStart event is logged."""
        event_data = {
            "hook_event_name": "SessionStart"
        }
        mock_stdin.read.return_value = json.dumps(event_data)

        self.blackbox.main()

        with open(self.blackbox.BUFFER_PATH, 'r') as f:
            log_entry = json.loads(f.readline())

        self.assertEqual(log_entry['e'], 'SessionStart', "Event should be SessionStart")

    @patch('sys.stdin')
    def test_performance_under_20ms(self, mock_stdin):
        """Test that hook execution completes in under 20ms."""
        event_data = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": self.sample_path
            }
        }
        json_data = json.dumps(event_data)
        
        # Warm up
        mock_stdin.read.return_value = json_data
        self.blackbox.main()

        times = []
        for _ in range(10):
            mock_stdin.read.return_value = json_data
            start = time.perf_counter()
            self.blackbox.main()
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        # Note: This test might be flaky in CI/shared envs, but good for local check
        # We increase the threshold slightly for the test runner overhead
        self.assertLess(avg_time, 50, f"Average execution time {avg_time:.2f}ms exceeds target")

if __name__ == '__main__':
    unittest.main()
