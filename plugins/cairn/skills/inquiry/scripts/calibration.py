#!/usr/bin/env python3
"""Report calibration — does stated confidence match actual hit rate? — or REFUSE
if the sample is too small to mean anything (the statistical-honesty core).

  calibration.py [--repo .] [--min-n 10]

Buckets observed predictions by confidence band and compares predicted vs actual
hit rate. Below --min-n observed predictions, refuses to report a meaningful number
(a hit rate over a handful of samples is noise). Advisory only: this does not feed
the capability ledger yet — that bridge is built later, on a real sample, on
evidence, never in anticipation.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import store

BANDS = [(0.0,0.4),(0.4,0.6),(0.6,0.8),(0.8,1.0)]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Report calibration or refuse below min-n.")
    ap.add_argument("--repo", default="."); ap.add_argument("--store", default=None)
    ap.add_argument("--min-n", type=int, default=10)
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    observed = [r for r in store.read_all(repo, args.store) if r.get("outcome") is not None]
    n = len(observed)
    if n < args.min_n:
        print(f"calibration NOT YET MEANINGFUL: {n} observed prediction(s), need >= {args.min_n}. "
              f"Reporting a hit rate now would be noise dressed as self-knowledge. Keep predicting.")
        return 0
    print(f"Calibration over {n} observed predictions:")
    for lo, hi in BANDS:
        band = [r for r in observed if lo <= r["confidence"] < hi or (hi==1.0 and r["confidence"]==1.0)]
        if not band: continue
        predicted = sum(r["confidence"] for r in band)/len(band)
        actual = sum(1 for r in band if r["outcome"]=="right")/len(band)
        gap = actual - predicted
        tag = "calibrated" if abs(gap)<0.1 else ("OVERCONFIDENT" if gap<0 else "underconfident")
        print(f"  conf {lo:.1f}-{hi:.1f}: predicted {predicted:.0%}, actual {actual:.0%} "
              f"(n={len(band)}) -> {tag}")
    print("\n(advisory — calibration does not raise license until the sample is robust.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
