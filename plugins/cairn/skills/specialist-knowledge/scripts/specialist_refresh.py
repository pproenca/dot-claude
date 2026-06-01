#!/usr/bin/env python3
"""Record a distilled specialist profile, or check profiles for drift.

  specialist_refresh.py --set ios-native-design --from-json profile.json
  specialist_refresh.py --check        # flag profiles whose pinned libs drifted

The --check gate is the facts/craft SEAM: a profile pins library versions
(pinned_libs); if library-knowledge now records a different confirmed_version for
a pinned lib, the craft may be stale and is flagged. Refresh is then a diff, not
a relearn. Exit != 0 if any profile is stale (gate-able in verify.py).

A profile JSON (the distillation output) looks like:
{
  "domain": "ios-native-design",
  "principles": ["respect safe-area and Dynamic Type; read metrics, never hard-code 44pt", ...],
  "anti_patterns": ["animating layout on the JS thread", ...],
  "checklist": ["does every touch target meet the platform minimum?", ...],
  "authorities": ["Apple Human Interface Guidelines (current)"],
  "pinned_libs": {"react-native": "0.85", "expo": "56"},
  "taste_deltas": ["large-title nav on top-level screens; inline on detail"]
}
confirmed_on is stamped automatically.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import store

# library-knowledge's store, queried for drift detection (the seam).
LIBK_JSONL = "lib-knowledge.jsonl"


def _libk_versions(repo: Path) -> dict:
    """Read confirmed_version per lib from library-knowledge's store, if present."""
    p = repo / LIBK_JSONL
    out: dict[str, str] = {}
    if not p.exists():
        return out
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("name") and rec.get("confirmed_version"):
                out[rec["name"]] = str(rec["confirmed_version"])
    return out


def do_set(repo: Path, store_path: str | None, domain: str, from_json: str) -> int:
    try:
        profile = json.loads(Path(from_json).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"error: cannot read profile json {from_json}: {e}", file=sys.stderr)
        return 2
    if not isinstance(profile, dict):
        print("error: profile json must be an object.", file=sys.stderr)
        return 2
    profile["domain"] = domain
    profile["confirmed_on"] = dt.date.today().isoformat()
    store.upsert(repo, store_path, profile)
    pins = ", ".join(f"{k}@{v}" for k, v in profile.get("pinned_libs", {}).items()) or "none"
    print(f"recorded specialist profile '{domain}' (confirmed {profile['confirmed_on']}; pinned: {pins}).")
    return 0


def do_check(repo: Path, store_path: str | None) -> int:
    libk = _libk_versions(repo)
    profiles = store.read_all(repo, store_path)
    if not profiles:
        print("no specialist profiles to check.")
        return 0
    stale = []
    unverifiable = []  # pinned to a lib NOT in library-knowledge — a typo'd pin
                       # would otherwise be silently never-checked (silent-fresh).
    for prof in profiles:
        for lib, pinned in prof.get("pinned_libs", {}).items():
            current = libk.get(lib)
            if current is None:
                unverifiable.append((prof["domain"], lib, pinned))
            elif str(pinned) != current:
                stale.append((prof["domain"], lib, pinned, current))
    if not stale and not unverifiable:
        print(f"all {len(profiles)} specialist profile(s) FRESH vs library-knowledge.")
        return 0
    if stale:
        print("STALE specialist profiles (pinned lib drifted — re-distill as a diff):")
        for domain, lib, pinned, current in stale:
            print(f"  {domain}: pinned {lib}@{pinned} but library-knowledge now says @{current}")
    if unverifiable:
        print("UNVERIFIABLE pins (lib not in library-knowledge — typo, or record the fact):")
        for domain, lib, pinned in unverifiable:
            print(f"  {domain}: pinned {lib}@{pinned} — library-knowledge has no '{lib}'; "
                  f"a misspelled pin can never be drift-checked.")
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Record or drift-check specialist profiles.")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--store", default=None)
    ap.add_argument("--set", dest="domain", default=None)
    ap.add_argument("--from-json", default=None)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()

    if args.check:
        return do_check(repo, args.store)
    if args.domain and args.from_json:
        return do_set(repo, args.store, args.domain, args.from_json)
    ap.error("use --set <domain> --from-json <file>, or --check")


if __name__ == "__main__":
    raise SystemExit(main())
