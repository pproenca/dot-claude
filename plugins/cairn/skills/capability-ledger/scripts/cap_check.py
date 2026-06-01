#!/usr/bin/env python3
"""Read a class's current maturity and what it licenses. Read-only (consumers
never write their own license here).

  cap_check.py --class render-perf
  cap_check.py --index
"""
from __future__ import annotations
import argparse
from pathlib import Path
import store
from maturity import compute_maturity, effective_maturity, licenses, credited

def main(argv=None):
    ap = argparse.ArgumentParser(description="Check earned license for a class.")
    ap.add_argument("--repo", default="."); ap.add_argument("--store", default=None)
    ap.add_argument("--class", dest="cls", default=None)
    ap.add_argument("--index", action="store_true")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()

    if args.index or not args.cls:
        rows = store.read_all(repo, args.store)
        if not rows:
            print("capability ledger empty — every class is novice (full gates)."); return 0
        print("Capability ledger:")
        for r in rows:
            m = effective_maturity(r)
            c = len(credited(r.get("solves", [])))
            dom = len({s.get("domain") for s in credited(r.get("solves", [])) if s.get("domain")})
            print(f"  {r['problem_class']:<32} {m:<10} ({c} credited solve(s), {dom} domain(s))")
        return 0

    entry = store.read_one(repo, args.store, args.cls)
    if not entry:
        print(f"'{args.cls}': novice (no record). Full gates: human confirms spec AND result.")
        return 0
    m = effective_maturity(entry)
    lic = licenses(m)
    print(f"'{args.cls}': {m}")
    print(f"  plan-gate auto-pass: {lic['plan_gate_autopass']}")
    print(f"  may delegate:        {lic['may_delegate']}")
    print(f"  larger blast radius: {lic['larger_blast_radius']}")
    if entry.get("last_demotion"):
        d = entry["last_demotion"]; print(f"  last demotion: {d['from']}->{d['to']} on {d['date']} (ratio {d['floor_ratio']})")
    if m == "proven" and entry.get("playbook"):
        print(f"  delegation playbook: {entry['playbook']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
