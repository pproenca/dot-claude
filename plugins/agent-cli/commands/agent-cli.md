---
description: Build, evolve, audit, or maintain a CLI tool for AI agents
argument-hint: [bootstrap|evolve|audit|spec-kit] [target]
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, AskUserQuestion
---

# agent-cli

Route the user to the right phase of the agent-CLI lifecycle. An "agent CLI" is a
command-line tool meant to be **driven by an AI agent** (a reviewer, fixer,
sweeper, sandbox runner, codegen tool, or any tool an agent invokes and parses)
and often **extended by agents** too.

The method is distilled from three production tools by the same author
(`openclaw/clawpatch`, `crabbox`, `clawsweeper`). The unifying insight:
**the properties that make a CLI good _for_ agents (JSON contract, exit codes,
resumable state, deterministic core, guarded mutation) are the same ones that let
a swarm of agents safely _extend_ it.**

## Routing

Argument `$1` (or infer from the request):

- **`bootstrap`** — starting a new agent CLI from zero → invoke the
  **bootstrap-agent-cli** skill (spec → one-shot scaffold → dogfood → honest v0.1).
- **`evolve`** — refactor, add a feature, add a provider/adapter, or harden an
  existing agent CLI → invoke the **evolve-agent-cli** skill (diagnose → pin →
  execute in mode → update contract docs).
- **`audit`** — review an existing CLI against the agent-CLI contract and safety
  model → invoke the **audit-agent-cli** skill.
- **`spec-kit`** — externalize an agent's behavior as versioned data
  (prompts/instructions/schema), or stand up an autonomous loop and its
  maintain/release rails → invoke the **agent-spec-kit** skill.

If `$1` is empty, ask the user which one they want (one `AskUserQuestion` with the
four options above), then route.

## Principle: decision-gate checkpoints

All four skills pause to ask the human ONLY at consequential/irreversible forks —
non-goals/scope, safety posture (proposal vs apply), state-vs-code separation,
provider/adapter choice, and schema-version bumps. Everywhere else, proceed on
sensible defaults and report. Do not interrogate the user about reversible
choices.

## Diagnostic

`scripts/repo-health.py <repo>` (bundled) powers the evolve/audit tracks: commit
type distribution, feat:fix ratio per scope (fragility), churn concentration
("where the real spec lives"), and refactor cadence. Run it before evolving or
auditing any existing repo.
