#!/usr/bin/env python3
"""Log a repeated manual motion. Flags it RIPE at the third occurrence — the Rule of
Three pointed at Cairn's own hand-work.

  motion_observe.py --motion "hand-check effects didn't leak into the core" --steps 6 [--repo .]
"""
from __future__ import annotations
import argparse, hashlib, sys
from pathlib import Path
import store


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="."); ap.add_argument("--store", default=None)
    ap.add_argument("--motion", required=True)
    ap.add_argument("--steps", type=int, default=0, help="rough manual cost (steps/min) of one occurrence")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    key = "motion:" + hashlib.sha1(args.motion.lower().encode()).hexdigest()[:8]
    def inc(existing):
        rec = existing or {"key": key, "kind": "motion",
                "motion": args.motion, "count": 0, "steps": args.steps, "tool": None}
        rec["motion"] = args.motion
        rec["count"] = int(rec.get("count", 0)) + 1
        if args.steps: rec["steps"] = args.steps
        return rec
    rec = store.update(repo, args.store, key, inc)
    ripe = rec["count"] >= 3 and not rec.get("tool")
    print(f"motion logged: '{args.motion}' x{rec['count']}"
          f"{' [RIPE — forge a tool: tool_forge.py]' if ripe else ''}")
    if rec.get("tool"):
        print(f"  (a tool already exists for this motion: {rec['tool']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
