---
name: build-golden-set
description: >
  Assemble or improve a golden query set (for search) or golden intent set (for recsys) for offline evaluation of a two-sided marketplace. Use when asking "build me a golden set for search", "add regression cases from last quarter's incidents", "grow our golden set from query logs", "what queries should I test my ranking change against?", "I need an eval set for the similar-listings module", "curate offline eval cases for our homefeed recsys", or "we need a golden set before we can review relevance changes".

  Pulls candidate queries from the data warehouse query logs, clusters by intent class, adds hand-curated regression cases from the gotchas log, captures must-appear and must-not-appear assertions, records provenance, and writes to golden-set.md in the company's marketplace-context skill. Prerequisite for /marketplace:review-change on any search-branch change.
argument-hint: "[search | recsys]"
---

# /marketplace:build-golden-set — Build or Improve a Golden Evaluation Set

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../../CONNECTORS.md).

Golden sets are the foundation of pre-ship confidence for search and recsys changes. This skill assembles one from real data and known regressions, then grows it over time.

## Usage

```
/marketplace:build-golden-set search
/marketplace:build-golden-set recsys
/marketplace:build-golden-set            # asks which type
```

## Workflow

### 1. Load Company Context

Read:
- `golden-set.md` — the existing golden set, if any. Don't duplicate cases.
- `events.md` — to know which tables hold query logs and impression history
- `gotchas.md` — **most important**. Every prior incident is a regression candidate.
- `marketplace.md` — to know what the primary conversion event is
- `surfaces.md` — to pick the target surface(s)

### 2. Choose the Mode

#### Search mode

Targets `~~search engine` — builds queries + expected-result assertions.

#### Recsys mode

Targets `~~personalisation engine` — builds user archetypes + expected-recommendation assertions.

If the argument is ambiguous, ask.

### 3. Branch A — Search Golden Set

#### 3a. Identify the target surface

Which search surface? Some systems have multiple (autocomplete, full search, zero-result fallback). Default to the main full-search surface.

#### 3b. Pull candidate queries

**From `~~data warehouse`** (query logs):

```sql
-- Top queries by 30-day volume
SELECT
  query_text,
  COUNT(*) AS n,
  AVG(clicked) AS ctr,
  AVG(result_count) AS avg_result_count,
  AVG(zero_result) AS zero_result_rate
FROM search_log
WHERE event_date >= CURRENT_DATE - INTERVAL 30 DAYS
  AND surface_id = '{{surface}}'
GROUP BY 1
ORDER BY n DESC
LIMIT 100
```

Then **cluster the queries by intent class**:

- **Transactional local** — "dog sitter brighton" (strong local + entity)
- **Transactional time** — "weekend stay" (time-bound)
- **Transactional combined** — "dog sitter brighton this weekend" (local + entity + time)
- **Exploratory** — "house sit europe" (broad, discovery-seeking)
- **Known-item** — the user is looking for a specific listing they've seen before
- **Navigational** — "login", "help" (not real search; should route elsewhere)
- **Zero-intent** — empty query or single-char noise

For each cluster, pick **3-5 representative queries** — high-volume + hard-case + edge-case.

#### 3c. Add regression candidates from `gotchas.md`

For every past incident with a query signature, add the exact query that broke. These are the **most valuable** cases — they catch the same bug from reappearing.

If `gotchas.md` is thin, ask: "Any past search regressions you remember? Give me the query that broke."

#### 3d. Add negative tests

**Critical**: negative tests (`must NOT appear`) catch more regressions than positive tests. Examples:

- For "dog sitter brighton", a cat-only listing MUST NOT appear in top-5
- For "long stay london" (21+ days), short-stay-only listings MUST NOT appear in top-10
- For "safe home" queries, listings flagged for moderation MUST NOT appear at all

For each cluster, propose at least one negative test.

#### 3e. Capture assertions

For each query, record:

```markdown
| Field | Content |
|-------|---------|
| Query | "{{text}}" |
| Intent class | {{class}} |
| Volume | {{30d count}} |
| Must appear in top-N | {{listing_ids or feature filter, e.g., "geo=brighton AND pet_friendly=dog"}} |
| Must NOT appear | {{listing_ids or filter}} |
| Ordering constraint | {{e.g., "listing X must rank above listing Y"}} (optional) |
| Provenance | {{log | hand-curated | regression-from gotchas.md#case}} |
| Notes | {{edge cases, gotchas, ambiguity}} |
```

Prefer **feature-filter assertions** ("any listing matching `geo=brighton AND pet=dog`") over **listing-ID assertions** — they survive listing churn.

#### 3f. Present and write

Show the draft to the user, ask for corrections, then write to `golden-set.md` in the context skill (or to a path the user specifies if no context skill exists).

### 4. Branch B — Recsys Golden Set

#### 4a. Identify the target surface

Homefeed? Similar listings? Saved search alert? Email? Each has different archetypes.

#### 4b. Pull candidate user archetypes

**From `~~data warehouse`**:

```sql
-- Sample users from each key cohort
WITH cohorts AS (
  SELECT
    user_id,
    CASE
      WHEN DATE_DIFF(CURRENT_DATE, signup_date, DAY) < 7 THEN 'new_paid'
      WHEN DATE_DIFF(CURRENT_DATE, signup_date, DAY) < 90 THEN 'recent_paid'
      WHEN first_booking_date IS NULL THEN 'paid_no_booking'
      ELSE 'repeat'
    END AS cohort,
    home_country,
    role,
    primary_pet_type
  FROM users
  WHERE active = TRUE
)
SELECT * FROM cohorts
SAMPLE 1 ROWS PER cohort, role, home_country
```

For each cohort × role × key geo, pick a representative user and define the archetype.

#### 4c. Add cold-start archetypes

Cold-start is the highest-leverage case for recsys golden sets. Always include:

- Anonymous visitor, new country, inferred role, no history
- Registered but < 5 interactions, role inferred from onboarding
- Paid but zero bookings, 2 weeks old
- Long-dormant user, no interactions in 90+ days (near-cold-start)

#### 4d. Add regression archetypes from `gotchas.md`

Every recsys incident that affected a cohort is a candidate archetype. Add one user per cohort-based regression.

#### 4e. Capture expected top-N and forbidden sets

For each archetype, record:

```markdown
| Field | Content |
|-------|---------|
| Archetype | {{cohort × role × geo × key constraint}} |
| Expected top-N features | {{e.g., "majority should be role=opposite AND geo=same-country AND pet_match=true"}} |
| Forbidden features | {{e.g., "no listings flagged cold-start-only", "no listings with 0 reviews"}} |
| Diversity constraint | {{optional — e.g., "top-10 must include ≥ 3 distinct suppliers"}} |
| Provenance | {{synthetic | sampled from logs | regression from gotchas.md#case}} |
| Notes | {{edge cases}} |
```

Prefer **feature-based** expected sets over **item-ID-based** sets — listings churn, features don't.

#### 4f. Present and write

Same as Branch A.

### 5. Grow Over Time

Golden sets are living documents. Every diagnosed incident (via `/marketplace:diagnose`) should add at least one new case. Prompt the user:

> "The diagnosis revealed a regression in {{pattern}}. Do you want to add {{n}} case(s) to the golden set?"

### 6. Maintain Quality

Apply these quality rules:

- **Minimum size**: 10 cases. Below that, coverage is too thin to be reliable.
- **Maximum manageable size**: around 300 cases. Beyond that, run eval sample-based.
- **Balance**: no more than 30% of cases from a single intent class / archetype.
- **At least 20% negative tests**: they catch more regressions than positive tests.
- **At least 10% from `gotchas.md`**: regression prevention is the whole point.
- **Provenance tracked for every case**: if you don't know where a case came from, you can't defend it when it breaks.

## Read-only posture

This skill reads from `~~search engine`, `~~data warehouse`, and `~~personalisation engine` but never writes. File writes are limited to `golden-set.md` in the user's context skill (and only with confirmation).

## Examples

### Build a search golden set from scratch

```
/marketplace:build-golden-set search
```

Pulls 30d of queries, clusters, proposes cases, captures assertions, writes to context skill.

### Grow an existing golden set with regression cases

```
/marketplace:build-golden-set search
```

If a golden set exists, go into iteration mode: enumerate unresolved cases from `gotchas.md`, propose new tests, merge.

### Build a recsys golden set for a new surface

```
/marketplace:build-golden-set recsys
```

Ask which surface, pull archetypes, capture expected top-N features, write.

## Tips

- **Start with gotchas.md.** Every past incident is a case you already know should pass.
- **Prefer feature-based assertions** over listing-ID-based ones. IDs churn; features don't.
- **Always include anonymous-visitor and cold-start cohorts** for recsys — they're the cases most likely to fail silently.
- **Always include a navigational case** for search — "login" should NEVER return listings, and this is a common regression point after query rewrites.
- **Don't skip negative tests.** A golden set with only positive tests misses 60%+ of real regressions.
- **Re-run the golden set weekly**, not just pre-ship. Silent degradation happens.

## Related Commands

- `/marketplace:bootstrap-context` — run first to ensure a home for the golden set
- `/marketplace:review-change` — the primary consumer of this artefact
- `/marketplace:diagnose` — every diagnosis session is an opportunity to add cases
