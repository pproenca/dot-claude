---
name: explore-events
description: >
  Profile event streams that power search, recommendations, and personalisation in a two-sided marketplace. Use when asking "what events do we have for the homefeed?", "are our impressions logging rank_position?", "does our click data have a feedback-loop bias?", "what's the schema of our conversion events?", "are anonymous sessions getting user_ids?", "what's wrong with our impression-click ordering?", or "profile the events for surface X before I build against them".

  Checks grain, ID stability, property completeness (rank_position, model_version, request_id, surface_id), impression-click ordering, feedback-loop bias (are impressions logged even when rank comes from the recsys itself?), and coverage gaps by side, geo, segment, or device. Flags quality issues and recommends fixes grounded in the marketplace knowledge libraries. Event-centric cousin of the data plugin's /explore-data.
argument-hint: "<surface | event-name | table>"
---

# /marketplace:explore-events — Profile Marketplace Event Streams

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../../CONNECTORS.md).

Profile an event stream for a surface, an event name, or a specific table. Understand the shape, quality, and biases of the data **before** building anything on top of it. This is the foundation every other action command depends on.

## Usage

```
/marketplace:explore-events homefeed-impressions
/marketplace:explore-events listing_impressed
/marketplace:explore-events main.marketplace.impressions
/marketplace:explore-events search
```

## Workflow

### 1. Load Company Context

Read the `<company>-marketplace-context` skill if present — especially `events.md`, `surfaces.md`, and `gotchas.md`. Any known issues listed there are candidates to verify first.

If no context skill exists, prompt the user to run `/marketplace:bootstrap-context` first, or fall back to direct-from-stack discovery.

### 2. Resolve the Target

Parse the argument and resolve to one or more concrete event streams:

- **Surface name** (e.g., `homefeed`) → list all events that surface fires (from `surfaces.md` or discovery)
- **Event name** (e.g., `listing_impressed`) → profile that single event across all surfaces
- **Table name** (e.g., `main.marketplace.impressions`) → profile the warehouse table backing the event

If the target is ambiguous, list candidates and ask the user to pick.

### 3. Discover Schema

**If `~~product analytics` is connected:**
1. Query the tracking plan (e.g., Amplitude event schema API, Twilio Segment tracking plan) to pull declared properties
2. List declared types, required / optional, deprecation flags

**If `~~data warehouse` is connected:**
1. Describe the backing table (`DESCRIBE TABLE ...`)
2. Note schema drift vs the tracking plan

**If neither:**
Ask the user to paste a sample event or a schema description.

Present the resolved schema as a table before running any profile queries.

### 4. Profile the Stream

Run the standard profile checks, announcing each query before execution.

#### 4a. Volume and trend

```sql
SELECT
  DATE(event_time) AS day,
  COUNT(*) AS events,
  COUNT(DISTINCT user_id) AS distinct_users,
  COUNT(DISTINCT session_id) AS distinct_sessions
FROM {{table}}
WHERE event_time >= CURRENT_DATE - INTERVAL 14 DAYS
GROUP BY 1
ORDER BY 1
```

Look for: sudden drops (instrumentation break), gradual growth (healthy), spikes (incidents).

#### 4b. Property completeness

For ranked-surface events, the critical properties are `rank_position`, `model_version`, `surface_id`, `request_id`. Check coverage:

```sql
SELECT
  COUNT(*) AS total,
  COUNT(rank_position) * 1.0 / COUNT(*) AS rank_position_coverage,
  COUNT(model_version) * 1.0 / COUNT(*) AS model_version_coverage,
  COUNT(surface_id) * 1.0 / COUNT(*) AS surface_id_coverage,
  COUNT(request_id) * 1.0 / COUNT(*) AS request_id_coverage,
  COUNT(user_id) * 1.0 / COUNT(*) AS user_id_coverage
FROM {{table}}
WHERE event_time >= CURRENT_DATE - INTERVAL 7 DAYS
```

**Flag levels**:
- **Red** (< 90% coverage on any critical property): ranking / training / eval is compromised. Fix before any ML work.
- **Amber** (90-99%): segment-by-missing-property to understand whether the gap is systematic.
- **Green** (≥ 99%): good enough for most purposes.

#### 4c. ID stability

Check that `user_id` is stable across sessions and devices:

```sql
SELECT
  session_id,
  COUNT(DISTINCT user_id) AS user_ids_per_session
FROM {{table}}
WHERE event_time >= CURRENT_DATE - INTERVAL 1 DAY
GROUP BY 1
HAVING user_ids_per_session > 1
LIMIT 20
```

Sessions with > 1 `user_id` indicate cookie drift, shared devices, or logout-in-session. Flag if > 1% of sessions.

#### 4d. Impression-click ordering

Check that every click has a preceding impression in the same session:

```sql
WITH clicks_with_impression AS (
  SELECT
    c.*,
    MAX(i.event_time) AS last_impression_time
  FROM clicks c
  LEFT JOIN impressions i
    ON i.user_id = c.user_id
    AND i.item_id = c.item_id
    AND i.event_time <= c.event_time
    AND i.event_time >= c.event_time - INTERVAL 30 MINUTE
  WHERE c.event_time >= CURRENT_DATE - INTERVAL 1 DAY
  GROUP BY c.user_id, c.item_id, c.event_time, c.session_id
)
SELECT
  COUNT(*) AS total_clicks,
  COUNT(last_impression_time) AS clicks_with_impression,
  COUNT(*) - COUNT(last_impression_time) AS orphan_clicks
FROM clicks_with_impression
```

**Orphan clicks** (clicks without a preceding impression) are a red flag for:
- Client-side impression tracking failure (most common)
- Cross-tab navigation that breaks the join
- Bots / abuse (if the volume is very high)

#### 4e. Feedback-loop bias

**The most important check** for ranked surfaces. Are impressions logged even when the ranking came from the recsys itself?

This requires that `model_version` is populated on impressions. If it is:

```sql
SELECT
  model_version,
  COUNT(*) AS impressions,
  AVG(rank_position) AS mean_rank,
  COUNT(DISTINCT item_id) AS distinct_items
FROM impressions
WHERE event_time >= CURRENT_DATE - INTERVAL 7 DAYS
  AND surface_id = '{{surface}}'
GROUP BY 1
ORDER BY impressions DESC
```

If `distinct_items` is declining over time or `mean_rank` is compressing toward 1, the model is recommending a narrowing set — a death-spiral leading indicator.

Also compute a Gini coefficient for the top-N item distribution:

```sql
WITH item_volumes AS (
  SELECT
    item_id,
    COUNT(*) AS n
  FROM impressions
  WHERE event_time >= CURRENT_DATE - INTERVAL 7 DAYS
    AND surface_id = '{{surface}}'
    AND rank_position <= 10
  GROUP BY 1
),
ranked AS (
  SELECT
    n,
    ROW_NUMBER() OVER (ORDER BY n) AS rank,
    COUNT(*) OVER () AS total_items,
    SUM(n) OVER () AS total_volume
  FROM item_volumes
)
SELECT
  1 - 2 * SUM((total_items - rank + 1) * n) * 1.0 / (total_items * total_volume) AS gini
FROM ranked
```

Gini > 0.72 for top-10 is the death-spiral threshold per `loop-detect-death-spirals`.

#### 4f. Coverage by segment

Decompose coverage by role, geo, device, and user age:

```sql
SELECT
  user_role,
  geo_country,
  device_type,
  COUNT(*) AS events,
  COUNT(rank_position) * 1.0 / COUNT(*) AS rank_coverage
FROM impressions
WHERE event_time >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY 1, 2, 3
HAVING events > 1000
ORDER BY rank_coverage ASC
LIMIT 20
```

Segments with < 90% rank_coverage are systematic instrumentation gaps — bias risk for every downstream model.

### 5. Present Findings

Structure the output as:

```markdown
## Event Profile: {{target}}

### Schema
{{table of declared properties}}

### Volume
- 7-day average: {{n}} events / day
- Trend: {{flat | growing | declining | spiky}}
- Distinct users / day: {{n}}

### Quality
- **Critical properties**: {{red | amber | green}} per property with coverage %
- **ID stability**: {{issues found, if any}}
- **Impression-click ordering**: {{% orphan clicks}}
- **Feedback-loop signal**: {{Gini, distinct-items trend, model_version spread}}
- **Segment gaps**: {{worst segments by rank_coverage}}

### Issues
{{numbered list with severity}}

### Recommended rules
- {{rule-reference}} — {{one-line why}}
- ...

### Suggested follow-ups
- {{what /marketplace:* command to run next}}
```

### 6. Update the Context Skill

If the context skill exists, offer to update `events.md` and `gotchas.md` with the findings. Ask before writing.

## Read-only posture

Every query above is a **read** against `~~data warehouse`, `~~product analytics`, or `~~search engine`. Announce before executing. Do not propose any `INSERT`, `UPDATE`, `DELETE`, or `PutEvents`.

## Examples

### Profile a surface

```
/marketplace:explore-events homefeed
```

Profiles all events firing on the homefeed surface — impression, click, conversion — and reports quality per event.

### Profile a single event

```
/marketplace:explore-events listing_impressed
```

Profiles one event name across all surfaces.

### Profile a table

```
/marketplace:explore-events main.marketplace.impressions
```

Profiles the backing table directly, useful when the event name doesn't match the table name.

## Tips

- **Run this before every new ML project.** It's cheap and it catches silent instrumentation breaks.
- **Re-run monthly on critical surfaces.** Regression from refactors is a top cause of training data drift (see `rank-position-missing-anonymous` pattern).
- **Coverage by segment is where biases hide.** A 98% global coverage can hide a 60% segment coverage. Always decompose.
- **If `model_version` isn't logged, you can't do feedback-loop analysis at all.** Fix this first — it's the single highest-leverage instrumentation change for any ranked surface.

## Related Commands

- `/marketplace:bootstrap-context` — run first to ground this in current state
- `/marketplace:diagnose` — the natural next step if quality issues point to a specific failure mode
- `/marketplace:build-golden-set` — depends on healthy event data from this skill
