#!/usr/bin/env python3
"""Tests for blackbox flight recorder."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hooks'))

def test_fast_hash_mmap_text_file():
    """Test hashing a normal text file."""
    from blackbox import fast_hash_mmap

    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    sample_path = os.path.join(fixtures_dir, 'sample.txt')

    file_hash, is_binary = fast_hash_mmap(sample_path)

    assert file_hash is not None, "Should return hash for text file"
    assert is_binary is False, "Should not detect as binary"
    assert len(file_hash) == 40, "SHA1 hash should be 40 hex chars"

def test_fast_hash_mmap_binary_file():
    """Test that binary files are detected and rejected."""
    from blackbox import fast_hash_mmap

    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    binary_path = os.path.join(fixtures_dir, 'binary.png')

    file_hash, is_binary = fast_hash_mmap(binary_path)

    assert file_hash is None, "Should return None for binary"
    assert is_binary is True, "Should detect as binary"

def test_fast_hash_mmap_oversized_file():
    """Test that oversized files are rejected."""
    from blackbox import fast_hash_mmap

    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    large_path = os.path.join(fixtures_dir, 'large.txt')

    file_hash, is_binary = fast_hash_mmap(large_path)

    assert file_hash is None, "Should return None for oversized file"

def test_fast_hash_mmap_empty_file():
    """Test hashing an empty file returns known SHA1."""
    from blackbox import fast_hash_mmap

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        temp_path = f.name

    try:
        file_hash, is_binary = fast_hash_mmap(temp_path)
        assert file_hash == "da39a3ee5e6b4b0d3255bfef95601890afd80709", "Empty file SHA1"
        assert is_binary is False
    finally:
        os.unlink(temp_path)

def test_fast_hash_mmap_nonexistent_file():
    """Test that nonexistent files return None gracefully."""
    from blackbox import fast_hash_mmap

    file_hash, is_binary = fast_hash_mmap('/nonexistent/path/file.txt')

    assert file_hash is None, "Should return None for nonexistent file"
    assert is_binary is False

def test_atomic_store_creates_blob():
    """Test that atomic_store creates blob in CAS."""
    from blackbox import atomic_store, fast_hash_mmap, OBJECTS_DIR, DATA_DIR
    import shutil

    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    sample_path = os.path.join(fixtures_dir, 'sample.txt')

    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)

    file_hash, _ = fast_hash_mmap(sample_path)
    atomic_store(sample_path, file_hash)

    prefix = file_hash[:2]
    suffix = file_hash[2:]
    blob_path = os.path.join(OBJECTS_DIR, prefix, suffix)

    assert os.path.exists(blob_path), f"Blob should exist at {blob_path}"

    with open(blob_path, 'rb') as f:
        blob_content = f.read()
    with open(sample_path, 'rb') as f:
        original_content = f.read()

    assert blob_content == original_content, "Blob content should match original"

def test_atomic_store_deduplicates():
    """Test that atomic_store skips existing blobs."""
    from blackbox import atomic_store, fast_hash_mmap, OBJECTS_DIR, DATA_DIR
    import shutil

    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    sample_path = os.path.join(fixtures_dir, 'sample.txt')

    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)

    file_hash, _ = fast_hash_mmap(sample_path)

    atomic_store(sample_path, file_hash)
    first_stat = os.stat(os.path.join(OBJECTS_DIR, file_hash[:2], file_hash[2:]))

    atomic_store(sample_path, file_hash)
    second_stat = os.stat(os.path.join(OBJECTS_DIR, file_hash[:2], file_hash[2:]))

    assert first_stat.st_mtime == second_stat.st_mtime, "Should not rewrite existing blob"

if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
