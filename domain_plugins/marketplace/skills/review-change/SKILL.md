---
name: review-change
description: >
  Pre-ship review of a search relevance change or a personalisation change in a production two-sided marketplace. Use when asking "review this synonym update before I ship", "sanity-check this mapping change", "would this analyzer tweak hurt anything?", "check this recipe swap before we retrain", "review this new serving-time filter", "does this ranking change pass our guardrails?", "run offline eval on this change", "sanity-check this ranker retrain", or "what could go wrong with this relevance tweak?".

  Routes to the right branch (search change vs personalisation change), pulls the relevant golden-set for offline eval, checks observability monitor thresholds and SLO headroom, walks the relevant rule checklist from the marketplace knowledge libraries, and produces a structured go / no-go recommendation with an experiment design when ship risk is non-trivial.
argument-hint: "<change-description | PR-link>"
---

# /marketplace:review-change — Pre-Ship Review of a Relevance or Personalisation Change

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../../CONNECTORS.md).

Stress-test a proposed change to search or personalisation **before** it ships. Pulls the golden set, runs offline eval, walks the rule checklist, checks observability for blind spots, and recommends a ship decision.

## Usage

```
/marketplace:review-change <free-form description of the change, or a PR link>
```

Examples:

```
/marketplace:review-change adding synonym map "doggy -> dog" and expanding "weekend" to "(friday OR saturday OR sunday)"
/marketplace:review-change swapping homefeed recipe from user-personalization-v1 to user-personalization-v2
/marketplace:review-change adding serving-time filter "cap-provider-4pct" to homefeed
/marketplace:review-change https://github.com/company/repo/pull/1234
```

## Workflow

### 1. Load Company Context

Read the `<company>-marketplace-context` skill:
- `indexes.md` — if the change touches `~~search engine`
- `recipes.md` — if the change touches `~~personalisation engine`
- `golden-set.md` — the offline eval corpus
- `observability.md` — the monitors that should catch a regression
- `gotchas.md` — any prior incidents matching the change type

### 2. Classify the Change

| Type | Signal |
|------|--------|
| **`~~search engine` relevance** | synonym, analyzer, mapping, BM25, LTR model, query rewrite, filter clause movement, boost weight |
| **`~~personalisation engine` change** | recipe swap, dataset schema, filter DSL, re-ranker, cold-start solution, feature set |
| **Observability / infrastructure** | monitor threshold, alert routing, dashboard only — route to `/marketplace:build-observability` instead |

If ambiguous, ask. If the change touches both types, split the review into two passes.

### 3. Branch A — Search Change

#### 3a. Summarise the change

Restate the change in structured form:
- **File(s) affected**: e.g., analyzer JSON, query builder, mapping template
- **Scope**: which index(es), which field(s), which query type
- **Reversibility**: trivial to roll back, or requires re-index?

#### 3b. Run offline eval against the golden set

Load `golden-set.md`. If empty or thin, advise running `/marketplace:build-golden-set search` first.

**If `~~search engine` is connected:**
1. Execute each golden query against the current production settings
2. Execute each against a staging clone or point-in-time snapshot with the proposed change applied
3. Compute per-query metrics: nDCG@10, MRR, zero-result rate, position delta for must-appear items
4. Report per-query diff, sorted by worst regression

**If not connected:**
Advise running the diff manually, and describe the minimal shape of the comparison the user should run.

#### 3c. Walk the rule checklist

Apply these checks (from `marketplace-search-recsys-planning`):

| Rule | Applies when | Check |
|------|-------------|-------|
| `query-curate-synonyms-by-domain` | synonym change | Are the synonyms validated per intent class? |
| `index-match-index-and-query-time-analyzers` | analyzer change | Do both sides use the same analyzer? |
| `rank-tune-bm25-parameters-last` | BM25 parameter change | Is the golden-set effect measured before rolling out? |
| `rank-normalise-scores-across-retrieval-primitives` | score change | Are scores from different primitives normalised? |
| `retrieve-use-filter-clauses-for-exact-matches` | filter→must movement | Does the change lose a hard constraint? |
| `retrieve-use-bool-structure-deliberately` | bool rewrite | Is the `should` / `must` / `filter` split explicit? |
| `query-use-fuzzy-matching-for-typos` | fuzzy change | Is the fuzziness budget bounded? |
| `query-normalise-before-anything-else` | any query-time change | Is normalisation still earliest in the pipeline? |
| `index-use-index-templates-for-consistency` | mapping change | Does the change propagate via template? |
| `measure-track-ndcg-mrr-zero-result-rate` | any | Will the deployed system track the metrics before / after? |

#### 3d. Check observability

From `observability.md`:
- Which monitors would catch a regression within 6 hours?
- Are they currently green? Any pre-existing alerts that would confuse the change's effect?
- Is SLO error budget sufficient to absorb a partial regression?

#### 3e. Produce review verdict

Structured output:

```markdown
## Review: {{change description}}

### Summary
{{1-paragraph restatement}}

### Golden-set diff
- **Aggregate**: nDCG@10 {{delta}}, MRR {{delta}}, zero-result {{delta}}
- **Worst regressions** ({{n}} queries):
  - {{query}}: nDCG {{old → new}} — {{suspected cause}}
  - ...
- **Improvements** ({{n}} queries):
  - ...

### Rule checklist
- [✓] {{rule}} — {{notes}}
- [✗] {{rule}} — {{issue + remediation}}

### Observability
- **Monitors that would catch regression**: {{list}}
- **SLO error budget**: {{state}}
- **Blind spots**: {{list}}

### Verdict
{{ship | ship-with-A/B | partial-rollback | no-ship}}

### Recommended next step
{{specific action}}

### Gotcha log entry (draft)
{{1-line entry for gotchas.md if this ships and something goes wrong}}
```

### 4. Branch B — Personalisation Change

#### 4a. Summarise the change

Restate in structured form:
- **Target**: dataset, solution, filter, re-ranker, feature, cold-start fallback
- **Scope**: which surfaces the change affects
- **Reversibility**: instant rollback (campaign / solution switch), re-train required, or requires dataset rebuild?

#### 4b. Sanity-check against the library

Apply these checks (from `marketplace-personalisation`):

| Rule | Applies when | Check |
|------|-------------|-------|
| `schema-design-conservatively` | schema change | Does the new schema deprecate a field safely? |
| `schema-meet-minimum-dataset-sizes` | recipe / dataset change | Are the minimum dataset size requirements still met? |
| `schema-include-context-everywhere` | schema change | Is the context propagated to training and serving? |
| `schema-prefer-categorical-fields` | feature change | Are features categorical where appropriate? |
| `recipe-default-to-user-personalization-v2` | recipe swap | Is the new recipe the right choice for this surface's intent? |
| `recipe-sims-for-item-page-only` | surface change | Is the recipe matched to the surface's job? |
| `recipe-defer-hpo-until-baseline-measured` | HPO change | Is a baseline measured first? |
| `cold-tag-cold-start-recs` | cold-start fallback change | Are cold-start impressions tagged for downstream analysis? |
| `cold-reserve-exploration-slots` | ranker change | Does exploration get reserved slots? |
| `loop-detect-death-spirals` | ranker change | Is the monitor in place? |
| `loop-reserve-random-exploration` | ranker change | Is there a serving-time exploration reserve? |
| `loop-optimize-completed-outcome` | label change | Is the ranking label the completed outcome (e.g., booking), not an intermediate (e.g., click)? |
| `match-balance-supply-demand` | ranker change | Does the ranker respect feasibility? |
| `match-cap-provider-exposure` | ranker change | Is there a single-supplier cap? |
| `infer-use-filters-api` | filter change | Is the filter using the managed API and not a hand-rolled rewrite? |
| `infer-cache-responses-short-ttl` | serving change | Is the TTL conservative enough to avoid staleness? |
| `track-use-stable-opaque-item-ids` | ID change | Are item IDs stable and opaque? |
| `track-stream-events-via-putevents` | event change | Is streaming used for live-user signals? |
| `track-capture-negative-signals` | event change | Are negative signals captured? |
| `obs-slice-metrics-by-segment` | observability | Are metrics decomposed by segment? |

**If the change introduces or modifies a feature** (text, vision, wizard-sourced, structured, or derived), also apply these rules from `marketplace-recsys-feature-engineering`:

| Rule | Applies when | Check |
|------|-------------|-------|
| `firstp-start-from-the-decision-not-the-algorithm` | any new feature | Is the feature tied to a specific decision, not "nice to have"? |
| `firstp-tie-every-feature-to-a-specific-solution` | any new feature | Does it have at least one named consuming solution? |
| `firstp-reject-features-you-cannot-serve-at-inference` | any new feature | Is training-serving parity guaranteed from design time? |
| `firstp-kill-features-a-popularity-baseline-already-captures` | any new feature | Does it beat a popularity-baseline ablation? |
| `audit-measure-coverage-before-modelling` | any new feature | Is the source asset ≥ 80% coverage? |
| `quality-version-feature-definitions-in-one-registry` | any new feature | Is the definition registered, versioned, and owned? |
| `quality-serve-training-and-inference-from-one-store` | any new feature | Is the feature served from the same store used for training? |
| `quality-gate-features-on-coverage-and-drift` | any new feature | Are coverage-floor and PSI-drift alarms configured? |
| `quality-scrub-pii-before-features-leave-secure-zone` | face / text feature | Is PII scrubbing in place before encoding? |
| `prove-ship-one-feature-at-a-time` | rollout | Is the change isolated to a single feature? |
| `prove-measure-lift-against-feature-ablated-variant` | rollout | Is the A/B against a feature-ablated variant (not just control)? |
| `prove-dedicate-random-exploration-slice-to-new-features` | rollout | Is a 3-5% exploration slice reserved? |
| `prove-kill-features-that-dont-earn-maintenance` | any existing feature being modified | Is it on the quarterly kill-review list? |

#### 4c. Check observability

Same as Search branch — which monitors catch the regression, what's SLO budget, blind spots.

#### 4d. Offline eval (if possible)

Personalisation offline eval is harder than search because labels are sparse. If a historical holdout set exists, run it. Otherwise, propose **online evaluation via a small A/B** as the eval mechanism.

#### 4e. Produce review verdict

Same structure as Branch A.

### 5. Experiment Design (if ship-with-A/B)

When the verdict is `ship-with-A/B`, draft an experiment:

```markdown
### Experiment Design

- **Primary outcome**: {{metric}} (directly tied to primary revenue event from `marketplace.md`)
- **Guardrails**: {{list, including latency and error rate}}
- **MDE**: {{minimum detectable effect, and the sample-size math}}
- **Cohort**: {{who sees treatment}}
- **Traffic split**: {{percentage}}
- **Duration**: {{estimate}}
- **Ship criterion**: {{explicit decision rule — "primary non-inferior + at least one guardrail positive"}}
- **Kill criterion**: {{explicit — "primary underperforms by MDE or any guardrail regresses by X"}}
- **Interleaving** (search only): {{use if a fast preference signal is feasible — see `measure-run-interleaving-for-fast-experiments`}}
```

### 6. Decisions Log

After review, offer to append the decision to a decisions log in the context skill (create if missing). Per `plan-maintain-a-decisions-log`: every relevance / recsys change should leave a trail.

## Read-only posture

This skill runs read-only queries against `~~search engine`, `~~personalisation engine`, `~~observability`, and `~~data warehouse`. It does **not** deploy changes, re-train models, or modify configurations. All writes are to files inside the context skill.

## Examples

### Search change

```
/marketplace:review-change adding synonym map "doggy -> dog" and expanding "weekend"
```

Returns the structured search review with golden-set diff, rule checklist, verdict, and experiment draft.

### Personalisation change

```
/marketplace:review-change swap homefeed recipe from user-personalization-v1 to v2
```

Returns the structured personalisation review with rule checklist, observability check, and experiment draft.

### Change to a surface lacking a golden set

```
/marketplace:review-change re-ranking listing-detail similar items
```

First advises running `/marketplace:build-golden-set recsys` for the similar-items surface, then proceeds with whatever eval is possible.

## Tips

- **Never ship a ranking change without at least a partial golden-set diff.** The cost of regression is much higher than the cost of the diff.
- **Watch for "obvious" synonym changes** — they have the highest surprise rate because they affect many queries silently.
- **Recipe swaps have a long tail** — changes that pass offline eval still can fail in production for 2-4 weeks as the feedback loop reshapes.
- **Prefer rollback readiness over forward-fix heroics.** A change that's easy to roll back is a change you can ship with confidence.
- **Don't review a change without checking `gotchas.md`.** Past incidents often preview the failure modes of similar future changes.

## Related Commands

- `/marketplace:build-golden-set` — prerequisite for any search-branch review
- `/marketplace:diagnose` — run after ship if the change shows unexpected effects
- `/marketplace:build-observability` — if the review reveals a monitoring blind spot
