---
name: feature-workflow
description: >-
  Apply whenever the task is to build, add, implement, or extend a FEATURE,
  endpoint, screen, flow, or job in an existing application — not a one-line
  fix. Enforces plan-before-code: a completed PLAN.md must pass the gate
  (scripts/plan_check.py) before any implementation begins. Drives the inner
  loop (compose this feature from the existing substrate, build only what's
  missing, place it via the boundary-discipline skill) and the outer loop (grow
  the reusable substrate via a promotion ratchet). Use this whenever someone
  says "build/add/implement X", "plan this feature", "how should I structure
  this feature", or is about to start writing feature code. Do NOT skip the gate
  because the feature "seems small"; the gate is what prevents duplication and
  entanglement. For a pure code review with no new feature, use
  boundary-discipline AUDIT mode directly instead.
---

# Feature Workflow

A machine for building features so the **marginal cost of feature N+1 slopes
down**: each feature composes more from what exists and builds less. It does
this by gating code behind a plan, composing from a reusable substrate (the
"shelf"), and growing that shelf on evidence.

This skill orchestrates; it **calls** the `boundary-discipline` skill (a sibling
skill — static placement of trust/effect/consistency/containment boundaries) at
the build and promote steps. Keep the two separate: this one decides *what to
build and what to reuse*; boundary-discipline decides *where each piece lives*.

## The failure modes this defends against

A capable model doesn't fail feature work from inability — it fails from
**momentum** (diving to code, trusting recall over checking the shelf) and
**drift** (re-deciding inconsistently across a long session). Those produce the
two ways feature cost slopes *up*: **duplication** (rebuilt what existed) and
**entanglement** (reused by coupling instead of composition). The gate beats
momentum; the externalized plan beats drift; the shelf-check kills duplication;
the seam-check kills entanglement.

## When to engage

- Building/extending a feature → **engage, gate first.**
- Pure audit / "is this robust" with no new feature → use `boundary-discipline`
  AUDIT directly; this skill is not needed.
- A genuine one-liner (typo, copy change, config bump) → no gate; just do it.
  (If unsure whether it's a one-liner, it isn't — gate it.)

## STEP 0 — Change-kind gate (the router; do this FIRST, always)

The loop is one spine; the **kind of change** determines the planning shape and
the test obligation, because each kind has a different dominant failure mode.
Classify by the **epistemic status of the existing behavior**, then route:

| Kind | Existing behavior | Dominant failure | Route to |
|---|---|---|---|
| **feature** | none — behavior is new | duplication / entanglement | this skill, STAGE 0 below |
| **refactor** | is the spec; preserve exactly | silent regression | `refactor-workflow` skill |
| **fix** | wrong in a bounded way | recurrence / neighbor break | `fix-workflow` skill |
| **spike** | approach itself unknown | committing to the wrong approach | `spike-workflow` skill |

The unifying law: **every kind contains an `unknown` that must be PARSED into a
trusted artifact — a test — before the change proceeds.** The test is the trust
boundary of the change loop; skipping it is proceeding on unparsed input, the
most serious violation in the model. Red-green *is* parse-then-proceed.

The sibling skills delegate back to the shared gate-runners here:
`change_new.py --kind <k>` scaffolds the kind's CHANGE manifest, `change_check.py
--kind <k>` gates it (fails closed on an undeclared obligation), and `verify.py`
enforces the obligation at ship. Only the planning shape and the parse artifact
differ per kind; the spine — gate → parse the unknown → build under the net →
verify the obligation → record/ratchet — is identical. The rest of this file is
the **feature** instance of that spine.

### Earned autonomy (capability-ledger)
Before the plan gate, consult `capability-ledger`'s `cap_check.py --class <c>` for
the problem class. The ledger tracks DEMONSTRATED, benchmark-proven competence and
returns what it licenses. If the class is **practiced** or **proven**, the PLAN
gate may auto-pass (proceed without plan confirmation) — but the verify gate and
human result-review still stand. If **proven**, the class may be delegated to a
sub-agent under the recorded playbook. This is how accumulated learning expands
blast radius: license is READ here, never written here (the loop cannot
self-license), it is earned only by measured near-floor outcomes, and it is
revoked instantly on a miss. A novice class always gets full gates.

## STAGE 0 — The gate (do this BEFORE writing any code)

This is the most important step and the one momentum will try to skip.

1. Scaffold the plan: `python scripts/plan_new.py --title "<feature name>"`
   (creates `PLAN.md` from `assets/PLAN.template.md`).
2. Fill sections 0–6. These are *judgment*, not paperwork — read
   `references/loop.md` (the six planning questions and why each exists) and
   `references/shelf.md` (the substrate model and the shelf-check). If a
   `boundary.config.json` exists, `plan_new` will have pre-filled section 3 with
   the real shelf inventory (via `shelf_index.py`) so the REUSE/EXTEND/BUILD
   classification is grounded in what actually exists rather than recalled. You
   still make the classification — the inventory only supplies the candidates.
3. Run the gate: `python scripts/plan_check.py PLAN.md`. It must **exit 0**
   before any implementation. A non-zero exit lists exactly which sections are
   unfilled — fill them, don't bypass them.

The plan is the workflow's trust boundary: establish ground truth once, then the
build phase gets to *assume* it. Code written before the gate passes is the
process equivalent of skipping the parse at ingress.

## STAGE 0.5 — Skeleton (interfaces before bodies)

The cheapest place to catch a conceptual error is the interface stage — concrete
enough to be wrong in checkable ways, abstract enough that fixing it is free
because no implementation exists yet. So before fleshing anything, write the
**skeleton**: the types, the boundary signatures, the port interfaces, and the
wiring, with bodies stubbed (`throw new Error("todo")` / `// ...`).

Two checks, both cheap:
- **It must typecheck.** A skeleton that compiles is proof the interfaces
  actually compose — a mechanical result prose can't give you. This is "make
  illegal states unrepresentable" verified at the type level before any logic.
- **Review the shape.** Run `python scripts/skeleton.py --feature <dir>` to derive
  the review view. It has four sections, each a boundary's face: **interfaces**
  (signatures, with trust/effect/sum-type tags as candidates), **schema** (the
  field shapes of the trust-boundary schemas — where "illegal states
  unrepresentable" is actually decided), **rules & invariants** (the spec), and
  **wiring** (how the units depend on each other). Judge it against the boundary
  model (boundary-discipline): is each boundary's signature its right kind (trust
  = `unknown → domain`; effects *injected* as ports, not returned)? Does the
  schema shape constrain illegal states (a sum type, not two optionals)? Does
  anything couple where it should compose?

This stage is also the **spec parse-point** — the one place the agent's guess
about *what you want* gets confirmed against ground truth (you), at the cheapest
ingress, before any bodies exist. So the rules section is the human-in-the-loop
surface. Invariants live **co-located** on the boundary they govern (a zod
`.refine` where the rule is schema-expressible; an `// @invariant: <rule>`
annotation where it's a claim not yet enforced), and the view classifies them:
- **established** — enforced in code already; confirmed; inherited by this feature
  with no re-work.
- **proposed** — an `@invariant` claim with no enforcement yet; the delta you
  adjudicate. Confirm it (it becomes an enforced refinement, co-located) or
  correct it (the cheapest possible place to catch a wrong rule).
- **blank** — a decision/trust boundary with no invariant is flagged; a blank is
  itself a review signal ("is there really no rule here?").

Each feature inherits the established invariants and asks you only about the
proposed delta, so spec-elicitation cost falls as the domain's spec-of-record
accumulates — the cost curve bending your attention, not just the code. When a
proposed invariant recurs or a near-miss proves it load-bearing, the
knowledge-ratchet promotes it left: annotation → enforced refinement → typed
contract.

This is "enforcement moves left" applied to the one stage that lacked a gate.
Fixing a wrong boundary here costs a signature edit; fixing it after the bodies
are written costs the bodies.

## STAGE 1 — Inner loop (build)

With a passing plan and a reviewed skeleton:

- **Compose first.** Implement every REUSE item by drawing it off the shelf and
  every EXTEND item by the smallest generalization that fits — before writing
  anything new.
- **Build only the BUILD items**, and for each, invoke `boundary-discipline`
  IMPLEMENT mode to place it in its correct home (trust at ingress, effects at
  the rim, invariants at the serialization point). Its scope guard already keeps
  implement-mode from drifting into a codebase audit — let it.
- **Hold scope.** You are building this feature, not improving the codebase. Any
  unrelated gap you notice goes in section 7 as "out of scope, for later" — not
  fixed now.

## STAGE 1.5 — The verify gate (BEFORE ship)

The inner feedback loop, and the structural twin of STAGE 0. The plan gate
manufactures trust before code; this manufactures trust before ship. Code that
hasn't passed verify is the process equivalent of data that hasn't been parsed
at ingress — do not let it cross into "shipped".

Run `python scripts/verify.py --repo <path>`. It runs the project's configured
checks (`verify` in `boundary.config.json`) and **fails closed**: it must exit 0
before STAGE 2. Two kinds of check:

- **Gating** (`must_pass: true`) — typecheck, tests, build. Objective; they
  block the ship.
- **Report-only** (`must_pass: false`) — e.g. the boundary-discipline scan,
  which surfaces candidates for judgment. They run and print but don't block;
  read them and decide if any is a real gap before shipping.

On failure the gate prints the failing check's output so you can act on it. That
output routes **back to STAGE 1 (build)** — generate, run, read the error, fix,
re-run verify. It does not route forward. A failing or unrunnable verify never
ships; "couldn't verify" is not "safe to ship".

For *what* checks a feature needs and *how* to construct them (per boundary, UI,
perf), and for debugging when the gate goes red, use the **verify-and-diagnose**
skill: its VERIFY mode produces the `verify[]` commands this gate runs, and its
DIAGNOSE mode finds the root cause of a failure. This gate is the runner; that
skill is the knowledge — they compose through `boundary.config.json`.

## STAGE 2 — Ship & record

Fill section 7 (**Shelf deposits**): what reusable units this feature added or
generalized, and where they live. Run `python scripts/plan_check.py PLAN.md
--stage post` to confirm the record is complete. This section is the input to
the outer loop.

## STAGE 3 — Outer loop (the ratchet — periodic, NOT per feature)

Grow the shelf on **evidence, not anticipation**. On the **third** occurrence of
a pattern (Rule of Three), promote a local unit to the shared substrate. Run
`python scripts/promote.py <unit> --symbol <name>` to check the candidate
mechanically — it counts uses (enforcing Rule of Three), checks single-concept,
flags feature-specific dependencies leaking through the interface, and checks
discoverability, then returns a verdict (READY / REVIEW / BLOCK). See
`references/shelf.md` for the criteria it encodes. Promotion itself is a
behavior-preserving relocation up the substrate — run it as a
`boundary-discipline` REFACTOR, not a rewrite.

Promoting a reused unit is one *kind* of friction. The general case — a recurring
scanner false-positive, a boundary misplaced the same way twice, a repeated
library decision — is owned by the **knowledge-ratchet** skill. At ship, log
friction with `ratchet.py --observe`; periodically run `ratchet.py --ripe` to see
what's owed a durable fix (defects fix on sight; abstractions wait for the Rule of
Three) and promote it to its leftmost durable home. `promote.py` is the
substrate-specific instrument; the ratchet is the general loop it feeds.

## Files

- `references/loop.md` — inner loop (6 planning questions) + outer loop (ratchet). Read during STAGE 0.
- `references/shelf.md` — substrate model, UI↔domain isomorphism, "definition of reusable". Read during STAGE 0.
- `assets/PLAN.template.md` — the plan artifact (the machine's interface).
- `assets/boundary.config.example.json` — copy to your repo root as
  `boundary.config.json`; maps substrate layers to directories. Read by the
  harness scripts (here and in boundary-discipline). All keys optional.
- `scripts/plan_new.py` — scaffold a PLAN.md from the template; if a config
  exists, pre-fills section 3 with the real shelf inventory (grounded shelf-check).
- `scripts/plan_check.py` — the gate: validate a PLAN.md is complete. Exit 0 = pass.
- `scripts/verify.py` — the verify gate (STAGE 1.5): run the project's configured
  checks and gate the ship. Fails closed; distinguishes gating from report-only
  checks. `python scripts/verify.py --repo <path>`.
- `scripts/shelf_index.py` — inventory the reusable substrate by layer; the
  anti-duplication ground truth behind the shelf-check. `python
  scripts/shelf_index.py --repo <path>`.
- `scripts/design_system.py` — generate the design-system catalog from the shelf
  (derive, don't hand-maintain); `--check` gates staleness. Conventions stay a
  ratchet-owned reference; the doc is the two composed.
- `scripts/promote.py` — run the outer-loop promotion checklist (Rule of Three +
  reusability criteria) on a local unit; reports blockers. Verdict drives exit
  code (0 READY / 1 REVIEW / 2 BLOCK) so it can gate a hook.

## Stack configuration

The harness scripts are general; the stack-specifics live in
`boundary.config.json` at your repo root (layer→directory globs, file
extensions, feature roots, verify checks). **Before the first feature, run the
`harness-setup` skill** — it detects your stack, proposes and validates the
config against your real repo (its doctor fails closed on a broken config), and
records it. Scripts fall back to sensible TS defaults if no config exists, but
an unvalidated config is how the shelf-check silently ungrounds — set it up
first. `assets/boundary.config.example.json` shows the shape.
