#!/usr/bin/env python3
"""Record confirmed library facts (write path) and check staleness (the gate).

The judgment+effect half — searching official docs and extracting decision-
relevant facts — is the agent's (see references/confirming.md). The mechanical
half — stamping the date, writing through the storage port, and detecting drift
against package.json — is this script.

  --set <name> --from-json <file>   merge a confirmed entry, stamp confirmed_on
  --check                           FRESH/STALE/UNKNOWN per entry; exit 1 if any STALE

Storage is behind store.py (JSONL today). The write keeps one line per name.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

import store


def do_set(repo: Path, st: str | None, name: str, from_json: str) -> int:
    try:
        entry = json.loads(Path(from_json).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"error: cannot read entry json {from_json}: {e}", file=sys.stderr)
        return 2
    if "confirmed_version" not in entry:
        print("error: entry must include confirmed_version (the version you actually confirmed).", file=sys.stderr)
        return 2
    entry["confirmed_on"] = _dt.date.today().isoformat()
    _src = str(entry.get("source_url", ""))
    if not _src or "nowhere" in _src or "example" in _src or "made up" in str(entry).lower():
        print("WARNING: no credible source_url — confirmed_on asserts a confirmation you may "
              "not have made. Record the source you actually checked.", file=sys.stderr)
    store.upsert(repo, st, name, entry)
    print(f"recorded {name} @ {entry['confirmed_version']} (confirmed {entry['confirmed_on']}).")
    return 0


def do_check(repo: Path, st: str | None) -> int:
    rows = list(store.iter_records(repo, st))
    if not rows:
        print("library-knowledge store is empty — nothing to check.")
        return 0
    stale = []
    print("freshness check (confirmed vs installed):")
    for r in sorted(rows, key=lambda x: x.get("name") or ""):
        name = r.get("name")
        inst = store.installed_version(repo, name)
        sv = store.staleness(r, inst)
        if sv == "STALE":
            stale.append(name)
        extra = f"  installed {inst}" if (inst and sv == "STALE") else ""
        print(f"  [{sv}] {name}  confirmed {r.get('confirmed_version')}{extra}")
    if stale:
        print(f"\nSTALE: {', '.join(stale)} — installed drifted past the confirmed facts. "
              f"Re-confirm against live docs and lib_refresh --set before trusting these.")
        return 1
    print("\nall entries fresh.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Record confirmed library facts / check staleness.")
    p.add_argument("--repo", default=".", help="Repo root (default: .).")
    p.add_argument("--store", default=None, help="Path to the store file.")
    p.add_argument("--set", dest="name", default=None, help="Library name to record.")
    p.add_argument("--from-json", default=None, help="JSON file with the confirmed entry.")
    p.add_argument("--check", action="store_true", help="Report staleness vs package.json (gate-able).")
    args = p.parse_args(argv)
    repo = Path(args.repo).resolve()
    if args.check:
        return do_check(repo, args.store)
    if args.name and args.from_json:
        return do_set(repo, args.store, args.name, args.from_json)
    p.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
