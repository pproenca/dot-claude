# agent-cli

Build, evolve, audit, and maintain **CLI tools for AI agents** — repeatably.

An "agent CLI" is a command-line tool meant to be **driven by an AI agent** (a reviewer,
fixer, sweeper, sandbox runner, codegen tool) and often **extended by agents** too. This
plugin distills the method behind three production tools by one prolific author
(`openclaw/clawpatch`, `crabbox`, `clawsweeper`) into four skills.

**The load-bearing idea:** the properties that make a CLI good _for_ agents (a JSON
contract, enumerated exit codes, resumable state, a deterministic core, guarded mutation)
are the same ones that let a swarm of agents safely _extend_ it. Design for the driver,
get the extensibility free.

## Skills

| Skill | Use it to | Mirrors |
|---|---|---|
| **bootstrap-agent-cli** | Start a new agent CLI: spec → one-shot scaffold (with tests + CI) → dogfood → honest v0.1 | clawpatch Phases 0–4 |
| **evolve-agent-cli** | Refactor / add a feature / add a provider / harden an existing one: diagnose → pin → execute in mode → update contract docs | the hardening loop (fix ≈ 48% of commits) |
| **audit-agent-cli** | Review a CLI against the agent-CLI contract + safety model before extending or trusting it | the §1 invariants + guarded-mutation model |
| **agent-spec-kit** | Externalize the agent's behavior as versioned data (prompts/policies/schema) and stand up an autonomous loop + release rails | clawsweeper |

Run `/agent-cli [bootstrap\|evolve\|audit\|spec-kit]` to route, or just describe the task
— each skill self-triggers on the matching intent.

## Design principle: decision-gate checkpoints
The skills pause to ask the human only at consequential/irreversible forks — non-goals,
safety posture (proposal vs apply), state-vs-code separation, provider/adapter choice,
schema-version bumps. Everywhere else they proceed on sensible defaults and report.

## Diagnostic
`scripts/repo-health.py <repo>` powers the evolve/audit tracks: commit-type distribution,
feat:fix ratio per scope (fragility), churn concentration ("where the real spec lives"),
and refactor cadence. Add `--bots-separate` for autonomous-loop repos.

```sh
python3 scripts/repo-health.py /path/to/repo
python3 scripts/repo-health.py /path/to/repo --bots-separate --emit-csv ./out
```

## Targeting
Concrete templates are TS/Node-first (zod, vitest, oxlint/oxfmt, strict tsconfig, GitHub
Actions); the principles, contract, and safety model are language-agnostic and transfer
to Go and others (crabbox is Go).

## Provenance
Reverse-engineered from a deep read of the three repos (interfaces, safety code, test
patterns, prompt/schema conventions, CI orchestration). Claims are grounded in source;
the diagnostic reproduces the metrics. See each skill's `references/` for quote-backed
detail.
