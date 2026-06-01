# Observing a Running System (shared reference)

Read this once per task, then return to your mode file (`verify.md` or
`diagnose.md`). You cannot confirm what you cannot observe, and you cannot
diagnose what you cannot reproduce and watch. Both modes stand on the same
observation surfaces; only the intent differs (confirm vs investigate).

## The principle

A running system emits signal across a fixed set of **surfaces**. Verification
asserts on those signals; diagnosis reads them. The discipline is the same in
both: **observe before you change.** Guessing-then-editing is the dominant
failure mode — it mutates the system before you've read it, destroying the
evidence. Look first.

## The observation surfaces

Each surface has a dev tool and a production analog. The analogs matter: this
reference is the foundation for the future production-telemetry skill — the
*same surfaces, observed remotely*. Inner loop watches localhost; outer loop
watches prod.

| Surface | What it shows | Dev tool | Prod analog |
|---|---|---|---|
| **Rendered UI / interaction** | what the user actually sees and does | browser + automation (Playwright/Puppeteer) | RUM, session replay |
| **Component / render state** | props, state, re-render counts, render cost | React DevTools (+ Profiler) | (mostly dev-only) |
| **Network** | requests, payloads, status, timing, waterfall | devtools Network panel / proxy | distributed traces (APM) |
| **Logs** | what the code reports it's doing | app logs, console, server stdout | log aggregation |
| **Runtime performance** | CPU, allocation, flamegraphs, memory | profiler, heap snapshots | APM, perf monitoring |
| **Errors / exceptions** | failures + stack traces (source-mapped) | console errors, debugger | error tracking |

Prefer **structured** signal over unstructured: a log line with fields you can
filter beats prose; an assertion on a value beats eyeballing a screenshot.

## The boundary signals (what each boundary looks like when observed)

The boundary model (see the boundary-discipline skill) is also an observation
map — each boundary has a characteristic signature on these surfaces:

- **Trust**: at ingress, a rejected parse should be *visible* (a logged 400 with
  the reason), and valid input should become a domain type. If garbage reaches
  the core, the trust signal was missing.
- **Effect**: an effect should be observable as a single, idempotent action on
  the network/log surface (one charge per key, even on retry). Repeated or
  missing effects show here.
- **Consistency**: a conflict at the serialization point should surface as a
  rejected write / constraint violation, not a silent double-commit.
- **Containment**: a failing dependency should surface as a bounded local error
  (timeout, open circuit) — not a hang that spreads.

## Discipline

- **Reproduce minimally.** Reduce to the smallest input/state that still shows
  the behavior. A minimal repro is both the verification fixture and the
  diagnostic starting point.
- **Capture, don't recall.** Save the screenshot, the trace, the log slice, the
  failing seed. Memory is lossy; evidence is not.
- **Change one variable.** Whether asserting or hypothesizing, isolate a single
  factor so the signal is attributable.
- **Determinism is the precondition.** Pin clocks, seeds, and IO at the effect
  boundary so the same input gives the same observation. Nondeterminism makes
  both verification (flaky checks) and diagnosis (un-reproducible bugs)
  impossible — it's the same root problem wearing two masks.
