---
name: bootstrap-context
description: >
  Generate or improve a company-specific marketplace-context skill by extracting knowledge from engineers and from the connected stack.

  BOOTSTRAP MODE - Triggers: "Create a marketplace context skill", "Set up marketplace personalisation for our stack", "Help me create a skill for our recsys", "Generate a marketplace context skill for [company]", "Bootstrap our recsys context"
  → Discovers surfaces / events / indexes / recipes / observability via MCPs, asks targeted questions, generates an initial skill with reference files.

  ITERATION MODE - Triggers: "Add context about [domain]", "The context skill needs more info about [topic]", "Update the marketplace context skill with [surfaces/events/indexes/recipes]", "Improve the [domain] section of the context skill"
  → Loads existing skill, asks targeted questions, appends/updates reference files.

  Use when engineers want Claude to understand their company's specific two-sided marketplace — the two sides, monetization model, surfaces, event taxonomy, index mappings, personalisation recipes, observability, KPIs, liquidity state, and known gotchas. The generated skill becomes the source of truth that every other /marketplace:* command loads before running.
argument-hint: "[bootstrap|iterate] [path]"
---

# /marketplace:bootstrap-context — Marketplace Context Extractor

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../../CONNECTORS.md).

A meta-skill that extracts company-specific marketplace knowledge from the connected stack and from a guided conversation with engineers, then generates a tailored marketplace-context skill.

## Why this exists

The marketplace plugin ships with three **general** knowledge libraries (`marketplace-pre-member-personalisation`, `marketplace-search-recsys-planning`, `marketplace-personalisation`) grounded in research and engineering literature. They describe the *principles*. They don't know the user's *specific* two-sided market, indexes, solutions, dashboards, gotchas, or golden set.

This skill bridges that gap: it generates a skill capturing everything specific to *this* company, so when the user later invokes `/marketplace:diagnose` or `/marketplace:expand-personalisation`, Claude has both the principles **and** the concrete state to act on.

## How It Works

Two modes:

1. **Bootstrap Mode** — Create a new marketplace-context skill from scratch
2. **Iteration Mode** — Improve an existing skill by adding a domain or updating a section

All other `/marketplace:*` commands check for the generated skill before running and use it as their source of company-specific truth.

---

## Bootstrap Mode

Use when: user wants to create a new marketplace-context skill for their stack.

### Phase 1: Stack Discovery

Detect which MCPs are connected. The skill works with any combination; more connected MCPs means less asking.

Check for these categories (see [CONNECTORS.md](../../CONNECTORS.md)):

- `~~search engine` — OpenSearch, Elasticsearch, Vespa, Algolia, ...
- `~~personalisation engine` — AWS Personalize, Recombee, Vertex AI, ...
- `~~product analytics` — Amplitude, Twilio Segment, Mixpanel, ...
- `~~observability` — Datadog, Grafana, New Relic, ...
- `~~data warehouse` — Databricks, Snowflake, BigQuery, ...
- `~~feature store` — Databricks Feature Store, SageMaker Feature Store, Feast, Tecton, ...

**Announce what was detected** before running any query, then proceed with targeted discovery. Examples:

**If `~~search engine` is connected:**
1. List indexes (`GET /_cat/indices` for OpenSearch/Elasticsearch, or equivalent)
2. Ask: "Which 3-5 of these are hit by production search? Which are backfill / built-once / staging?"
3. For the production indexes: pull mapping, analyzer definitions, approximate doc count, approximate size

**If `~~personalisation engine` is connected:**
1. List datasets, solutions/campaigns/recommenders, filters
2. Ask: "Which solutions are in production? Which are experimental? Which recipe does each use?"
3. For production solutions: pull recipe metadata, training metrics, dataset schema, filter definitions

**If `~~observability` is connected:**
1. List dashboards matching marketplace-relevant names: `search`, `relevance`, `homefeed`, `recsys`, `personalisation`, `conversion`, `funnel`, `recommendation`
2. For each: pull key monitors, alert thresholds, SLO definitions

**If `~~product analytics` is connected:**
1. List top events by volume in the last 7 days
2. Ask: "Which of these are impression / click / conversion events for ranked surfaces? Which lack `rank_position` or `model_version`?"

**If `~~data warehouse` is connected:**
1. List tables / views matching marketplace patterns: `events`, `impressions`, `clicks`, `bookings`, `listings`, `users`, `sessions`, `searches`
2. Sample a few rows from each to understand grain and key columns

**If `~~feature store` is connected:**
1. List feature views / feature groups / registered features
2. For each production feature: pull definition, owner, coverage, freshness, training-serving parity status
3. Cross-reference against the `~~personalisation engine` solutions to see which features feed which recipe
4. Ask: "Which features are in production? Which are experimental? Any suspected kill candidates (features not earning their maintenance)?"

Every query is **announced before running** and **read-only**. Do not write to any data source.

### Phase 2: Marketplace Fundamentals

Ask these questions conversationally (not all at once), using stack-discovery results to pre-fill context.

**Two Sides**
> "What are the two sides of your marketplace? How do they depend on each other? Is the value exchange money-for-service, service-for-service (barter), or mixed?"

Listen for:
- Side labels (e.g. "owners and sitters", "hosts and guests", "drivers and riders")
- Dependency direction (who needs whom more, and when)
- Symmetry of the value exchange
- Whether one side is typically the buyer and one the seller, or both are peers
- Frequency of participation per side (daily, seasonal, one-off)

**Monetization**
> "How does the platform make money? Subscription, per-transaction, hybrid, tiered memberships? What's the primary revenue-linked event that ranking should care about?"

Listen for:
- Subscription vs transaction fee vs hybrid vs listing fee
- Tier structure and what each tier unlocks
- Primary revenue event (membership purchased, booking confirmed, transaction completed)
- How revenue events depend on marketplace health (slow renewal game vs fast transactional)
- Whether revenue signal can be used as a ranking label (it almost always can — even for subscription, `did this session lead to first booking?` is trackable)

**Surfaces**
> "What surfaces in the product serve ranked or recommended content? Which are personalised today, which aren't?"

Listen for (prompt the user with the [surfaces-to-personalise.md](../expand-personalisation/references/surfaces-to-personalise.md) menu if needed):
- Homepage, search, category / collection pages, listing detail, messaging, email, push, onboarding, paywall, landing, saved searches, alerts, profile, zero-result fallback, abandoned-browse re-engagement, first-stay path for new suppliers
- Current personalisation state per surface (none, static, rule-based, collaborative, content-based, ML re-ranker, ML ranker, bandit)
- Which surface drives the most conversion
- Which surface is most neglected relative to its traffic

**Event Taxonomy**
> "Walk me through how impressions, clicks, and conversions are tracked. Which events are the ground truth?"

Listen for:
- Impression vs view vs hover tracking distinctions
- Whether impressions log `rank_position`, `model_version`, `surface_id`, and `request_id`
- Click attribution (to impression, to session, to user)
- Conversion events — which one is the revenue-linked one
- Known gaps and data quality issues

**KPIs and Guardrails**
> "What are the 2-3 metrics you'd protect with your life? Which ones are trending up or down right now?"

Listen for:
- North-star metric
- Supporting metrics (conversion rate by funnel stage, retention, engagement)
- Guardrails (p95 latency, error rate, infra cost)
- Current trend direction and any open investigations

**Liquidity**
> "Where is the marketplace thin? Which geos, segments, or seasons have supply-demand imbalance?"

Listen for:
- Geo thinness (city / country / region)
- Seasonal variation (peak / trough)
- Side-specific thinness (too many suppliers vs too many seekers)
- Current mitigations in flight

**Gotchas and Incidents**
> "What incidents have you had with search or personalisation? What failure patterns do you watch for?"

Listen for:
- Death spirals, popularity bias events
- Relevance regressions with root cause
- Cold-start failures
- Data quality incidents
- Feedback-loop blow-ups

### Phase 3: Generate the Skill

Create a skill directory at the path the user specified, or default to `./.claude/skills/<name>-marketplace-context/` in the current working directory.

The `<name>` should be a short kebab-case identifier — ask the user if not provided.

Structure:

```
<name>-marketplace-context/
├── SKILL.md              # Auto-generated with frontmatter + navigation
├── marketplace.md        # Two sides, monetization model, KPIs, guardrails
├── surfaces.md           # Surface inventory with current personalisation state
├── events.md             # Event taxonomy, known gaps
├── indexes.md            # ~~search engine indexes, mappings, analyzers
├── features.md           # ~~feature store registry, per-feature coverage / freshness / owner / solution mapping
├── recipes.md            # ~~personalisation engine datasets, solutions, filters
├── observability.md      # ~~observability dashboards, monitors, SLOs
├── liquidity.md          # Supply-demand state per geo / season / side
├── gotchas.md            # Known incidents and lessons (append-only)
└── golden-set.md         # Offline evaluation queries and intents
```

Use [references/skill-template.md](references/skill-template.md) for the generated `SKILL.md`.

For each reference file, use the structure and question bank in [references/sections.md](references/sections.md).

See [references/example-output.md](references/example-output.md) for a complete worked example.

Only generate files for sections the user has content for. Skip empty sections and note them in the SKILL.md navigation as "to be filled" so iteration mode can fill them later.

### Phase 4: Present and Verify

1. Show the user a one-line summary per generated section
2. Ask: "Anything missing? Anything that should be corrected?"
3. Apply corrections in place
4. Announce: "The skill is at `<path>`. Other `/marketplace:*` commands will load it automatically when they're relevant to your marketplace."

---

## Iteration Mode

Use when: user has an existing marketplace-context skill but needs to add or update a section.

### Step 1: Load Existing Skill

Ask the user for the path, or search common locations (`./.claude/skills/*-marketplace-context/`, `~/.claude/skills/*-marketplace-context/`).

Read the current SKILL.md and all section files to understand current state.

### Step 2: Identify the Gap

Ask: "Which section needs more context? What's out of date, missing, or wrong?"

Common gaps:
- A new surface was added to the product
- The event taxonomy changed (new events, renamed properties, dropped fields)
- A new `~~search engine` index or `~~personalisation engine` solution went to production
- A new observability dashboard or monitor
- A recent incident to add to `gotchas.md`
- New golden-set cases from a regression investigation
- A monetization change (new tier, price change, feature unlock change)

### Step 3: Targeted Discovery

For the identified section:

1. Query the relevant MCPs (if connected) for the current state
2. Ask section-specific questions from [references/sections.md](references/sections.md)
3. Diff against the current file to show what changed

### Step 4: Update and Present

1. Append (for `gotchas.md`, `golden-set.md`) or update (for everything else) the section file
2. Update SKILL.md's navigation section if a new file was added
3. Show the diff
4. Ask for confirmation before writing

---

## Read-Only Posture

This skill is **read-only** against every MCP it touches (`~~search engine`, `~~personalisation engine`, `~~observability`, `~~product analytics`, `~~data warehouse`). It writes files only inside the generated marketplace-context skill directory. Every query is **announced before execution**.

## Quality Checklist

Before presenting a generated skill, verify:

- [ ] `SKILL.md` has complete frontmatter (`name`, `description`)
- [ ] Two sides are named and the value-exchange asymmetry is documented in `marketplace.md`
- [ ] Monetization model is explicit in `marketplace.md` (not assumed)
- [ ] Primary revenue event is named
- [ ] At least one surface per broad category (search, feed, email/push, onboarding, paywall) in `surfaces.md`
- [ ] Impression event in `events.md` documents whether `rank_position` and `model_version` are logged
- [ ] At least one production index in `indexes.md` (if `~~search engine` connected)
- [ ] At least one production feature in `features.md` with owner, coverage, and consuming-solution mapping (if `~~feature store` connected)
- [ ] At least one production solution in `recipes.md` (if `~~personalisation engine` connected)
- [ ] At least one dashboard and one SLO in `observability.md` (if `~~observability` connected)
- [ ] `gotchas.md` has at least one entry (the user will add more over time)
- [ ] `golden-set.md` has at least 10 queries / intents (prompt to build more via `/marketplace:build-golden-set`)

## Reference Files

| File | Description |
|------|-------------|
| [references/skill-template.md](references/skill-template.md) | Template for the generated `SKILL.md` |
| [references/sections.md](references/sections.md) | Structure, questions, and MCP queries for each section |
| [references/example-output.md](references/example-output.md) | Example of a complete marketplace-context skill |

## Related Commands

- `/marketplace:explore-events` — run after bootstrap to deepen the `events.md` section with live data profiling
- `/marketplace:build-golden-set` — run after bootstrap to fill `golden-set.md` from production query logs
- `/marketplace:expand-personalisation audit` — run after bootstrap to fill the "could be personalised but isn't" backlog
