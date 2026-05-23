---
name: bootstrap-agent-cli
description: Use this skill when starting a NEW command-line tool meant to be driven by AI agents — a code reviewer, fixer, sweeper, sandbox runner, codegen tool, or anything an agent invokes and parses. Triggers on "build a new CLI", "scaffold an agent CLI", "bootstrap a tool for agents", "new agent tool", "start a CLI project for agents". Walks spec to one-shot scaffold (with tests + CI) to dogfood to honest v0.1, pausing at decision gates. TS/Node-first.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# Bootstrap an agent CLI

Stand up a new CLI that an AI agent will both **drive** (invoke + parse) and later
help **extend**. Method distilled from `openclaw/clawpatch` (built zero→v0.4 in 8
days). Phases 0–4 are one focused session; 5–9 hand off to the other agent-cli
skills.

**Core idea:** design for the agent-driver (JSON contract, exit codes, resumable
state, deterministic core) and you get agent-extensibility for free. Read
[`references/contract.md`](references/contract.md) for the invariants this scaffold
must satisfy, and [`references/scaffold.md`](references/scaffold.md) for the actual
TS code patterns to generate.

## Phase 0 — Stake the claim
One commit: `LICENSE` only, plus the chosen name + registry scope. Reserve the npm
name. (clawpatch & crabbox both: commit 1 = LICENSE only.)

## Phase 1 — Spec as generator  🔶 DECISION GATE
Write ONE design doc precise enough to *generate* the code. Use
[`templates/SPEC.template.md`](templates/SPEC.template.md). It must specify: goals,
**hard non-goals**, the full CLI contract (every flag, every exit code, output
shape), every persisted record schema, pipeline stages, the provider/adapter
interface, safety posture, testing + release criteria, open questions.

Before writing the spec, **ask the human the decision-gate questions** (one
`AskUserQuestion`, multiple questions) — these are choices only they can make and
they shape everything downstream:

1. **Non-goals / scope** — what will v0 deliberately NOT do? (Push for a ruthless
   list; this is what keeps you and future agents on-scope.)
2. **Safety posture** — is the tool read-only/report-only by default with mutation
   behind an explicit subcommand? (Almost always yes for agent CLIs. Confirm.)
3. **State location** — where does persisted state live, and is it gitignored /
   separated from code? (`.{tool}/` dirs, gitignored runtime subdirs.)
4. **First provider/adapter** — which single agent provider or backend ships first?
   (One path proven before any matrix — a hard non-goal.)

Gate: every command's I/O and every record schema is written down. The spec is a
*prompt*, not scripture — expect the code to diverge later (clawpatch's shipped
tree diverged from its own spec skeleton; that's fine).

## Phase 2 — One-shot scaffold
Generate the WHOLE skeleton in one commit from
[`references/scaffold.md`](references/scaffold.md): CLI entry with the flag table +
dispatch + stdout/stderr discipline + top-level error→exit-code catch; `errors.ts`
with the typed error class (string `code` + numeric `exitCode`); zod schemas for
every record; atomic state I/O + lock files; the provider interface + ONE provider
(start with a `mock` provider for tests + your real one); the plugin/mapper
interface with one example; contract tests; CI (`typecheck + lint + format:check +
test + build + pack:smoke`); README stating limits honestly.

**Tests and CI ship in THIS commit — never "later."** (clawpatch commit 2 = 5,866
LOC including a 636-line workflow test + CI.)

Gate: CI green; `--json` output snapshot stable.

## Phase 3 — Dogfood immediately
Point the tool at its own repo; let its output drive the first refactor.
Gate: the tool produces valid state on itself.

## Phase 4 — Ship honest v0.1  🔶 DECISION GATE (publish)
Publish. **Version reflects maturity** — don't oversell (clawpatch shipped 0.9.1
then *corrected down* to 0.1.0). README says "early." Start `CHANGELOG.md`
(see [`templates/AGENTS-and-changelog.md`](templates/AGENTS-and-changelog.md)).
Confirm with the human before publishing to a public registry.

Gate: installs from registry, exposes the bin, release-criteria met.

## Phases 5–9 — hand off
- Adding features / refactoring / adding providers → **evolve-agent-cli**.
- Reviewing against the contract + safety model → **audit-agent-cli**.
- Externalizing prompts/policies/schema or standing up an autonomous loop →
  **agent-spec-kit**.

## Definition of done (v0.1)
- [ ] LICENSE committed first; name reserved
- [ ] Spec doc with explicit non-goals
- [ ] Scaffold: CLI contract + zod schemas + atomic state + locks + one provider +
      one plugin/adapter example + tests + CI, all in one commit
- [ ] `--json` / `--no-input` / enumerated exit codes / stdout=result, stderr=progress
- [ ] State gitignored / separated from code
- [ ] AGENTS.md + CHANGELOG.md + honest README
- [ ] Dogfooded on itself; CI green
