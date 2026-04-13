---
name: build-observability
description: >
  Design observability for a search, recommender, or personalisation surface in a two-sided marketplace. Use when asking "build a dashboard for the homefeed", "what monitors do we need for search relevance?", "we have no observability on the paywall surface", "design SLOs for the recsys", "what metrics should I track for a new ranker?", "build alerting for death-spiral detection", or "what's the minimum observability for a ranked surface at production scale?".

  Produces a design for `~~observability` dashboards, monitors, SLOs, and alert routing tailored to the surface type (search, recsys, pre-member, hybrid). Canonical output format is Datadog when that's the connected provider. Covers the standard metric set for ranked surfaces — Gini, coverage, top-N staleness, nDCG@k, freshness, cold-start conversion, booking conversion, side-cap balance, p95 latency, error rate, model version gauge, filter miss rate — plus surface-specific additions. Emits dashboard JSON and monitor definitions when the observability MCP is connected.
argument-hint: "<surface-name | surface-type>"
---

# /marketplace:build-observability — Design Observability for a Surface

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../../CONNECTORS.md).

Design the dashboards, monitors, and SLOs that catch regressions in a marketplace surface. Outputs a tailored metric set, alert thresholds, and routing — and emits dashboard JSON + monitor definitions when `~~observability` is connected.

## Usage

```
/marketplace:build-observability <surface-name | surface-type>
```

Examples:

```
/marketplace:build-observability homefeed
/marketplace:build-observability search-results
/marketplace:build-observability paywall
/marketplace:build-observability onboarding-flow
/marketplace:build-observability search          # surface type, for a generic search surface
```

## Workflow

### 1. Load Company Context

Read:
- `surfaces.md` — confirm the surface exists and classify its type
- `observability.md` — see what's already monitored (avoid duplication)
- `events.md` — confirm which events can feed metrics
- `marketplace.md` — pull the north-star metric and guardrails
- `gotchas.md` — incidents tell you what failure modes to monitor against

### 2. Classify the Surface

Match the surface to one or more **surface types**. Each type has a default metric set.

| Surface type | Examples | Default metrics |
|-------------|----------|-----------------|
| **Search** | search results, autocomplete, zero-result fallback | nDCG@k (vs baseline), MRR, zero-result rate, query-type distribution, p95 query latency |
| **Recsys** | homefeed, similar items, saved search alerts, email recs | Gini top-N, coverage 7d, top-N staleness, cold-start fallback rate, model version gauge, serving p95 latency, filter miss rate |
| **Hybrid** | search-plus-recs blended surface | both sets |
| **Pre-member** | onboarding, paywall, landing hero | conversion rate by cohort, drop-off per step, paywall touch rate, time-to-convert |
| **Lifecycle** | email, push, re-engagement | open rate, click rate, conversion-after-touch, unsubscribe rate |
| **Operational** | any | p95 latency, error rate, throughput, request volume, infra cost |

### 3. Design the Dashboard

Structure every dashboard in three tiers:

#### Tier 1 — Health at a glance (top of dashboard)

Four widgets, always:

1. **Volume** — requests / impressions per minute. The first thing to check if anything looks weird.
2. **Latency** — p95 serving latency. SLO line overlaid.
3. **Errors** — error rate (4xx, 5xx, timeouts). SLO line overlaid.
4. **Traffic split** — current experiment arm allocation if an A/B is running.

#### Tier 2 — Surface-specific signals (middle)

Add the surface-type metrics from the table above. Each widget should have:
- The current value
- A 7-day trend
- A threshold line (from `obs-slice-metrics-by-segment` — always thresholded, never unbounded)

**For search surfaces, always include**:
- nDCG@10 vs baseline (requires golden set)
- Zero-result rate by query type
- Top-N query volume and its latency

**For recsys surfaces, always include**:
- Top-10 Gini coefficient (death-spiral monitor — per `loop-detect-death-spirals`)
- Distinct items served / 7d (coverage — per `obs-track-coverage-and-gini`)
- Cold-start fallback rate
- Model version gauge (which model is serving?)
- Filter miss rate

**For pre-member surfaces, always include**:
- Funnel drop-off per step
- Paywall touch rate
- Conversion rate decomposed by cohort — anonymous source, inferred role, geo

#### Tier 3 — Per-segment decomposition (bottom)

A row of metrics decomposed by segment: role × geo × device × user age bucket. This is where biases hide.

### 4. Design Monitors

Every dashboard has a matching set of **monitors**. Thresholds come from the rules; routing comes from `observability.md` → team ownership.

**For any surface**:
- `{{surface}}-latency-p95` — p95 > SLO for 15 minutes → page
- `{{surface}}-error-rate` — error rate > 0.5% for 10 minutes → page
- `{{surface}}-volume-drop` — volume < 70% of 7d trailing average for 30 minutes → page (catches instrumentation breaks)

**For search surfaces**:
- `{{surface}}-ndcg-regression` — nDCG@10 delta < -0.03 vs baseline for 6h → page
- `{{surface}}-zero-result-spike` — zero-result rate > 2x trailing for 1h → notify

**For recsys surfaces**:
- `{{surface}}-gini-drift` — top-10 Gini > 0.72 for 24h → page (the death-spiral leading indicator)
- `{{surface}}-coverage-collapse` — distinct items 7d drops > 30% vs 30d trailing → page
- `{{surface}}-cold-start-fallback-rate` — fallback rate deviates ± 20% from steady state → notify
- `{{surface}}-model-version-stuck` — no new model versions for N days → notify (if retraining is expected)

**For pre-member surfaces**:
- `{{surface}}-conversion-rate-regression` — stage conversion rate drops > MDE vs 14d trailing → page
- `{{surface}}-cohort-disparity` — conversion rate between two key cohorts diverges > X → notify

### 5. Define SLOs

Propose 1-3 SLOs per surface. Prefer **fewer, higher-quality** SLOs over many weak ones.

For a ranked surface, a healthy SLO set looks like:

1. **Latency SLO** — "p95 serving latency < {{ms}} over 30d"
2. **Availability SLO** — "successful responses ≥ 99.9% over 30d"
3. **Quality SLO** (if golden set exists) — "nDCG@10 ≥ baseline - 0.02 over 7d"

Each SLO needs:
- **Definition** (explicit metric and window)
- **Target** (numeric)
- **Error budget** (implied from target + window)
- **Burn rate alerts** (short window and long window)

### 6. Alert Routing

From `observability.md` team ownership. Every monitor routes to:
- A **channel** (for notify-level) — Slack / email / PagerDuty low-sev
- A **person / rotation** (for page-level) — oncall rotation

Never route a page-level monitor to a channel-only destination. Never route a notify-level monitor to a rotation.

### 7. Produce Artefacts

#### If `~~observability` is connected (e.g., Datadog):

Emit:
- **Dashboard JSON** using the provider's dashboard API schema
- **Monitor definitions** using the provider's monitor API schema
- **SLO definitions** using the provider's SLO API schema

When the connected provider is Datadog, use the Datadog dashboard/monitor/SLO schemas. For other providers (Grafana, New Relic, Honeycomb, CloudWatch), emit the equivalent schema for that provider — or a tool-agnostic markdown form if the provider schema is unknown.

**Do not deploy automatically.** Write files to a local `./observability/{{surface}}/` directory and print a manifest of what was written. The user applies via their infrastructure tooling.

#### If not connected:

Emit the same artefacts as **tool-agnostic markdown** — a table of widgets, a table of monitors, a table of SLOs — suitable for translation to whatever observability stack the user runs.

### 8. Update the Context Skill

After generation, offer to update `observability.md` in the context skill with:
- The new dashboard link (once deployed)
- The new monitors and their thresholds
- The new SLOs and their error budgets
- Any blind spots that remain

## Read-only posture

This skill is **read-only** against `~~observability`. It fetches existing dashboards, monitors, and SLOs to avoid duplication but does **not** deploy anything automatically. All artefacts are written as files for the user to review and deploy via their own tooling.

## Examples

### Build for the homefeed

```
/marketplace:build-observability homefeed
```

Returns a three-tier dashboard design (volume/latency/errors/traffic, Gini/coverage/staleness/fallback-rate, segment decomposition), a set of monitors including the death-spiral detector, 2-3 SLOs, and emitted JSON.

### Build for a new surface with no prior monitoring

```
/marketplace:build-observability paywall
```

Routes to pre-member surface type. Designs funnel-stage dashboards, cohort-decomposition panels, and cohort-disparity monitors. Since the paywall likely has zero existing monitoring, this is a greenfield design.

### Build for a generic surface type

```
/marketplace:build-observability recsys
```

Returns a template dashboard + monitor set for any recsys surface, to be adapted. Useful when designing observability before a new surface is named.

## Tips

- **Don't build every possible metric** — pick the ones that change your decision. Unused dashboards rot.
- **Every monitor needs an owner** — an alert with no owner is an alert that will be muted.
- **Page sparingly** — most monitors should be notify-level. Reserve pages for SLO-burning or user-visible regressions.
- **Always include the Gini + coverage pair on recsys** — this is the #1 missing observability pair, and the one that catches death spirals.
- **Always include per-segment decomposition** — Simpson's paradox hides regressions that look fine globally.
- **Treat `obs-slice-metrics-by-segment` as the baseline rule** — all metrics should be decomposable by role × geo × device.

## Related Commands

- `/marketplace:bootstrap-context` — run first to discover what already exists
- `/marketplace:diagnose` — run after ship to confirm the monitors are catching what you expect
- `/marketplace:review-change` — pair with any ranker change to add monitors alongside
