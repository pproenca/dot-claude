# Project Context

## Purpose

A Claude Code plugin marketplace containing development workflow plugins. The main plugin (`dev-workflow`) enforces TDD, systematic debugging, and code review through skills and commands. Domain plugins (`dev-python`, `dev-ts`, `dev-cpp`, `dev-shell`, `skills-template`) provide language-specific guidance and best practices.

**Goals:**
- Provide reusable development methodology skills for Claude Code
- Enforce consistent workflows across projects (TDD, debugging, verification)
- Share language-specific best practices via domain plugins
- Enable parallel task execution through native Claude Code primitives

## Tech Stack

- **Shell scripts** (Bash) - Hooks, validation scripts, helpers
- **YAML frontmatter** - Component metadata in Markdown files
- **JSON** - Plugin manifests (`plugin.json`)
- **Markdown** - Skills, commands, agents, documentation
- **Python 3.11+** - Tooling via `uv` (pre-commit only)
- **bats-core** - Shell script testing framework
- **shellcheck** - Shell script linting
- **pre-commit** - Git hooks for validation

## Project Conventions

### Code Style

**Shell Scripts:**
- Use `shellcheck` for linting (with `-x` for sourced files)
- Follow Google Shell Style Guide (via `dev-shell` plugin)
- Scripts in `scripts/` or `hooks/` directories

**Markdown Components:**
- All skills, commands, and agents require YAML frontmatter
- Use kebab-case for file and directory names
- Skills go in `skills/<name>/SKILL.md`
- Commands go in `commands/<name>.md`
- Agents go in `agents/<name>.md`

**Naming:**
- Plugin names: kebab-case (`dev-workflow`, `dev-python`)
- Skill names: kebab-case matching directory (`test-driven-development`)
- Command names: kebab-case (invoked as `/plugin:command`)

### Architecture Patterns

**Plugin Structure:**
```
plugins/<name>/
  .claude-plugin/
    plugin.json          # Manifest with name, description, author
  skills/               # SKILL.md files with frontmatter
  commands/             # Slash commands
  agents/               # Subagent definitions
  hooks/                # Event handlers (SessionStart, etc.)
  scripts/              # Helper scripts
  tests/                # Bats tests
  references/           # Shared documentation
```

**Component Frontmatter:**

Skills:
```yaml
---
name: skill-name
description: Trigger phrases for skill discovery
allowed-tools: [Read, Edit, Bash]  # optional
---
```

Commands:
```yaml
---
description: What the command does
allowed-tools: [Read, Task, TodoWrite]
---
```

Agents:
```yaml
---
name: agent-name
description: When to dispatch via Task tool
model: sonnet | opus
tools: [Glob, Grep, Read]
---
```

**Valid Tools:** `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `Task`, `TodoWrite`, `AskUserQuestion`, `Skill`, `WebFetch`, `WebSearch`, `NotebookEdit`, plus `mcp__*` for MCP tools.

**Skill Categories:**
| Category | Examples | Execution |
|----------|----------|-----------|
| Rigid | TDD, systematic-debugging, verification-before-completion | Follow exactly |
| Flexible | brainstorm, pragmatic-architecture | Adapt to context |

### Testing Strategy

- **Unit tests:** bats-core for shell scripts (`tests/*.bats`)
- **Validation levels:**
  - Level 1: JSON/YAML syntax
  - Level 2: Required frontmatter fields
  - Level 4: Argument validation
  - Level 5: File reference validation
  - Level 6: Shellcheck
  - Level 7: Integration tests (bats)
- **Quick validation:** `make check` or `scripts/validate-all.sh --quick`
- **Full tests:** `make test-all` (includes slow integration tests)

### Git Workflow

- **Pre-commit hooks:** Validate syntax, frontmatter, and bash scripts on every commit
- **Branch strategy:** Feature branches merged to `master`
- **Validation before merge:** `make check` must pass
- **Commit messages:** Conventional commits style encouraged

## Domain Context

**Plugin Types:**
1. **Workflow plugins** (`plugins/`) - Core methodology (TDD, debugging, planning)
2. **Domain plugins** (`domain_plugins/`) - Language-specific guidance

**Key Workflow:**
```
SessionStart hook → loads getting-started skill
  ↓
/dev-workflow:brainstorm (optional) → refine ideas
  ↓
EnterPlanMode → design implementation
  ↓
ExitPlanMode(launchSwarm: true) → parallel execution
  ↓
Post-swarm: code review + finish branch
```

**Skills with Checklists:** Require TodoWrite tracking during execution.

## Important Constraints

- **No external runtime dependencies** - Plugins should work with only git installed
- **Claude Code native primitives** - Use built-in tools (EnterPlanMode, Task, TodoWrite) rather than custom solutions
- **Frontmatter validation** - All components must pass validation levels 1-2
- **Shellcheck compliance** - All bash scripts must pass shellcheck

## External Dependencies

**Required:**
- `git` - Version control

**Development:**
- `bats-core` - Testing framework
- `shellcheck` - Shell linting
- `jq` - JSON processing
- `uv` - Python package manager (for pre-commit)
- `pre-commit` - Git hook management
