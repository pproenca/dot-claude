#!/usr/bin/env python3 -S
"""Blackbox Flight Recorder - CAS Storage with mmap hashing."""
import os
import hashlib
import mmap

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
MAX_STDIN_SIZE = 256 * 1024  # 256KB
PLUGIN_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PLUGIN_ROOT, "data")
BUFFER_PATH = os.path.join(DATA_DIR, "buffer.jsonl")
OBJECTS_DIR = os.path.join(DATA_DIR, "objects")

def fast_hash_mmap(filepath):
    """Hash file using mmap. Returns (sha1_hash, is_binary)."""
    try:
        fd = os.open(filepath, os.O_RDONLY)
        try:
            stat = os.fstat(fd)
            if stat.st_size > MAX_FILE_SIZE:
                return None, False
            if stat.st_size == 0:
                return "da39a3ee5e6b4b0d3255bfef95601890afd80709", False

            header = os.read(fd, 512)
            if b'\0' in header:
                return None, True

            os.lseek(fd, 0, os.SEEK_SET)
            with mmap.mmap(fd, 0, access=mmap.ACCESS_READ) as mm:
                sha1 = hashlib.sha1(mm).hexdigest()
                return sha1, False
        finally:
            os.close(fd)
    except OSError:
        return None, False

def atomic_store(filepath, file_hash):
    """Store file to CAS using write-tmp-rename pattern."""
    prefix = file_hash[:2]
    suffix = file_hash[2:]
    target_dir = os.path.join(OBJECTS_DIR, prefix)
    target_path = os.path.join(target_dir, suffix)

    if os.path.exists(target_path):
        return

    try:
        os.makedirs(target_dir, exist_ok=True)
        tmp_path = target_path + ".tmp"

        with open(filepath, 'rb') as src, open(tmp_path, 'wb') as dst:
            dst.write(src.read())

        os.rename(tmp_path, target_path)
    except OSError:
        pass

if __name__ == "__main__":
    pass
