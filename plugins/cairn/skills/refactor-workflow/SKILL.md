---
name: refactor-workflow
description: >-
  Apply when changing the STRUCTURE of code while preserving its observable
  behavior exactly — extracting a unit, renaming, reshaping a module, splitting
  a god-function, moving a boundary, detangling coupling. Use this whenever the
  task is "refactor X", "clean up", "extract", "restructure", "detangle", or
  "preserve behavior but change how it is organized". The dominant failure mode
  is SILENT REGRESSION, so the rule is: capture a GREEN characterization net
  that pins current behavior BEFORE touching anything, change under that net, and
  prove behavior is identical after. This is the refactor instance of the
  one-spine change loop in feature-workflow; it delegates to that skill's
  change_new.py/change_check.py/verify.py gate-runners with --kind refactor. Do
  NOT use for new behavior (feature-workflow), bug fixes (fix-workflow), or
  approach-unknown problems (spike-workflow). For a boundary-level refactor, use
  boundary-discipline REFACTOR mode as the tool inside this loop.
---

# Refactor Workflow

Change structure; preserve behavior **exactly**. The existing behavior *is* the
spec — but it is `unknown` until proven, because you *believe* it does X without
having pinned it. So the parse is a **characterization test net**, captured
GREEN before any edit. Refactoring without it is editing on unparsed input.

## The loop (the feature-workflow spine, refactor instance)
1. **STEP 0 already classified this as a refactor.** Scaffold the manifest:
   `change_new.py --kind refactor --name "..."`.
2. **Parse the unknown (STAGE 0.5 equivalent):** capture characterization tests
   that pin the *current* observable behavior and run them GREEN. If you cannot
   make them green first, you do not yet understand the behavior you are about to
   preserve — stop. (See `references/characterize.md`.)
3. **Gate:** `change_check.py --kind refactor <manifest>` — blocks until the net
   is declared.
4. **Change under the net**, one behavior-preserving move at a time. A boundary
   move → use `boundary-discipline` REFACTOR mode.
5. **Verify obligation:** the same net is GREEN after, behavior identical, no new
   behavior added. `verify.py` gates ship.
6. **Record/ratchet:** a refactor that paid down real coupling is shelf signal;
   a near-regression the net caught is a `knowledge-ratchet` observation.

## The one law here
A refactor changes exactly one thing — *structure* — and holds *behavior*
invariant. If behavior must change too, it is not a refactor: split it into a
refactor (under the net) plus a feature or fix (its own loop).

## Files
- `references/characterize.md` — how to capture a behavior-pinning net cheaply.
