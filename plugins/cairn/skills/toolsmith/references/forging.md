# Forging a tool: when ripe, how to scope, how to compute payback

## When a motion is ripe
A motion is a thing you do BY HAND in the course of working: a check, a trace, a
scaffold, a probe, a transformation. Log it each time you catch yourself doing it.
At the THIRD occurrence it is ripe — the shape is clear enough to automate
correctly. Earlier, you risk forging the wrong tool (the over-built script for a
motion that turns out to vary every time).

## Scope the tool small
A tool does ONE motion well. The temptation is to build the grand multi-purpose
script; resist it for the same reason you resist premature abstraction. Forge the
narrow tool that kills the specific repeated hand-work, and let a second tool be a
second tool. Narrow tools compose; grand tools entangle.

## Compute payback honestly
- N = rough steps/minutes the motion costs by hand, once.
- K = times you've already done it by hand (>= 3 to be ripe).
- M = steps/minutes to build the tool.
- Payback after about M/N reuses. If you don't expect that many future uses, the
  tool is debt — say so and don't build it, or build the cheapest possible version.
A tool that has been catalogued but never reused past payback should be RETIRED;
the workshop is a toolbox, not a junk drawer.

## The bright line, concretely
A tool may read anything and may act on the repo/product. A tool may NOT write to:
- any skill's `scripts/` or `references/`
- any knowledge store (`*-knowledge.jsonl`, `mental-models.jsonl`,
  `capability-ledger.jsonl`, `inquiry-log.jsonl`)
- the gate/ledger/floor/maturity logic
These are Cairn's constitution, unchangeable-by-learning on purpose. tool_forge
refuses a tool whose declared write-target lands inside them.

## When the harness rejects a tool
Claude Code may refuse a tool's action (permission, file boundary). That rejection
is a falsifying observation: you predicted the tool was safe/useful, the harness
disagreed. Record it as a surprise (inquiry), update, rebuild narrower. Rejection
is cheap learning, not failure.
