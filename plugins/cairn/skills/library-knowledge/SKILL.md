---
name: library-knowledge
description: >-
  Consult or refresh confirmed, version-stamped facts about the external
  libraries a repo depends on, in a token-efficient way the rest of the harness
  can query. Use this BEFORE writing configuration or code that depends on a
  fast-moving library (build tools, styling systems, validation, frameworks),
  before deciding whether to reuse a library capability instead of hand-rolling
  one, and whenever a version may have changed. It maintains a repo-local store
  (lib-knowledge.json): per library, the confirmed version, the date it was
  confirmed, decision-relevant key facts, the delta from the prior version, the
  capability it provides, and the source. Look up an entry to get current facts
  cheaply; refresh an entry by confirming against live docs when it is missing
  or stale. Use this whenever you would otherwise emit a library's current API
  from memory — that memory is stale the moment a version ships.
---

# Library Knowledge

The external-knowledge shelf. `shelf_index` (feature-workflow) inventories the
substrate you *built*; this inventories the substrate you *depend on*. It exists
because a skill is static text and rots on the training clock — the very problem
it solves — so this skill is not the knowledge. It is a **librarian**: a
version-stamped, queryable store plus scripts that refresh it against live
sources and serve it cheaply.

The value: **confirm once (expensive, effectful), cache, serve many times cheap,
refresh only on drift.**

## The store entry (the interface)

`lib-knowledge.jsonl` at the repo root — one self-describing record per line (JSONL):
- `confirmed_version` + `confirmed_on` — provenance. An entry behind the
  installed version is unparsed knowledge; trusting it blind is the stale-config
  bug.
- `key_facts` — decision-relevant only, not documentation.
- `delta_from_prior` — refresh is a diff from the recorded version, not a relearn.
- `capability` — what problem it solves, so the VENDOR rung can ask "already solved?"
- `source_url` — where the fact was confirmed.

## Consult (cheap, frequent)

All reads go through `store.py` (the storage port) and are token-cheap by
construction — the agent's context only ever holds what it asked for:
- `python scripts/lib_lookup.py <name>` → ONE entry + staleness, streamed from
  the JSONL with an early exit at the matching line (never the whole store).
- `python scripts/lib_lookup.py` → the index: name + version + date per line only.
- `python scripts/lib_lookup.py --search "<capability terms>"` → ranked library
  names + one-line capabilities (not full entries) — the path the VENDOR rung
  uses to ask "is this already solved?".

## Refresh (effectful, rare) — confirm, then record

Freshness only comes from going to the world, so refresh has two halves:
- **Judgment + effect (the agent):** search the library's official
  docs/changelog for the *installed* version and extract decision-relevant
  facts. See `references/confirming.md`. This is "observe before you change"
  aimed at documentation — verify against the live source instead of memory.
- **Mechanical (the script):** `python scripts/lib_refresh.py --set <name>
  --from-json <entry.json>` merges the entry and stamps `confirmed_on`.

Trigger refresh on: a **miss** (no entry), a **stale** verdict (installed drifted
past confirmed), or at **seed** (framework-defining deps only).

## Staleness is the gate

`python scripts/lib_refresh.py --check` compares every entry's confirmed_version
to the installed version and exits non-zero if any is STALE. Wire it as a
verify-gate check so generated code can't ship against facts the lockfile has
already moved past — the check that would have caught a stale config.

## Storage is behind a port (token-efficient, swappable)

`store.py` is the ONLY module that touches the store; the scripts and the harness
call it, never the file. Backend today is **JSONL**: one record per line, read by
streaming, so lookup cost is one record and the store can grow to hundreds of
libraries without becoming a context hoarder. It is also grep-friendly and
imports into SQLite trivially (one row per line).

Because every consumer sees only the port's interface, the backend can change
with zero caller changes. **SQLite / FTS5 is the documented swap** — adopt it
only when capability-search across a large store becomes a hot path (lookup and
index don't need it; a filesystem/stream already serves those in one record).
Until then, adding a database would fail the VENDOR cost test we apply to every
dependency: it solves a token cost we don't have rather than a search-at-scale
cost we haven't hit.

## How the harness consults it (the four seams)

- **harness-setup** seeds the framework-defining deps at boot.
- **feature-workflow** shelf-check (the VENDOR rung) queries `capability` to ask
  "is this already solved by a library?" before hand-rolling.
- **verify** runs `lib_refresh --check` as a freshness gate.
- On a miss or stale verdict, the **refresh** path fires: confirm against docs,
  record, proceed.

## Seeding policy

Eager only for the framework-defining deps (framework, styling system, language
runtime) at setup; lazy for the rest — confirm a library the first time a feature
reaches for it. Evidence, not anticipation; the store never bloats with libraries
no feature touches.

## Files

- `scripts/store.py` — the storage port (JSONL today; the one place to swap in SQLite). The only module that touches the store.
- `scripts/lib_lookup.py` — cheap reads: one entry, the index, or `--search` over capabilities.
- `scripts/lib_refresh.py` — record a confirmed entry (`--set`), or check staleness (`--check`).
- `references/confirming.md` — how to confirm a fact against live sources (the judgment half).
