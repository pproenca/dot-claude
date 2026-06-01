---
name: knowledge-ratchet
description: >-
  Capture recurring friction during development and promote it into durable
  fixes so it stops recurring — the outer feedback loop that improves the harness
  itself. Use this whenever something rubs more than once: a scanner or check
  produces a false positive, the same boundary gets misplaced the same way, a
  primitive gets reused a third time, a library decision repeats, or a plan keeps
  hitting the same snag. It maintains a small repo-local log (ratchet.jsonl) that
  counts recurrences and distinguishes defects (fix on sight) from abstractions
  (gated by the Rule of Three), tells you what is RIPE to promote, and records
  where each durable fix landed (a type constraint, a scan/lint rule, a reference,
  a convention in AGENTS.md, or — rarely — a new skill). Engage it at a feature's
  record/ship step to log friction, and whenever you ask "has this come up
  before, and should I fix it for good?"
---

# Knowledge Ratchet

The harness has three feedback loops. The **inner** loop (feature-workflow) ships
a feature. The **outermost** loop (production telemetry) tells you whether shipped
features worked — deferred until there's a running system. This is the **middle**
loop, at design time: it improves the harness itself by turning friction that
recurs into a fix that holds.

Without it, the same annoyances recur every feature and the lessons live only in
whoever happened to notice. With it, the third time something rubs, the system
says "this is a pattern — fix it for good," and names where the fix should live.

## The discipline

**Observe** friction as it happens (cheap; over-log rather than under-log):

    ratchet.py --observe "<what rubbed>" --key <slug> --kind defect|abstraction --where <loc>

**Check** what's actionable. Two ripeness rules, because they're different:
- **defect** (something is wrong) → ripe at one occurrence; fix on sight.
- **abstraction** (a candidate generalization) → ripe at three (Rule of Three);
  earlier is the wrong-abstraction trap.

    ratchet.py --ripe        # the queue owed a durable fix (gate-able: exit 1 if any)
    ratchet.py --status      # the whole log, with recurrence counts

**Promote** — give it a durable home and close it:

    ratchet.py --promote <key> --as <sink> --landed <where>

## Choosing the sink (see references/promoting.md)

The maturity ladder applied to process learning — prefer the leftmost, the fix
that needs the least vigilance: **type-constraint** (unrepresentable) →
**scan-pattern / lint-rule** (automated) → **reference** (in-context guidance) →
**convention** (a line in AGENTS.md). And: project-specific learnings go to a
repo-local sink (AGENTS.md / a reference), never a new skill; only a genuinely
reusable, cross-project *capability* justifies minting a skill.

## How it connects to the rest of the harness

- **feature-workflow** record/ship step feeds friction here (`--observe`), and a
  ripe-check (`ratchet.py --ripe`) can gate ship so debt is named, not buried.
- **harness-setup** wrote the `AGENTS.md` "Repo conventions & learnings" section
  — the home for `convention`-sink promotions.
- **boundary-discipline / verify-and-diagnose** are common sources of friction
  (a scan false-positive, a recurring misplacement); their scripts/references are
  common promotion targets.

## Why a plain JSONL, no port

Frictions are rare, so the log stays small. A storage port or search (as in
library-knowledge) would be anticipation, not evidence — the exact premature
abstraction this skill tells you to avoid. If the log ever grows large enough to
need search, that's itself a ripe friction to promote.

## Files

- `scripts/ratchet.py` — observe friction, list what's ripe, promote a fix. Store: `ratchet.jsonl`.
- `references/promoting.md` — defect vs abstraction, and the sink-choice ladder.

## Sibling: motions, not just code
This ratchet promotes a fix when a defect recurs and a shelf item when an
abstraction recurs. A third recurrence — a repeated manual MOTION — is
`toolsmith`'s domain: the third time a hand-motion repeats, forge a tool. Same
Rule of Three, pointed at Cairn's own working rather than at the product.
