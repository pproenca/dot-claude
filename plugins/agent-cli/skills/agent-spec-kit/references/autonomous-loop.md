# The autonomous loop (CI orchestration) + maintain/release

How clawsweeper runs an agent CLI unattended on GitHub Actions. **Do not stand this up
until the safety model passes audit-agent-cli at the "autonomous loop" posture** — the
loop multiplies whatever safety (or lack of it) the tool has.

## Trigger surfaces (one workflow, three ways in)
```yaml
on:
  schedule:
    - cron: "*/5 * * * *"     # hot intake lane
    - cron: "3,18,33,48 * * * *"   # apply-closures lane
    - cron: "6,21,36,51 * * * *"   # comment-sync lane
    - cron: "7 */6 * * *"          # audit lane
  repository_dispatch:
    types: [tool_item, tool_target_sweep]   # low-latency event-driven runs
  workflow_dispatch: { inputs: { mode: { type: choice, options: [plan, execute, autonomous] } } }
```
**Cron lane = job type.** Different cadences select different work; decode the lane in the
`run-name`/`concurrency` expression. Target repos forward exact issue/PR events via
`repository_dispatch` for one-item latency instead of waiting for the next cron.

## The read/write token split (the core safety mechanism in CI)
Two jobs, two credential scopes:
```yaml
jobs:
  review:                       # the model runs here — READ ONLY
    permissions: { contents: read, issues: read, pull-requests: read }
    steps: [ ... run model with a read-scoped token ... ]
  apply-existing:               # the deterministic applicator — WRITE
    permissions: { contents: write, issues: write, pull-requests: write }
    if: ${{ vars.TOOL_ALLOW_EXECUTE == '1' && (inputs.mode == 'execute' || inputs.mode == 'autonomous') && !inputs.dry_run }}
    steps: [ ... re-fetch live state, recheck drift, then mutate ... ]
```
`workflow_run` chains deterministic post-processing after the worker completes:
```yaml
on: { workflow_run: { workflows: ["tool cluster worker"], types: [completed] } }
```
A `repair-self-heal` cron retries failed jobs.

## Comment-command routing (`@bot` / `/command`)
A versioned `parseCommand` regex maps maintainer comments to a fixed intent set
(`review`, `fix`, `autofix`, `automerge`, `re_review`, `stop`, `implement_issue`,
`freeform_assist`). The target repo forwards `issue_comment` events via
`repository_dispatch`; a router workflow parses them. The bot also reads its own hidden
verdict markers (`<!-- tool-verdict:needs-changes -->`) to route trusted automation
without re-parsing prose.

## State in a separate repo
Generated decision records / jobs / results / dashboard live on a `state` branch of a
**separate** `<tool>-state` repo, keyed `records/<repo-slug>/items/<id>.md` (and
`closed/`). The code repo stays "source, workflows, docs, tests" only. The state repo is
in the deny-list so the bot never reviews its own state. CI/CodeQL `paths-ignore` the
record dirs. Hydrate locally with a `hydrate-state` script.

## Maintain & release rails (all three repos)
- **Merge + credit:** every CHANGELOG entry credits the contributor (`thanks @handle`).
  Maintainer days = many commits, little code churn — healthy delegation.
- **Release notes from the CHANGELOG**, extracted by the matching version section and
  **failing the release if the section is missing**:
  ```bash
  notes="$(awk -v v="$VERSION" '$1=="##" && $2==v {f=1} f && $1=="##" && $2!=v {exit} f' CHANGELOG.md)"
  [ -n "$notes" ] || { echo "::error::CHANGELOG has no section for $VERSION"; exit 1; }
  ```
- **Bracket publish** with a pre-flight credential check (e.g. can the tap token reach the
  tap repo?) and post-publish verification (the downstream formula/package actually bumped).
- **`docs/release-prep.md`** is audit-only: `gh release list`, `npm view <pkg> version`,
  the validation gate, dry-run package contents — it never tags or publishes.
- **Release cadence is rapid + version-driven**; the CHANGELOG is the single source of
  truth for what shipped.
