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
allowed-tools: [Read, Task, TodoWrite]
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

`Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `Task`, `TodoWrite`, `AskUserQuestion`, `Skill`, `WebFetch`, `WebSearch`, `NotebookRead`, `NotebookEdit`, `LS`, plus `mcp__*` for MCP tools.

### Skill Categories

| Category | Skills | Execution |
|----------|--------|-----------|
| Rigid | TDD, systematic-debugging, verification-before-completion | Follow exactly |
| Flexible | brainstorm, pragmatic-architecture | Adapt to context |

Skills with checklists require TodoWrite tracking.

## Development Workflow

The `dev-workflow` plugin uses native Claude Code primitives:

1. `SessionStart` hook loads `getting-started` skill with planning methodology
2. `/dev-workflow:brainstorm` refines ideas via Socratic dialogue
3. `EnterPlanMode` → `ExitPlanMode(launchSwarm: true)` for parallel execution
4. Post-swarm: code review + finish branch

Alternative: `/dev-workflow:write-plan` → `/dev-workflow:execute-plan` for plan persistence.

## Dependencies

**Required:** `git`
**Development:** `bats-core`, `shellcheck`, `jq`, `pre-commit`

All Python tooling uses `uv`:
```bash
uv sync                    # Install Python deps
uv run pre-commit install  # Setup pre-commit hooks
```
