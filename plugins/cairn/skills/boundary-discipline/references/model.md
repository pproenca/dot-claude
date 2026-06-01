# The Boundary Model (shared reference)

Read this once per task, then return to your mode file (`audit.md`,
`implement.md`, or `refactor.md`). Everything below is mode-independent
vocabulary — the modes are just three different things you *do* with it.

## What a boundary is

A boundary is a place where data changes its **epistemic status**:
untrusted→proven, decided→done, proposed→authoritative, risky→bounded. Inside a
boundary you **assume**; crossing it you **verify**. Robustness = put the checks
at the boundaries and make the interior as large, pure, and assumption-rich as
possible.

**The one law — one unit, one epistemic status.** A function/module operates
*entirely* on data of one status: it parses untrusted input OR works on proven
data; it decides OR acts; it owns exactly one invariant's atomicity. Every
misplacement is a unit straddling two statuses — the boundary is living *inside*
the unit instead of *around* it. (This is single-responsibility expressed in
data status.)

## The four boundary kinds

Each is a function with an in/out signature. The signature is what makes
placement decidable: **one boundary's output is the input the next is allowed to
assume.**

| Boundary | Signature (in → out) | Manufactures | Physical fingerprint | Home | Push |
|---|---|---|---|---|---|
| **Trust** | `unknown → Proven<T> \| Rejection` | trust, by narrowing | input you didn't construct: `req.body`, `JSON.parse`, env, file/queue/webhook payloads, **DB reads** | earliest point (ingress) | **in** |
| **Effect** | `Decision → IO<Outcome>` | contact with reality + its uncertainty | non-determinism: `await`, `fetch`, fs, DB writes, `Date.now()`, `Math.random()` | latest point (rim) | **out** |
| **Consistency** | `(State, Δ) → Committed<State'> \| Conflict` | arbitration of concurrent writes | read-then-write, check-then-act, count-against-limit, must-sum-to | the serialization point (DB constraint / lock / append), scoped to exactly one invariant | at the write |
| **Containment** | `Risky → Bounded<Risky>` (wrapper) | bounded failure (changes failure-form, not data) | network/IO call with no timeout; shared pool | wrapping the effect boundary | one-way, outward |

Trust pushed inward + effects pushed outward ⇒ the gap between them **is** the
pure, authoritative **functional core**.

## Why each home (the placement reasons)

- **Trust → earliest.** Trust is monotonic inward and erased by serialization,
  so the edge is the only point both necessary and sufficient. Every un-parsed
  line before first use is forced to defend itself; parse at entry and zero
  interior lines defend.
- **Effect → latest.** Blast radius and testability scale with core size, so
  push effects out to maximize the pure core.
- **Consistency → serialization point.** Only it sees every concurrent writer,
  so the verdict is uncomputable upstream. And the invariant *defines* the
  aggregate, not the reverse — find the invariant, let it draw the boundary
  around exactly the data it constrains.
- **Containment → around the effect boundary.** The only thing that turns an
  unbounded cascade into a local, known failure.

## Flow rules (what propagates, what walls)

- **Proof accumulates inward, monotonic — within one process.** Parse once at
  ingress; the core never re-checks. Forced pipeline: `ingress → decision → commit`.
- **Trust resets to zero at every serialization edge — hard wall.**
  Serialization erases the type; a value proven upstream arrives as `unknown`.
  "Validated on the client / upstream service" is a category error. This is why
  the structure is **fractal**: every process re-establishes trust at its own
  ingress.
- **The world's uncertainty does not flow inward.** Outcome returns as data; the
  provider's *model* is converted at the anti-corruption layer, never leaks past.
- **Concurrency verdicts don't flow outward as guarantees.** "It looked free" is
  a belief, not a proof; only the serialization point's verdict is authoritative.
- **Effects flow out and don't return.** No type-level retraction once the
  charge/email fires — compensation is a *forward* correcting effect, not a rollback.

## Concept families (slot a new technique into a known boundary)

- **Trust:** parse-don't-validate · value objects / smart constructors · make-illegal-states-unrepresentable (sum types over flag-soup) · newtype/branded types (don't mix `PatientId` & `ClinicId`) · total functions (return `Result`/`Option`, don't throw) · be *strict* in what you accept.
- **Effect:** functional-core/imperative-shell · command-query separation · dependency inversion / ports & adapters / hexagonal · idempotency keys · anti-corruption layer · sagas / compensating transactions · explicit effects in the signature.
- **Consistency:** aggregate (one tx = one aggregate) · invariant-at-serialization-point · optimistic/pessimistic lock · event sourcing · transactional outbox · CQRS.
- **Containment:** fail-fast (crash at boot on bad config) · bulkhead · circuit breaker · timeout · backpressure · let-it-crash + supervision.

Load-bearing concepts straddle two boundaries (idempotency = effect+consistency;
anti-corruption = trust+effect; typed state machine = trust+consistency). These
are highest-leverage — identify them first.

## Misplacement diagnostics (used by audit to classify, by refactor to target)

Two symptoms, and which one tells you the direction it drifted.

| Symptom | Means | Drifted | Fix (see refactor.md) |
|---|---|---|---|
| Same field validated in 2+ places | trust boundary too **late** | downstream | parse once at ingress; delete the rest |
| `?.`/`!`/null-guards in the domain core | untrusted-ness **leaked inward** | parse missing at edge | move parse to ingress |
| Must mock the world to test a *rule* | effect boundary too **deep** (decide+act fused) | inward | split decision (pure) from action (IO) |
| Domain rule lives in a webhook/adapter | decision **leaked outward** into the shell | outward | move policy to core; adapter only translates |
| One tx must touch two aggregates | consistency boundary drawn **through** an invariant | too small | enlarge aggregate to span the invariant |
| Unrelated writes block on one aggregate | aggregate too **big** (>1 reason to change) | too large | split along independent invariants |

## Maturity ladder (assess + target)

Maturity = how far **left** the *enforcement* sits, not how many boundaries exist.

- **L0 Implicit** — boundaries exist physically but undefended; scattered `if`s + hope.
- **L1 Runtime-checked at edges** — parse at main ingresses, some effect split, key invariants on DB constraints; enforced by review convention.
- **L2 Correct by construction** — domain types that can't hold invalid state; functional-core/imperative-shell is the real structure; aggregates drawn around invariants; idempotent effects. Boundaries are *types*, not conventions.
- **L3 Compiler-enforced** — effects in signatures; core only accepts `Proven<T>` so undefended data won't compile; outbox + conflict handling on the consistency edge. The wrong thing fails to build.
- **L4 Fractal + automated** — every process repeats edge→core→egress; new code has an obvious home; violations caught by lint/CI/types. Placement questions answer themselves.

Target: move each boundary's *discovery-of-violation* leftward —
production → runtime → compile-time → unrepresentable.
