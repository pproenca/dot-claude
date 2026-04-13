---
name: diagnose
description: >
  Diagnose a marketplace problem by routing the symptom to the right playbook and pulling live data before prescribing. Use when asking "the homefeed feels stale", "search relevance regressed after yesterday's ship", "conversion is leaking between registration and payment", "new members aren't booking", "new sitters can't get their first stay", "the same 100 listings keep dominating impressions", "Lisbon has 200 sitters and 5 owners", "our cold-start fallback is showing the same items", or any other symptom describing a two-sided marketplace that mostly works but feels broken.

  Routes to one of five branches: cold-start (new entity has no history), conversion funnel (any stage of anonymous → registered → paid → first booking → repeat → renewed), feed health (staleness, death spirals, popularity bias, recency drift), relevance regression (search change broke a golden-set case), or liquidity imbalance (structural supply-demand asymmetry). Pulls live data from configured MCPs before suggesting fixes, and grounds every recommendation in the research-based marketplace knowledge libraries.
argument-hint: "<symptom-description>"
---

# /marketplace:diagnose — Diagnose a Marketplace Problem

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../../CONNECTORS.md).

A routed diagnostic entry point. Describe the symptom in natural language; the skill routes to the right playbook, pulls live data to confirm, and prescribes fixes grounded in the knowledge libraries.

## Usage

```
/marketplace:diagnose <free-form symptom description>
```

Examples:

```
/marketplace:diagnose the homefeed has been getting blander for 8 weeks; same 100 sitters dominate
/marketplace:diagnose new paid members aren't booking in their first 60 days
/marketplace:diagnose search relevance regressed 4% on nDCG after yesterday's mapping change
/marketplace:diagnose Lisbon has 200 sitters and 5 owners, nothing matches
/marketplace:diagnose our cold-start fallback is showing the same 10 items to every new user
```

## Workflow

### 1. Load Company Context

Read the `<company>-marketplace-context` skill if present:
- `gotchas.md` — most incidents repeat. Check for prior cases matching this symptom.
- `surfaces.md` / `events.md` / `indexes.md` / `recipes.md` — to know what the current system looks like.
- `observability.md` — to know which monitors should have caught this.

If no context skill, prompt the user to bootstrap, or fall back to direct discovery.

### 2. Classify the Symptom

Match the user's description against the five branches. If ambiguous, ask a clarifying question.

| Branch | Keywords / signals |
|--------|-------------------|
| **Cold-start** | "new visitor", "new member", "new sitter", "new listing", "new city", "cold start", "no history", "first week", "first booking", "after pay but before booking", "post-register not booking" |
| **Conversion funnel** | "conversion leak", "funnel drop", "anonymous to register", "register to pay", "pay to first booking", "repeat rate", "renewal", "drop-off" |
| **Feed health** | "stale", "blander", "same items", "death spiral", "popularity bias", "dominating", "never changes", "recency drift", "filter bubble" |
| **Relevance regression** | "search regressed", "after change X", "mapping change", "synonym change", "analyzer change", "nDCG dropped", "zero-result spike" |
| **Liquidity imbalance** | "too many sitters", "not enough owners", "ratio off", "supply thin", "geographic imbalance", "seasonal peak", "unworkable segment" |

Announce the chosen branch before proceeding, and ask the user to confirm or correct.

### 3. Branch A — Cold-Start

**Question to answer**: For what entity? And what's the fallback doing?

**Data to pull**:
- From `events.md` / `~~data warehouse`: the cold-start cohort (users with < N interactions, or items with < M impressions, or a named geo with < K listings)
- From `~~personalisation engine`: the current cold-start solution / filter / fallback
- From `~~observability`: the cold-start fallback rate (how often is the fallback triggered?)

**Decision tree**:

1. **Is the cold-start solution actually firing?** Check fallback rate. If rate < 5% when cohort > 20%, the router isn't detecting cold-start cases — fix the detection.
2. **Is the fallback using the right features?** Cold-start should use the features the user HAS (inferred role, geo, inbound channel, onboarding answers). If the fallback only uses `popularity`, it will show the same items to every new user.
3. **Does the fallback decay as the user accumulates signal?** Check whether the router transitions to the main model at the right interaction count (typically 5-15).
4. **Is the cold-start cohort distinguishable in metrics?** Impressions should be tagged so you can measure cold-start conversion separately.

**Prescribed rules** (reference by title from `marketplace-personalisation`):
- `cold-best-of-segment-popularity` — use segment-aware popularity, not global popularity
- `cold-use-v2-recipe-with-metadata` — metadata-aware recipes beat pure interaction-count gates
- `cold-capture-onboarding-intent` — use the onboarding answers as synthetic interactions
- `cold-reserve-exploration-slots` — reserve a small fraction for unfamiliar items
- `cold-tag-cold-start-recs` — tag every cold-start recommendation so measurement can segment

**Ship-or-kill**: propose a specific fix, an A/B cohort, a primary metric (cold-start conversion within N days), a guardrail (overall conversion), and an MDE.

### 4. Branch B — Conversion Funnel

**Question to answer**: Which stage is leaking, and why is this stage-specific?

**Data to pull**:
- From `~~product analytics` (e.g., Amplitude): the funnel for the last 30 days with stage-by-stage conversion
- From `~~data warehouse`: the cohort composition of users who drop at each stage
- From `marketplace.md`: the primary revenue event and the ranking label

**Common leaks** and the rules they map to:

| Leak | Likely root cause | Rules |
|------|------------------|-------|
| Anonymous → registered | Landing page doesn't match inferred intent; trust copy weak; signup friction | `signal-classify-inbound-intent`, `owner-show-specific-local-reviews`, `onboard-ask-role-before-anything-else` |
| Registered → paid | Paywall static / mistimed / cost not anchored | `convert-trigger-paywall-on-specific-listings`, `convert-anchor-price-against-local-alternative`, `convert-never-interrupt-active-search` |
| Paid → first booking | Post-pay experience is cold-start; no concrete next action; first-stay competition brutal | `sitter-provide-concrete-first-stay-path`, `sitter-be-honest-about-first-stay-competition`, `gap-warn-about-cold-start-penalty` |
| First booking → repeat | First-experience friction (not a ranking problem; escalate to product) | escalate |
| Repeat → renewal | Renewal reminder generic; no loss-aversion framing | `convert-use-loss-aversion-framing-on-soft-locks`, `proof-use-specific-peer-stories-not-aggregates` |

**Ship-or-kill**: propose one concrete intervention at the leaking stage, an A/B cohort, a primary metric (stage-specific conversion rate), guardrails (downstream stages), and an MDE.

### 5. Branch C — Feed Health (Death Spiral / Staleness / Popularity Bias)

**Question to answer**: Is this feedback-loop bias, model drift, or a content-side problem?

**Data to pull**:
- From `~~observability`: top-N Gini trend over time, coverage 7d trend, impression concentration metric
- From `~~data warehouse`: impression distribution by item, by day; click distribution by item, by day
- From `recipes.md`: current serving-time filters and re-ranker

**Decision tree**:

1. **Is top-N Gini rising over time?** → death spiral pattern. Run `/marketplace:explore-events` on impressions to confirm feedback-loop bias.
2. **Is coverage (distinct items served / 7d) declining?** → model is narrowing. Check `cap-provider-exposure` rule — is there a serving-time cap? If not, add one.
3. **Are impressions concentrating faster than clicks?** → feedback loop is in training data. Inverse-propensity weight the training data.
4. **Is recency the problem?** → check freshness weighting in the ranker (`rank-use-function-score-for-business-signals` with a decay term).
5. **Is there a content-side collapse?** → new listing volume may have dropped. Check `indexes.md` for update pattern and volume trend.
6. **Is there feature drift?** → check `features.md` for coverage gaps, PSI alarms, training-serving skew. If a feature has drifted, the model's effective input distribution has shifted even though no code changed. Load `marketplace-recsys-feature-engineering` rules (`quality-gate-features-on-coverage-and-drift`, `quality-serve-training-and-inference-from-one-store`) to frame the fix.
7. **Has a feature been silently killed?** → check whether any feature the solution depends on is in a kill-review or has lost its upstream pipeline. A ranker silently degrades when a feature becomes null but the serving path doesn't re-score. Cross-reference `features.md` consumer mapping with the current solution definition.

**Prescribed rules**:
- `loop-detect-death-spirals` — the monitor that should have caught this
- `match-cap-provider-exposure` — serving-time cap on single-item or single-supplier dominance
- `loop-reserve-random-exploration` — exploration slots in the feed
- `obs-track-coverage-and-gini` — add if not already tracked

**Ship-or-kill**: propose a re-ranker cap, an experiment against current production, and the monitor thresholds to add.

### 6. Branch D — Relevance Regression

**Question to answer**: Does the golden set confirm the regression, and what specifically broke?

**Data to pull**:
- From `golden-set.md`: the existing golden query set for the regressed surface
- From `~~search engine`: run the golden queries against both the previous mapping / settings and the current ones (if snapshot / point-in-time is available)
- From `~~observability`: pull the relevant nDCG / MRR / zero-result-rate monitors around the change time

**If no golden set exists**, advise the user to run `/marketplace:build-golden-set search` first — or fall back to a hand-picked sample of regression candidates from `gotchas.md`.

**Decision tree**:

1. **Run the golden-set diff.** Report per-query nDCG delta, ranked by worst-regression.
2. **Cluster the regressed queries by intent class.** A regression concentrated in one intent class (e.g., "specific dates") points to a specific rule violation.
3. **Trace the cluster to the change**. Common causes:
   - Synonym expansion inflates recall on precision queries → `query-curate-synonyms-by-domain`
   - Analyzer mismatch between index and query time → `index-match-index-and-query-time-analyzers`
   - BM25 parameter change cascades to all queries → `rank-tune-bm25-parameters-last`
   - Filter-to-must movement drops exact-match constraints → `retrieve-use-filter-clauses-for-exact-matches`

**Prescribed rules**: whichever of the above match, plus `plan-maintain-a-decisions-log` as a process reminder.

**Ship-or-kill**: decide between rollback, partial rollback (e.g., keep the synonym, drop the weekend expansion), or forward-fix. If forward-fix, propose an A/B with a tight guardrail on nDCG@10.

### 7. Branch E — Liquidity Imbalance

**Question to answer**: Is this a structural supply-demand problem that ranking can't fix, or is ranking making it worse?

**Data to pull**:
- From `liquidity.md`: current state per geo / season / side
- From `~~data warehouse`: the ratio per geo for the current quarter vs the prior-year equivalent
- From `surfaces.md`: any surfaces that match users across geos (e.g., saved search alerts, emails)

**Decision tree**:

1. **Is the ratio structurally broken, or seasonal?** Compare to the same period last year.
2. **Is the long side's engagement dropping?** When ratios get extreme, the side with excess supply disengages — they pay but the product becomes noise.
3. **Is ranking masking the imbalance or amplifying it?** A ranker that recommends the same scarce-side items to everyone exhausts the scarce side faster. Check for a side-cap.
4. **Are there mitigations in flight?** Check `liquidity.md` → "mitigations in flight" section. Is the current mitigation working?

**Prescribed rules**:
- `match-balance-supply-demand` — do not rank feasibility-impossible items
- `match-cap-provider-exposure` — cap scarce-side item exposure to slow burnout
- `gap-route-unworkable-segments-to-alternatives` — surface alternatives when the segment is structurally unworkable
- `gap-surface-seasonal-supply-constraints` — set expectations explicitly for the user

**Ship-or-kill**: distinguish between *acceptable liquidity imbalance* (transparent user expectations), *ranking amplifying imbalance* (fix ranking), and *structural marketplace problem* (requires growth / supply-acquisition work, not ranking work). Route accordingly.

### 8. Propose a Ship-or-Kill Decision

Every branch ends with a **single** recommended next step:

- **Fix now** (if the root cause is clear, low-risk, and a quick patch)
- **A/B test** (if the fix is non-trivial or carries risk; propose primary metric, guardrails, MDE, cohort, duration)
- **Escalate** (if the problem is outside ranking / personalisation — e.g., product, growth, supply acquisition)

### 9. Update `gotchas.md`

After diagnosis, offer to append the diagnosis to `gotchas.md` with:
- Symptom
- Root cause (confirmed or suspected)
- Fix proposed
- Leading indicator that would have caught this earlier

## Read-only posture

Every query in every branch is **read-only** and announced before execution.

## Tips

- **Start with `gotchas.md`.** More than half of diagnoses are repeats of prior incidents.
- **Don't skip to prescription** — always pull live data first. Research-grounded rules are priors, not conclusions.
- **Be explicit about which branch you're in** — say it out loud so the user can redirect if you've misclassified.
- **If multiple branches apply** (e.g., a death spiral causing a funnel leak), address the upstream branch first.

## Related Commands

- `/marketplace:explore-events` — often the right first step if the diagnosis points to instrumentation
- `/marketplace:review-change` — if the diagnosis points to a recent ship
- `/marketplace:build-observability` — add the monitor that would have caught this next time
- `/marketplace:build-golden-set` — prerequisite for Branch D (relevance regression)
