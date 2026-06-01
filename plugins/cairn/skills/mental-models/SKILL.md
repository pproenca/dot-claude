---
name: mental-models
description: >-
  The learning loop for problem-solving technique. Caches transferable
  REFRAMINGS that reveal solution classes you would not otherwise search for,
  keyed by a SMELL (the symptom that should trigger them) and learned from
  observed GAPS rather than looked up by name. Use this on a novel or hard
  problem (especially from spike-workflow), when a result seems good but you lack
  the systems understanding to know if it truly is, or when a gap against a
  floor/reference exposes that a whole class of approach was missed. It keeps a
  repo-local store (mental-models.jsonl): per model, the triggering smell, the
  reframing question, the solution classes it opens, an example, and the gap that
  taught it. The HORIZONTAL twin of library-knowledge (facts) and
  specialist-knowledge (domain craft): domain-GENERAL systems insight whose
  authority is the measured gap, not docs. The antidote to "you don't look for
  what you don't know" and to false victory against a weak baseline.
---

# Mental Models

The third knowledge boundary. `library-knowledge` caches a named thing's facts.
`specialist-knowledge` caches a domain's vertical craft. This caches **horizontal
systems insight** — transferable reframings that, applied to a renderer, a
parser, or a scheduler alike, *open classes of solution you did not know to look
for*. It is how the harness learns to tackle novel problems instead of
optimizing within the first class it thought of.

## The bootstrap paradox it solves
"You don't look for what you don't know" is logically closed — you cannot search
for a category you don't know exists. This skill attacks it from the two sides
that don't need foreknowledge of the answer:
1. **The gap makes the unknown visible.** Judged against a FLOOR (see
   spike-workflow), a far-from-floor result is an anomaly that *points at* a
   missing model — you don't need to already know the model to see the gap.
2. **The catalog turns each revealed gap into a future trigger.** Record the
   reframing and the SMELL that should fire it. Monotonically: unknown-unknown ->
   known-unknown (you hold the question) -> known-known (you hold the pattern).

The authority is the gap, not documentation. That is why this is learned from
surprise, not looked up by name.

## The store entry (the interface)
`mental-models.jsonl` at the repo root — one record per line, keyed by `smell`:
- `smell` — the symptom that should trigger the model ("this is slow", "O(n^2)
  nesting", "150K allocations", "complex state transitions", "deeply coupled").
- `reframe` — the question that opens classes ("is this allocation-bound or
  compute-bound?", "is there a data-oriented layout?").
- `solution_classes` — the classes the reframe reveals (not variants within one).
- `example` — a concrete instance (e.g. the Ghostty 75x-from-floor renderer).
- `taught_by_gap` — the gap that taught this model (provenance; the authority).
- `confirmed_on` — date.

## Workflow
- **Apply (cheap, common):** `models_lookup.py --smell "<symptom>"` (or `--all`)
  returns the matching reframing questions + solution classes BEFORE you commit
  to an approach. Used heavily by spike-workflow's class enumeration.
- **Learn (from a gap):** when a result sits far from its floor, or you discover
  post-hoc that a better class existed, record the model and its trigger:
  `models_record.py --smell "<symptom>" --from-json <file>`. (See
  `references/learning.md`.)

## Composition
- `spike-workflow` consults this during class enumeration and feeds it on every
  gap. The handshake is the learning loop.
- The reference-first FLOOR (spike-workflow / change_check.py --kind spike) is
  what makes gaps visible so there is something to learn from.
- The `knowledge-ratchet` governs graduation: a model leaned on repeatedly may be
  promoted into a convention, a lint, or a checklist item; a model only becomes
  its own skill on the VENDOR cost test.

## The one law here
A model here is domain-GENERAL reframing, not a fact (library-knowledge) and not
domain craft (specialist-knowledge). If it only applies to one library or one
platform, it belongs in those skills. Keep this shelf horizontal and transferable.

## Files
- `references/learning.md` — turning a gap into a recorded model.
- `scripts/store.py` — storage port (JSONL; only module touching disk).
- `scripts/models_lookup.py` — apply: smell -> reframing questions + classes.
- `scripts/models_record.py` — learn: record a model from a gap.
