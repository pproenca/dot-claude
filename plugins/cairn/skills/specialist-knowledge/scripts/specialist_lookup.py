#!/usr/bin/env python3
"""Apply a specialist profile cheaply — the common, token-light path.

  specialist_lookup.py --domain ios-native-design     # one profile, for build/0.5
  specialist_lookup.py --index                         # what's on the craft shelf

Returns the load-bearing principles + anti-patterns + checklist for a domain, so
the agent applies confirmed craft instead of emitting generic advice from memory.
Missing/stale -> distill via specialist_refresh.py first.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import store


def _fmt(profile: dict) -> str:
    out = [f"# Specialist profile: {profile['domain']}",
           f"_confirmed {profile.get('confirmed_on', '?')}_  ·  "
           f"pinned: {', '.join(f'{k}@{v}' for k, v in profile.get('pinned_libs', {}).items()) or 'none'}",
           ""]
    if profile.get("principles"):
        out.append("## Principles (load-bearing)")
        out += [f"- {p}" for p in profile["principles"]]
        out.append("")
    if profile.get("anti_patterns"):
        out.append("## Anti-patterns (what a master avoids)")
        out += [f"- {a}" for a in profile["anti_patterns"]]
        out.append("")
    if profile.get("checklist"):
        out.append("## Checklist (apply at STAGE 0.5 / build)")
        out += [f"- [ ] {c}" for c in profile["checklist"]]
        out.append("")
    if profile.get("taste_deltas"):
        out.append("## Taste (user-adjudicated)")
        out += [f"- {t}" for t in profile["taste_deltas"]]
        out.append("")
    if profile.get("authorities"):
        out.append("_authorities: " + "; ".join(profile["authorities"]) + "_")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Apply a specialist profile.")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--store", default=None)
    ap.add_argument("--domain", default=None)
    ap.add_argument("--index", action="store_true")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()

    if args.index or not args.domain:
        idx = store.read_index(repo, args.store)
        if not idx:
            print("no specialist profiles yet — distill one with specialist_refresh.py")
            return 0
        print("Craft shelf:")
        for e in sorted(idx, key=lambda x: x["domain"]):
            pins = ", ".join(f"{k}@{v}" for k, v in e["pinned_libs"].items()) or "—"
            print(f"  {e['domain']:<34} confirmed {e['confirmed_on']:<12} pinned: {pins}")
        return 0

    profile = store.read_one(repo, args.store, args.domain)
    if profile is None:
        print(f"no profile for '{args.domain}' — distill it (see references/distilling.md), "
              f"then record with specialist_refresh.py --set {args.domain} --from-json <file>")
        return 1
    print(_fmt(profile))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
