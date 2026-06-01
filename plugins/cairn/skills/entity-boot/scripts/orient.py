#!/usr/bin/env python3
"""Session-start honest self-report. Reads the stores and says, plainly, what the
entity knows, is proven at, and does NOT — so knowledge informs behavior and no
file creates an illusion of competence. A new repo is novice everywhere; that is
stated, not hidden.

  orient.py --repo .
"""
from __future__ import annotations
import argparse, json
from pathlib import Path


def _jsonl(p: Path):
    if not p.exists(): return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line: continue
        try: out.append(json.loads(line))
        except json.JSONDecodeError: continue
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Honest entity self-report at session start.")
    ap.add_argument("--repo", default=".")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()

    caps = _jsonl(repo / "capability-ledger.jsonl")
    libs = _jsonl(repo / "lib-knowledge.jsonl")
    models = _jsonl(repo / "mental-models.jsonl")
    profs = _jsonl(repo / "specialist-profiles.jsonl")
    ratchet = _jsonl(repo / "ratchet.jsonl")

    print("# Orientation — what I honestly know in this repo\n")

    if not any([caps, libs, models, profs]):
        print("I am newly hatched here. I know nothing yet about this codebase, am")
        print("PROVEN at nothing, and every problem class gets full gates. That is")
        print("correct for a new repo — I earn competence by demonstrating it, not by")
        print("claiming it. Let's solve the first problem; the curve bends after.")
        return 0

    # capability
    proven = [c["problem_class"] for c in caps if c.get("maturity") == "proven"]
    practiced = [c["problem_class"] for c in caps if c.get("maturity") == "practiced"]
    novice = [c["problem_class"] for c in caps if c.get("maturity") not in ("proven", "practiced")]
    print("## Capability (demonstrated, not claimed)")
    print(f"- proven (may delegate / larger blast radius): {', '.join(proven) or 'none yet'}")
    print(f"- practiced (plan gate may auto-pass): {', '.join(practiced) or 'none yet'}")
    print(f"- novice / untested (full gates): {', '.join(novice) or 'none'}")
    print(f"  -> I will surface before acting on any earned license.\n")

    # knowledge + honesty about staleness
    print("## Knowledge")
    print(f"- library facts: {len(libs)} cached; specialist profiles: {len(profs)}; "
          f"mental models: {len(models)}")
    print(f"- open friction in the ratchet: {sum(1 for r in ratchet if 'PROMOTED' not in json.dumps(r))}")
    print("  (run the per-skill --check / --stale gates for exact staleness; I flag, I don't assume)\n")

    print("## Honest gaps")
    print("- Anything not listed above, I have NOT demonstrated. I will say so when it comes up,")
    print("  keep the gate, and earn it rather than pretend.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
