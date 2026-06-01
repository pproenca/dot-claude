#!/usr/bin/env python3
"""Gate a CHANGE manifest before the change proceeds.

Structural twin of plan_check.py, but the obligation it enforces is per-kind and
derived from the dominant failure mode:

  refactor -> a characterization net must be declared and GREEN-before-touch
  fix      -> a failing repro (RED first) must be declared
  spike    -> a FLOOR (theoretical limit / reference) must be declared, AND the
              result must be expressed as a ratio to that floor — never to the
              naive starting point. This is the anti-"agent-psychosis" gate:
              1.5ms is only a win against a floor, not against your own 88ms.

Fails closed: an unfilled sentinel or a missing obligation BLOCKS. The test is
the trust boundary of the change; skipping it is proceeding on unparsed input.

Usage:
    change_check.py --kind refactor CHANGE_refactor_x.md
    change_check.py --kind spike    CHANGE_spike_y.md
Exit: 0 = gate passed, 1 = gate failed.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

SENTINEL = re.compile(r"\(\([^)]*\)\)")

OBLIGATION = {
    "refactor": [
        (re.compile(r"characterization tests captured BEFORE.*?:\s*(?!\(\()", re.I | re.DOTALL),
         "declare the characterization net (path/status) — must be GREEN before any change"),
    ],
    "fix": [
        (re.compile(r"failing repro test \(RED.*?:\s*(?!\(\()", re.I | re.DOTALL),
         "declare the failing repro test (must be RED first)"),
    ],
    "spike": [
        (re.compile(r"FLOOR.*?:\s*\n?\s*(?!\(\()", re.I | re.DOTALL),
         "declare the FLOOR (theoretical limit / reference) — results are judged against it"),
        (re.compile(r"vs\s+FLOOR.*?:\s*(?!\(\()", re.I | re.DOTALL),
         "report the best result AS A RATIO TO THE FLOOR, not to the starting point"),
    ],
}



def _cited_files_exist(text: str, manifest: Path) -> list[str]:
    """A declared test artifact that cites a path must EXIST. Declared-but-absent
    is a lie the gate CAN catch (unlike whether the test is honest, which it can't).
    Looks for common test/source tokens and checks them relative to the manifest
    dir and repo root."""
    missing = []
    for tok in re.findall(r"[\w./-]+\.(?:(?:test|spec)\.)?(?:ts|tsx|js|jsx|py|go|rs)\b", text):
        cand = (manifest.parent / tok)
        if not cand.exists() and not (manifest.parent / "../" / tok).exists():
            missing.append(tok)
    return missing


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Gate a CHANGE manifest.")
    ap.add_argument("manifest")
    ap.add_argument("--kind", required=True, choices=["refactor", "fix", "spike"])
    args = ap.parse_args(argv)
    p = Path(args.manifest)
    if not p.exists():
        print(f"GATE FAILED: {args.manifest} not found.")
        return 1
    text = p.read_text(encoding="utf-8")

    problems = []
    leftover = SENTINEL.findall(text)
    if leftover:
        problems.append(f"{len(leftover)} unfilled sentinel(s) (( )) remain — complete the manifest.")
    for rx, msg in OBLIGATION[args.kind]:
        if not rx.search(text):
            problems.append(f"obligation not met: {msg}")

    # Truth-check (cheap): cited test files must exist. Form-check (declaration)
    # alone is not enough where existence is mechanically verifiable.
    if args.kind in ("refactor", "fix"):
        missing = _cited_files_exist(text, p)
        if missing:
            problems.append("cited test file(s) do not exist: " + ", ".join(missing[:3])
                            + " — a declared net/repro must actually be there.")

    if problems:
        print(f"GATE FAILED ({args.kind}): {p.name}")
        for pr in problems:
            print(f"  - {pr}")
        print("\nThe test/floor is the trust boundary of this change. Declare it before proceeding.")
        return 1
    verified = "verified" if args.kind in ("refactor","fix") else "DECLARED (not verified — a floor/invariant's TRUTH needs a human or a run; the gate only confirms it is stated)"
    print(f"GATE PASSED ({args.kind}): {p.name} — obligation {verified}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
