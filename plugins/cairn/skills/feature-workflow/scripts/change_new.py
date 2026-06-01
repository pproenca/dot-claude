#!/usr/bin/env python3
"""Scaffold a CHANGE manifest for a non-feature change — the STEP-0 gate output.

The loop is one spine; the change KIND determines the planning shape and the
test obligation. This is the refactor/fix/spike analogue of plan_new.py: it
writes a kind-specific manifest whose sections are derived from the dominant
failure mode of that kind, with `((fill))` sentinels the author must complete
before change_check.py will pass.

The unifying idea (see each sibling skill): every change kind contains an
`unknown` that must be PARSED into a trusted artifact (a test) before the change
proceeds. The manifest names that unknown and its parse.

Usage:
    change_new.py --kind refactor --name "extract booking state machine"
    change_new.py --kind fix      --name "deposit rounding off-by-one"
    change_new.py --kind spike    --name "appointment render big-O"
"""
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

COMMON_HEAD = """<!-- change kind: {kind} -->
# CHANGE ({kind}): {name}

## 0. Change kind & the unknown
- **Kind:** {kind}
- **The unknown (what is not yet trusted):** (({unknown}))
- **The parse (test artifact that makes it trusted):** (({parse}))
- **Dominant failure mode guarded:** {failure}
"""

BODIES = {
    "refactor": """
## 1. Behavior to preserve (the spec IS the current behavior)
- **Observable behavior that must not change:** ((list the outputs/contracts))
- **Characterization tests captured BEFORE touching code:** ((path / status — must be GREEN before any change))
- **Out of scope (explicitly NOT preserved — e.g. timing only):** ((none / list))

## 2. Structural change
- **What moves / is renamed / is reshaped:** ((...))
- **Boundary refactor? -> use boundary-discipline REFACTOR mode as the tool:** ((yes/no))

## 3. Seam & blast radius
- **What calls this; is contact composition or coupling?** ((...))

## 4. Verify obligation
- characterization net GREEN before AND after (identical behavior); no new behavior added.
""",
    "fix": """
## 1. The bug (bounded, specific)
- **Wrong behavior, precisely:** ((observed vs expected))
- **Failing repro test (RED before the fix):** ((path / status — must FAIL first, proving it captures the bug))
- **Root cause / why it's wrong:** ((...))

## 2. The change (one place)
- **The single boundary/unit changed:** ((...))
- **Why this is the right home (not a symptom patch):** ((...))

## 3. Neighbor safety
- **What could this break; covered by existing tests?** ((...))

## 4. Verify obligation
- repro test RED -> GREEN and STAYS green (regression locked); full suite still green.
""",
    "spike": """
## 1. The approach is unknown (do NOT commit to one yet)
- **The question being resolved:** ((what approach / structure / algorithm?))
- **The FLOOR (theoretical limit — judge results against THIS, not the naive baseline):**
  (({floor} — e.g. big-O lower bound, zero-allocation ideal, memory-bandwidth ceiling, hand-rolled reference))

## 2. Solution-class enumeration (defeat "you don't look for what you don't know")
- **Reframing checklist consulted (mental-models skill):** ((which smells/questions))
- **Candidate solution CLASSES (not variants within one):** ((class A / class B / class C ...))
- **Discriminating benchmark across classes:** ((what measures the difference))

## 3. Result & gap
- **Best result vs FLOOR (the ratio that forbids false victory):** ((Xms vs floor Yms = Nx gap))
- **Chosen class + why:** ((...))
- **Gap that exposed a MISSING mental model -> record in mental-models:** ((none / model + trigger))

## 4. Collapse
- **This spike collapses into a:** ((feature / refactor / perf-refactor)) — run that kind next.

## 5. Verify obligation
- a FLOOR is declared and the result is reported AS A RATIO TO THE FLOOR (not to the starting point);
  for a perf change, both a characterization test (output identical) AND a benchmark-vs-floor gate.
""",
}

SEED = {
    "refactor": ("the current behavior (believed, not proven)", "characterization tests (pin behavior before touching)", "silent regression"),
    "fix": ("the bug (believed broken in way Y)", "a failing repro test (RED first)", "recurrence / neighbor break"),
    "spike": ("the right approach (unknown class of solution)", "a benchmark-vs-floor that discriminates classes", "committing to the wrong approach / false victory vs a weak baseline"),
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Scaffold a CHANGE manifest for a non-feature change.")
    ap.add_argument("--kind", required=True, choices=["refactor", "fix", "spike"])
    ap.add_argument("--name", required=True)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    unknown, parse, failure = SEED[args.kind]
    head = COMMON_HEAD.format(kind=args.kind, name=args.name, unknown=unknown, parse=parse, failure=failure)
    body = BODIES[args.kind].format(floor="declare the floor")
    slug = "".join(c if c.isalnum() else "-" for c in args.name.lower()).strip("-")[:40]
    out = Path(args.out) if args.out else repo / f"CHANGE_{args.kind}_{slug}.md"
    out.write_text(head + body + f"\n<!-- scaffolded {dt.date.today().isoformat()} -->\n", encoding="utf-8")
    print(f"wrote {out.name} — fill the (({'(...)'} )) sentinels, then run change_check.py --kind {args.kind} {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
