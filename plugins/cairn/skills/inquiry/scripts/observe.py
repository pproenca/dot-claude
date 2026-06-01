#!/usr/bin/env python3
"""Record what was observed, compute the surprise, and (on a significant surprise)
feed mental-models with a reframing whose authority is 'a confident prediction was
wrong'. The confidence is NOT editable here — only the outcome.

  observe.py --id ab12cd34 --outcome wrong --observation "validated in the service layer" \
      --reframe "check the call graph before assuming where parsing lives" [--repo .]

surprise = confidence * wrongness, where wrongness = {right:0, partial:0.5, wrong:1}.
A surprise >= --threshold (default 0.5) is significant and teaches a model.
"""
from __future__ import annotations
import argparse, subprocess, sys, tempfile, json
from pathlib import Path
import store

WRONGNESS = {"right": 0.0, "partial": 0.5, "wrong": 1.0}


def _find_models_record(repo: Path):
    """Resolve mental-models' recorder deterministically across BOTH layouts:
    dev (skills/<s>/scripts/) and install (.harness/<s>/, flattened). Explicit
    candidates first; rglob only as last resort, and then preferring a copy under
    .harness so a stray vendored/backup copy can't capture the teach."""
    here = Path(__file__).resolve().parent
    for c in [here.parent / "mental-models" / "scripts" / "models_record.py",  # dev sibling
              here.parent.parent / "mental-models" / "scripts" / "models_record.py",  # dev
              here.parent / "mental-models" / "models_record.py",  # install sibling (.harness)
              repo / ".harness" / "mental-models" / "models_record.py"]:  # install by repo
        if c.exists(): return c
    hits = list(repo.rglob("models_record.py"))
    harnessed = [h for h in hits if ".harness" in h.parts]
    return (harnessed or hits or [None])[0]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Record an observation and score the surprise.")
    ap.add_argument("--repo", default="."); ap.add_argument("--store", default=None)
    ap.add_argument("--id", required=True)
    ap.add_argument("--outcome", required=True, choices=["right", "partial", "wrong"])
    ap.add_argument("--observation", default="")
    ap.add_argument("--reframe", default="")
    ap.add_argument("--threshold", type=float, default=0.5)
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    rec = store.read_one(repo, args.store, args.id)
    if not rec:
        print(f"no prediction with id {args.id}.", file=sys.stderr); return 2
    if rec.get("outcome") is not None:
        print(f"prediction {args.id} already observed (outcome cannot be rewritten).", file=sys.stderr); return 2
    surprise = rec["confidence"] * WRONGNESS[args.outcome]
    rec.update({"observation": args.observation, "outcome": args.outcome,
                "surprise": round(surprise, 3), "reframe": args.reframe or None})
    store.upsert(repo, args.store, rec)
    sig = surprise >= args.threshold
    print(f"observed: {args.outcome}. surprise = {surprise:.2f} "
          f"({'SIGNIFICANT — a confident belief was wrong; this teaches' if sig else 'below threshold — expected, noise'}).")
    if sig and args.reframe:
        mm = _find_models_record(repo)
        if mm:
            j = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
            json.dump({"reframe": args.reframe, "solution_classes": [],
                       "taught_by_gap": f"confident prediction ({rec['confidence']}) was wrong: {rec['claim']}"}, j)
            j.close()
            subprocess.run([sys.executable, str(mm), "--repo", str(repo),
                            "--smell", rec["claim"][:60], "--from-json", j.name], capture_output=True)
            print("  -> taught mental-models (authority: a confident prediction was wrong).")
    elif sig and not args.reframe:
        print("  -> significant surprise but no --reframe given; the lesson is unrecorded. "
              "What would have predicted correctly?")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
