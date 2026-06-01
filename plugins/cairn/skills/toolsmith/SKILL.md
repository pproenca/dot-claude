---
name: toolsmith
description: >-
  When you notice you are doing the same thing BY HAND again — the same check,
  trace, scaffold, or detection you did before — that noticing is the signal for
  this. It is the instinct to externalize repeated effort into tools: never do
  the same manual work twice. Use this when a motion has recurred: "I keep hand-checking
  whether effects leaked into the core", "I keep manually tracing the call graph".
  The Rule of Three pointed at Cairn's OWN repeated actions: the third time you do
  a thing by hand, forge a tool so the fourth is free. Tools live in a sandboxed
  workshop and may take real actions (run commands, scaffold, probe), trusting the
  outer harness (Claude Code) to bound the blast radius — a tool the harness
  rejects is itself a lesson. A tool is justified by MEASURED payback (manual cost
  x times done, vs build cost); one that never pays back is debt, and is retired.
  The bright line: a tool may never rewrite Cairn's own constitution — gates,
  ledger, floor, ladder.
---

# Toolsmith — never do the same manual work twice

The most basic thing a builder does: when the work is repetitive, make a thing so
it isn't. Cairn can learn, recall, grow trust, and think under fog — but without
this it works with bare hands forever. This is the faculty that makes the others
compound, because a tool doesn't just help once; it changes what is CHEAP, and
changing what is cheap changes what Cairn will attempt.

## Why this is the third way the cost curve bends
The marginal cost of feature N+1 slopes down three ways: the shelf (reusable code
parts), knowledge (don't re-derive), and — the most powerful because it compounds —
reusable CAPABILITY: tools Cairn forges for its own working. A mental-model makes
you think better next time; a tool means you need not think at all next time,
because the motion is automated. Tools become substrate the next tool is built
from. That is the runaway humans have and other learners don't.

## The trigger — Rule of Three on your OWN motions
The ratchet already promotes a fix when a defect recurs and a shelf item when an
abstraction recurs. This is the third recurrence it was blind to: a repeated MANUAL
MOTION. The third time you catch yourself doing the same hand-work — a check, a
trace, a scaffold, a probe — that is a tool waiting to be born. Two times might be
coincidence; three is a pattern with a shape clear enough to automate correctly.
Building on the first motion is how you forge the wrong tool, more expensive than
the manual work it replaced.

## Tools may act — the harness is the safety, and rejection teaches
A tool may take real actions: run a command, scaffold a file, probe the repo. Cairn
does not need training wheels here, because it does not work alone — it runs inside
an outer harness (Claude Code) with permission prompts, file boundaries, version
control, and a human in the loop. A tool that tries something destructive hits that
harness and is REJECTED, and that rejection is not a failure — it is the cheapest
falsifying observation about the tool. Treat it as inquiry applied to your own
creations: you predicted the tool was safe and useful; the harness disagreed;
record the surprise, update, and rebuild. Cairn is not the last line of defense and
must not act as if it were.

## The one bright line
A tool may help Cairn WORK; a tool may never rewrite Cairn's own CONSTITUTION. The
gates, the capability-ledger math, the floor semantics, the maturity ladder — these
are the substrate made unchangeable-by-learning on purpose, and a tool that edits
them is the agent-psychosis failure with a power drill. Tools live in the workshop
(`.cairn/tools/`), sandboxed from the skills' own scripts and stores. A tool is a
lever Cairn picks up, never a rewrite of Cairn's spine.

## Justified by measured payback, retired if it doesn't earn its keep
A tool is not justified by being clever; it is justified by the manual cost it
eliminates. Record: this motion cost ~N steps by hand, done K times; the tool cost
M to build; it pays back after about M/N reuses. A tool that never reaches payback
is debt, not leverage — the same law as premature abstraction, pointed at the
workshop. The instinct to build is paired with the honesty to retire a tool that
didn't earn its keep, so the workshop stays a toolbox and not a junk drawer.

## Discoverable, or it gets rebuilt
A tool nobody can find is a tool that gets rebuilt, and you have grown duplication
in the workshop instead of the product. Every tool is catalogued by the motion it
replaces, so the next time the smell appears, the tool surfaces instead of being
forged again.

## Files
- `references/forging.md` — when a motion is ripe, how to scope a tool small, and
  how to compute payback.
- `scripts/store.py` — the workshop catalogue (JSONL): tools by the motion they replace.
- `scripts/motion_observe.py` — log a repeated manual motion; flags it RIPE at three.
- `scripts/tool_forge.py` — register a forged tool with its payback math; refuses a
  tool whose target path is inside a skill or store (the bright line).
- `scripts/tool_check.py` — surface the tool for a motion; report tools below payback
  as candidates to retire.
