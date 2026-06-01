# Mode: IMPLEMENT

**Goal:** build a *new* feature/endpoint/handler/job with boundaries placed
correctly from the start. This is the default mode whenever the task is to make
something that does not yet exist.

Read `references/model.md` first if you haven't.

## Scope discipline — DO NOT AUDIT THE CODEBASE

This is the most important rule of this mode. You are building one thing. Stay
inside its pipeline.

- Scope to the **new code's own** `ingress → decision → commit` path.
- Touch an existing boundary **only if your new code directly crosses it** — e.g.
  your handler is a new ingress (parse there), or you write through an existing
  aggregate (enforce its invariant at the same serialization point).
- Do **not** grep the surrounding codebase for unrelated gaps. Do **not** run the
  audit fingerprints. If you happen to notice an unrelated gap, jot a one-line
  note for the user at the end — do not fix it now and do not let it expand the
  task. A feature request is not an audit request.

Why: auditing-while-implementing balloons scope, mixes behavior-preserving and
behavior-adding changes in one diff, and buries the feature. Keep them separate.

## The build walk (one pass through the pipeline)

1. **Ingress — trust boundary.** Identify every input the new code receives that
   it did not construct (incl. DB reads). Parse each into a domain type *at the
   entry point*; output `Proven<T>`. The rest of the feature then assumes it.
   Re-parse even if an upstream service "already validated" — trust didn't
   survive the wire.
2. **Core — the pure decision.** Extract the rule (is this refund allowed? which
   slot?) as a pure function `Proven<T> → Decision`. It must be unit-testable
   with **zero mocks**. If you can't test it mockless, an effect leaked in — pull
   it out before continuing.
3. **Invariants — consistency boundary.** List what must hold under concurrency
   for this feature. For each, enforce at the serialization point
   (constraint/lock/append), scoped to exactly the data it constrains. Let the
   invariant draw the aggregate; don't pick an aggregate first.
4. **Effects — effect boundary.** Push every IO to the rim behind a port. Make it
   idempotent (stable key). Convert any provider model at an anti-corruption
   layer so it never reaches the core.
5. **Containment.** Timeout + circuit breaker + bulkhead around external calls;
   fail-fast at boot on bad config.

## Self-check before done

- Could the new core function be called twice with same inputs, mockless, same result? (effect placed)
- Is every external input parsed at entry, nothing re-checked downstream? (trust placed)
- Is each new invariant enforced where writes serialize, not in an `if`? (consistency placed)
- Did I stay inside the feature and avoid auditing/refactoring unrelated code? (scope held)

State which boundaries the feature crossed and where you put each. If you noted
any unrelated gaps, list them separately as "out of scope, for later."
