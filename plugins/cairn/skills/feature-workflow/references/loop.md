# The Two Loops

Read during STAGE 0. The **inner loop** builds *this* feature by composing from
the substrate and depositing reusable parts back. The **outer loop** tends the
substrate so its inventory grows in reusability over time. They share one goal:
keep the marginal cost of feature N+1 sloping **down**.

Each question below is tagged with the failure mode it prevents — **Dup**
(duplication: rebuilt what existed) or **Ent** (entanglement: reused by coupling
instead of composition).

## Inner loop — the six planning questions (fill PLAN.md sections 1–6)

These run *before* code. Answering them upfront is what converts "be careful"
into a forced, checkable plan.

### 1. Boundary decomposition (Ent)
What does this feature cross? Run the `boundary-discipline` model over it: which
**ingresses** (trust), which pure **decisions**, which **invariants**
(consistency), which **effects**. This gives the feature its shape before any
implementation — and it reuses the method we already have. A feature you can't
decompose into boundaries you don't yet understand well enough to build.

### 2. Bill of materials (Dup)
For each crossing, list the concrete units needed. UI: which components, which
tokens, which patterns. Domain: which value objects, which aggregate, which
port. Be specific enough that the next step can check each against the shelf — a
vague BOM produces a useless shelf-check.

### 3. Shelf check — classify every item (Dup)
For each item in the BOM, decide: **REUSE** (internal, exists, fits — take it
as-is), **EXTEND** (internal, exists, needs a small generalization), **VENDOR**
(an external library already solves this — reuse its capability), or **BUILD**
(nothing solves it — write it). This is the direct defense against duplication:
*you cannot reuse what you did not check for.* Reason over the actual repo (or
the shelf index).

**VENDOR outranks BUILD — check the ecosystem before hand-rolling.** Before
writing anything bespoke, ask "is this a solved problem someone maintains?" —
runtime validation, date math, state machines, crypto are almost always VENDOR,
not BUILD (hand-rolling a parser instead of using a validation library is the
classic miss). Consult the `library-knowledge` skill for the capability and the
*confirmed current* API before reaching for a library — its facts are
version-stamped, your memory of its API is not.

But VENDOR is **not free**, so it has a cost test: every library is a new
external **trust boundary** (its output still needs parsing at your edge) and a
new **effect/maintenance** boundary (its breaking changes become yours). Vendor
when you're reusing a real, maintained capability that *replaces* code you'd
otherwise own (zod replacing a hand-rolled parser: yes — and you gain checks you
didn't have). Don't vendor a dependency for something trivial you'd write once.
Default suspicion both ways: most "new" needs are already solved internally
(REUSE) or externally (VENDOR) — BUILD is the last resort, not the first.

### 4. Build items: local or shared? (Ent)
For each BUILD item, default to **local** (lives with the feature). Promote to
shared only on *evidence* of reuse, not anticipation — premature abstraction is
its own debt. The exception is units the domain *guarantees* are shared from day
one (a design token, a domain ID type like `PatientId`, a `Money`): these are
shelf items immediately because reuse isn't a guess. Recording local-vs-shared
now prevents both the speculative platform *and* the buried-reusable-thing.

### 5. Fit check (Ent)
Does each new unit conform to established patterns — naming, structure, the
boundary homes, the design tokens? Conformance is the "constraints liberate"
move: it's what keeps the shelf composable. A deviation is acceptable **only if
intentional and recorded here**; the real danger is *accidental drift*, which
turns one coherent system into N dialects nobody can compose against.

### 6. Seam & blast-radius check (Ent)
What existing code does this feature touch, and is each contact **composition**
(you call a stable, published interface — cheap) or **coupling** (you reach into
internals, depend on an unstable shape — expensive)? Decide this *before*
writing it, not in review. Every coupling contact is a future change-amplifier;
name them now so they're a conscious choice, not an accident.

## Outer loop — the ratchet (PLAN.md section 7 feeds this)

The ratchet promotes an earned one-off into a shared shelf item. It is the
answer to "it exists but isn't reusable — now what." It runs **periodically, not
per feature.**

### Trigger — the Rule of Three
Extract on the **third** occurrence, not the first. Two uses may be coincidence;
three reveals a stable shape you can abstract *correctly*. Abstracting on the
first use is how you get the wrong abstraction — more expensive than the
duplication it was meant to remove.

### Promotion criteria — "definition of reusable"
A local unit may move to the shared shelf only when it:
- owns exactly **one concept** (the one-unit-one-responsibility law),
- exposes a **stable interface** with no feature-specific dependencies leaking
  through,
- is **documented and discoverable** — without this it gets rebuilt, and you've
  grown duplication instead of the shelf.

### Extraction procedure
Behavior-preserving, characterization-tested, one unit at a time — this *is* the
`boundary-discipline` REFACTOR discipline. Promotion is relocation up the
substrate, never a rewrite.

### Cataloguing
One obvious home per kind of thing, named so it's findable. A shelf nobody can
search is a shelf nobody uses — and an unsearchable shelf manufactures
duplication on the next feature.

## What must stay true (the stay-on-path forces)

Not willpower — make the on-path choice the cheap/default one and off-path
expensive/visible:
- **One obvious home per concern**, so find-before-rebuild is the natural move.
- **Composition is the path of least resistance** — if reuse is harder than
  rebuilding, people rebuild, and no rule survives that.
- **The ratchet has a trigger and extraction is cheap**, so promotion happens
  instead of debt silently accruing.
- **Drift is caught early** — lint/types/review at PR or compile time, not in
  production. Shift-left applied to substrate consistency.
- **Promote on evidence, not anticipation** — so the machine doesn't grow the
  speculative platform that itself becomes debt.
