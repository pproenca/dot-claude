#!/usr/bin/env python3
"""
Query blackbox event log.

Usage:
    query.py --last N                  # Show last N events
    query.py --event-type <type>       # Filter by event type
    query.py --file <pattern>          # Filter by file pattern
    query.py --stats                   # Show storage statistics
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


def get_entries():
    """Load all entries from buffer.jsonl."""
    if not os.path.exists(BUFFER_PATH):
        return []
    
    entries = []
    with open(BUFFER_PATH, "r") as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def show_last(count, event_type=None, file_pattern=None):
    """Show last N events with optional filters."""
    entries = get_entries()
    
    # Apply filters
    if event_type:
        entries = [e for e in entries if e.get("e") == event_type]
    if file_pattern:
        entries = [
            e for e in entries
            if file_pattern.lower() in 
               e.get("d", {}).get("tool_input", {}).get("file_path", "").lower()
        ]
    
    # Get last N
    entries = entries[-count:]
    entries.reverse()
    
    if not entries:
        print("No matching events found.")
        return
    
    print(f"{'Time':<20} {'Event':<15} {'Hash':<14} {'File'}")
    print("-" * 70)
    
    for entry in entries:
        from datetime import datetime
        ts = datetime.fromtimestamp(entry.get("t", 0)).strftime("%Y-%m-%d %H:%M:%S")
        event = entry.get("e", "")[:14]
        hash_val = (entry.get("h") or "")[:12] + ("..." if entry.get("h") else "-")
        file_path = entry.get("d", {}).get("tool_input", {}).get("file_path", "-")
        # Truncate long paths
        if len(file_path) > 40:
            file_path = "..." + file_path[-37:]
        print(f"{ts:<20} {event:<15} {hash_val:<14} {file_path}")


def show_stats():
    """Show storage statistics."""
    entries = get_entries()
    
    # Count objects
    object_count = 0
    total_size = 0
    if os.path.exists(OBJECTS_DIR):
        for root, dirs, files in os.walk(OBJECTS_DIR):
            for f in files:
                object_count += 1
                total_size += os.path.getsize(os.path.join(root, f))
    
    # Count by event type
    event_counts = {}
    for entry in entries:
        event = entry.get("e", "unknown")
        event_counts[event] = event_counts.get(event, 0) + 1
    
    print("Blackbox Storage Statistics")
    print("=" * 40)
    print(f"Total events:     {len(entries)}")
    print(f"Stored objects:   {object_count}")
    print(f"Storage size:     {total_size / 1024:.1f} KB")
    print()
    print("Events by type:")
    for event, count in sorted(event_counts.items()):
        print(f"  {event}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Query blackbox event log")
    parser.add_argument("--last", "-n", type=int, default=10, help="Show last N events")
    parser.add_argument("--event-type", "-e", help="Filter by event type")
    parser.add_argument("--file", "-f", help="Filter by file pattern")
    parser.add_argument("--stats", "-s", action="store_true", help="Show statistics")

    args = parser.parse_args()

    if args.stats:
        show_stats()
    else:
        show_last(args.last, args.event_type, args.file)


if __name__ == "__main__":
    main()
