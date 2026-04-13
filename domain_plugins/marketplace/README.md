# Marketplace Plugin

An action toolkit for engineers planning, diagnosing, improving, and operating **search, recommender, and pre-member personalisation systems** in two-sided trust marketplaces. Seven user-invokable commands, a context-extractor meta-skill that captures your specific stack, and three research-grounded knowledge libraries working together.

## Installation

```
claude plugins add pproenca/dot-claude marketplace
```

## What It Does

This plugin transforms Claude into a marketplace relevance + personalisation collaborator. It helps you:

- Find new places to personalise beyond the obvious listing feed
- Diagnose cold-start, conversion-funnel, feed-staleness, relevance-regression, and liquidity-imbalance problems against live data
- Review search and personalisation changes before shipping against golden sets and monitor thresholds
- Design Datadog observability and golden evaluation sets for every surface
- Bootstrap a company-specific context skill that makes everything else sharper

The plugin composes **three layers**:

1. **Action commands** — what you type when you want Claude to do something. Structured workflows, connector-aware, always announce read queries before executing.
2. **Context extractor** (`/marketplace:bootstrap-context`) — interrogates your stack and generates a company-specific marketplace-context skill with your surfaces, events, indexes, recipes, observability, KPIs, liquidity state, gotchas, and golden set. Mirrors the `data` plugin's `data-context-extractor` pattern.
3. **Knowledge libraries** — three distilled rule libraries grounded in published research and engineering literature. Auto-loaded when relevant. They cover the pre-member journey, search and retrieval on OpenSearch, and the AWS Personalize lifecycle.

### With your stack connected (example)

Pre-configure MCP servers for OpenSearch, AWS Personalize, Twilio Segment, Amplitude, Databricks, and Datadog — or any compatible alternatives. Claude will:

- Query your event streams and warehouse to ground every recommendation in live data
- Inspect your index mappings, Personalize solutions, Datadog monitors and SLOs
- Run offline evaluations against your golden set before shipping a change
- Announce every read query before executing (read-only by default)

### Without your stack connected

You can still use every command. Action skills will ask for data you paste or upload, walk the same workflows manually, and ship the same research-grounded recommendations.

## Commands

| Command | Description |
|---------|-------------|
| `/marketplace:bootstrap-context` | Bootstrap or iterate a company-specific marketplace-context skill by interrogating your stack |
| `/marketplace:expand-personalisation` | Audit surfaces that aren't yet personalised, or design personalisation for a named surface |
| `/marketplace:diagnose` | Diagnose cold-start, conversion, feed-health, relevance-regression, or liquidity-imbalance symptoms |
| `/marketplace:explore-events` | Profile event streams — grain, ID stability, feedback-loop bias, coverage gaps, impression-click ordering |
| `/marketplace:review-change` | Pre-ship review of an OpenSearch relevance change or an AWS Personalize change |
| `/marketplace:build-observability` | Design Datadog dashboards and monitors for a surface's relevance and personalisation health |
| `/marketplace:build-golden-set` | Assemble or improve a golden query set (search) or intent set (recsys) for offline evaluation |

## Knowledge Libraries (auto-loaded)

| Skill | Rules | Role |
|-------|-------|------|
| `marketplace-pre-member-personalisation` | 53 in 10 categories | Anonymous landing through onboarding, registration, and the paywall. Anonymous signal inference, side-specific validation, information-asymmetry closure, social proof, conversion psychology, identity stitching. Grounded in Cialdini, Kahneman, Roth, Fogg, Bandura, Slovic, NN/g, and the Airbnb/DoorDash engineering literature. |
| `marketplace-search-recsys-planning` | 57 in 10 categories | Planning and design for search and recommender systems. User-intent framing, surface taxonomy, index design, query understanding, retrieval strategy, ranking, search-plus-recs blending, measurement, dashboard and alerting. Canonical example: OpenSearch. |
| `marketplace-personalisation` | 49 in 9 categories | Designing, building, and improving the personalisation lifecycle. Event tracking, dataset and schema design, two-sided matching, cold start, feedback loops, bias control, recipe selection, serving-time re-ranking, observability. Canonical example: AWS Personalize. |

Each library ships with a `SKILL.md` entry point, an `AGENTS.md` long-form table of contents, one `references/` file per rule (with primary-source citations), planning and improving playbooks, living gotchas logs, and authoring templates. The action commands above invoke these libraries as their research backbone.

## Example Workflows

### Bootstrap your context on a new codebase

```
You: /marketplace:bootstrap-context bootstrap

Claude: [connects to configured MCPs]
       → [lists available OpenSearch indexes, Personalize solutions, Datadog dashboards]
       → [asks: "Which 3-5 indexes are hit by production search?"
                "What's your event taxonomy for impressions and clicks?"
                "Which surfaces are personalised today, which aren't?"
                "What's your monetization model -- subscription, transaction, hybrid?"
                "What are the two sides of your marketplace and how do they depend
                 on each other?"]
       → [generates ./.claude/skills/<name>-marketplace-context/ with surfaces.md,
          events.md, indexes.md, recipes.md, observability.md, kpis.md, liquidity.md,
          gotchas.md, golden-set.md pre-filled from the conversation and the MCP
          discovery]
```

### Find new places to personalise

```
You: /marketplace:expand-personalisation audit

Claude: [loads <your-name>-marketplace-context for current state]
       → [loads references/surfaces-to-personalise.md (30+ candidate surfaces)]
       → [ranks non-personalised surfaces by leverage x feasibility x risk]
       → [produces backlog: "1. Onboarding flow branches (high leverage, feasibility
           gated on role-inference quality). 2. Abandoned-browse re-engagement email
           (high leverage, blocked on identity-stitching gap in events.md). 3. ..."]
       → [for the top 3: drafts dataset shape, algo choice, guardrails, A/B design,
           grounded in marketplace-personalisation and marketplace-pre-member rules]
```

### Diagnose a stalling surface

```
You: /marketplace:diagnose the homefeed has been getting blander for 8 weeks, same
     100 sitters keep dominating impressions

Claude: [routes to feed-health branch]
       → [queries ~~observability for Gini, coverage, top-N staleness]
       → [queries ~~data warehouse for impression and click distribution]
       → [loads marketplace-personalisation playbooks/improving.md]
       → [identifies: "classic death-spiral pattern, top-10 Gini trending from 0.62
           to 0.78 over 8 weeks, impressions concentrating 3x faster than clicks"]
       → [recommends rules: loop-detect-death-spirals + match-cap-provider-exposure
           + obs-track-coverage-and-gini]
       → [drafts ship-or-kill experiment against current production]
```

### Review a relevance change before ship

```
You: /marketplace:review-change adding synonym map "doggy -> dog" and query rewrite
     that expands "weekend" to "(friday OR saturday OR sunday)"

Claude: [routes to ~~search engine relevance branch]
       → [loads golden-set.md from context skill]
       → [runs offline diff against current mapping via ~~search engine MCP]
       → [loads rules: query-curate-synonyms-by-domain, rank-tune-bm25-parameters-last,
           measure-track-ndcg-mrr-zero-result-rate]
       → [flags: "weekend expansion inflates recall 2.4x on precision queries;
           nDCG@10 drops 4% on the 'specific dates' cluster"]
       → [reminds: log change in decisions log per plan-maintain-a-decisions-log]
       → [advises: gate behind experiment before full roll-out]
```

### Explore an event stream

```
You: /marketplace:explore-events homefeed impressions

Claude: [queries ~~product analytics for impression event schema and volumes]
       → [queries ~~data warehouse to profile grain, nulls, ID stability,
           impression-click ordering]
       → [flags: "22% of impressions lack rank_position -- feedback-loop bias risk:
           training data will underweight the tail"]
       → [flags: "user_id is null for 8% of anonymous sessions -- identity stitching
           gap blocks deduplication for the golden-set builder"]
       → [recommends rules: track-use-stable-opaque-item-ids,
           track-log-rank-position-always]
```

## Plugin Shape

```
anonymous visitor  ─►  registered  ─►  paid member  ─►  booked  ─►  retained
       ▲                                    ▲                           ▲
       │                                    │                           │
  pre-member-personalisation   search-recsys-planning       personalisation
                                      │                           │
                                      └───────── shared ──────────┘

          All three are invoked by the action commands above
                             │
                             ▼
              bootstrap-context captures your stack
              everything else uses that context
```

## Connecting Your Stack

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](CONNECTORS.md).

This plugin works best when connected to your production stack via MCP servers. Categories:

- **Search engine**: OpenSearch, Elasticsearch, Vespa, Algolia, Typesense
- **Personalisation engine**: AWS Personalize, Recombee, Vertex AI, Algolia Recommend
- **Product analytics**: Twilio Segment (CDP) + Amplitude (query), Mixpanel, PostHog
- **Observability**: Datadog, Grafana, New Relic, Honeycomb, CloudWatch
- **Data warehouse**: Databricks, Snowflake, BigQuery, Redshift

Edit `.mcp.json` to point at your own servers. All skills are read-only by default and announce every query before executing.

## Conventions

Each knowledge library follows the [dev-skill](../../plugins/dev-skill) `distillation` discipline:

- Rules live in `references/<prefix>-<verb>-<noun>.md`, one per file, named after the action they enforce
- Each rule cites its primary source (AWS docs, OpenSearch docs, KDD/RecSys papers, engineering blogs, consumer-trust research)
- Categories are ordered by **cascade impact** — upstream rule failures poison downstream rules, so earlier categories carry higher impact
- Living artefacts (`gotchas.md`, decisions logs, golden query set) carry context across releases. Skills explicitly tell Claude to read them before suggesting and to update them after every shipped change

## Related Plugins

- [`dev-skill`](../../plugins/dev-skill) — the discipline framework the knowledge libraries are built on (`/dev-skill:validate`, `/dev-skill:eval`, `/dev-skill:evolve`)
- [`dev-workflow`](../../plugins/dev-workflow) — TDD, debugging, and verification workflows that compose with the diagnostic playbooks
- The `data` plugin — the inspiration for this plugin's shape (action commands + knowledge skills + connector abstraction + context extractor)
