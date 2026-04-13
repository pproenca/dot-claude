# Example Output

A complete worked example for a fictional two-sided marketplace called **Pawmates**, a pet-owner / pet-sitter platform.

The example shows what the generated skill looks like after a bootstrap session. Use it as a reference for shape and depth — not as a literal template.

---

## Directory layout

```
pawmates-marketplace-context/
├── SKILL.md
├── marketplace.md
├── surfaces.md
├── events.md
├── indexes.md
├── recipes.md
├── observability.md
├── liquidity.md
├── gotchas.md
└── golden-set.md
```

---

## `SKILL.md`

```markdown
---
name: pawmates-marketplace-context
description: >
  Company-specific marketplace context for Pawmates. Load this skill whenever working on search, recommendations, personalisation, cold-start, conversion funnel, feed health, relevance regression, or liquidity for Pawmates' two-sided marketplace between pet owners and pet sitters.

  Contains the authoritative record of surfaces, event taxonomy, OpenSearch indexes, AWS Personalize recipes, Datadog observability, KPIs, liquidity state, known gotchas, and the golden evaluation set. Every /marketplace:* command that targets Pawmates' systems should load this skill first.

  Triggers: any task mentioning Pawmates, pet owners, pet sitters, homefeed, search, recsys, conversion funnel, death spiral, cold start, or the surfaces listed in surfaces.md.
---

# Pawmates Marketplace Context

## Marketplace at a glance

- **Two sides**: pet owners ↔ pet sitters
- **Value exchange**: service-for-service (sitters stay free, owners get pet care)
- **Monetization**: tiered subscription with optional per-sit booking fee
- **Primary revenue event**: `membership_purchased` (annual, high lifetime value)
- **Secondary revenue event**: `booking_fee_charged` (per-sit, for non-top-tier owners)
- **North-star metric**: paid members who book within 60 days
- **Production stack**: OpenSearch, AWS Personalize, Twilio Segment + Amplitude, Datadog, Databricks

## Navigation

| File | What it contains |
|------|-----------------|
| [marketplace.md](marketplace.md) | Two sides, monetization, KPIs, guardrails |
| [surfaces.md](surfaces.md) | 14 surfaces (7 personalised, 7 not) |
| [events.md](events.md) | Event taxonomy and 4 known gaps |
| [indexes.md](indexes.md) | 3 production indexes (sitter_profiles, owner_listings, saved_searches) |
| [recipes.md](recipes.md) | 2 production solutions, 3 filters, cold-start strategy |
| [observability.md](observability.md) | 5 dashboards, 12 monitors, 3 SLOs |
| [liquidity.md](liquidity.md) | Liquidity state per 30 geos, seasonal pattern |
| [gotchas.md](gotchas.md) | 6 historical incidents |
| [golden-set.md](golden-set.md) | 48 search queries, 22 recsys intents |

## How to use

- Before making any Pawmates-specific suggestion, read the relevant section.
- Start with `gotchas.md` when diagnosing — most incidents repeat.
- Check `observability.md` for regression-catching monitors before shipping a change.
- Check `surfaces.md` to avoid duplicating personalisation work.

## Keeping this skill up to date

- `/marketplace:bootstrap-context iterate` to refresh a specific section
- `/marketplace:explore-events <surface>` to deepen `events.md`
- `/marketplace:build-golden-set` to grow `golden-set.md`
- Append to `gotchas.md` after every incident

## Related skills

- `marketplace-pre-member-personalisation` (general, auto-loaded)
- `marketplace-search-recsys-planning` (general, auto-loaded)
- `marketplace-personalisation` (general, auto-loaded)
```

---

## `marketplace.md`

```markdown
# Marketplace Fundamentals

## Two sides

- **Pet owners** — people who have pets and need care while travelling. Typically engage 2-6 times per year (around trips). Primary motivation: trustworthy free pet care at home.
- **Pet sitters** — people who want to travel and care for pets in exchange for free accommodation. Typically engage 6-30 times per year. Primary motivation: low-cost travel experience.

### Dependency

Owners need sitters **before** a trip (2-12 weeks lead time). Sitters need inventory **always** (they plan continuously). When sitters are thin in a geo, owners fail to find care and churn. When owners are thin, sitters can't travel and their app engagement drops — they still pay but disengage, hurting renewal the year after.

### Value exchange

Service-for-service, not money-for-service. No money flows between owners and sitters directly. The platform monetizes via membership fees and a per-sit booking fee for non-top-tier owners.

## Monetization

- **Model**: tiered subscription with optional per-transaction fee
- **Tiers**:
  - Basic: low price, includes per-sit booking fee
  - Standard: mid price, includes per-sit booking fee
  - Premium: high price, no booking fee (escape hatch for heavy users)
- **Primary revenue event**: `membership_purchased` — annual, lifetime value drives everything
- **Secondary revenue events**: `membership_renewed`, `booking_fee_charged`, `tier_upgraded`
- **Ranking label candidates**:
  - For pre-paid surfaces: `session_led_to_membership_within_7d`
  - For post-paid surfaces: `session_led_to_booking_confirmed_within_60d`

## North-star metric

**Paid members who book within 60 days** — tracked in Amplitude cohort `nsm_paid_to_first_booking_60d`, dashboarded in Datadog `Pawmates / Conversion / North Star`. Trending flat over the last quarter after a 12% YoY increase in the prior year.

## Supporting metrics

- **Conversion funnel**: anonymous → registered → paid → first booking → repeat booking → renewed
- **Engagement**: weekly active members, average listings viewed per session
- **Quality**: sit completion rate, owner satisfaction score, sitter acceptance rate

## Guardrails

- **Performance**: p95 search latency ≤ 180ms, p95 homefeed latency ≤ 250ms, error rate ≤ 0.1%
- **Cost**: infra cost per MAU ≤ {{internal target}}
- **Fairness**: no single sitter gets more than 4% of impressions on any surface
```

---

## `surfaces.md` (excerpt)

```markdown
# Surfaces

| Surface | Position | State | Traffic | Conversion weight | Algo | Owner |
|---------|----------|-------|---------|-------------------|------|-------|
| Anonymous landing | anonymous | static | very high | medium | — | Growth |
| Homefeed (members) | paid | ML ranker | very high | high | user-personalization-v2 + rerank | Discovery |
| Search results | paid | ML reranker | very high | very high | BM25 + LTR | Search |
| Listing detail related | paid | rule-based | high | medium | same-pet-type popularity | Listing |
| Saved search alert email | post-paid | rule-based | medium | high | new-listings-matching-saved-filter | Lifecycle |
| Abandoned-browse email | anonymous re-engagement | none | medium | low | — | Growth |
| Paywall screen | pre-paid | static | high | very high | — | Growth |
| Onboarding intent capture | registered | branched static | high | high | role-based branching | Growth |
| New-sitter first-stay path | pre-paid | none | low | high | — | Sitter Success |
| Push re-engagement | retained | time-based rule | medium | medium | last-active-day | Lifecycle |
| Profile completeness nudges | registered | none | medium | medium | — | Growth |
| Zero-result fallback | active search | rule-based | low | medium | broaden-filter-cascade | Search |
| Category / theme collections | paid | none | medium | medium | — | Discovery |
| Similar-sitter on profile | paid | rule-based | medium | medium | embedding cosine | Listing |

## Per-surface detail

### Homefeed (members)

- **Position in journey**: paid
- **Current state**: ML ranker in production
- **Ranking label**: `listing_view_led_to_application_within_7d`
- **Cold-start handling**: fallback solution `pawmates-cold-start-v1` using popularity-by-segment for users with < 5 interactions
- **Known issues**: top-10 Gini trending up (see gotchas `homefeed-death-spiral-2025q3`)
- **Links**: code path `src/home/feed.ts`, Personalize solution `pawmates-homefeed-v2`, Datadog dashboard `Pawmates / Homefeed`

### Paywall screen

- **Position in journey**: pre-paid (registered but not yet paid)
- **Current state**: static — same copy for every user
- **Conversion weight**: very high (single highest-value impression in the funnel)
- **Known issue**: not personalised at all. Prime candidate for expand-personalisation.
- **Links**: code path `src/paywall/screen.tsx`

(... remaining surfaces ...)
```

---

## `events.md` (excerpt)

```markdown
# Event Taxonomy

## Impression events

### `listing_impressed`

- **Definition**: Fired client-side when a listing card enters the viewport for ≥ 500ms
- **Properties**: `user_id`, `session_id`, `surface_id`, `listing_id`, `rank_position`, `model_version`, `request_id`, `geo_ip_country`
- **Volume**: ~140M / day
- **Source**: client (React intersection observer)
- **Known gaps**:
  - `rank_position` missing for 22% of anonymous sessions on the landing page (known bug, tracked as PAW-1843)
  - `model_version` missing for the legacy similar-sitter module

## Click / engagement events

### `listing_clicked`

- **Definition**: Fired when a user clicks a listing card or its title link
- **Properties**: inherits from impression (joined via `request_id`) + `click_element`
- **Volume**: ~12M / day
- **Source**: client

## Conversion events

### `membership_purchased` (primary revenue event)

- **Revenue-linked**: yes
- **Attribution window**: 7 days from first qualifying event
- **Dedup logic**: one per user per year
- **Source**: server (Stripe webhook → Segment)

### `booking_confirmed` (primary ranking label for post-paid surfaces)

- **Revenue-linked**: partial (only charges booking fee for non-Premium)
- **Attribution window**: 60 days
- **Dedup logic**: one per sit, not per session

## Negative signals

- **Skip / scroll-past**: NOT tracked (gap)
- **Dwell-below-threshold**: NOT tracked (gap)
- **Report / block / dismiss**: tracked as `listing_reported`, `listing_blocked`

## Known quality issues

1. `rank_position` missing for 22% of anonymous landing impressions (tracked in PAW-1843)
2. No skip / scroll-past tracking — ranking loss function cannot learn strong negatives
3. `request_id` not threaded through the abandoned-browse email → conversion path, so email-attributed conversions can't be joined back to the impression that drove them
4. `model_version` missing on similar-sitter module
```

---

## `recipes.md` (excerpt)

```markdown
# Personalisation Recipes

## Datasets

### `pawmates-interactions` (INTERACTIONS)

- **Schema fields**: `USER_ID`, `ITEM_ID`, `EVENT_TYPE`, `EVENT_VALUE`, `TIMESTAMP`, `SURFACE_ID`, `GEO`, `PET_TYPE`
- **Update pattern**: streaming via `PutEvents`
- **Volume**: ~150M events / day (impressions + clicks + bookings)
- **Retention**: 180 days

### `pawmates-users` (USERS)

- **Schema fields**: `USER_ID`, `ROLE` (owner/sitter), `SIGNUP_DATE`, `HOME_COUNTRY`, `PET_TYPES_OWNED`
- **Update pattern**: batch nightly from Databricks

### `pawmates-items` (ITEMS)

- **Schema fields**: `ITEM_ID`, `LOCATION`, `PET_TYPES_ACCEPTED`, `LISTING_DATE`, `REVIEW_COUNT`, `AVG_STARS`
- **Update pattern**: streaming via CDC from OpenSearch → S3 → Personalize

## Solutions

### `pawmates-homefeed-v2`

- **Dataset group**: `pawmates-main`
- **Recipe**: `aws-user-personalization-v2`
- **Deployed on surfaces**: Homefeed (members), Saved search alert (candidate gen)
- **Cold-start handling**: `pawmates-cold-start-v1` fallback for users with < 5 interactions — popularity ranked by segment (role × country)
- **Last retrained**: nightly
- **Training metrics**: coverage 0.82, precision@10 0.14, MRR 0.31
- **Filters at serving**: `exclude-seen-last-14d`, `include-pet-match`, `cap-provider-4pct`

### `pawmates-cold-start-v1`

- **Dataset group**: `pawmates-main`
- **Recipe**: `aws-popularity-count`
- **Deployed on surfaces**: Homefeed (fallback), Anonymous landing featured strip
- **Filters**: `include-country-match`

## Filters

### `exclude-seen-last-14d`

- **Expression**: `EXCLUDE ItemID WHERE user_interactions.TIMESTAMP > TIME - 14 DAYS`
- **Purpose**: avoid showing the same listing repeatedly within two weeks

### `cap-provider-4pct`

- **Expression**: serving-time re-ranker in `src/homefeed/rerank.ts`, not a Personalize-native filter
- **Purpose**: prevent single-sitter dominance (the death-spiral mitigation from `homefeed-death-spiral-2025q3`)
```

---

## `observability.md` (excerpt)

```markdown
# Observability

## Dashboards

### Pawmates / Homefeed

- **Link**: https://app.datadoghq.com/dashboard/pw-home
- **Surfaces covered**: Homefeed, Saved search alert
- **Key panels**: Gini coefficient (top-10 impressions), coverage (unique items served / 7d), p95 latency, error rate, cold-start fallback rate, model version gauge
- **Owner**: Discovery team

### Pawmates / Search Relevance

- **Link**: https://app.datadoghq.com/dashboard/pw-search
- **Surfaces covered**: Search results, Zero-result fallback
- **Key panels**: nDCG@10 (vs baseline), MRR, zero-result rate, query latency, top-query volume
- **Owner**: Search team

## Monitors / alerts

### homefeed-gini-drift

- **Metric**: `pawmates.homefeed.impressions.gini_top10`
- **Threshold**: > 0.72 for 24h
- **Window**: 24h rolling
- **Routes to**: #discovery-oncall

### search-ndcg-regression

- **Metric**: `pawmates.search.ndcg_at_10`
- **Threshold**: delta vs baseline < -0.03 for 6h
- **Window**: 6h rolling
- **Routes to**: #search-oncall

## SLOs

### homefeed-latency-p95

- **Definition**: p95 homefeed render latency < 250ms over 30d
- **Current**: 238ms — green
- **Error budget**: 68% remaining

## Blind spots

- **Onboarding / paywall / email surfaces**: no dashboards today. These are the highest-conversion-weight surfaces and have zero monitoring. Build one via `/marketplace:build-observability onboarding` and `/marketplace:build-observability paywall`.
- **Cold-start conversion**: tracked globally but not decomposed by segment (role × geo × device).
```

---

## `liquidity.md` (excerpt)

```markdown
# Liquidity

## Current state

| Geo | Owners | Sitters | Ratio | Health |
|-----|--------|---------|-------|--------|
| London | 8420 | 2180 | 3.86 | thin (sitter-side) |
| Paris | 4110 | 3950 | 1.04 | healthy |
| Berlin | 2220 | 4810 | 0.46 | thin (owner-side) |
| ... | ... | ... | ... | ... |

## Seasonal patterns

- **Peak**: July-August and December — owner demand spikes, sitter-side runs out in London / Lisbon / Barcelona
- **Trough**: February-March — sitter excess capacity, owner discovery drops

## Known thin segments

- **Cat-only households in Berlin** — most sitters list as "dog-friendly", owners with only cats face 3x fewer matches
- **Long stays (> 3 weeks)** — feasibility is 1/5 of the average-length pool

## Mitigations in flight

- Sitter acquisition push in London and Lisbon (Growth team, Q4)
- Search default "dogs accepted" removed for cat-only searchers (shipped 2025-09)
```

---

## `gotchas.md` (excerpt)

```markdown
# Gotchas

## homefeed-death-spiral-2025q3 — 2025-09-14

**Symptom**: Homefeed engagement flat for 8 weeks, top-10 Gini climbed from 0.62 to 0.78, same ~100 sitters dominated impressions. Member complaints ("the feed keeps showing me the same people").

**Root cause**: Feedback loop. `pawmates-homefeed-v2` was trained on impressions + clicks without de-biasing for position. Impressions concentrated → clicks concentrated → training reinforced concentration.

**Fix**:
1. Added serving-time `cap-provider-4pct` re-ranker in `src/homefeed/rerank.ts`
2. Added `homefeed-gini-drift` monitor in Datadog
3. Added inverse-propensity weighting to the training pipeline (PAW-2011)

**Watch for**: top-10 Gini > 0.72 for 24h is the leading indicator — the earlier the catch, the cheaper the fix.

**Related rules**:
- `loop-detect-death-spirals`
- `match-cap-provider-exposure`
- `obs-track-coverage-and-gini`

---

## rank-position-missing-anonymous — 2025-07-02

**Symptom**: Discovered during a golden-set build that impressions from the anonymous landing page had `rank_position` missing for ~20% of sessions. LTR training was underweighting the anonymous cohort.

**Root cause**: Client-side intersection observer on the anonymous landing wasn't threading rank through to the analytics payload. Regression from a refactor 6 months earlier.

**Fix**: Client patch in `src/landing/feed.tsx` (PAW-1843). Retrained LTR after 14 days of clean data.

**Watch for**: periodic coverage check via `/marketplace:explore-events` on any ranked surface — at least monthly.

**Related rules**:
- `track-log-rank-position-always`
- `measure-segment-by-channel-and-visitor-profile`
```

---

## `golden-set.md` (excerpt)

```markdown
# Golden Set

## Search queries

| Query | Intent class | Must appear in top-N | Must NOT appear | Notes |
|-------|-------------|---------------------|-----------------|-------|
| "dog sitter brighton this weekend" | transactional-local-time | brighton-dog-friendly listings fri/sat/sun | cats-only, non-brighton | weekend = fri/sat/sun |
| "long stay london" | transactional-long-duration | listings with stay_duration_max > 21d | < 21d max | |
| "cat sitter berlin" | transactional-local-pet-type | berlin cats-accepted listings | dogs-only, non-berlin | thin segment |
| ... | ... | ... | ... | ... |

## Recsys intents

| Cohort / archetype | Expected top-N items | Forbidden | Notes |
|--------------------|---------------------|-----------|-------|
| new owner, anonymous, London IP, no role specified yet | London popular-this-month listings | non-London, sitter-exclusive | cold-start test |
| repeat owner, 2 dogs, cat, Brighton | dog-AND-cat-accepted listings in Brighton | dogs-only | pet match test |
| new sitter, Lisbon target, no reviews | Lisbon long-stay opportunities | no-inexperience-welcome listings | first-stay path test |
| ... | ... | ... | ... |

## Provenance

- Queries 1-20: top queries by 30d volume from OpenSearch query logs
- Queries 21-35: hand-curated by Search team for known ambiguous intents
- Queries 36-48: regression cases from past incidents (see gotchas.md)
- Recsys intents 1-10: archetypes from user research
- Recsys intents 11-22: regression cases from `homefeed-death-spiral-2025q3`
```

---

## Notes for the generator

When running bootstrap mode, **do not** produce the above verbatim. The generator should:

- Match the **shape** (headings, table layout, bulleted lists)
- Match the **depth** (concrete names, paths, URLs, monitor IDs, rule references)
- Adapt the **volume** to what the user actually has — if they only have 2 surfaces documented, don't invent 14

The example is for shape, not content.
