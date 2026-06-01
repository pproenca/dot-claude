# Mode: VERIFY

**Goal:** construct the checks that *prove* a feature meets spec, and run them.
This is confirmatory — binary, repeatable, gate-shaped. The output is a set of
command strings that live in `boundary.config.json`'s `verify[]` array; the
verify gate (`feature-workflow/scripts/verify.py`) executes them at STAGE 1.5.
This skill supplies the *what and how*; the gate supplies the *run and block*.

Read `references/observe.md` first if you haven't. When a check fails, switch to
`diagnose.md` — confirming and investigating are different jobs.

## What makes a check gate-worthy

- **Deterministic** — pinned clock/seed/IO; no flake. A flaky check is worse
  than no check: it trains everyone to ignore red.
- **Hermetic** — no order dependence, no shared mutable state between checks.
- **One concept** — asserts one behavior, names it clearly.
- **Fast-first** — cheap checks ordered before slow ones so the gate fails early.
- **Gating vs report-only** — objective+deterministic ⇒ `must_pass: true`
  (typecheck, unit, integration). Slow or judgment-laden ⇒ `must_pass: false`
  (visual regression, perf trend, the boundary scan): they inform, don't block.

## Push the check as far left as it goes (shift-left)

The cheapest verification is the one you don't have to run. Before writing a
test, ask whether a **type** could make the failure unrepresentable instead — a
compile error beats a unit test beats an integration test beats an e2e test, in
both speed and reliability. Write the test for what the type can't prove.

## What to verify, by boundary

The boundary model doubles as the verification checklist — each boundary has a
characteristic check:

- **Trust** — invalid input is rejected at ingress; valid input parses to the
  domain type. (unit/integration on the parser)
- **Decision** — the pure rule, exhaustively, with **zero mocks**. Cheapest and
  highest-value: if the core is pure, this is a fast unit test covering the real
  logic. Spend most of your assertions here.
- **Consistency** — the invariant holds **under concurrency**. This is the check
  unit tests structurally miss: fire two conflicting writes and assert exactly
  one wins (the double-booking / double-refund test). Integration-level.
- **Effect** — the port is invoked with the right command, and idempotency holds
  (same key twice ⇒ one effect). Contract/integration test against a fake or
  recorded adapter.
- **Containment** — inject a dependency failure/timeout and assert the system
  degrades to a bounded local error rather than hanging or cascading.

## What to verify, UI

- **Renders + interacts** — mounts without error; key user flows complete
  (browser automation / e2e via `observe.md`'s UI surface).
- **Accessibility** — automated axe-style checks (often gating; cheap).
- **Visual regression** — screenshot diff (usually report-only — needs human
  judgment on intentional changes).
- **Performance budget** — bundle size, render counts, LCP/INP against a budget.
  Gating if you have a hard budget; report-only if you're tracking a trend.

## Output

Emit the checks as `verify[]` entries, e.g.:
`{ "name": "consistency-double-book", "cmd": "npm run test:int -- slot.concurrent", "must_pass": true }`.
Order cheap→expensive. Keep gating checks objective; route the judgment ones to
report-only. Then the gate runs them; a failure hands off to `diagnose.md`, and
a *newly discovered* failure mode should come back here as a permanent check
(shift-left: every fixed bug earns a regression check so it can never reship).
