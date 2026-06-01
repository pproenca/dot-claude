# Confirming a library fact

The refresh write-path is mechanical (`lib_refresh.py` stamps and stores); this
is the judgment half — how to produce a *confirmed* fact rather than a recalled
one. This is "observe before you change" (from the verify-and-diagnose skill)
pointed at documentation instead of a running system.

## The rule

Never emit a fast-moving library's current API from memory. Training knowledge
of a versioned library is `unknown`-typed the moment a new version ships:
confidently shaped, often stale. Confirm against a live source, then record.

## How to confirm

1. **Read the installed version first.** Check `package.json` / lockfile for the
   version the repo actually uses. Facts are version-specific; confirm the facts
   for *that* major, not "latest in general".
2. **Go to a primary source.** Official docs, the changelog/release notes, or the
   npm page — in that order of preference. Avoid blog posts except to orient;
   they age and disagree. Capture the `source_url`.
3. **Extract decision-relevant facts only.** Not documentation — the few things
   that change a build or design decision. Good: "NativeWind 4 → Tailwind v3,
   JS config + global.css + metro withNativeWind". Noise: the full options table.
4. **Record the delta from prior**, if you have a previous entry. Refresh is a
   diff, not a relearn — note what changed from the version before so the next
   refresh is cheap.
5. **Capture the capability** — what problem the library solves, in one line — so
   the shelf-check's VENDOR rung can ask "is this already solved?" before
   anything is hand-rolled.

## Entry shape (what lib_refresh.py --set expects)

```json
{
  "confirmed_version": "4.x",
  "capability": "what problem it solves, one line",
  "key_facts": ["decision-relevant fact", "..."],
  "delta_from_prior": "what changed vs the previous major (or null)",
  "source_url": "https://primary-source"
}
```

`confirmed_on` is stamped by the script — never hand-write it; the stamp is the
provenance, and a hand-faked date defeats the staleness check.

## When to refresh

- **Miss** — the harness looked up a library with no entry. Confirm on demand.
- **Stale** — `lib_lookup`/`lib_refresh --check` reports the installed version
  drifted past the confirmed version. Re-confirm the delta before trusting.
- **Seed** — at setup, confirm the framework-defining deps (the ones that shape
  everything: the framework, the styling system, the language runtime). Leave
  the long tail to be confirmed lazily, per feature, when something reaches for
  it — evidence, not anticipation.
