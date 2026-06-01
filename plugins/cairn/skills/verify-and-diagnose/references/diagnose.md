# Mode: DIAGNOSE

**Goal:** find the **root cause** of a failure or regression — not patch the
symptom. This is investigative: open-ended, hypothesis-driven, search-shaped.
You enter this mode when a check fails, the verify gate blocks, something
renders/behaves wrong, a bug is flaky, or performance regressed.

Read `references/observe.md` first if you haven't. When you've confirmed the
cause and want to prove the fix, hand back to `verify.md`.

## The loop

1. **Reproduce** — minimal, deterministic. If you can't reproduce it reliably,
   that *is* the first bug (usually hidden nondeterminism — see below). No repro,
   no diagnosis.
2. **Observe** — read the relevant surfaces (`observe.md`) *before* editing.
   Capture the evidence.
3. **Hypothesize** — one specific, falsifiable cause.
4. **Test one variable** — change exactly one thing that would confirm or kill
   the hypothesis. Not a fix — a probe.
5. **Narrow** — repeat until the cause is located, not just correlated.
6. **Confirm** — show the cause explains the *full* symptom, then fix.

## Localize with the boundary model (the fast path)

Don't poke randomly — the **symptom names the boundary**. This turns debugging
from search into directed lookup:

| Symptom | Likely boundary | Where to look |
|---|---|---|
| Garbage/invalid data deep in the core; `undefined` where a domain value should be | **Trust** | a parse missing or wrong at ingress — the bad value entered un-narrowed |
| Works sometimes; order-dependent; "works on my machine"; flaky test | **Effect** | hidden nondeterminism — unmocked clock/random/IO, shared mutable state |
| Only fails under load / two users / rapid repeats | **Consistency** | invariant enforced in app code, not at the serialization point — a race |
| One slow/broken dependency stalls unrelated things | **Containment** | missing timeout / bulkhead / circuit breaker; failure cascading |
| Effect happened twice (double charge) or not at all | **Effect/Consistency** | idempotency key missing, or commit/publish not atomic (outbox) |

Match the symptom, go straight to that boundary, confirm with observation.

## Techniques

- **Bisection** — `git bisect` to find *when* it broke (binary search in time);
  binary search the call path / input to find *where* (disable half, see if it
  persists).
- **Differential** — compare a working case to the broken one; the delta is the
  suspect. "What changed?" is the highest-yield question.
- **Minimization** — delete code/inputs until it stops reproducing; the last
  removal points at the cause.
- **Instrumentation** — add *observation* (logs, breakpoints, a trace), not
  fixes. Resist editing logic before the cause is known.

## Anti-patterns

- Changing several things at once — you lose attribution.
- Fixing the symptom — adding a null-guard deep in the core instead of the
  missing parse at ingress. (That's a trust boundary leaking inward; the fix
  belongs at the edge — a boundary-discipline REFACTOR.)
- Guessing without a reproduction, or without capturing evidence.

## On confirmation — close the loop

A confirmed root cause produces two artifacts, both feeding the wider machine:

1. **A regression check** handed to `verify.md` — the bug becomes a permanent
   gating check so it can never reship. This is shift-left: a production-class
   failure pushed left into the gate.
2. **A capture for the knowledge ratchet** — if this is the *third* bug of the
   same shape, promote the pattern into durable guidance (a new boundary `scan`
   pattern, a lint rule, a reference note). Recurring bugs of one shape are
   evidence the substrate is missing a defense.

If the fix relocates a boundary (parse to ingress, effect to the rim, invariant
to the serialization point), run it as a **boundary-discipline REFACTOR** —
behavior-preserving, characterized first.
