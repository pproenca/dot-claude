# PLAN: ((fill: feature name))

> Pre-flight for a feature. Sections 0–6 are the **gate** — they must be filled
> and pass `plan_check.py` BEFORE any code is written. Section 7 is filled at
> ship time (`--stage post`). Replace every `((fill: ...))` with real content;
> any remaining `((fill` token means the gate fails. Read `references/loop.md`
> and `references/shelf.md` while filling this.

## 0. Feature

- **Name:** ((fill: short name))
- **Customer pain / outcome:** ((fill: the pain this removes, in one sentence))
- **Adoption signal:** ((fill: how we'll know it's adopted — the observable that proves it solved the pain))
- **Open decisions carried in (from a spike, if any):** ((fill: the spike's open-decisions list, or "none". Each is resolved at the STAGE 0.5 spec interview — recommended answer first, codebase-explored before asking, human only for intent/taste.))

## 1. Boundary decomposition

Which boundaries does this feature cross? (See boundary-discipline model.) Delete
rows that don't apply; keep at least one.

- **Trust (ingresses):** ((fill: each untrusted input + where it's parsed))
- **Decisions (pure core):** ((fill: the rule(s) computed, mockless))
- **Consistency (invariants):** ((fill: what must hold under concurrency + the serialization point))
- **Effects (rim):** ((fill: side effects + their ports/idempotency))
- **Containment:** ((fill: external calls to bound — timeouts/breakers — or "none"))

## 2. Bill of materials

Concrete units this feature needs, specific enough to check against the shelf.

- **UI:** ((fill: components / tokens / patterns))
- **Domain:** ((fill: value objects / aggregates / ports / pipelines))

## 3. Shelf check (REUSE / EXTEND / BUILD)

Classify every BOM item. One row per item. Use one of REUSE, EXTEND, VENDOR (external library), BUILD in the Decision column.
VENDOR outranks BUILD — check `library-knowledge` for a maintained capability before hand-rolling.

| Item | Layer | Exists? (where) | Decision | Note |
|---|---|---|---|---|
| ((fill: item)) | ((fill: layer)) | ((fill: path or "no")) | ((fill: REUSE/EXTEND/BUILD)) | ((fill: detail)) |

## 4. Build items: local vs shared

For each BUILD (and EXTEND that changes a shared unit) from section 3:

- ((fill: item — LOCAL (default) or SHARED, and the reason. SHARED requires either an atomic-layer guarantee or demonstrated reuse.))

## 5. Fit check

Does each new/extended unit conform to existing patterns (naming, structure,
boundary homes, design tokens)?

- **Conforms:** ((fill: yes — or list the units checked))
- **Intentional deviations:** ((fill: any deliberate departure + why — or "none"))

## 6. Seam & blast-radius check

Existing code this feature touches, and whether each contact is composition or
coupling.

| Touched code | Contact type | Why / mitigation |
|---|---|---|
| ((fill: module/interface)) | ((fill: COMPOSITION or COUPLING)) | ((fill: stable interface? or coupling justification + plan)) |

---

## 7. Shelf deposits (fill at SHIP time — `--stage post`)

What reusable units this feature added or generalized, and where they live (feeds
the outer-loop ratchet).

- **Added/generalized:** ((fill: unit → layer → path, or "none"))
- **Out of scope, for later:** ((fill: unrelated gaps noticed but not fixed, or "none"))
- **Promotion candidates:** ((fill: any local unit now at 2+ uses to watch for Rule-of-Three, or "none"))
