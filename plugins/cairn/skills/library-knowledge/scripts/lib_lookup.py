#!/usr/bin/env python3
"""Consult the library-knowledge store cheaply (the read path).

Token-efficient by construction: a name returns ONE record (streamed via the
storage port, never the whole store); no name returns the compact index
(name + version + date); --search returns ranked names + one-line capabilities,
not full entries. The agent's context only ever holds what it asked for.

Storage lives behind store.py (JSONL today, swappable to SQLite/FTS later with
no change here). Staleness compares each entry to the repo's package.json.

Usage:
    python lib_lookup.py                      # index (cheap)
    python lib_lookup.py nativewind           # one entry + staleness
    python lib_lookup.py --search "validation runtime"   # capability search
    python lib_lookup.py zod --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import store


def render_index(repo: Path, st: str | None) -> str:
    rows = store.read_index(repo, st)
    if not rows:
        return "library-knowledge store is empty. Seed it with lib_refresh.py."
    out = ["library-knowledge index (consult one with: lib_lookup.py <name>):"]
    for r in sorted(rows, key=lambda x: x.get("name") or ""):
        name = r.get("name")
        inst = store.installed_version(repo, name)
        sv = store.staleness(r, inst)
        out.append(f"  {name:<18} confirmed {str(r.get('confirmed_version')):<12} "
                   f"on {r.get('confirmed_on')}  [{sv}]"
                   + (f"  installed {inst}" if inst and sv == 'STALE' else ""))
    return "\n".join(out)


def render_entry(repo: Path, name: str, e: dict) -> str:
    inst = store.installed_version(repo, name)
    sv = store.staleness(e, inst)
    out = [f"{name} — confirmed {e.get('confirmed_version')} on {e.get('confirmed_on')}  [{sv}]"]
    if sv == "STALE":
        out.append(f"  ⚠ installed {inst} drifted past the confirmed version — REFRESH before trusting.")
    if sv == "UNKNOWN":
        out.append("  (not a declared dependency here, or version unreadable.)")
    if e.get("capability"):
        out.append(f"  capability: {e['capability']}")
    for f in e.get("key_facts", []):
        out.append(f"  - {f}")
    if e.get("delta_from_prior"):
        out.append(f"  delta from prior: {e['delta_from_prior']}")
    if e.get("source_url"):
        out.append(f"  source: {e['source_url']}")
    return "\n".join(out)


def render_search(repo: Path, st: str | None, terms: str) -> str:
    hits = store.search(repo, st, terms)
    if not hits:
        return f"no library matches '{terms}'. If nothing on the shelf solves it, confirm a candidate against docs and record it."
    out = [f"capability matches for '{terms}' (best first):"]
    for score, r in hits:
        out.append(f"  [{score}] {r.get('name')} — {r.get('capability','(no capability recorded)')}")
    out.append("consult one with: lib_lookup.py <name>")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Consult the library-knowledge store (cheap read path).")
    p.add_argument("name", nargs="?", default=None, help="Library name. Omit for the index.")
    p.add_argument("--search", default=None, help="Capability query (ranked names, not full entries).")
    p.add_argument("--repo", default=".", help="Repo root (default: .).")
    p.add_argument("--store", default=None, help="Path to the store file.")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    repo = Path(args.repo).resolve()

    if args.search:
        if args.json:
            print(json.dumps([{"name": r.get("name"), "capability": r.get("capability"), "score": s}
                              for s, r in store.search(repo, args.store, args.search)], indent=2))
        else:
            print(render_search(repo, args.store, args.search))
        return 0

    if args.name is None:
        if args.json:
            print(json.dumps([{**r, "staleness": store.staleness(r, store.installed_version(repo, r.get("name")))}
                              for r in store.read_index(repo, args.store)], indent=2))
        else:
            print(render_index(repo, args.store))
        return 0

    e = store.read_one(repo, args.store, args.name)
    if not e:
        print(f"no entry for '{args.name}'. Confirm it against live docs, then record with lib_refresh.py.",
              file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({**e, "staleness": store.staleness(e, store.installed_version(repo, args.name))}, indent=2))
    else:
        print(render_entry(repo, args.name, e))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
