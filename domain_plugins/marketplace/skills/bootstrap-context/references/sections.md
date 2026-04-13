# Section Guide

For each file in the generated marketplace-context skill, this document defines:

- **Purpose** — what the section captures
- **Structure** — the headings to use
- **Questions** — what to ask the user (in iteration-friendly order)
- **MCP queries** — what to pull from the connected stack, if available
- **Quality checks** — what must be present before the section is considered complete

All MCP queries are **read-only** and must be **announced before execution**.

---

## `marketplace.md`

**Purpose**: Record the fundamentals — who, how they exchange value, how the platform makes money, what the north-star is, and what guardrails protect it. This section is the frame every other section lives inside.

### Structure

```markdown
# Marketplace Fundamentals

## Two sides

- **{{side-a}}** (e.g., "pet owners") — {{description, frequency, primary motivation}}
- **{{side-b}}** (e.g., "pet sitters") — {{description, frequency, primary motivation}}

### Dependency

{{who needs whom most, when, and what breaks if one side is thin}}

### Value exchange

{{money-for-service | service-for-service | hybrid}} — {{one paragraph explaining}}

## Monetization

- **Model**: {{subscription | per-transaction | hybrid | tiered}}
- **Tiers** (if any): {{list with what each unlocks}}
- **Primary revenue event**: `{{event_name}}` — {{what it means and where it's tracked}}
- **Secondary revenue events**: {{list}}
- **Ranking label candidates**: {{which events can be used as supervised labels}}

## North-star metric

{{definition, how it's calculated, where it's dashboarded, current trend}}

## Supporting metrics

- **Conversion funnel**: anonymous → registered → paid → first conversion → repeat → retained
- **Engagement**: {{session depth, return frequency}}
- **Quality**: {{satisfaction, complaint rate, refund rate}}

## Guardrails

- **Performance**: p95 latency ≤ {{ms}}, error rate ≤ {{%}}
- **Cost**: {{infra budget or cost-per-request target}}
- **Fairness**: {{supply exposure caps, any regulatory constraints}}
```

### Questions

1. "What are the two sides of your marketplace? What does each side do?"
2. "Who needs whom more? What happens when one side is thin?"
3. "Is the value exchange money-for-service, service-for-service, or hybrid?"
4. "How does the platform make money? Subscription, per-transaction, hybrid, tiered?"
5. "What tiers exist? What does each unlock?"
6. "What's the primary revenue-linked event that ranking should care about? Where is it tracked?"
7. "What's your north-star metric? Where is it dashboarded? What direction is it trending?"
8. "Which latency, error rate, or cost thresholds would trigger an auto-rollback?"

### MCP queries

- **`~~data warehouse`**: `SHOW TABLES LIKE '%revenue%'` / `%subscription%` / `%booking%` / `%transaction%` to ground the revenue event discussion
- **`~~observability`**: list dashboards matching north-star metric name

### Quality checks

- [ ] Both sides are named with specific labels (not "buyers and sellers")
- [ ] Dependency direction is documented
- [ ] Monetization model is one of the standard categories
- [ ] Primary revenue event is a concrete event name, not a metric
- [ ] North-star metric is named and its dashboard is linked
- [ ] At least one performance guardrail is numeric

---

## `surfaces.md`

**Purpose**: Enumerate every surface serving ranked or recommended content, and record the current personalisation state of each. This section is the working set for `/marketplace:expand-personalisation`.

### Structure

```markdown
# Surfaces

| Surface | Position in journey | Current state | Traffic | Conversion weight | Personalisation algo | Owner |
|---------|-------------------|---------------|---------|-------------------|---------------------|-------|
| Homepage logged-out | anonymous landing | static | high | medium | — | Growth |
| Homefeed logged-in | registered pre-paid | ML ranker | high | high | content + recsys | Discovery |
| Search results | active | ML reranker | very high | very high | BM25 + LTR | Search |
| Listing detail related | active | rule-based | medium | medium | popularity | Listing |
| Abandoned-browse email | off-site re-engagement | none | low | low | — | Lifecycle |
| ... | ... | ... | ... | ... | ... | ... |

## Per-surface detail

### {{surface name}}

- **Position in journey**: {{anonymous | registered | paid | repeat | retained}}
- **Current state**: {{none | static | rule-based | collaborative | content-based | ML reranker | ML ranker | bandit}}
- **Ranking label (if ML)**: {{event_name}}
- **Cold-start handling**: {{description}}
- **Known issues**: {{list}}
- **Links**: {{code path | index | solution | dashboard}}
```

### Questions

1. "What surfaces in the product serve ranked or recommended content? I'll prompt with a menu if needed." (Use [../expand-personalisation/references/surfaces-to-personalise.md](../../expand-personalisation/references/surfaces-to-personalise.md) as the prompting menu.)
2. "For each surface, what's its current personalisation state — none, static, rule-based, or ML?"
3. "Which surface drives the most conversion? Which is most neglected relative to its traffic?"
4. "Which surfaces feed each other? (e.g., homefeed clicks train search-detail related)"

### MCP queries

- **`~~product analytics`**: list surface_ids in the last 7 days by volume to cross-check completeness
- **`~~search engine`**: `_search` log sampling (if log shipping is configured) to discover surfaces that route through search
- **`~~personalisation engine`**: list solutions/campaigns and the surface_ids they're deployed on

### Quality checks

- [ ] At least one surface per broad category (search, feed, email/push, onboarding, paywall)
- [ ] Each surface's current state is explicit (not "I think it's personalised")
- [ ] Conversion weight is ranked relative to other surfaces
- [ ] Ownership is named (team or person) for at least the top-5 surfaces

---

## `events.md`

**Purpose**: Document the event taxonomy for impressions, clicks, conversions, and any upstream signals. This section grounds every `/marketplace:explore-events`, `/marketplace:diagnose`, and `/marketplace:build-golden-set` invocation.

### Structure

```markdown
# Event Taxonomy

## Impression events

### `{{impression_event_name}}`

- **Definition**: {{when fired}}
- **Properties**: `user_id`, `session_id`, `surface_id`, `item_id`, `rank_position`, `model_version`, `request_id`, ...
- **Volume**: {{per day}}
- **Source**: {{client | server}}
- **Known gaps**: {{e.g., "rank_position missing for ~20% of anonymous sessions"}}

## Click / engagement events

...

## Conversion events

### `{{primary_conversion_event}}`

- **Revenue-linked**: yes / no
- **Attribution window**: {{duration}}
- **Dedup logic**: {{description}}

## Negative signals

- **Skip / scroll-past**: {{tracked? how?}}
- **Dwell-below-threshold**: {{tracked?}}
- **Report / block / dismiss**: {{tracked?}}

## Known quality issues

1. {{issue 1 with impact}}
2. {{issue 2 with impact}}
```

### Questions

1. "Walk me through how impressions are tracked. Client-side, server-side, or both?"
2. "Does every impression log `rank_position`, `model_version`, `surface_id`, `request_id`?"
3. "How is a click attributed back to an impression? What's the key?"
4. "What's the primary conversion event for ranking? What's its dedup logic?"
5. "Do you track negative signals? Skips, scroll-past, dismissals?"
6. "What quality issues do you know about? Missing properties, volume drops, schema drift?"

### MCP queries

- **`~~product analytics`** (Amplitude): `/api/2/events/list` to enumerate top events by volume
- **`~~product analytics`** (Segment tracking plan): fetch tracking plan for declared properties
- **`~~data warehouse`**: profile impression / click / conversion tables for null rate of `rank_position`, `model_version`, `user_id`, `item_id`, `surface_id`
  ```sql
  SELECT
    COUNT(*) AS total,
    COUNT(rank_position) / COUNT(*) AS rank_position_coverage,
    COUNT(model_version) / COUNT(*) AS model_version_coverage,
    COUNT(user_id) / COUNT(*) AS user_id_coverage
  FROM impressions
  WHERE event_date >= CURRENT_DATE - INTERVAL 7 DAYS
  ```

### Quality checks

- [ ] Impression, click, and conversion event names are listed
- [ ] Each has a property list including `rank_position` and `model_version` (or an explicit "missing")
- [ ] Attribution logic is documented for clicks
- [ ] Primary revenue event is explicitly mapped to a ranking label
- [ ] At least one known quality issue is listed (every system has them)

---

## `indexes.md`

**Purpose**: Document every production `~~search engine` index that powers a ranked surface. Grounds `/marketplace:review-change` for relevance changes.

### Structure

```markdown
# Search Indexes

## `{{index_name}}`

- **Purpose**: {{what it powers}}
- **Surfaces using it**: {{list}}
- **Doc count**: {{approx}}
- **Size**: {{approx GB}}
- **Shards / replicas**: {{n / m}}
- **Update pattern**: {{real-time | batch daily | etc.}}

### Mapping summary

| Field | Type | Analyzer | Notes |
|-------|------|----------|-------|
| title | text | english | multi-field with keyword |
| location | geo_point | — | |
| ... | ... | ... | ... |

### Analyzer definitions

{{paste the critical custom analyzers, or link to the file in the app repo}}

### Known quirks

- {{e.g., "legacy field `desc` is deprecated but still indexed, ignore in new queries"}}
```

### Questions

1. "Which indexes power production search? Which are backfill / built-once / staging?"
2. "What's the update pattern for each — real-time CDC, batch daily, event-driven?"
3. "Any legacy fields or analyzers with known quirks?"
4. "Any fields that are mandatory for a correct query (e.g., tenant filter, geo filter)?"

### MCP queries

- **`~~search engine`** (OpenSearch/Elasticsearch):
  - `GET /_cat/indices?v` — list all indexes with sizes
  - `GET /{{index}}/_mapping` — pull mapping
  - `GET /{{index}}/_settings` — pull analyzer definitions
  - `GET /{{index}}/_count` — doc count

### Quality checks

- [ ] At least one production index is documented
- [ ] Mapping summary lists the critical searchable fields
- [ ] Analyzer quirks are noted
- [ ] Update pattern is explicit

---

## `features.md`

**Purpose**: Record the state of the `~~feature store` (or feature catalogue) — every feature in production, its owner, coverage, freshness, training-serving-parity status, and which `~~personalisation engine` solutions consume it. Grounds `/marketplace:review-change` for feature-level changes and `/marketplace:expand-personalisation` for proposals that require new features. Pairs with the `marketplace-recsys-feature-engineering` knowledge library — that library has the principles; this file has the state.

### Structure

```markdown
# Feature Store

## Registry

### `{{feature_name}}`

- **Type**: {{categorical | numeric | multi-hot | embedding | derived-score}}
- **Source**: {{raw listing metadata | listing photo | sitter wizard | event stream | derived from other features}}
- **Extraction**: {{pipeline path, model (if learned), batch or streaming}}
- **Entity**: {{user | item | pair | context}}
- **Consuming solutions**: {{list of ~~personalisation engine solutions}}
- **Consuming indexes**: {{list of ~~search engine indexes if the feature is indexed}}
- **Coverage**: {{% non-null in live data over 7d}}
- **Freshness**: {{max age at serving time — SLA + observed p95}}
- **Training-serving parity**: {{served from same store? | offline-only? | online-only?}}
- **Owner**: {{team or person}}
- **Registered at**: {{date}}
- **Known drift**: {{notes}}
- **Notes**: {{anything else}}

## Per-entity index

### Listing features

| Feature | Type | Coverage | Freshness | Owner | Consumers |
|---------|------|---------|-----------|-------|-----------|
| ... | ... | ... | ... | ... | ... |

### User features

| Feature | Type | Coverage | Freshness | Owner | Consumers |
|---------|------|---------|-----------|-------|-----------|
| ... | ... | ... | ... | ... | ... |

### Pair features (u2u, u2i at scoring time)

| Feature | Type | Coverage | Freshness | Owner | Consumers |
|---------|------|---------|-----------|-------|-----------|
| ... | ... | ... | ... | ... | ... |

## Feature pipelines

- **Vision extraction**: {{pipeline: CLIP / fine-tuned model / vendor API, frequency, cost}}
- **Text extraction**: {{pipeline: sentence-transformer, topic model, etc.}}
- **Structured transforms**: {{H3 geo-hashing, stay-duration binning, pet triple parsing}}
- **Derived composition**: {{two-tower, ANN shelf, subscore blends}}

## Known gaps

1. {{feature we know we need but haven't built}}
2. {{feature that exists but doesn't clear the maintenance bar}}

## Kill candidates

{{features under review for deprecation, with attributed lift measurement}}

## Training-serving skew log

{{append-only log of observed skew incidents and their root cause}}
```

### Questions

1. "What's in your feature store today? Which features are in production?"
2. "For each production feature: what entity, what type, what pipeline, what coverage, what freshness?"
3. "Which features power which `~~personalisation engine` solution? Any features with no consumer?"
4. "Any features you suspect are redundant with a popularity baseline — i.e., they don't beat a feature-ablated variant?"
5. "Any features you can't actually serve at inference at the required latency?"
6. "What's your governance model — who can write, who reviews, how are schemas versioned, is there a single registry?"
7. "What's the extraction pipeline for vision, text, and derived scores? Any batch vs streaming split worth knowing?"
8. "Any known training-serving skew incidents?"
9. "Any feature gaps you know about — signals humans use that your model can't see?"

### MCP queries

- **`~~feature store`**:
  - `list_feature_views` / `list_features` / `list_entities`
  - `get_feature_view({{name}})` to pull definition, schema, owner
  - `describe_feature({{name}})` for lineage

- **`~~data warehouse`**: profile coverage for the top-used features
  ```sql
  SELECT
    feature_name,
    COUNT(*) AS total,
    COUNT(feature_value) * 1.0 / COUNT(*) AS coverage,
    MAX(feature_asof_ts) AS freshest,
    MIN(feature_asof_ts) AS oldest
  FROM feature_values
  WHERE snapshot_date = CURRENT_DATE - 1
  GROUP BY 1
  ORDER BY coverage DESC
  ```

- **`~~observability`**: list monitors matching `feature` / `drift` / `coverage` / `psi` to see what's already watched

### Quality checks

- [ ] At least one production feature per entity type (user, item, pair)
- [ ] Every feature has an owner and at least one consuming solution (or is flagged as orphan)
- [ ] Training-serving parity is explicit per feature (same store, offline-only, or online-only)
- [ ] Known gaps section has at least one entry (every system has them)
- [ ] Kill candidates section exists, even if empty (per `prove-kill-features-that-dont-earn-maintenance`)

---

## `recipes.md`

**Purpose**: Document every production `~~personalisation engine` dataset, solution / campaign / recommender, and filter. Grounds `/marketplace:review-change` for personalisation changes.

### Structure

```markdown
# Personalisation Recipes

## Datasets

### `{{dataset_name}}` ({{INTERACTIONS | USERS | ITEMS}})

- **Schema fields**: {{list}}
- **Update pattern**: {{streaming via PutEvents | batch via dataset import | hybrid}}
- **Volume**: {{events / day}}
- **Retention**: {{days}}

## Solutions / Campaigns

### `{{solution_name}}`

- **Dataset group**: {{name}}
- **Recipe**: {{e.g., aws-user-personalization-v2}}
- **Deployed on surfaces**: {{list}}
- **Cold-start handling**: {{description}}
- **Last retrained**: {{date}}
- **Training metrics**: {{coverage, precision@k, mrr}}
- **Filters applied at serving**: {{list}}

## Filters

### `{{filter_name}}`

- **Expression**: {{the filter DSL}}
- **Purpose**: {{what it enforces — cold-start segment, side cap, exclusion, etc.}}
```

### Questions

1. "Which solutions are in production? Which are experimental?"
2. "Which recipe does each use? Any custom recipe or only managed?"
3. "How is cold-start handled — filters, fallback solution, rule-based override?"
4. "Any serving-time filters to enforce side balance, exposure caps, freshness?"

### MCP queries

- **`~~personalisation engine`** (AWS Personalize via AWS MCP):
  - `list_dataset_groups`, `list_datasets`, `list_solutions`, `list_campaigns`, `list_filters`
  - `describe_solution({{solution_arn}})` — pull recipe + training metrics
  - `describe_campaign({{campaign_arn}})` — pull min provisioned TPS, model version

### Quality checks

- [ ] At least one production solution is documented
- [ ] Its recipe is named (not "some ML thing")
- [ ] Cold-start strategy is explicit
- [ ] Serving-time filters are listed

---

## `observability.md`

**Purpose**: Document dashboards, monitors, and SLOs that catch relevance or personalisation regressions. Grounds `/marketplace:build-observability` and `/marketplace:review-change`.

### Structure

```markdown
# Observability

## Dashboards

### `{{dashboard_name}}`

- **Link**: {{url}}
- **Surfaces covered**: {{list}}
- **Key panels**: {{list of key metrics — Gini, coverage, p95 latency, nDCG@k, cold-start conversion, etc.}}
- **Owner**: {{team}}

## Monitors / alerts

### `{{monitor_name}}`

- **Metric**: {{metric name}}
- **Threshold**: {{condition}}
- **Window**: {{duration}}
- **Routes to**: {{oncall team / channel}}

## SLOs

### `{{slo_name}}`

- **Definition**: {{e.g., "p95 search latency < 200ms over 30d"}}
- **Current**: {{current state}}
- **Error budget**: {{remaining}}

## Blind spots

- {{surfaces / metrics that are NOT monitored today}}
```

### Questions

1. "Which dashboards cover search or personalisation? Paste links."
2. "Which monitors would auto-page someone if relevance regressed or a recsys feed went stale?"
3. "What SLOs exist? Any with error budget exhausted right now?"
4. "Which surfaces have NO monitoring today?"

### MCP queries

- **`~~observability`** (Datadog):
  - `list_dashboards` filtered by keywords
  - `get_monitor({{monitor_id}})` for key monitors
  - `list_slos` to enumerate current SLOs and error budgets

### Quality checks

- [ ] At least one dashboard per major surface
- [ ] At least one auto-paging monitor for relevance or recsys
- [ ] At least one SLO is documented
- [ ] Blind spots are explicitly listed (never empty — every system has them)

---

## `liquidity.md`

**Purpose**: Document the current supply-demand state per side / geo / season. Grounds `/marketplace:diagnose liquidity` and `/marketplace:expand-personalisation` feasibility scoring.

### Structure

```markdown
# Liquidity

## Current state (as of {{date}})

| Geo | {{side-a}} count | {{side-b}} count | Ratio | Health |
|-----|----------------|----------------|-------|--------|
| {{region 1}} | ... | ... | ... | healthy / thin / saturated |
| ... | ... | ... | ... | ... |

## Seasonal patterns

- **Peak**: {{months}} — {{which side is in short supply}}
- **Trough**: {{months}} — {{which side has excess capacity}}

## Known thin segments

- {{segment 1 with what's thin}}
- {{segment 2}}

## Mitigations in flight

- {{current supply-acquisition or demand-seeding effort}}
```

### Questions

1. "Where is the marketplace thin right now? Which geos?"
2. "What's the seasonal pattern? Summer peak? Winter trough?"
3. "Which side runs out first in peak season? Which in trough?"
4. "What mitigations are currently in flight?"

### MCP queries

- **`~~data warehouse`**:
  ```sql
  SELECT geo, side_a_count, side_b_count, side_a_count / NULLIF(side_b_count, 0) AS ratio
  FROM marketplace_liquidity_snapshot
  WHERE snapshot_date = CURRENT_DATE - 1
  ORDER BY ratio DESC
  ```

### Quality checks

- [ ] At least 5 geos listed with a ratio
- [ ] Seasonal pattern is described
- [ ] At least one thin segment is explicit
- [ ] At least one in-flight mitigation is named

---

## `gotchas.md`

**Purpose**: Append-only log of incidents, failure patterns, and hard-won lessons. Grounds every `/marketplace:diagnose` invocation — most incidents repeat.

### Structure

```markdown
# Gotchas

## {{incident-short-name}} — {{date}}

**Symptom**: {{what broke}}

**Root cause**: {{one or two sentences}}

**Fix**: {{what was done}}

**Watch for**: {{the leading indicator that would catch this earlier next time}}

**Related rules**: {{rule references from marketplace-* knowledge libraries}}

---
```

### Questions

1. "What incidents have you had with search or personalisation? Even small ones."
2. "What failure patterns do you watch for now?"
3. "Anything that's a 'oh, that thing again' in your team?"

### MCP queries

None — gotchas are narrative, not discoverable from the stack.

### Quality checks

- [ ] At least one entry (prompt the user — every system has at least one)
- [ ] Each entry has a leading indicator (the whole point is to catch it earlier next time)

---

## `golden-set.md`

**Purpose**: The offline evaluation corpus — queries for search, intents for recsys. Grounds `/marketplace:review-change` and `/marketplace:build-golden-set`.

### Structure

```markdown
# Golden Set

## Search queries

| Query | Intent class | Must appear in top-N | Must NOT appear | Notes |
|-------|-------------|---------------------|-----------------|-------|
| "dog sitter brighton this weekend" | transactional local | {{listing ids}} | {{listing ids}} | weekend = fri/sat/sun |
| ... | ... | ... | ... | ... |

## Recsys intents

| Cohort / user archetype | Expected top-N items | Forbidden items | Notes |
|------------------------|---------------------|-----------------|-------|
| new owner, anonymous, Brighton IP | {{listing ids}} | {{listing ids}} | cold-start test |
| ... | ... | ... | ... |

## Provenance

- {{where each query came from — production logs, hand-curated, regression case}}
```

### Questions

1. "Do you have an existing golden set? Where?"
2. "What queries / intents would you absolutely break on if a change hurt relevance?"
3. "Any regression cases from past incidents?"

### MCP queries

- **`~~data warehouse`**: sample top-N queries by volume and by bounce rate from the last 30 days
- **`~~search engine`**: query log sampling (if shipped to logs)

### Quality checks

- [ ] At least 10 queries or intents
- [ ] At least 2 with `must NOT appear` constraints (negative tests are the ones that catch the most regressions)
- [ ] Provenance is documented per case
- [ ] At least one case from a past incident

---

## General rules

- Fill sections **only when you have content** for them. Empty sections become noise.
- Prefer **concrete pointers** (file paths, dashboard URLs, monitor IDs, solution ARNs) over abstract descriptions.
- When a section is mostly unknown, write a TODO-flagged stub so iteration mode can fill it later. Don't fake content.
- When the user's answers conflict with MCP discovery, **trust the MCP** and flag the discrepancy.
