#!/usr/bin/env python3
"""Apply mental models: a smell -> the reframing questions + solution classes.

  models_lookup.py --smell "this is slow, 150k allocations"
  models_lookup.py --all
"""
from __future__ import annotations
import argparse
from pathlib import Path
import store


def _fmt(rec: dict) -> str:
    out = [f"## smell: {rec.get('smell','?')}",
           f"- **reframe:** {rec.get('reframe','')}"]
    if rec.get("solution_classes"):
        out.append("- **opens classes:** " + "; ".join(rec["solution_classes"]))
    if rec.get("example"):
        out.append(f"- _example:_ {rec['example']}")
    if rec.get("taught_by_gap"):
        out.append(f"- _learned from gap:_ {rec['taught_by_gap']}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Apply mental models by smell.")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--store", default=None)
    ap.add_argument("--smell", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--stale", action="store_true",
                    help="Surface models not reviewed in --max-age-days for re-validation.")
    ap.add_argument("--max-age-days", type=int, default=365)
    ap.add_argument("--review", default=None,
                    help="Restamp a model (by smell) as re-confirmed today.")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()

    # --review: the human re-confirms a model is still true (mental-models has no
    # external oracle like a package.json or a pinned lib — its authority is the
    # human + recurrence — so re-validation is an explicit restamp).
    if args.review:
        import datetime as dt
        rec = next((r for r in store.read_all(repo, args.store) if r.get("smell") == args.review), None)
        if not rec:
            print(f"no model with smell '{args.review}'."); return 1
        rec["reviewed_on"] = dt.date.today().isoformat()
        store.upsert(repo, args.store, rec)
        print(f"re-confirmed '{args.review}' on {rec['reviewed_on']}.")
        return 0

    # --stale: the decay gate. Without it the catalog grows write-only and a
    # reframing learned years ago is asserted forever even as reality moves.
    if args.stale:
        import datetime as dt
        today = dt.date.today()
        old = []
        for r in store.read_all(repo, args.store):
            stamp = r.get("reviewed_on") or r.get("confirmed_on")
            try:
                age = (today - dt.date.fromisoformat(stamp)).days if stamp else 10**6
            except ValueError:
                age = 10**6
            if age > args.max_age_days:
                old.append((r.get("smell", "?"), age))
        if not old:
            print(f"all models reviewed within {args.max_age_days} days.")
            return 0
        print(f"STALE models (not reviewed in {args.max_age_days}d — re-validate or retire):")
        for smell, age in sorted(old, key=lambda x: -x[1]):
            print(f"  [{age}d] {smell}  —  models_lookup.py --review \"{smell}\"  (or remove if obsolete)")
        return 1

    if args.all or not args.smell:
        recs = store.read_all(repo, args.store)
        if not recs:
            print("no mental models yet — record one with models_record.py when a gap teaches it.")
            return 0
        print(f"Mental-model shelf ({len(recs)}):")
        for r in recs:
            print(f"  [{r.get('smell','?')}] -> {r.get('reframe','')}")
        return 0

    hits = store.search(repo, args.store, args.smell)
    if not hits:
        print(f"no model matches smell '{args.smell}'. If a gap reveals one, record it "
              f"(models_record.py) so next time it's a known question.")
        return 1
    print(f"Reframings for '{args.smell}':\n")
    for r in hits[:4]:
        print(_fmt(r)); print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
