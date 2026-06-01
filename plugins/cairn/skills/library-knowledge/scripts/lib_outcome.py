#!/usr/bin/env python3
"""Record the outcome of USING a recalled fact: was it fresh (helped) or stale
(failed — you had to re-derive anyway)? This is how Cairn learns, from its own
experience, which knowledge is worth caching.

A stale hit is a confident prediction that was wrong (Cairn trusted the cache), so
when a fact's verdict flips to 're-derive' it also teaches mental-models — the same
surprise->reframing path inquiry uses — keyed to the smell of relying on this kind
of cached knowledge. The lesson is both structural (the verdict, which the recall
path now surfaces) and intuitive (the model, which the reflex surfaces next time).

  lib_outcome.py --repo . --name react --fresh
  lib_outcome.py --repo . --name repo-file-map --stale \
      --situation "trusting cached file locations in a fast-refactoring repo" \
      --reframe "in this repo, file locations churn; re-derive the path, don't trust the cache"
"""
from __future__ import annotations
import argparse, os, subprocess, sys, tempfile, json
from pathlib import Path
import store, freshness


def _find_models_record(repo: Path):
    here = Path(__file__).resolve().parent
    for c in [repo / ".harness" / "mental-models" / "models_record.py",
              here.parent / "mental-models" / "scripts" / "models_record.py",
              here.parent.parent / "mental-models" / "scripts" / "models_record.py",
              here.parent / "mental-models" / "models_record.py"]:
        if c.exists():
            return c
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Record whether a recalled fact was fresh or stale when used.")
    ap.add_argument("--repo", default="."); ap.add_argument("--store", default=None)
    ap.add_argument("--name", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fresh", action="store_true", help="the cached fact was still true; it saved work")
    g.add_argument("--stale", action="store_true", help="the cached fact was outdated; the approach failed")
    ap.add_argument("--situation", default="", help="(stale) the smell: relying on this kind of cached knowledge")
    ap.add_argument("--reframe", default="", help="(stale) what to do instead — usually 're-derive, don't trust cache'")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()

    entry = store.read_one(repo, args.store, args.name)
    if not entry:
        print(f"no cached fact '{args.name}'. (record it first, or it was never cached.)", file=sys.stderr)
        return 2

    before = freshness.verdict(entry)["policy"]
    freshness.record_outcome(entry, fresh=args.fresh)
    after = freshness.verdict(entry)
    # persist (store.upsert keeps one line per name)
    store.upsert(repo, args.store, args.name, {k: v for k, v in entry.items() if k != "name"})

    v = after
    print(f"recorded {'FRESH' if args.fresh else 'STALE'} recall of '{args.name}'. "
          f"verdict: {v['policy']} — {v['basis']}.")

    # The bet is negative: teach the lesson when Cairn supplies a reframe for a stale
    # recall whose verdict is now 're-derive'. Teaching is idempotent at the mental-models
    # layer (keyed by smell), so re-teaching the same smell is harmless; we avoid noise by
    # only teaching on a STALE outcome (the failure) with an explicit reframe.
    if args.stale and after["policy"] == "re-derive" and args.reframe:
        if before != "re-derive":
            print("  -> caching this has become a LOSING BET. Cairn should stop trusting this cache "
                  "and re-derive for this problem.")
        mm = _find_models_record(repo)
        if mm:
            smell = args.situation or f"relying on cached '{args.name}'"
            j = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
            try:
                json.dump({"reframe": args.reframe, "solution_classes": [],
                           "taught_by_gap": f"cached fact '{args.name}' was stale {entry.get('stale_hits')}/"
                                            f"{entry.get('uses')} recalls — caching it is a losing bet (re-derive)"}, j)
                j.close()
                proc = subprocess.run([sys.executable, str(mm), "--repo", str(repo),
                                "--smell", smell[:60], "--from-json", j.name],
                                      text=True, capture_output=True)
                if proc.returncode != 0:
                    if proc.stderr:
                        print(proc.stderr.strip(), file=sys.stderr)
                    if proc.stdout:
                        print(proc.stdout.strip(), file=sys.stderr)
                    print("  -> mental-model teaching FAILED; stale outcome was recorded.", file=sys.stderr)
                    return proc.returncode
                print("  -> taught mental-models (authority: a cached fact proved volatile in practice); "
                      "the reflex will catch it next time.")
            finally:
                try:
                    os.unlink(j.name)
                except OSError:
                    pass
        else:
            print("  -> (could not resolve mental-models recorder; record the reframe by hand.)")
    elif args.stale and after["policy"] == "re-derive" and not args.reframe:
        print("  -> caching this is a losing bet; pass --reframe to record what to do instead "
              "(usually: re-derive, don't trust the cache).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
