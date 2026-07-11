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
/dev-workflow:brainstorm (optional) → /dev-workflow:write-plan → /dev-workflow:execute-plan
                                                                          ↓
                                                             SessionStart injects methodology:
                                                             - TDD task structure
                                                             - Pragmatic architecture
                                                             - Dependency-based parallelism
                                                             - Post-completion actions (code review, finish branch)
```

**Hooks** (`hooks/hooks.json`):
- `SessionStart` → loads getting-started skill with planning methodology

**Helper functions**: `scripts/hook-helpers.sh` provides plan parsing and task grouping functions.

## Component Frontmatter

All components require YAML frontmatter — patterns and the valid-tools list live in the repo root `CLAUDE.md` (Plugin Component Patterns).

## Skill Categories

| Category | Skills | Execution |
|----------|--------|-----------|
| Rigid | TDD, systematic-debugging, verification-before-completion | Follow exactly |
| Flexible | brainstorm, architecture | Adapt to context |

Skills with checklists require TaskCreate/TaskUpdate tracking.

## References

- `references/skill-integration.md` — Decision trees, skill chains, trigger patterns
- `references/planning-philosophy.md` — Task granularity, file organization, TDD cycles
