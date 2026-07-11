---
name: spike-workflow
description: >-
  Apply when the right APPROACH is unknown and must be discovered before
  committing — a hard algorithm or big-O/rendering decision, a complex state
  machine, tricky native/platform integration, a gnarly gesture/animation
  problem, a performance optimization, anything where you would otherwise guess
  an approach and build it. Use this whenever the task is "figure out how to...",
  "what is the best way to...", "optimize X", "this is slow/complex", "spike on
  Y". The dominant failure mode is COMMITTING TO THE WRONG APPROACH and DECLARING
  FALSE VICTORY against a weak baseline (agent psychosis). The rule is:
  establish the FLOOR (theoretical limit / reference) FIRST and judge every
  result against it, enumerate solution CLASSES (consult the mental-models skill)
  rather than optimizing within one, benchmark, then collapse the spike into a
  feature or refactor. Delegates to feature-workflow's change-kind gate-runners
  with --kind spike. Do NOT use once the approach is known — collapse and run
  that kind's loop.
---

# Spike Workflow

Resolve an unknown *approach* before committing to one. The unknown is which
*class* of solution is right — and the trap is that you cannot search for a class
you do not know exists ("you don't look for what you don't know"). So the parse
is a **benchmark against a FLOOR**, plus a **solution-class enumeration** driven
by transferable reframings.

## Why the FLOOR is non-negotiable (the anti-psychosis gate)
A result is only good against the *limit*, never against your own starting point.
The cautionary case: an agent drove a renderer 88ms → 1.5ms (150K → ~500 allocs)
and declared triumph; a hand-written reference did the same work in ~20µs with 0
allocations — a 75× gap it could not see because it compared to its own naive
baseline, not the floor. **Trusting "good" without parsing it against the limit
is the quality twin of trusting unparsed input.** Estimate the floor without
knowing the winning approach: big-O lower bound, zero-allocation ideal, memory
bandwidth ceiling, a hand-rolled reference. Then a result that sits far from the
floor *forbids* declaring victory — the unknown-unknown becomes a visible anomaly.

## The loop (the feature-workflow spine, spike instance)
1. **STEP 0 classified this as a spike.** `change_new.py --kind spike --name "..."`
   creates `docs/spikes/CHANGE_spike_<slug>.md`.
2. **Establish the FLOOR first** and write it into the manifest. (See
   `references/floor.md`.)
3. **Enumerate solution CLASSES, not variants.** Consult the `mental-models`
   skill: feed it the smell ("this is slow", "this is O(n^2)", "deep nesting")
   and it returns the reframing questions that *open classes you would not have
   searched for* (allocation-bound vs compute-bound? data-oriented layout?
   asymptotically better structure? mechanical sympathy?).
4. **Gate:** `change_check.py --kind spike docs/spikes/CHANGE_spike_<slug>.md`
   — blocks unless a floor is declared AND results are expressed as a ratio to it.
5. **Benchmark across classes**, report best-vs-floor as a ratio.
6. **Collapse:** the chosen class turns the spike into a feature (new behavior),
   a refactor (behavior-preserving restructure), or a perf-refactor (output
   identical, timing changed → needs BOTH a characterization net and a
   benchmark-vs-floor gate). Run that kind's loop next.
7. **Feed the learning loop:** any gap that exposed a *missing* model — a class
   you didn't think to consider — is recorded in `mental-models` with its trigger
   smell. The gap is the authority. That is how unknown-unknowns become known.

## The one law here
A spike produces a *decision backed by a floor-anchored benchmark*, not code you
keep. Resist building the first plausible approach; the cost of the wrong class
dwarfs the cost of the spike.

## Files
- `references/floor.md` — estimating a floor without knowing the answer; the
  reframing-checklist handshake with mental-models.
