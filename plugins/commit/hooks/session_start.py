#!/usr/bin/env python3 -S
"""
SessionStart hook for commit plugin.

Context injection removed - guidelines available via skill lookup when needed.
This reduces SessionStart context pollution per Claude Code best practices.
"""
import json


def main() -> dict:
    """Return empty response - no context injection."""
    return {}


if __name__ == "__main__":
    result = main()
    print(json.dumps(result))
