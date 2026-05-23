# The "Read when:" doc convention

crabbox opens 70+ docs with a `Read when:` trigger list so an agent can **self-select**
which docs to pull into context. Adopt it for any agent CLI — it is the single best
defense against doc drift, because docs become addressable by task.

```markdown
# <Doc Title>

Read when:

- <trigger 1 — a task that requires this doc>;
- <trigger 2>;
- <trigger 3>.

<one-line statement of what this doc is and how to use it>
```

Foundational always-on reference (architecture.md, security.md) may skip the header;
agent-facing task docs should have it.

## The three doc roles (keep distinct, cross-link them)

1. **`source-map.md` — behavior → files.** The "source-backed check before changing a
   behavior claim." Organized by behavior area; each bullet maps a behavior to the exact
   implementation files. This is what an agent reads to find where to make a change.
   Regenerate the touched section whenever you move code.

2. **`refactor/<area>.md` / `plan/<feature>.md` — design context + migration.** Per-effort
   docs. A refactor doc carries: `## Context`, `## Design Principle`, `## Goals` /
   `## Non-Goals`, a numbered `## Migration Plan` where **each phase has a `Status:`
   line** (`Status: implemented for X` / `Status: pending`), `## Tests`,
   `## Acceptance Criteria`, `## Open Questions`. A plan doc carries: `## Goal`, ownership
   split, `## CLI Surface`, `## Implementation Files` (a literal file checklist),
   `## Tests`, `## Gates` (exact gate commands), numbered `## Acceptance Criteria`,
   `## Deferred`. These docs forward to the handrail.

3. **`<area>-backends.md` — the authoring handrail.** The durable how-to for adding one
   more of the breadth thing (a provider, a mapper, a target). Walks: choose the shape →
   optional interfaces → package layout → registration (with a copy-pasteable minimal
   example) → spec → flags/config → implement → a final **Review Checklist** (e.g. "the
   provider has a folder under `internal/providers/<name>`", "spec.Kind matches the real
   execution model", "docs and source map are updated"). The refactor/plan doc says
   "for step-by-step guidance, read the handrail; this doc captures design context."

## Why three roles, not one
- The **handrail** is stable and reusable (rarely changes) — agents read it to *add* code.
- The **refactor/plan** doc is per-effort and disposable-ish (captures the *why* and the
  migration state) — agents read it to *understand a change in flight*.
- The **source-map** is a living index — agents read it to *locate* code.
Conflating them produces a doc that's simultaneously stale, too long, and hard to trust.
