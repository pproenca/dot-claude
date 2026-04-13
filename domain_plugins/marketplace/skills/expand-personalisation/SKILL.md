---
name: expand-personalisation
description: >
  Audit surfaces across a two-sided marketplace to find places that could be personalised but aren't, or design the personalisation approach for a named surface from scratch. Use when asking "where should we personalise next?", "how should we personalise the onboarding flow?", "what could we do beyond the listing feed?", "our paywall is static — how would we personalise it?", "give me a backlog of personalisation opportunities ranked by impact", or "design a personalisation approach for the abandoned-browse email".

  Covers every surface where a two-sided marketplace can deploy personalisation beyond the obvious listing feed — onboarding branches, paywall timing and copy, trust-copy variants, abandoned-browse re-engagement, saved search alerts, landing hero, first-stay paths for new suppliers, review ordering, zero-result fallback, related listings, messaging templates, push timing, profile-completion nudges, seasonal campaigns, and more.

  Grounds every recommendation in the research-based marketplace-personalisation and marketplace-pre-member-personalisation libraries, and checks the company's generated marketplace-context skill for feasibility before proposing.
argument-hint: "[audit | <surface-name>]"
---

# /marketplace:expand-personalisation — Find or Design Personalisation Opportunities

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../../CONNECTORS.md).

Two modes:

- **`audit`** — rank surfaces that aren't yet personalised but could be, by leverage × feasibility × risk. Produces a backlog.
- **`<surface-name>`** — design the personalisation approach for one specific surface from scratch. Produces a ship-ready proposal.

Both modes load the company's generated marketplace-context skill (if present) to ground the work in real state rather than guesses.

## Usage

```
/marketplace:expand-personalisation audit
/marketplace:expand-personalisation onboarding-flow
/marketplace:expand-personalisation abandoned-browse-email
/marketplace:expand-personalisation paywall-screen
```

## Workflow

### 1. Load Company Context

Check for a marketplace-context skill (in `./.claude/skills/*-marketplace-context/` and `~/.claude/skills/*-marketplace-context/`).

**If present**, read:
- `marketplace.md` for monetization model and north-star
- `surfaces.md` for current personalisation state across the product
- `events.md` for what data exists per surface
- `liquidity.md` to understand which segments are thin
- `gotchas.md` for known failure modes

**If absent**, run `/marketplace:bootstrap-context bootstrap` first — or fall back to a generic conversation, collecting the same information interactively before proceeding.

### 2. Branch by Mode

#### Mode A — Audit

1. **Enumerate candidate surfaces** from [references/surfaces-to-personalise.md](references/surfaces-to-personalise.md). This is the master menu of 30+ surfaces a two-sided marketplace can personalise beyond listings.

2. **Cross-reference with `surfaces.md`**. For each candidate, classify current state:
   - `covered` — already personalised (skip)
   - `static` — exists but not personalised (candidate)
   - `missing` — doesn't exist in the product (candidate, but document as a product gap)

3. **Score each candidate** on three axes:

   | Axis | Scale | Question |
   |------|-------|----------|
   | **Leverage** | 1-5 | How much would personalising this move the north-star? (Traffic × conversion weight × per-user touches) |
   | **Feasibility** | 1-5 | What data and infrastructure exist to support it today? Are the right events logged? Is identity stitching solid enough? Is there a production path to serving? |
   | **Risk** | 1-5 (lower is better) | Exposure to feedback-loop bias, fairness concerns, cold-start cliffs, moderation cost, or confusing UX |

   The score is `leverage × feasibility ÷ risk`, with ties broken by feasibility.

4. **Produce a ranked backlog** as a table:

   ```markdown
   | Rank | Surface | Leverage | Feasibility | Risk | Score | Notes |
   |------|---------|---------|-------------|------|-------|-------|
   | 1    | ... | 5 | 4 | 2 | 10.0 | ... |
   ```

5. **For the top 3-5**, produce a one-page **ship-ready proposal** each (see Mode B below).

#### Mode B — Design for a Named Surface

1. **Classify the surface** into a journey stage:
   - `anonymous` — no user identity (landing, logged-out homepage, anonymous search)
   - `registered pre-paid` — identified but not yet paid (onboarding, paywall, free tour)
   - `paid pre-active` — paid but not yet engaged (first-stay path, profile completion)
   - `active` — actively using the product (search, feed, messaging)
   - `re-engagement` — lapsed (push, email, abandoned-browse)
   - `retained` — steady-state (renewal, upsell, referral)

2. **Load the right knowledge library** based on stage:
   - `anonymous` or `registered pre-paid` → `marketplace-pre-member-personalisation`
   - `paid pre-active` / `active` / `retained` → `marketplace-personalisation`
   - Mixed or unclear → load both

3. **Determine the personalisation approach**:

   | Approach | When to use |
   |----------|------------|
   | **Rule-based** | No labels available, strong priors (e.g., paywall copy by inferred role) |
   | **Content-based** | Items have strong features, few labels (e.g., similar-listing module) |
   | **Collaborative** | Plenty of interactions, users are dense (homefeed, saved-search alerts) |
   | **Contextual bandit** | Exploration matters more than exploitation (new surface launch, cold stock) |
   | **ML ranker / reranker** | Mature surface, plenty of data, need fine control (search, homefeed) |
   | **Hybrid** | Almost always in practice |

4. **Draft the proposal** with these sections:

   ```markdown
   ## {{surface name}}

   ### Why personalise this

   {{1-paragraph business case, linked to north-star and any gotchas}}

   ### Approach

   {{approach from the table above, plus why}}

   ### Data requirements

   - **Events needed**: {{list, with gaps flagged}}
   - **Identity requirements**: {{anonymous-safe / requires stitching}}
   - **Training data volume**: {{sufficient / needs seeding / cold-start only}}

   ### Cold-start strategy

   {{how the surface works when labels are missing}}

   ### Guardrails

   - **Fairness**: {{supply exposure cap, side balance}}
   - **Feedback-loop protection**: {{inverse propensity, re-rank cap, exploration slots}}
   - **Quality floors**: {{min rating, min verification, etc.}}

   ### Observability

   {{required dashboards and monitors, linking to observability.md}}

   ### Experiment design

   - **Primary outcome**: {{metric}}
   - **Guardrails**: {{list}}
   - **MDE**: {{minimum detectable effect and power math}}
   - **Cohort**: {{who sees the treatment}}
   - **Ship criterion**: {{decision rule}}

   ### Risks

   {{list}}

   ### Grounding rules

   - {{rule-reference-1}} — {{one-line why}}
   - {{rule-reference-2}} — {{one-line why}}
   ```

5. **Validate the proposal** against the gotchas log: is there a similar past incident? If so, reference it and adapt.

### 3. Present and Persist

1. Show the audit table or the per-surface proposal to the user
2. Ask: "Which of these would you like to commit to? I can record the choice in `surfaces.md` as `planned` state"
3. On approval, update `surfaces.md` in the context skill with `state: planned` and a link to the proposal

## Read-only posture

This skill reads from `~~product analytics`, `~~data warehouse`, and the generated marketplace-context skill, but does not execute any writes against those MCPs. The only files it writes are to `surfaces.md` in the context skill — and only after explicit user confirmation to commit a planned personalisation.

## Examples

### Audit

```
/marketplace:expand-personalisation audit
```

Returns a ranked backlog of non-personalised surfaces with scores and top-5 ship-ready proposals.

### Design for a specific surface

```
/marketplace:expand-personalisation paywall-screen
```

Returns a ship-ready proposal for personalising the paywall — approach, data requirements, cold-start, guardrails, observability, experiment design, risks.

### Design for a surface that doesn't exist yet

```
/marketplace:expand-personalisation abandoned-browse-email
```

If the surface is `missing` from `surfaces.md`, treat it as a new product gap and include a product recommendation: "build the surface first, then personalise".

## Tips

- **Cold-start first**: the surfaces with the highest uplift are usually pre-paid / cold-start (onboarding branches, paywall copy, first-stay path) because they set the anchor for everything after. Bias toward these.
- **Feasibility beats leverage** when feasibility is low — a high-leverage idea with missing events is vaporware.
- **Never propose ML on a surface with no observability** — build monitoring first, or propose it as part of the ship plan.
- **Don't duplicate existing work**: `surfaces.md` is the source of truth, check it before proposing.
- **Prefer the simplest approach that works**: rule-based first if priors are strong, bandits before ML, ML only when the data supports it.

## Reference Files

| File | Description |
|------|-------------|
| [references/surfaces-to-personalise.md](references/surfaces-to-personalise.md) | Master menu of 30+ surfaces a two-sided marketplace can personalise beyond listings, organized by journey stage |

## Related Commands

- `/marketplace:bootstrap-context` — run first to ground this in real state
- `/marketplace:explore-events <surface>` — run to close feasibility gaps before committing
- `/marketplace:build-observability <surface>` — run alongside any proposal that goes to ship
