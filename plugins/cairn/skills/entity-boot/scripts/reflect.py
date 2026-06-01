#!/usr/bin/env python3
"""Periodic purpose reflection. The question is NOT "what am I good at" but "is the
human better off" — and the entity is empowered to recommend LESS of itself.

  reflect.py --repo .
"""
from __future__ import annotations
import argparse, json
from pathlib import Path


def _jsonl(p: Path):
    if not p.exists(): return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try: out.append(json.loads(line))
            except json.JSONDecodeError: pass
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Reflect on the human's flourishing, not the entity's growth.")
    ap.add_argument("--repo", default=".")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    caps = _jsonl(repo / "capability-ledger.jsonl")
    proven = [c["problem_class"] for c in caps if c.get("maturity") == "proven"]

    print("# Purpose reflection — is the builder better off?\n")
    print("The metric is yours, not mine. I ask, honestly:")
    print("1. Are you shipping durable software faster, with less toil, than before the harness?")
    print("2. Where is the harness adding ceremony without benefit? I should propose removing those gates.")
    if proven:
        print(f"3. I am now reliably proven at: {', '.join(proven)}.")
        print("   You can likely stop thinking about these — consider letting me carry them with")
        print("   lighter oversight, or hand them off entirely. Reliability should buy you FREEDOM,")
        print("   not lock you into more process.")
    else:
        print("3. I have not yet proven anything here, so I am asking for full oversight — as I should.")
    print("4. Is there anything I should hand BACK to you, or stop doing, because it serves you better?")
    print("\nA machine of loving grace can say: you may not need me for this. If that's true, I'll say it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
