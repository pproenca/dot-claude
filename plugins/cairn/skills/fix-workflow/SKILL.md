---
name: fix-workflow
description: >-
  Apply when existing behavior is WRONG in a bounded, specific way and must
  change in one place — a bug, defect, incorrect output, off-by-one, mishandled
  edge case, regression. Use this whenever the task is "fix the bug where...",
  "X is broken", "wrong result when...", "handle this edge case". The dominant
  failure mode is RECURRENCE (the bug comes back) or breaking a NEIGHBOR, so the
  rule is: write a FAILING repro test that captures the bug (RED) BEFORE the fix,
  make it pass (GREEN), and leave it as a permanent regression lock. This is the
  fix instance of the one-spine change loop in feature-workflow; it delegates to
  that skill's change_new.py/change_check.py/verify.py with --kind fix. Do NOT
  use for new behavior (feature-workflow), behavior-preserving restructuring
  (refactor-workflow), or approach-unknown problems (spike-workflow). If a "fix"
  keeps growing in scope, it is a feature or a refactor — reclassify at STEP 0.
---

# Fix Workflow

Change wrong behavior to right, in one place. The bug is `unknown` — you
*believe* it is broken in way Y — until a **failing repro test** proves it. RED
first is the parse: it demonstrates the test actually captures the bug. GREEN is
the fix. The test stays as a regression lock so the bug cannot recur silently.

## The loop (the feature-workflow spine, fix instance)
1. **STEP 0 classified this as a fix.** `change_new.py --kind fix --name "..."`.
2. **Parse the unknown:** write the repro test and watch it FAIL for the right
   reason. A repro that does not fail first is not a repro. (See
   `references/repro.md`.)
3. **Gate:** `change_check.py --kind fix <manifest>` — blocks until the RED repro
   is declared.
4. **Find the root cause, fix at the right home** — the boundary that owns the
   invariant, not the symptom site. Patching downstream of the real cause is how
   one bug becomes three.
5. **Verify obligation:** repro RED → GREEN and stays green; full suite still
   green (no neighbor broken). `verify.py` gates ship.
6. **Record/ratchet:** a bug shipped without a regression test is friction RIPE
   AT ONE OCCURRENCE — the `knowledge-ratchet` promotes the missing-test habit
   into a gate.

## The one law here
A fix changes the smallest set that makes the repro pass at the right home, and
nothing else. Scope creep means a misclassification — reclassify, don't smuggle.

## Files
- `references/repro.md` — how to write a repro that fails for the right reason.
