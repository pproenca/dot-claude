---
name: agent-spec-kit
description: Use this skill when an agent CLI's behavior should be versioned data rather than code strings — managing prompts, policies, and output schemas — or when standing up an autonomous loop (scheduled/event-driven runs with guarded apply) and its maintain/release rails. Triggers on "externalize the prompt", "version the agent's policy", "the agent's output schema", "make this CLI run on a schedule", "autonomous bot", "agent decision contract", "set up the maintainer loop", "release the CLI". Distilled from openclaw/clawsweeper.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# Agent spec kit

Treat an agent CLI's *behavior* as versioned, reviewable data — and, when it runs
unattended, stand up the loop and the maintain/release rails. Distilled from
`clawsweeper` (an autonomous bot whose entire job is four data layers over a
deterministic engine).

## Part 1 — Behavior as data
Pull the agent's behavior out of code strings into four sibling directories, each
diffable and reviewable in a PR. Full patterns:
[`references/behavior-as-data.md`](references/behavior-as-data.md).

- **`prompts/`** — the task spec as markdown (role, scope guardrails, a read-only command
  allowlist, a confidence/evidence bar, references to the target repo's `AGENTS.md` and
  `.agents/maintainer-notes/`, and a one-line pointer to the output schema). Mode is a
  swappable prompt layer (`plan` / `execute` / `autonomous`) over a shared system prompt.
  Template: [`templates/prompt.template.md`](templates/prompt.template.md).
- **`instructions/`** — policy docs the model reads at runtime. Each = a gate (when it
  applies) + positive criteria + a ranked evidence order + a hard "Never" list + literal
  comment templates + escalation verbs (`needs_human`, `route_security`) with an
  anti-overuse clause. Template: [`templates/policy.template.md`](templates/policy.template.md).
- **`schema/`** — the output contract as a **closed** JSON Schema
  (`additionalProperties: false`), handed to the model as `--output-schema` AND
  re-validated on parse. Bake provenance in (every evidence item requires `file`+`sha`)
  and **lock safety-critical fields with `const`** (e.g. `security_sensitive: false`,
  `merge_preflight.security_status: "cleared"`). Template:
  [`templates/decision.schema.template.json`](templates/decision.schema.template.json).
- **`config/`** — per-target profiles + limits (worker caps, deny-lists).

🔶 DECISION GATE (schema bump): if you change the output schema, ask the human before
bumping its version and confirm consumers/validators are updated in lockstep.

## Part 2 — The autonomous loop  🔶 DECISION GATE (safety posture)
Only stand up unattended execution after confirming with the human that the safety model
holds (run **audit-agent-cli** with the *autonomous loop* posture first). The loop is
GitHub Actions; patterns in [`references/autonomous-loop.md`](references/autonomous-loop.md):
- A single overloaded `schedule:` where **cron lane = job type**.
- Custom `repository_dispatch` event types for low-latency event-driven runs.
- `workflow_run` chaining for deterministic post-processing.
- **Separate read-token (plan/review) and write-token (execute) jobs**, the execute job
  gated by an org var + explicit mode.
- A versioned `parseCommand` regex turning `@bot` / `/command` comments into a fixed
  intent set; the bot routes off its own hidden verdict markers, not prose.
- **Generated state committed to a separate state repo** (keeps the code repo clean and
  the decision history independently auditable).

## Part 3 — Maintain & release
The maintainer-mode rails (all three OpenClaw repos):
- **Merge + credit:** accept breadth PRs; every CHANGELOG entry credits the contributor
  (`thanks @handle`). Maintainer days are high-commit / low-churn — that's healthy.
- **Honest, frequent releases:** `Unreleased` stub → `## X.Y.Z - YYYY-MM-DD`; version
  reflects maturity. Automate release notes by extracting the matching CHANGELOG section
  (fail the release if it's missing). Bracket publish with pre-flight credential checks
  and post-publish verification.
- **Release-prep checklist** (`docs/release-prep.md`): audit-only — changelog
  completeness, `npm view` current version, dry-run package contents — no tag/publish.

## Definition of done
- [ ] behavior lives in `prompts/` + `instructions/` + `schema/` (+ `config/`), not code strings
- [ ] output schema is closed, handed to the model AND re-validated, with safety fields `const`-locked
- [ ] (if a loop) read/write token split, recheck-before-mutate, state in a separate repo,
      audited at the autonomous-loop posture
- [ ] CHANGELOG credits contributors; release notes automated from it
