---
name: verify-and-diagnose
description: >-
  Apply when verifying that a feature works at runtime or debugging why it
  doesn't. Two modes: VERIFY (confirmatory — decide what checks a feature needs
  and construct them: typecheck, unit, integration, concurrency, browser/e2e,
  accessibility, performance budgets) and DIAGNOSE (investigative — find the
  root cause of a failure, regression, flaky test, or performance problem using
  browser automation, React and Chrome devtools, logs, network inspection, and
  profiling). Use this whenever a test or the verify gate fails, when something
  renders or behaves wrong, when chasing a slow or intermittent bug, or when
  deciding which checks to add. The verify-gate runner
  (feature-workflow/scripts/verify.py) executes checks; this skill is the
  knowledge of what to check and how to debug. Pick the mode before starting:
  confirming "does it meet spec" is VERIFY, investigating "why doesn't it" is
  DIAGNOSE.
---

# Verify and Diagnose

The runtime feedback loop. The whole build discipline is worthless if you can't
tell whether what you built works, and can't find out why when it doesn't. This
skill is the two halves of that: **confirm** (verify) and **investigate**
(diagnose). Both stand on observation.

It composes with the rest of the system. The verify *gate* lives in
`feature-workflow` (STAGE 1.5) and runs commands from `boundary.config.json`'s
`verify[]`; this skill is the knowledge of *what those commands should be* and
*how to debug when they go red*. The interface is config — no code coupling.
The boundary-discipline model is used here as a map: it tells you what to verify
and where bugs live.

## STEP 0 — Pick the mode

| If you are… | Mode | File |
|---|---|---|
| confirming a feature meets spec; deciding/constructing checks; setting up the gate | **VERIFY** | `references/verify.md` |
| finding why something fails, regressed, is flaky, or is slow | **DIAGNOSE** | `references/diagnose.md` |

Decision rule: **confirming → VERIFY. investigating → DIAGNOSE.** They differ in
shape — verify is binary, repeatable, gate-shaped; diagnose is open-ended,
hypothesis-driven, search-shaped. They share tooling and hand off constantly
(verify fails → diagnose → fix → verify), which is why they're one skill.

Then read `references/observe.md` once (the shared observation surfaces), and
follow your mode file.

## When to engage

- Building a feature and deciding what proves it works → **VERIFY** (the checks
  feed the gate).
- The verify gate or a test failed; something misbehaves → **DIAGNOSE**.
- Pure static placement of boundaries (no running system) → that's
  `boundary-discipline`, not this skill.

## The handoff back to the machine

A confirmed root cause should leave two deposits: a **regression check** added
to the gate (shift-left — the bug can't reship) and, on the third bug of one
shape, a **capture for the knowledge ratchet** (a new scan pattern / lint rule /
reference). A fix that moves a boundary is a **boundary-discipline REFACTOR**.

## Files

- `references/observe.md` — shared: how to observe a running system (browser,
  devtools, network, logs, profiler) + the boundary signals. Read once per task.
- `references/verify.md` — confirmatory mode: construct gate-worthy checks,
  grounded in the boundary model and shift-left.
- `references/diagnose.md` — investigative mode: hypothesis-driven debugging with
  the boundary model as a localization map.

## Note on the outer loop

`observe.md` is written so its surfaces have production analogs (RUM, traces,
log aggregation, error tracking). The future production-telemetry skill is the
*same observation reference pointed at prod* — this skill is the foundation for
the outer feedback loop, not only the inner one.
