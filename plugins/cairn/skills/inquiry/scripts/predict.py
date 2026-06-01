#!/usr/bin/env python3
"""Log a prediction + confidence BEFORE observing. This is the honest core: the
confidence is stamped now, and cannot be revised after the observation.

  predict.py --claim "input is validated at the controller, not the service" --confidence 0.7 [--repo .]

Prints the prediction id to use with observe.py. A claim with no confidence, or a
confidence outside (0,1), is refused — an unfalsifiable or unscored prediction is
not a prediction.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, sys
from pathlib import Path
import store


def main(argv=None):
    ap = argparse.ArgumentParser(description="Log a prediction before observing.")
    ap.add_argument("--repo", default="."); ap.add_argument("--store", default=None)
    ap.add_argument("--claim", required=True)
    ap.add_argument("--confidence", type=float, required=True)
    args = ap.parse_args(argv)
    if not (0.0 < args.confidence < 1.0):
        print("REFUSED: confidence must be in (0,1). 0 or 1 is certainty, not a prediction.", file=sys.stderr)
        return 2
    repo = Path(args.repo).resolve()
    now = dt.datetime.now().isoformat(timespec="seconds")
    pid = hashlib.sha1((args.claim + now).encode()).hexdigest()[:8]
    store.upsert(repo, args.store, {
        "id": pid, "claim": args.claim, "confidence": args.confidence,
        "made_at": now, "observation": None, "outcome": None, "surprise": None, "reframe": None})
    print(f"prediction {pid} logged @ confidence {args.confidence}. "
          f"Make the cheapest FALSIFYING observation, then: observe.py --id {pid} --outcome right|wrong|partial")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
