# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Claude Code plugin enforcing TDD, systematic debugging, and code review. Skills load at session start via `SessionStart` hook.

## Commands

```bash
./scripts/validate.sh              # Full validation (JSON, permissions, frontmatter, shellcheck)
./scripts/setup.sh                 # Contributor setup (bats, pre-commit)
bats tests/                        # Run all tests
bats tests/session-start.bats     # Run single test file
```

Tests run on commit via pre-commit hook.

## Architecture

**Plugin flow (native tools):**
```text
/dev-workflow:brainstorm (optional) → EnterPlanMode → ExitPlanMode(launchSwarm: true)
                                           ↓
                              SessionStart injects methodology:
                              - TDD task structure
                              - Pragmatic architecture
                              - Parallel grouping
                              - Post-swarm actions (code review, finish branch)
```

**Hooks** (`hooks/hooks.json`):
- `SessionStart` → loads getting-started skill with planning methodology

**Helper functions**: `scripts/hook-helpers.sh` provides `frontmatter_get`/`frontmatter_set` for safe YAML parsing.

## Component Frontmatter

All components require YAML frontmatter.

**Valid tools:** `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `Task`, `TodoWrite`, `AskUserQuestion`, `Skill`, `WebFetch`, `WebSearch`, `NotebookRead`, `NotebookEdit`, `LS`

**MCP tools:** Use `mcp__*` wildcard to grant access to all MCP server tools, or `mcp__<server>__<tool>` for specific tools (e.g., `mcp__plugin_serena_serena__find_symbol`).

**Skills** (`skills/<name>/SKILL.md`):
```yaml
---
name: skill-name
description: Trigger phrases for skill discovery
allowed-tools: [Read, Edit, Bash]
---
```

**Commands** (`commands/<name>.md`):
```yaml
---
description: What the command does
allowed-tools: [Read, Task, TodoWrite]
---
```

**Agents** (`agents/<name>.md`):
```yaml
---
name: agent-name
description: When to dispatch via Task tool
model: sonnet | haiku
tools: [Glob, Grep, Read]
---
```

## Skill Categories

| Category | Skills | Execution |
|----------|--------|-----------|
| Rigid | TDD, systematic-debugging, verification-before-completion | Follow exactly |
| Flexible | brainstorm, architecture | Adapt to context |

Skills with checklists require TodoWrite tracking.

## Directory Structure

```text
hooks/           # Event handlers (SessionStart)
scripts/         # Validation, setup, helpers
skills/          # SKILL.md per skill with optional references/
commands/        # Slash commands (/dev-workflow:*)
agents/          # Subagent definitions
references/      # Shared docs (skill-integration, planning-philosophy)
tests/           # Bats tests for hooks and scripts
```

## References

- `references/skill-integration.md` — Decision trees, skill chains, trigger patterns
- `references/planning-philosophy.md` — Task granularity, file organization, TDD cycles

## Dependencies

**Required:** `git`
**Optional:** `jq`, `bats-core`, `shellcheck`, `pre-commit`

## Optional: LSP Code Navigation

Enable [cclsp](https://github.com/ktnyt/cclsp) for enhanced symbol navigation:

```bash
/dev-workflow:setup-lsp
```

**Feature detection:** Agents check for `mcp__cclsp__*` tools at runtime. When available, LSP tools are preferred over grep-based search for:
- Symbol definitions (`find_definition` vs `Grep`)
- Reference lookup (`find_references` vs `Grep`)
- Type diagnostics (`get_diagnostics` — no fallback)
- Safe refactoring (`rename_symbol` — no fallback)

The plugin works fully without cclsp. LSP tools are an optional enhancement.
