#!/usr/bin/env python3
"""Record a truth-checked solve, or a demoting miss. Recomputes maturity.

  cap_record.py --class render-perf --floor-ratio 1.8 --domain renderer --benchmark bench/frame.json
  cap_record.py --class render-perf --miss --floor-ratio 40 --domain parser

A solve with no --benchmark is REFUSED: no measurement, no credit. A --miss drops
the class one rung immediately (asymmetric: grant slow, revoke fast).
"""
from __future__ import annotations
import argparse, datetime as dt, sys
from pathlib import Path
import store
from maturity import compute_maturity, effective_maturity, licenses, demote, credited

def main(argv=None):
    ap = argparse.ArgumentParser(description="Record a capability solve or miss.")
    ap.add_argument("--repo", default="."); ap.add_argument("--store", default=None)
    ap.add_argument("--class", dest="cls", required=True)
    ap.add_argument("--floor-ratio", type=float, required=True)
    ap.add_argument("--domain", default=None)
    ap.add_argument("--benchmark", default=None, help="path/ref to the recorded measurement")
    ap.add_argument("--miss", action="store_true", help="a failure: demote one rung now")
    ap.add_argument("--playbook", default=None, help="proven approach (for delegation)")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    entry = store.read_one(repo, args.store, args.cls) or {
        "problem_class": args.cls, "solves": [], "maturity": "novice", "playbook": None, "last_demotion": None}

    if args.miss:
        before = entry.get("maturity", "novice")
        entry["maturity"] = demote(before)
        entry["last_demotion"] = {"date": dt.date.today().isoformat(),
                                  "floor_ratio": args.floor_ratio, "domain": args.domain,
                                  "from": before, "to": entry["maturity"]}
        store.upsert(repo, args.store, entry)
        print(f"MISS recorded for '{args.cls}': demoted {before} -> {entry['maturity']} "
              f"(floor_ratio {args.floor_ratio}). License revoked fast.")
        return 0

    # a SOLVE must be truth-checked: a benchmark ref is mandatory.
    if not args.benchmark:
        print("REFUSED: a solve needs --benchmark (a recorded measurement). "
              "No measurement, no capability credit — license is earned, not declared.", file=sys.stderr)
        return 2
    # Idempotency: a given measurement counts ONCE. The same benchmark_ref recorded
    # twice (a retry, a re-run of close_loop) must not inflate competence — the
    # ledger's authority is distinct measured outcomes, not call count.
    if any(s.get("benchmark_ref") == args.benchmark for s in entry["solves"]):
        print(f"already recorded: benchmark '{args.benchmark}' for '{args.cls}' is in the ledger. "
              f"A measurement counts once; not double-counting.", file=sys.stderr)
        print(f"'{args.cls}': maturity {entry.get('maturity','novice')} (unchanged).")
        return 0
    entry["solves"].append({"floor_ratio": args.floor_ratio, "domain": args.domain,
                            "date": dt.date.today().isoformat(), "benchmark_ref": args.benchmark})
    if args.playbook: entry["playbook"] = args.playbook
    before = entry.get("maturity", "novice")
    entry["maturity"] = effective_maturity(entry)
    store.upsert(repo, args.store, entry)
    c = len(credited(entry["solves"])); near = args.floor_ratio <= 2.0
    print(f"solve recorded for '{args.cls}' (floor_ratio {args.floor_ratio}"
          f"{'' if near else ' — NOT near-floor, no credit'}). "
          f"credited solves: {c}. maturity: {before} -> {entry['maturity']}.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
