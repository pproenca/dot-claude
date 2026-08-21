---
name: setup-pstack
description: Configure which models pstack uses per role. Detects the models this session can spawn and writes a config file that overrides the skill defaults. Use for /setup-pstack, "configure pstack models", or changing pstack's model choices.
---

# Setup pstack

Write `~/.claude/pstack-models.md`, the config file that sets pstack's model per role. Every pstack skill reads it and falls back to its inline default when a line is absent, so this is an override layer, not a requirement.

A project can override the user-level file with `.claude/pstack.local.md` in the repo root, same shape. Project beats user; a role absent from both keeps the skill default. Add `.claude/*.local.md` to the repo's `.gitignore`.

## Value syntax

A role's value is `<model>` or `<model>[<effort>]`.

- `<model>` is one of `opus`, `fable`, `sonnet`, `haiku`, or `inherit`.
- `inherit` means the role runs on the parent session's model. Spawn it by omitting `model` on the `Agent` call.
- `[<effort>]` is optional and one of `low`, `medium`, `high`, `xhigh`, `max`. The `Agent` tool has no effort parameter and ignores it. A fan-out routed through the `Workflow` tool passes it as `opts.effort`. Carry the suffix through either way, so the same config serves both.

A panel role's value is a comma-separated list. One subagent runs per entry, `inherit` entries included, so the list length sets the fan-out width.

## Steps

### 1. Detect available models

Enumerate the models you can pass to an `Agent` subagent in this session. The `Agent` tool's own schema is the dependable source; its `model` enum is the entitled set. Never write a model you have not confirmed is spawnable. `inherit` is always valid.

### 2. Load current state

The default role-to-model mapping is the file shape in step 5. If `~/.claude/pstack-models.md` already exists, read it and treat its values as the current choices. Otherwise start from the defaults.

### 3. Map and confirm

Show every role with its current model, marking any value not in the detected set as needing a choice. Ask whether to accept as-is or change specific roles, offering the detected models plus `inherit`. Prefer `AskUserQuestion` over free text.

For panel roles (how critics, arena runners, architect runners, interrogate reviewers) the value is a list and its length sets the fan-out. `arena cross-judge pool` is also a list, but Arena selects one entry from it whose model differs from the parent's when possible. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

Panels get their diversity from four model tiers plus per-entry effort. Two entries on the same model at different efforts are a real difference in behavior, not a duplicate, and the panel skills give each reviewer a distinct lens on top. Keep at least two distinct models in any panel.

### 4. Validate

Every model written must be in the detected set; `inherit` always passes. If a chosen model is not available, stop and ask again. A config pointing at a model the user cannot spawn breaks every delegation that reads it.

### 5. Write the config

Write `~/.claude/pstack-models.md` with one line per role, using the same labels poteto-mode uses. Overwrite the whole file so re-runs stay idempotent. Shape:

```markdown
---
description: pstack per-role model choices (overrides skill defaults)
---
# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# Value is <model> or <model>[<effort>]. `inherit` runs the role on the parent session's model (omit `model` on the Agent call).
# Effort applies only to fan-outs routed through the Workflow tool; the Agent tool ignores it.
feature, refactoring: sonnet[high]
bug-fix: opus[high]
perf-issue: opus[high]
hillclimb: opus[high]
judgment and prose: fable[max]
hardest tasks: fable[max]
how explorer: sonnet[high]
how explainer: fable[max]
how critics: fable[max], opus[high], sonnet[high], opus[max]
why investigators: sonnet[high]
why synthesizer: fable[max]
reflect tooling: opus[high]
reflect judgment, divergent, synthesizer: fable[max]
arena runners: fable[max], opus[high], sonnet[high], opus[max]
arena cross-judge pool: fable[max], opus[high], sonnet[high], opus[max]
swarm workers: sonnet[high]
architect runners: fable[max], opus[high], sonnet[high], opus[max]
interrogate reviewers: fable[max], opus[high], sonnet[high], opus[max]
```

The defaults split work by model strength. Fast mechanical code goes to `sonnet`. Precisely specified sequences and debugging go to `opus` at high effort. Prose and judgment go to `fable`. The hardest calls go to `opus[max]`.

### 6. Confirm

Tell the user the config was written and that skills read it on their next run. Re-running this skill updates it.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /create-verification-skill." On yes, invoke `/create-verification-skill`. On no, move on without pushing.
