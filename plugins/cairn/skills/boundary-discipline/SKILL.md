---
name: boundary-discipline
description: >-
  Apply when working on software robustness through "boundaries" — the points
  where data changes status (untrusted→proven, decided→done,
  proposed→authoritative, risky→bounded). THREE MODES: AUDIT (find undefended or
  misplaced boundaries in existing code and report them), IMPLEMENT (place
  boundaries correctly while building a NEW feature/endpoint/handler/job), and
  REFACTOR (relocate a known-misplaced boundary, behavior-preserving). Use this
  whenever the task touches request/queue/webhook handlers, parsing or
  validation, side effects (DB writes, payments, email, external APIs),
  transactions or race conditions, or any "where should this
  validation/check/effect/lock live" question — and whenever someone wants to
  make invalid states unrepresentable or shrink a blast radius. Select the mode
  BEFORE doing anything; do NOT audit the codebase when the task is to build a
  feature.
---

# Boundary Discipline

A robust system is built from **boundaries**: places where data changes its
*epistemic status*. Inside a boundary you **assume**; crossing it you
**verify**. The discipline has one law and four boundary kinds — but the *work*
splits three ways, and picking the right one is the first and most important
step.

## STEP 0 — Pick the mode (do this before anything else)

| If the task is… | Mode | File |
|---|---|---|
| assess / review / "find problems" / "is this robust" / "where are the risks" in **code that exists** | **AUDIT** | `references/audit.md` |
| add / build / create / implement a feature, endpoint, handler, or job that **doesn't exist yet** | **IMPLEMENT** | `references/implement.md` |
| move / extract / clean up / "this is duplicated" / fix a **known-misplaced** boundary, behavior-preserving | **REFACTOR** | `references/refactor.md` |

Decision rule: **building something new → IMPLEMENT. Reporting on what exists →
AUDIT. Restructuring what exists without changing behavior → REFACTOR.**

**Anti-pattern to avoid (the reason these are separate):** when the task is to
*build a feature*, do NOT first audit the surrounding codebase. Implement mode
scopes to the new code's own pipeline and only touches boundaries that code
directly crosses. A feature request is not an audit request — mixing them
balloons scope and buries the work. The modes hand off explicitly instead: an
audit *reports* a misplaced boundary; fixing it is a separate refactor.

Then read `references/model.md` once (the shared vocabulary), and follow your
chosen mode file.

## The one law (always keep in mind)

**One unit, one epistemic status.** A function/module operates *entirely* on
data of one status: it parses untrusted input OR works on proven data; it
decides OR acts; it owns exactly one invariant's atomicity. Every misplaced
boundary is a unit straddling two statuses — the boundary living *inside* the
unit instead of *around* it. (Single-responsibility, in terms of data status.)

## The four boundaries (one line each — full reference in model.md)

- **Trust** `unknown → Proven<T> | Rejection` — parse untrusted input into a
  domain type. Home: earliest point (ingress). Fingerprint: input you didn't
  construct (`req.body`, `JSON.parse`, env, DB reads).
- **Effect** `Decision → IO<Outcome>` — turn a pure decision into a side effect.
  Home: latest point (rim). Fingerprint: `await`, `fetch`, fs, DB writes, clocks, randomness.
- **Consistency** `(State, Δ) → Committed | Conflict` — arbitrate concurrent
  writes against an invariant. Home: the serialization point (constraint/lock).
  Fingerprint: read-then-write, check-then-act.
- **Containment** `Risky → Bounded` — bound the failure of a risky call. Home:
  wrapping the effect boundary. Fingerprint: un-timed network/IO, shared pools.

Trust pushed inward + effects pushed outward = the pure **functional core** in
between. Structure is **fractal**: trust resets at every process edge, so every
service re-parses at its own ingress.

## Files

- `references/model.md` — shared reference: signatures, flow rules, concept
  families, misplacement diagnostics, maturity ladder. Read once per task.
- `references/audit.md` — find & report gaps in existing code.
- `references/implement.md` — place boundaries in new code (with scope guard).
- `references/refactor.md` — relocate a misplaced boundary, behavior-preserving.
- `scripts/scan.py` — mechanizes the AUDIT fingerprints into triage candidates
  (grouped by boundary, with hotspots). Run it at the start of an audit to find
  candidates fast, then classify each by hand against `audit.md` — the script
  surfaces, the model judges. Config-driven (`boundary.config.json`) with TS
  defaults, so it runs zero-config: `python scripts/scan.py <path>`.
