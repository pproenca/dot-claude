# The Shelf (substrate model)

Read during STAGE 0, alongside `loop.md`. The "shelf" is the layered inventory
of reusable units a feature draws from. Features depend **downward** (compose
from lower-layer primitives); growth pushes **downward** (the ratchet promotes
one-offs into shared lower layers). Keeping the shelf healthy is what makes each
feature build less.

## The isomorphism — one discipline, two shelves

UI and domain/boundaries are the **same** kind of substrate. A design token and
a `Money` value object are the same kind of thing: the smallest unit you've
decided to trust and reuse everywhere. A UI pattern and a use-case pipeline are
the same kind of thing: a named composition of primitives that encodes "the way
we solve this recurring problem here." Learn the discipline once, apply it to
both.

| Substrate layer | UI shelf | Domain / boundary shelf |
|---|---|---|
| **Atomic, no logic** | design tokens (color, spacing, type scale, motion) | value objects / branded types (`TimeSlot`, `PatientId`, `Money`) — domain "tokens", parse-guarded at the trust edge |
| **Single-purpose unit** | primitive components (Button, Input, Card) | aggregates / entities — each owning one invariant at its consistency boundary |
| **Reusable seam** | shared hooks, providers, context | ports + adapters — reusable effect boundaries, provider models walled behind the ACL |
| **Composition encoding a recurring solution** | patterns (Form, Modal flow, List+Detail) | use-case pipelines (`ingress → decide → commit`) |
| **Scaffold** | layouts / nav shell / templates | the service's process structure — the fractal edge→core→egress shell |
| **The product** | the app = composition of the above | the service = composition of the above |

The same sentence describes both: *a layered inventory of single-responsibility,
stable-interface units, drawn from by composition and grown by a promotion
ratchet, kept coherent by making the conforming choice the cheapest one.*

## How to run the shelf-check (PLAN.md section 3)

For each item in the bill of materials, walk **down** the layer table and ask
"does a unit at this layer already cover it?":

- **Found, fits as-is** → REUSE. Take it; write nothing.
- **Found, almost** → EXTEND. Make the *smallest* generalization that fits both
  the old and new use. Do not fork it (that's duplication wearing a disguise).
- **Not found at any layer** → BUILD. Then go to section 4 (local vs shared).

Bias hard toward the lower layers first: most "new" needs are a new *composition*
of existing primitives, not a new primitive. A feature that introduces new
atomic tokens or new primitives should be rare and deliberate.

## Local vs shared (PLAN.md section 4)

- **Default local.** A BUILD item lives with its feature until reuse is
  *demonstrated* (Rule of Three). This keeps the shelf free of speculative
  abstractions that were never actually reused.
- **Shared on day one — only when reuse is guaranteed, not guessed:** the atomic
  layer (a new design token, a domain ID/`Money` type). These are
  cross-cutting by definition.
- Everything between is local-until-promoted. Recording the decision here is
  what lets the outer-loop ratchet later find promotion candidates.

## Definition of reusable (the promotion bar — outer loop)

A local unit is ready to move to the shared shelf only when all hold:
1. **One concept** — single responsibility; one reason to change.
2. **Stable interface** — no feature-specific assumptions or dependencies leak
   through its boundary.
3. **Discoverable** — documented and catalogued in its layer's obvious home, so
   the next feature finds it instead of rebuilding it.

Miss any one and promotion is premature: an unstable or undiscoverable "shared"
unit grows coupling or duplication rather than reducing it.

## Why the shelf is the same shape as the boundary model

Trust pushed inward and effects pushed outward leave a pure core; the shelf is
that core's *inventory*, organized by layer. A value object is a trust-boundary
output you decided to reuse. A port is an effect boundary you decided to reuse.
A use-case pipeline is the `ingress→decide→commit` flow you decided to name.
That's why the two skills compose cleanly: boundary-discipline says *where a unit
lives*; this shelf model says *whether it's reusable and at which layer it sits*.
