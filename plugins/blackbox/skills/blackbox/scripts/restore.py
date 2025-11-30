#!/usr/bin/env python3
"""
Restore file content from blackbox CAS.

Usage:
    restore.py --hash <sha1>           # Restore by exact hash
    restore.py --search <pattern>      # Search buffer.jsonl for file pattern
    restore.py --list                  # List recent snapshots

Output goes to stdout. Redirect to file to save.
"""

import argparse
import json
import os
import sys

DATA_DIR = os.path.expanduser(
    "~/.claude/plugins/marketplaces/dot-claude/plugins/blackbox/data"
)
BUFFER_PATH = os.path.join(DATA_DIR, "buffer.jsonl")
OBJECTS_DIR = os.path.join(DATA_DIR, "objects")


def get_blob_path(sha1_hash):
    """Get path to blob in CAS."""
    return os.path.join(OBJECTS_DIR, sha1_hash[:2], sha1_hash[2:])


def restore_by_hash(sha1_hash):
    """Restore and print file content by hash."""
    blob_path = get_blob_path(sha1_hash)
    if not os.path.exists(blob_path):
        print(f"Error: No blob found for hash {sha1_hash}", file=sys.stderr)
        sys.exit(1)

    with open(blob_path, "rb") as f:
        sys.stdout.buffer.write(f.read())


def search_buffer(pattern):
    """Search buffer.jsonl for entries matching pattern."""
    if not os.path.exists(BUFFER_PATH):
        print("Error: No buffer.jsonl found", file=sys.stderr)
        sys.exit(1)

    matches = []
    with open(BUFFER_PATH, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                data = entry.get("d", {})
                file_path = data.get("tool_input", {}).get("file_path", "")
                if pattern.lower() in file_path.lower() and entry.get("h"):
                    matches.append(
                        {
                            "hash": entry["h"],
                            "file": file_path,
                            "time": entry.get("t", 0),
                            "event": entry.get("e", ""),
                        }
                    )
            except json.JSONDecodeError:
                continue

    if not matches:
        print(f"No snapshots found matching '{pattern}'", file=sys.stderr)
        sys.exit(1)

    matches.sort(key=lambda x: x["time"], reverse=True)

    print(f"Found {len(matches)} snapshot(s) matching '{pattern}':\n", file=sys.stderr)
    for i, m in enumerate(matches[:10]):
        from datetime import datetime
        ts = datetime.fromtimestamp(m["time"]).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  [{i+1}] {ts} | {m['hash'][:12]}... | {m['file']}", file=sys.stderr)

    print(f"\nTo restore, run: restore.py --hash <full-hash>", file=sys.stderr)


def list_recent(count=10):
    """List recent snapshots."""
    if not os.path.exists(BUFFER_PATH):
        print("Error: No buffer.jsonl found", file=sys.stderr)
        sys.exit(1)

    entries = []
    with open(BUFFER_PATH, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("h"):
                    entries.append(entry)
            except json.JSONDecodeError:
                continue

    entries = entries[-count:]
    entries.reverse()

    print(f"Last {len(entries)} snapshots:\n")
    for entry in entries:
        from datetime import datetime
        ts = datetime.fromtimestamp(entry.get("t", 0)).strftime("%Y-%m-%d %H:%M:%S")
        file_path = entry.get("d", {}).get("tool_input", {}).get("file_path", "unknown")
        print(f"  {ts} | {entry['h'][:12]}... | {file_path}")


def main():
    parser = argparse.ArgumentParser(description="Restore files from blackbox CAS")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--hash", help="SHA1 hash of file to restore")
    group.add_argument("--search", help="Search pattern for file path")
    group.add_argument("--list", action="store_true", help="List recent snapshots")
    parser.add_argument("-n", type=int, default=10, help="Number of entries (default: 10)")

    args = parser.parse_args()

    if args.hash:
        restore_by_hash(args.hash)
    elif args.search:
        search_buffer(args.search)
    elif args.list:
        list_recent(args.n)


if __name__ == "__main__":
    main()
