# <tool> spec

<one-line product statement — what it does, in one sentence>

<2–3 sentence expansion: what it maps/reviews/runs, what it persists, what it does
only on explicit command>

## Goals
- <Review/operate by semantic unit, not file list>
- <Persist every run, decision, and command>
- <Resume safely after crash / quota / auth / Ctrl-C>
- <Strict machine-readable records + terse human output>
- <Default to report-only; mutate only on explicit subcommand>
- <Never overwrite user changes>

## Non-goals for v0   ← BE RUTHLESS. This list is what keeps you and future agents on-scope.
- No <autonomous repo-wide action>
- No <implicit commit / push / PR>
- No <provider matrix before one provider path works well>
- No <custom database — start with project-local JSON files>
- No <general-purpose agent shell>

## Package
- repo / npm name / CLI bin / runtime (Node >= 22) / language (strict TS)
- formatter `oxfmt` · linter `oxlint` · tests Vitest

## CLI contract
- Global flags: `--root --state-dir --config --json --plain -q/--quiet -v/--verbose --debug --no-color --no-input --version -h`
- stdout = result (JSON under `--json`); stderr = progress/diagnostics; no spinners on non-TTY
- **Exit codes:** 0 ok · 1 runtime · 2 invalid usage · 3 dirty worktree · 4 provider auth ·
  5 provider quota · 6 validation failed · 7 lock conflict · 8 malformed model output
- Interactivity: prompts only on TTY; `--no-input` fails instead of prompting; mutating
  commands need explicit intent and may prompt unless `--yes`

## Commands
For each command: usage line, behavior (numbered), output (human + `--json` shape).
`init` · `map`/`scan` · `status` · `<review/run>` · `report` · `<fix/apply>` ·
`revalidate` · `doctor` · `clean-locks` · (`open-pr` / `land` post-v0)

## Config
Discovery order, precedence (flags > env > project config > defaults), initial config
JSON, env var names, secrets policy (never as flags, never printed).

## State layout
`.{tool}/` dir tree (config/project/<records>/runs/locks/...); which subdirs are
gitignored; record-ID rules (deterministic slug/hash).

## Schemas
Every persisted record as a typed/zod definition with `schemaVersion`.

## <Pipeline> stages
Numbered deterministic steps; where the single model call sits; prompt-assembly rules
(included files, omitted-due-to-budget, token estimate); output schema.

## Provider / adapter contract
The interface every provider/backend implements; which ONE ships first.

## Safety
Report-only by default · guarded mutation behind explicit subcommand · refuse dirty
worktree (excluding state dir) · record base SHA + re-verify before commit · never
destructive git · allowlist user-supplied refs.

## Testing requirements
Unit list (config precedence, ID stability, schema validation, malformed-JSON failure,
lock behavior, provider parse failures, command selection). Fixtures. Snapshot/JSON
schema examples.

## Release criteria for v0.1
Installs + exposes bin · `init` writes valid state · core command works on fixtures and
on the tool itself · strict TS / lint / format / tests pass in CI · README honest about limits.

## Open questions
- <unresolved choice 1 — delete each as you answer it>
