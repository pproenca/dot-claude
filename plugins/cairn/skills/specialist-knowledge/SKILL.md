---
name: specialist-knowledge
description: >-
  Summon, cache, and apply a distilled "specialist profile" — the load-bearing
  craft of a domain expert (native iOS design, high-performance React Native,
  Expo idioms, accessibility, animation) — instead of emitting generic, stale
  advice from memory or hand-authoring a new skill per specialty. Use this
  BEFORE building in a domain that needs specialist taste, when a screen or
  module must feel native, be high-performance, or follow platform conventions,
  and whenever the model would otherwise produce plausible-but-mediocre output
  from its priors. It keeps a repo-local store (specialist-profiles.jsonl): per
  domain, the load-bearing principles, the anti-patterns a master avoids, a
  review checklist, the authorities confirmed against, the library versions it
  is pinned to, the user-taste deltas, and the date. Look up a profile to apply
  it cheaply; distill or refresh one by confirming against authority AND
  adjudicating contested taste with the user. Twin of library-knowledge: facts there, craft here.
---

# Specialist Knowledge

The craft shelf — the twin of `library-knowledge`. That skill caches a domain's
**facts** (what version, what API, what capability). This one caches a domain's
**craft** (what a master *does* — the idioms, taste, and performance patterns
that make iOS feel native or RN run at 60fps).

It exists because the model's priors for craft are **generic and stale**: asked
to "make it native" from memory, it produces the plausible-but-mediocre average
of its training data — the generic-AI-aesthetic problem. And hand-authoring a
skill per specialty (`ios-specialist`, `rn-perf-specialist`, …) is the
*duplication* failure at the meta level, plus speculative pre-building for
platforms you may never touch. So this skill is **not** the expertise. It is a
**distiller**: a repeatable procedure that summons a specialist's soul on
demand, confirmed against authority, adjudicated for taste with you, and cached
as a small reusable profile.

The value: **distill once (confirm authority + adjudicate taste), cache, apply
many times cheap, refresh only on drift.**

## Why a separate boundary from library-knowledge

Both are external truth-sources the agent can't fill from priors; both
confirm-cache-reconfirm. The difference that earns a separate skill: library
facts are **verifiable and single-sourced** (the docs say RN is 0.85, period),
so they need no human. Craft is **contested and partly subjective**, so *you*
are a first-class truth-source — the way you are at the spec parse-point. This
skill is the synthesis of the harness's two existing external boundaries: it
confirms against authority like library-knowledge, and it adjudicates taste with
you like the skeleton's spec gate.

## The store entry (the interface)

`specialist-profiles.jsonl` at the repo root — one self-describing record per
line (JSONL), keyed by `domain` (e.g. `ios-native-design`,
`high-performance-react-native`, `expo`):
- `principles` — the load-bearing few, not an encyclopedia. The compressed soul.
- `anti_patterns` — what a master *avoids* (often more diagnostic than the do's).
- `checklist` — the review questions to apply at skeleton/build time.
- `authorities` — the sources confirmed against (e.g. Apple HIG, RN/Expo perf docs).
- `pinned_libs` — the library-knowledge entries + versions this craft is bound to.
  **This is the seam:** craft references facts so it never drifts from the real
  API surface. `react-native@0.85`, `expo@56` — if those bump, the profile is stale.
- `taste_deltas` — the user-adjudicated, app-specific judgments (contested calls).
- `confirmed_on` — provenance + the staleness clock.

## Workflow

- **Apply (cheap, the common path):** `specialist_lookup.py --domain <d>` returns
  one profile's principles + checklist for use at STAGE 0.5 / build. Stale or
  missing → distill/refresh first. Never emit craft advice from memory when a
  profile exists.
- **Distill (expensive, effectful, rare):** when a domain is first needed or has
  gone stale, run the distillation procedure (see `references/distilling.md`):
  scope the specialist → confirm current authority (web, pinned to
  library-knowledge versions) → **adjudicate contested taste with the user** →
  compress to load-bearing principles + anti-patterns + checklist → cache.
  Record via `specialist_refresh.py --set <domain> --from-json <file>`.
- **Refresh on drift:** `specialist_refresh.py --check` flags a profile whose
  `pinned_libs` no longer match library-knowledge, or that the user says is out
  of date. Refresh is a diff, not a relearn.

## Composition (how it plugs into the harness)

- Profiles are **applied at STAGE 0.5 and build** (feature-workflow): the
  checklist becomes review questions; the principles shape the implementation.
- `pinned_libs` is queried against **library-knowledge** — the facts/craft seam.
- Profiles are **inherited**: the tenth iOS screen summons nothing, it reuses the
  cached soul. Craft-elicitation cost slopes down like spec cost does.
- The **knowledge-ratchet** governs graduation: a recurring specialist correction
  climbs the ladder (ad-hoc → cached profile → convention/lint). A profile
  graduates to its *own dedicated skill* only on the VENDOR cost test — when the
  federation truly needs it — so the federation surface stays controlled instead
  of sprouting one skill per platform.

## The one law, here

A profile is **craft, not facts, not spec**: keep version facts in
library-knowledge (referenced via `pinned_libs`), product intent in the spec
(skeleton invariants), and only the *taste and technique* here. One profile, one
domain's soul — small enough to stay load-bearing, pinned enough to stay honest.

## Files
- `references/distilling.md` — the distillation procedure (how to render a soul).
- `scripts/store.py` — the storage port (JSONL; the only module touching disk).
- `scripts/specialist_lookup.py` — apply a profile cheaply (one entry / index).
- `scripts/specialist_refresh.py` — distill/record a profile; `--check` staleness
  vs library-knowledge.
