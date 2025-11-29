#!/usr/bin/env python3 -S
"""Blackbox Flight Recorder - CAS Storage with mmap hashing."""
import os
import hashlib
import mmap

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

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

if __name__ == "__main__":
    pass
