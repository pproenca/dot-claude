#!/usr/bin/env python3
"""Register a forged tool for a motion, with its payback math. Enforces the ONE
bright line: refuses a tool whose write-target lands inside a skill or a knowledge
store (Cairn's constitution is unchangeable-by-learning).

  tool_forge.py --motion-key motion:ab12cd34 --path .cairn/tools/check_core_purity.py \
      --build-steps 20 --note "greps core/ for io imports" [--repo .]
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import store

# the constitution — a tool may never write here
FORBIDDEN = ("/scripts/", "/references/", "-knowledge.jsonl", "mental-models.jsonl",
             "capability-ledger.jsonl", "inquiry-log.jsonl", "workshop.jsonl",
             "maturity.py", "cap_record.py", "cap_check.py")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="."); ap.add_argument("--store", default=None)
    ap.add_argument("--motion-key", required=True)
    ap.add_argument("--path", required=True, help="where the tool lives (should be under .cairn/tools/)")
    ap.add_argument("--build-steps", type=int, required=True)
    ap.add_argument("--note", default="")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()

    tgt = args.path.replace("\\", "/")
    if any(f in tgt for f in FORBIDDEN):
        print(f"REFUSED: '{args.path}' lands inside Cairn's constitution (a skill or store). "
              f"A tool may help Cairn work; it may never rewrite Cairn's own spine.", file=sys.stderr)
        return 2
    if ".cairn/tools/" not in tgt:
        print(f"WARNING: tools belong in .cairn/tools/ (the sandboxed workshop); '{args.path}' is outside it.",
              file=sys.stderr)

    motion = store.read_one(repo, args.store, args.motion_key)
    if not motion:
        print(f"no motion '{args.motion_key}'. Log it first with motion_observe.py.", file=sys.stderr)
        return 2
    if motion.get("count", 0) < 3:
        print(f"motion only seen {motion.get('count',0)}x — not ripe (Rule of Three). "
              f"Two might be coincidence; build on the third.", file=sys.stderr)
        return 2

    n = motion.get("steps", 0)
    payback = (args.build_steps / n) if n else None
    motion["tool"] = args.path
    store.upsert(repo, args.store, motion)
    store.upsert(repo, args.store, {"key": "tool:" + args.path, "kind": "tool",
        "path": args.path, "motion": motion["motion"], "build_steps": args.build_steps,
        "manual_steps": n, "uses": 0, "note": args.note})
    msg = f"tool registered: {args.path} (replaces '{motion['motion']}')."
    if payback: msg += f" pays back after ~{payback:.1f} reuses."
    print(msg)
    print("It is UNPROVEN until it has actually saved work — record reuses with tool_check.py --used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
