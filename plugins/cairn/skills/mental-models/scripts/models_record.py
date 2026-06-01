#!/usr/bin/env python3
"""Learn a mental model from a gap.

  models_record.py --smell "150k allocations per frame" --from-json model.json

model.json:
{
  "reframe": "allocation-bound or compute-bound? profile before tuning.",
  "solution_classes": ["arena/pool allocation","struct-of-arrays layout","reuse buffers across frames"],
  "example": "Ghostty renderer: 1.5ms/500allocs looked great but floor was 20us/0allocs (75x gap).",
  "taught_by_gap": "agent optimized within the naive class; missed data-oriented class entirely."
}
smell + confirmed_on are set from the flags/date.
"""
from __future__ import annotations
import argparse, datetime as dt, json, sys
from pathlib import Path
import store


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Record a mental model learned from a gap.")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--store", default=None)
    ap.add_argument("--smell", required=True)
    ap.add_argument("--from-json", required=True)
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    try:
        model = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"error: cannot read model json {args.from_json}: {e}", file=sys.stderr)
        return 2
    if not isinstance(model, dict):
        print("error: model json must be an object.", file=sys.stderr)
        return 2
    model["smell"] = args.smell
    if not model.get("taught_by_gap"):
        print("WARNING: no taught_by_gap recorded. A mental model's authority IS the measured "
              "gap; recording one without it is unsourced assertion, not learning.", file=sys.stderr)
    model["confirmed_on"] = dt.date.today().isoformat()
    store.upsert(repo, args.store, model)
    print(f"recorded model for smell '{args.smell}' "
          f"({len(model.get('solution_classes', []))} solution class(es)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
