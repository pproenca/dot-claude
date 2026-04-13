# Generated Skill Template

Use this template for the `SKILL.md` inside the generated `<name>-marketplace-context/` directory. Fill in placeholders marked `{{like-this}}`.

---

```markdown
---
name: {{name}}-marketplace-context
description: >
  Company-specific marketplace context for {{company}}. Load this skill whenever working on search, recommendations, personalisation, cold-start, conversion funnel, feed health, relevance regression, or liquidity for {{company}}'s two-sided marketplace ({{side-a}} and {{side-b}}).

  Contains the authoritative record of surfaces, event taxonomy, ~~search engine indexes, ~~personalisation engine recipes, observability, KPIs, liquidity state, known gotchas, and the golden evaluation set. Every /marketplace:* command that targets {{company}}'s systems should load this skill first.

  Triggers: any task mentioning {{company}}, {{side-a}}, {{side-b}}, or the production surfaces listed in surfaces.md.
---

# {{company}} Marketplace Context

Company-specific record for {{company}}'s two-sided marketplace between {{side-a}} and {{side-b}}.

> This skill holds company-specific facts. For general best-practice principles, the generic `marketplace-pre-member-personalisation`, `marketplace-search-recsys-planning`, and `marketplace-personalisation` skills are loaded alongside.

## Marketplace at a glance

- **Two sides**: {{side-a}} ↔ {{side-b}}
- **Value exchange**: {{value-exchange}} (e.g., `service-for-service`, `money-for-service`, `hybrid`)
- **Monetization**: {{monetization-model}} (e.g., `subscription`, `per-transaction`, `hybrid`, `tiered subscription with per-sit fee`)
- **Primary revenue event**: {{primary-revenue-event}} (e.g., `booking_confirmed`, `membership_purchased`)
- **North-star metric**: {{north-star}}
- **Production stack**: {{search-engine}}, {{personalisation-engine}}, {{analytics-stack}}, {{observability-stack}}, {{warehouse-stack}}

## Navigation

| File | What it contains |
|------|-----------------|
| [marketplace.md](marketplace.md) | Two sides, monetization, KPIs, guardrails |
| [surfaces.md](surfaces.md) | Surface inventory with current personalisation state |
| [events.md](events.md) | Event taxonomy and known gaps |
| [indexes.md](indexes.md) | ~~search engine indexes, mappings, analyzers |
| [recipes.md](recipes.md) | ~~personalisation engine datasets, solutions, filters |
| [observability.md](observability.md) | ~~observability dashboards, monitors, SLOs |
| [liquidity.md](liquidity.md) | Supply-demand state per geo / season / side |
| [gotchas.md](gotchas.md) | Known incidents and lessons (append-only) |
| [golden-set.md](golden-set.md) | Offline evaluation queries and intents |

## How to use

- **Before making any company-specific suggestion**, read the relevant section file. Do not rely on assumptions.
- **When diagnosing**, start with `gotchas.md` — most incidents repeat.
- **When shipping a change**, check `observability.md` for the monitors that would catch regressions, and `golden-set.md` for offline eval.
- **When adding new personalisation**, check `surfaces.md` for what's already covered.

## Keeping this skill up to date

Update via:

- `/marketplace:bootstrap-context iterate` to refresh a specific section
- `/marketplace:explore-events <surface>` to deepen `events.md`
- `/marketplace:build-golden-set` to grow `golden-set.md`

Append to `gotchas.md` after every incident, no matter how small.

## Related skills

- `marketplace-pre-member-personalisation` (general, auto-loaded)
- `marketplace-search-recsys-planning` (general, auto-loaded)
- `marketplace-personalisation` (general, auto-loaded)
```

---

## Frontmatter rules

The generated `description` must include:

- At least one company-specific term (name, two-side labels) so auto-discovery triggers on real tasks
- A short list of trigger topics ("search, recommendations, personalisation, cold-start, conversion, feed health, relevance regression, liquidity")
- A pointer to the section files so Claude knows to read them
- A note that this skill holds company-specific facts distinct from the general libraries

## Description length

Keep the description 3-6 sentences. Dense enough for triggering, short enough to be readable.

## What not to include in `SKILL.md`

- Don't inline section content — keep `SKILL.md` as a navigation + frontmatter-only document
- Don't list individual events, dashboards, indexes, or recipes in `SKILL.md` — they belong in the section files
- Don't include any plugin-level best practices — those live in the general libraries
