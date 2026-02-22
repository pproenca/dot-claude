<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A Claude Code plugin marketplace containing development workflow plugins. The main plugin (`dev-workflow`) enforces TDD, systematic debugging, and code review through skills and commands. Domain plugins (`dev-python`, `dev-ts`, `dev-cpp`, `dev-shell`) provide language-specific guidance.

## Commands

```bash
# Full validation (JSON, frontmatter, shellcheck, integration)
make check

# Fast pre-commit validation (levels 1-2)
scripts/validate-all.sh --quick

# Run tests
make test                              # Fast tests (skips integration)
make test-all                          # All tests including slow integration
bats plugins/dev-workflow/tests/       # Run bats directly

# Lint shell scripts
make lint

# Plugin-specific validation
make validate

# Install dev dependencies
make install
```

## Architecture

### Repository Structure

```
plugins/
  dev-workflow/          # Main plugin - TDD, debugging, workflows
    skills/              # SKILL.md files with frontmatter
    commands/            # Slash commands (/dev-workflow:*)
    agents/              # Subagent definitions
    hooks/               # SessionStart hook
    scripts/             # Validation helpers
    tests/               # Bats tests
    references/          # Shared docs

domain_plugins/          # Language-specific plugins
  dev-python/            # Python with uv, ruff, pydantic
  dev-ts/                # TypeScript/JavaScript
  dev-cpp/               # C++ with clangd
  dev-shell/             # Shell scripting

scripts/                 # Marketplace-level validation
  level-1-syntax.sh      # JSON/YAML syntax checks
  level-2-frontmatter.sh # Required fields
  level-4-arguments.sh   # Argument validation
  level-5-file-refs.sh   # File reference validation
  level-6-bash.sh        # Shellcheck
  level-7-integration.sh # Bats tests
  validate-all.sh        # Orchestrates all levels
```

### Plugin Component Patterns

All components use YAML frontmatter:

**Skills** (`skills/<name>/SKILL.md`):
```yaml
---
name: skill-name
description: Trigger phrases for skill discovery
allowed-tools: [Read, Edit, Bash]  # optional
---
```

**Commands** (`commands/<name>.md`):
```yaml
---
description: What the command does
allowed-tools: [Read, Task, TaskCreate, TaskUpdate]
---
```

**Agents** (`agents/<name>.md`):
```yaml
---
name: agent-name
description: When to dispatch via Task tool
model: sonnet | opus
tools: [Glob, Grep, Read]
---
```

### Valid Tools for Frontmatter

`Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `Task`, `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet`, `TaskStop`, `TaskOutput`, `AskUserQuestion`, `Skill`, `WebFetch`, `WebSearch`, `NotebookEdit`, plus `mcp__*` for MCP tools.

### Skill Categories

| Category | Skills | Execution |
|----------|--------|-----------|
| Rigid | TDD, systematic-debugging, verification-before-completion | Follow exactly |
| Flexible | brainstorm, pragmatic-architecture | Adapt to context |

Skills with checklists require TaskCreate/TaskUpdate tracking.

## Development Workflow

The `dev-workflow` plugin uses native Claude Code primitives:

1. `SessionStart` hook loads `getting-started` skill with planning methodology
2. `/dev-workflow:brainstorm` refines ideas via Socratic dialogue
3. `/dev-workflow:write-plan` → `/dev-workflow:execute-plan` for parallel execution
4. Post-completion: code review + finish branch

Alternative: `EnterPlanMode` → `ExitPlanMode` for quick 1-3 task features without plan persistence.

## Dependencies

**Required:** `git`
**Development:** `bats-core`, `shellcheck`, `jq`, `pre-commit`

All Python tooling uses `uv`:
```bash
uv sync                    # Install Python deps
uv run pre-commit install  # Setup pre-commit hooks
```
