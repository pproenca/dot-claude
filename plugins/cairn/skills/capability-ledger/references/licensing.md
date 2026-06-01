# Computing earned license

Maturity is a pure function of the solve history — never hand-set, never
self-assessed. This file defines that function so it is auditable.

## What counts as a solve
A solve is credited only if:
1. it has a `benchmark_ref` (a recorded measurement — no measurement, no credit), and
2. its `floor_ratio` is at or under the class's near-floor threshold (default 2.0:
   the result is within 2x of the declared floor).
A result far from floor is NOT a solve — it is, at best, a logged attempt, and if
it occurred where the class was already promoted it is a MISS (see demotion).

## The maturity function
Given the credited solves for a class:
- **proven**   if >= 3 credited solves spanning >= 2 distinct domains.
- **practiced** if >= 3 credited solves (any domains).
- **novice**   otherwise.
Domains matter for `proven` because cross-domain success is what distinguishes a
transferable capability from a single-context fluke — the same reason mental-models
prizes horizontal reframings.

## What each rung licenses
- novice: nothing auto. Full gates; human confirms spec and result.
- practiced: the PLAN gate may auto-pass for this class. Build still verifies;
  human still reviews the result. (Autonomy over PLANNING, not over OUTCOME.)
- proven: may DELEGATE the class to a sub-agent under the recorded playbook, and
  attempt larger blast radius. Delegation hands over the playbook, the floor to
  beat, and the boundaries to respect — the sub-agent's result is itself
  benchmarked and flows back as a solve or a miss.

## What no rung ever licenses

No maturity licenses skipping the spec parse-point (feature-workflow STAGE 0.5).
Auto-pass covers the PLAN gate — planning *shape* — because that is what
benchmarked solves demonstrate. Intent is not a problem class and is never
demonstrated, so the human's confirmation of the proposed-invariant delta is
required at novice, practiced, and proven alike. License shrinks the delta (via
inherited invariants); it never removes the act of confirming it. A loop that let
proven-ness silence the spec interview would be declaring competence at the one
thing — knowing what the human wants — that cannot be earned against a floor.

## Demotion (instant, asymmetric)
A `--miss` (a result that failed to reach near-floor, or a shipped regression in
the class) drops the class ONE rung immediately and records `last_demotion`. This
is intentional asymmetry: climbing needs repeated cross-domain proof; falling
needs one failure. Over-licensing is far costlier than under-licensing, so the
ladder is biased to revoke fast and grant slow.

## Why this is safe to let raise autonomy
The promotion oracle is the floor gate, which is truth-checked (a benchmark must
exist and be near floor) — not the form-checked declaration gates that the
adversarial pass showed are gameable. Claude cannot promote itself by asserting
competence; it can only accumulate benchmarked outcomes it did not author the
grading of. That is what makes earned autonomy un-fakeable by the agent.
