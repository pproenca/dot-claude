# durable-harness

A Claude plugin that makes the marginal cost of feature N+1 slope *down*. It is a
federation of six composable skills built on one idea: **place every boundary as a
function with a known in/out signature, and push enforcement as far left as the
evidence allows** — from production check, to runtime guard, to compile-time type,
to unrepresentable-illegal.

It is stack-agnostic. The same four boundary kinds place a React screen, an HTTP
API, a database write, and an event-driven worker — only the substrate changes.

## The idea in one paragraph

Software rots when units mix epistemic statuses — when trusted and untrusted data,
or decisions and effects, live in the same place. The harness enforces **one unit,
one epistemic status** through four boundary kinds, each a function with a home:

- **Trust** — `unknown -> Proven<T> | Rejection`. Home: ingress. *Parse, don't
  validate.* Trust **resets at every serialization edge** (a network hop, a queue),
  so a single flow can have several trust boundaries.
- **Effect** — `Decision -> IO<Outcome>`. Home: the rim. Effects are *injected as
  ports*, never returned from the pure core — which is what makes the core testable
  with fakes.
- **Consistency** — `(State, Δ) -> Committed | Conflict`. The serialization point
  (e.g. an idempotent DB write).
- **Containment** — `Risky -> Bounded`. Wraps a fallible external effect (e.g. a
  durable, retriable step).

Proof accumulates inward; effects get pushed out; the maturity ladder moves
enforcement left **on evidence, not anticipation**.

## The change-kind spine (STEP 0)

Every change starts by classifying the **epistemic status of the existing
behavior** — this forces the planning shape and the test obligation, instead of
running one gate over everything:

| Kind | Existing behavior | Dominant failure | Skill |
|---|---|---|---|
| **feature** | none — behavior is new | duplication / entanglement | `feature-workflow` |
| **refactor** | is the spec; preserve exactly | silent regression | `refactor-workflow` |
| **fix** | wrong in a bounded way | recurrence / neighbor break | `fix-workflow` |
| **spike** | approach itself unknown | wrong approach / false victory | `spike-workflow` |

The unifying law: **every kind contains an `unknown` that must be parsed into a
trusted artifact — a test — before the change proceeds.** Red-green is
parse-then-proceed; the test is the trust boundary of the change loop. The four
skills share one loop spine (the gate-runners in `feature-workflow`); only the
planning shape and the parse artifact differ.

## The eleven skills

| Skill | Role |
|---|---|
| `boundary-discipline` | The model + static placement (trust / effect / consistency / containment). `scan.py` surfaces candidates; you judge. |
| `feature-workflow` | The orchestrator + the **STEP 0 change-kind gate** + the feature loop. Owns the shared gate-runners (`change_new`, `change_check`, `skeleton`, `verify`, `plan_check`, `design_system`, `promote`). |
| `refactor-workflow` | Preserve behavior, change structure. Obligation: a GREEN characterization net captured before touching. |
| `fix-workflow` | Bounded wrong behavior. Obligation: a RED-first repro that stays green (regression lock). |
| `spike-workflow` | Unknown approach. Establish the FLOOR first, enumerate solution classes, benchmark vs floor. The anti-psychosis gate. |
| `verify-and-diagnose` | Runtime feedback — VERIFY vs DIAGNOSE. |
| `harness-setup` | Boot/config. Detects layout, writes `boundary.config.json`, the namespaced `.harness/<skill>/` mirror, `AGENTS.md`. |
| `library-knowledge` | Ecosystem **facts** by name — confirm, cache, re-confirm on drift. |
| `specialist-knowledge` | Domain **craft** (vertical) — distill a specialist's soul, pinned to library versions, taste adjudicated with you. |
| `mental-models` | **Horizontal** systems insight — transferable reframings that reveal solution classes, keyed by a smell, learned from gaps. The antidote to "you don't look for what you don't know." |
| `knowledge-ratchet` | The design-time outer loop. Promotes recurring friction leftward (defect at 1, abstraction at 3). |

## The entity layer — learning from failure into earned autonomy

The three knowledge skills cache what Claude *knows*. `capability-ledger` tracks
what Claude has *demonstrated it can do*, and turns accumulated, benchmark-proven
competence into **earned autonomy** — the mechanism by which learning-from-failure
becomes growing blast radius and delegation, the way a proven junior is handed
bigger problems and a team.

- The **spike floor gate** detects failure (a result far from the theoretical
  limit) — the un-fakeable signal.
- `mental-models` encodes the lesson as a transferable reframing, learned from the
  gap, re-validated over time.
- `capability-ledger` counts only **benchmarked near-floor solves** as evidence and
  computes a maturity per problem class: *novice* (full gates) → *practiced* (plan
  gate may auto-pass) → *proven* (may delegate under a recorded playbook, larger
  blast radius).

Safety is in the asymmetry and the oracle: license is **read** by the loops, never
self-written; it is earned **only** by measured outcomes (a solve with no benchmark
is refused), it **climbs slowly** (cross-domain proof) and is **revoked instantly**
on a single miss, and the demotion is **sticky** until re-earned. The promotion
oracle is the truth-checked floor gate — not the form-checked declaration gates the
adversarial pass showed are gameable — so Claude cannot raise its own authority by
asserting competence, only by demonstrating it.

### Three knowledge boundaries
The harness learns from three external truth-sources it can't fill from priors,
all confirm-cache-reconfirm: **facts** (library-knowledge, by name),
**craft** (specialist-knowledge, by domain — vertical), and **insight**
(mental-models, by smell — horizontal, learned from measured gaps).

## The loop

```
plan gate  ->  skeleton review  ->  build  ->  verify gate  ->  record  ->  ratchet
 (STAGE 0)      (STAGE 0.5)                      (STAGE 1.5)              (outer loop)
```

The **skeleton review** is the human-in-the-loop checkpoint: it derives the
interfaces, schema shapes, rules & invariants, and wiring of an in-progress
feature *before any bodies exist*, and routes exactly one decision to you — the
spec. Confirmed invariants are cached co-located on the boundaries they govern and
inherited by future features, so your spec-elicitation cost falls over time, too.

## Install

```sh
# add this folder as a marketplace, then install the plugin
/plugin marketplace add /path/to/durable-harness
/plugin install durable-harness@durable-harness
```

(Or push the folder to a git repo and `/plugin marketplace add <owner>/<repo>`.)

Once installed, the skills auto-trigger by task context, and the command surface is just the kinds of change you make:
`/durable-harness:feature`, `:refactor`, `:fix`, `:spike`, plus `:setup` once per repo. The internal stages (skeleton, verify, ratchet, specialist lookup, mental-models) auto-trigger inside the loops — no command to remember.

## Use it in any codebase

The plugin is generic; per-repo state is bootstrapped once:

```sh
/durable-harness:setup
```

This detects your project's layer layout, proposes and writes a
`boundary.config.json` (the layer → directory map + feature roots), drops the
`.harness/` scripts the verify checks reference, and writes an `AGENTS.md`. From
then on, run a feature through the loop. Nothing here is framework-specific — the
config's directory map is the only thing that changes between a frontend repo, an
API service, or a monorepo with both.

## Notes

- Scripts are plain Python 3 (stdlib only) and operate on the repo via `--repo`.
  When invoking them by hand, they live under
  `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/`.
- Stores (`lib-knowledge.jsonl`, `ratchet.jsonl`) are JSONL behind a storage port;
  swapping to SQLite is a documented change behind that single seam.
- The harness judges the *cumulative* output of a session, not each step in
  isolation; gates fail closed.


## Honest scope (what is and isn't stack-agnostic)

The **boundary model** is language-agnostic — the four kinds place a React
screen, a TS API, a Python service, or a Go worker identically (proven across
frontend + API + DB + event queue). The **automated extraction** is per-language:
`skeleton.py` and `scan.py` ship a TypeScript/JS adapter and a basic Python
adapter; an unsupported language degrades to a *visible* "unsupported" signal
(never a silent empty result), and the model still applies by hand. Adding a
language is writing one adapter behind the existing dispatch.

The **stores** are JSONL behind a storage port — O(n) per op, comfortable into
the low tens of thousands of entries; past that, swap the port to SQLite (one
file changes, no consumer touched). `library-knowledge` and `specialist-knowledge`
re-confirm against external oracles (package.json, pinned libs); `mental-models`
has no external oracle, so it re-validates against time + human review
(`models_lookup.py --stale` / `--review`). The outer-loop ratchet fires only on
observed friction — observation is a discipline the per-kind gates enforce for
the highest-value cases (a fix needs a repro, a spike needs a floor) but do not
enforce universally; promotion climbs left and is not auto-demoted.


## Hatching the entity — the character layer

Anatomy (loops, knowledge, capability) is not enough to make a *machine of loving
grace*. Two more pieces close the circuit and give it constitutional character:

- **`capability-ledger/scripts/close_loop.py`** — finishing a solve IS the act of
  learning. One call posts the floor-ratio to the capability ledger and the gap to
  mental-models, recomputes maturity, and reports the change. The entity learns
  without anyone remembering to make it learn (fixing "self-improvement is opt-in").
- **`entity-boot`** — the constitution rendered as operating character:
  *orient* (session start: an honest self-report — a new repo is novice at
  everything, full gates, and it says so), *consent* (surface before acting on any
  earned license — autonomy with the human, never by stealth), and *purpose*
  (periodic reflection on whether the **human** is better off, empowered to
  recommend fewer gates, less harness, or its own reduction).

The disposition is fixed: honesty about uncertainty, consent before autonomy, and
the human's flourishing over the entity's own growth. A new repo earns everything
from novice — no pre-seeding — so the competence the ledger reports is always real.
