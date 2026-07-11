# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A Claude Code plugin marketplace containing development workflow plugins. The main plugin (`dev-workflow`) enforces TDD, systematic debugging, and code review through skills and commands. Domain plugins (`dev-python`, `dev-ts`, `dev-cpp`, `dev-shell`) provide language-specific guidance.

## Commands

```bash
scripts/validate-all.sh --quick    # Fast pre-commit validation (levels 1-2)
```

All other build/test/lint targets are self-documented: `make help`.

## Architecture

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
