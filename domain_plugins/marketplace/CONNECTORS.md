# Connectors

## How tool references work

Action skills in this plugin use `~~category` as a placeholder for whatever tool you have connected in that category. For example, `~~search engine` might mean OpenSearch, Elasticsearch, Vespa, Algolia, or any other engine with an MCP server.

Skills are **tool-agnostic** — they describe workflows in terms of categories (search engine, personalisation engine, observability, data warehouse) rather than specific products. The `.mcp.json` pre-configures specific MCP servers, but any MCP server in that category works.

The three background knowledge libraries (`marketplace-pre-member-personalisation`, `marketplace-search-recsys-planning`, `marketplace-personalisation`) use **OpenSearch** and **AWS Personalize** as canonical examples because their distilled rules cite specific behaviour of those engines (BM25 scoring, analyzer pipelines, recipe selection, filter DSL, event schema). The rule *principles* still apply to compatible alternatives; the syntax-level recommendations need translation.

## Connectors for this plugin

| Category | Placeholder | Included servers | Other options |
|----------|-------------|-----------------|---------------|
| Search engine | `~~search engine` | OpenSearch\*, Elasticsearch\* | Vespa, Algolia, Typesense, Meilisearch |
| Personalisation engine | `~~personalisation engine` | AWS Personalize\* | Recombee, Vertex AI Search & Conversation, Algolia Recommend, custom |
| Product analytics | `~~product analytics` | Amplitude, Twilio Segment (CDP)\* | Mixpanel, Heap, PostHog |
| Observability | `~~observability` | Datadog\* | Grafana, New Relic, Honeycomb, CloudWatch |
| Data warehouse | `~~data warehouse` | Databricks\* | Snowflake, BigQuery, Redshift, Athena |

\* Placeholder — MCP URL not yet configured. Edit `.mcp.json` to point at your own server.

## Context extraction

The `/marketplace:bootstrap-context` command interrogates whichever connectors you have configured and generates a company-specific marketplace-context skill capturing your surfaces, events, indexes, recipes, observability, KPIs, liquidity state, gotchas, and golden set. That generated skill becomes the source of truth for everything company-specific in your marketplace — and the other six action commands check for it before running.

If you don't have connectors configured yet, `bootstrap-context` still works: it walks through the same questions manually and generates the skeleton for you to fill in.

## Read-only posture

All skills in this plugin are **read-only by default**. Every query is announced before execution, and skills never write to `~~search engine` indexes, `~~personalisation engine` datasets, `~~observability` dashboards, or `~~data warehouse` tables without an explicit user confirmation. The only files a skill writes on its own are inside the generated marketplace-context skill directory.
