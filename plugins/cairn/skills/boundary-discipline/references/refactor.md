# Mode: REFACTOR

**Goal:** move a *known-misplaced* boundary to its correct home **without
changing behavior**. Refactor fixes structure; it does not add features (that's
`implement.md`) and does not survey the codebase (that's `audit.md`). It is the
natural follow-on when an audit found a `duplicated`, `leaked`, or `unsized`
boundary.

Read `references/model.md` first if you haven't.

## Scope discipline — ONE boundary at a time

Refactor exactly the boundary you were asked about (or the single finding you're
acting on). Do not turn it into a rewrite, and do not start auditing adjacent
code. If you discover a second misplacement, finish the first, then treat the
second as a new refactor.

## R1 — Name the misplacement precisely

Using the diagnostics table in `model.md`, pin down three things:
- **which boundary kind** (trust / effect / consistency / containment),
- **which direction it drifted** (too late / leaked inward / too deep / leaked
  outward / unsized), and
- **its target home** (the placement rule from `model.md`).

If you can't name all three, you're not ready to move it — go back to audit.

## R2 — Build the safety net FIRST

The whole point is correctness, so never move a boundary without a net.
Characterize current behavior with tests *before* touching anything — especially
the edge cases the misplaced check currently handles. These tests must stay
green through every step. (If the area is untestable as-is, that itself is the
first small refactor: introduce a seam, then characterize.)

## R3 — Move in the safe order for that boundary kind

**Trust too late (duplicated) / leaked inward:**
introduce the domain type + parse at ingress → then delete downstream re-checks
and inward `?.`/`!` guards *one at a time*, leaning on the type to show you what
breaks. The compiler is your worklist.

**Effect too deep (decide+act fused):**
extract the pure decision first (return a `Decision` value, touch nothing) →
leave the IO behind a port → verify the decision is now mockless-testable →
re-wire the shell to call decide-then-act.

**Decision leaked outward (rule in adapter/webhook):**
move the policy into the core → leave the adapter as pure translation only →
confirm the adapter no longer imports domain rules.

**Consistency unsized:**
- too small (tx spans two aggregates): widen the aggregate to cover the invariant.
- too big (unrelated writes contend): split along independent invariants.
- moving the guard: add the DB constraint/lock **first** (it becomes the new
  source of truth) → *then* delete the now-redundant application-level `if`.
  Never the reverse order, or you open a race window mid-refactor.

## R4 — Verify

- Characterization tests still green (behavior preserved).
- The moved boundary now satisfies **one unit, one epistemic status**.
- Re-run *only the relevant audit fingerprint* (`model.md`) to confirm the
  specific smell is gone — not a full audit.

State what moved, from where to where, and which diagnostic it resolved.
