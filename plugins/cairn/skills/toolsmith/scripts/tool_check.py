#!/usr/bin/env python3
"""Surface the tool for a motion (so it's reused, not rebuilt), record a reuse, and
flag tools that never reached payback as candidates to RETIRE.

  tool_check.py --motion "hand-check effects leaked into core" [--repo .]   # find tool
  tool_check.py --used .cairn/tools/check_core_purity.py [--repo .]          # record a reuse
  tool_check.py --audit [--repo .]                                          # list debt tools
"""
from __future__ import annotations
import argparse, hashlib
from pathlib import Path
import store


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="."); ap.add_argument("--store", default=None)
    ap.add_argument("--motion", default=None)
    ap.add_argument("--used", default=None)
    ap.add_argument("--audit", action="store_true")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()

    if args.used:
        rec = store.read_one(repo, args.store, "tool:" + args.used)
        if not rec:
            print(f"no tool registered at {args.used}."); return 2
        rec["uses"] = rec.get("uses", 0) + 1
        store.upsert(repo, args.store, rec)
        bs, ms = rec.get("build_steps", 0), rec.get("manual_steps", 0) or 1
        saved = rec["uses"] * ms - bs
        print(f"reuse recorded: {args.used} (used {rec['uses']}x). "
              f"net {'SAVED' if saved>=0 else 'still costs'} ~{abs(saved)} steps "
              f"({'past payback' if saved>=0 else 'not yet paid back'}).")
        return 0

    if args.audit:
        debt = []
        for r in store.read_all(repo, args.store):
            if r.get("kind") != "tool": continue
            bs, ms, u = r.get("build_steps",0), r.get("manual_steps",0) or 1, r.get("uses",0)
            if u * ms < bs:
                debt.append((r["path"], u, bs, ms))
        if not debt:
            print("workshop healthy: every tool has earned its keep.")
        else:
            print("tools below payback (candidates to RETIRE if not expected to recur):")
            for path, u, bs, ms in debt:
                print(f"  {path}: used {u}x, build cost {bs}, saves {ms}/use -> needs {bs//ms - u} more uses")
        return 0

    if args.motion:
        key = "motion:" + hashlib.sha1(args.motion.lower().encode()).hexdigest()[:8]
        m = store.read_one(repo, args.store, key)
        if m and m.get("tool"):
            print(f"tool exists for this motion: {m['tool']} — use it, don't rebuild it.")
        else:
            print("no tool for this motion yet" + (f" (seen {m['count']}x)" if m else "") + ".")
        return 0

    ap.print_help(); return 1


if __name__ == "__main__":
    raise SystemExit(main())
