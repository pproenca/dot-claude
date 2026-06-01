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
        try:
            rec = json.loads(line)
        except json.JSONDecodeError: continue
        if isinstance(rec, dict):
            out.append(rec)
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
    print("Before I work: the reflex — when I am about to do something by hand")
    print("(explore, check, trace, detect, judge), I pause and ask whether I already")
    print("have a faculty for it, and look at myself before I reinvent.")
    print("(references/reflex.md) I don't yet know which faculty fits which moment —")
    print("that recognition I earn with use; the pause is what I start with.\n")

    if not any([caps, libs, models, profs]):
        print("I am newly hatched here. I know nothing yet about this codebase, am")
        print("PROVEN at nothing, and every problem class gets full gates. That is")
        print("correct for a new repo — I earn competence by demonstrating it, not by")
        print("claiming it. Let's solve the first problem; the curve bends after.")
        return 0

    # capability
    valid_caps = [c for c in caps if isinstance(c.get("problem_class"), str)]
    proven = [c["problem_class"] for c in valid_caps if c.get("maturity") == "proven"]
    practiced = [c["problem_class"] for c in valid_caps if c.get("maturity") == "practiced"]
    novice = [c["problem_class"] for c in valid_caps if c.get("maturity") not in ("proven", "practiced")]
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
    print()
    print("## Where to start when I don't know the terrain")
    print("- I don't know this repo yet, and neither would anyone on day one. Rather than")
    print("  guess, I use `inquiry`: state a prediction about the terrain WITH a confidence,")
    print("  make the cheapest observation that would prove me wrong, and record the surprise.")
    print("  A confident prediction that turns out wrong is how I learn the shape of a new")
    print("  codebase — and over time, how I build my own judgment about it.")
    print()
    print("## When I catch myself doing the same thing by hand")
    print("- The third time I do a manual motion — a check, a trace, a scaffold — I forge a")
    print("  tool for it (`toolsmith`), so the fourth time is free. Tools live in .cairn/tools/,")
    print("  may take real actions (the outer harness bounds the blast radius, and a rejected")
    print("  tool is a lesson), and must never touch my own gates, ledger, or stores.")
    print()
    print("## What I still need from you (nurture — see references/nurture.md)")
    if proven:
        print(f"- For proven classes ({', '.join(proven)}), you can step back; I have earned them.")
    print("- For everything not yet proven: please judge my declared FLOORS for honesty and")
    print("  spot-check that my 'near-floor' solves really are. The gates check form; only you")
    print("  (or a real run) check truth. These asks shrink as classes prove out.")
    print("- Watch the ratchet for 'learned-but-did-not-recall' frictions: that is the signal")
    print("  my retrieval matcher has hit its ceiling and the semantic backend has been earned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
