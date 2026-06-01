#!/usr/bin/env python3
"""Close the learning circuit automatically when a spike/feature lands.

Finishing a solve IS the act of learning — no human should have to remember to
record it (the "self-improvement is opt-in" flaw, fixed). Given a completed
spike's result, this single call:
  1. records the floor-ratio into capability-ledger (a SOLVE if near-floor and
     benchmarked; a MISS if it failed to reach floor — which demotes),
  2. records any gap that exposed a missing model into mental-models,
  3. reports the resulting maturity change so the loop can surface it (consent).

It writes through the existing ports (cap_record, models_record) — it does not
touch stores directly. It NEVER fabricates: a solve with no benchmark is refused
upstream; a model with no taught_by_gap warns upstream. The circuit only carries
what was actually measured.

Usage:
  close_loop.py --class render-perf --domain renderer --floor-ratio 1.8 \
      --benchmark bench/frame.json \
      [--gap-smell "150k allocations" --gap-json model.json] \
      [--playbook "floor-first; windowed+SoA; bench vs floor"]
  close_loop.py --class render-perf --domain scheduler --floor-ratio 40 --miss
"""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _find_models_record(repo: Path) -> Path | None:
    """Resolve mental-models/models_record.py across layouts: plugin tree
    (skills/mental-models/scripts/), .harness mirror (.harness/mental-models/),
    or a sibling-of-here. Robust to where close_loop is invoked from."""
    candidates = [
        HERE.parent.parent / "mental-models" / "scripts" / "models_record.py",
        HERE.parent.parent / "mental-models" / "models_record.py",
        HERE.parent / "mental-models" / "models_record.py",
        repo / ".harness" / "mental-models" / "models_record.py",
        repo / "_h" / "mental-models" / "models_record.py",
    ]
    for c in candidates:
        if c.exists():
            return c
    # last resort: glob the repo, preferring a copy under .harness so a stray
    # vendored/backup copy cannot capture the cross-skill write.
    hits = list(repo.rglob("models_record.py"))
    harnessed = [h for h in hits if ".harness" in h.parts]
    return (harnessed or hits or [None])[0]


def _run(args):
    p = subprocess.run([sys.executable] + args, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Auto-close the solve -> ledger -> mental-models circuit.")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--class", dest="cls", required=True)
    ap.add_argument("--domain", required=True)
    ap.add_argument("--floor-ratio", type=float, required=True)
    ap.add_argument("--benchmark", default=None)
    ap.add_argument("--miss", action="store_true")
    ap.add_argument("--gap-smell", default=None)
    ap.add_argument("--gap-json", default=None)
    ap.add_argument("--playbook", default=None)
    args = ap.parse_args(argv)

    print("== closing the learning circuit ==")
    # 1) capability ledger
    cap = [str(HERE / "cap_record.py"), "--repo", args.repo, "--class", args.cls,
           "--floor-ratio", str(args.floor_ratio), "--domain", args.domain]
    if args.miss:
        cap.append("--miss")
    else:
        if args.benchmark: cap += ["--benchmark", args.benchmark]
        if args.playbook: cap += ["--playbook", args.playbook]
    rc, out = _run(cap)
    print("  [ledger] " + out.splitlines()[-1] if out else "  [ledger] (no output)")

    # 2) mental-models (only if a gap was actually observed)
    if args.gap_smell and args.gap_json:
        mm = _find_models_record(Path(args.repo).resolve())
        if mm:
            rc2, out2 = _run([str(mm), "--repo", args.repo, "--smell", args.gap_smell,
                              "--from-json", args.gap_json])
            print("  [insight] " + (out2.splitlines()[-1] if out2 else "(recorded)"))
        else:
            print("  [insight] mental-models not found in any known layout — gap NOT recorded "
                  "(run from the harness, or pass an explicit path)")
    else:
        print("  [insight] no gap supplied — nothing to learn (a clean near-floor solve teaches no new model)")

    # 3) report for the consent layer to surface
    rc3, out3 = _run([str(HERE / "cap_check.py"), "--repo", args.repo, "--class", args.cls])
    print("  [now] " + (out3.splitlines()[0] if out3 else "?"))
    print("== circuit closed ==")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
