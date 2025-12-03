# dot-claude

Claude Code plugins for productivity workflows - skills, agents, commands, and hooks.

## Overview

dot-claude is a collection of plugins that extend Claude Code with specialized capabilities for software engineering workflows. It provides:

- **30 Skills** - Reusable workflow patterns for TDD, debugging, documentation, and more
- **19 Agents** - Specialized subagents for code review, security analysis, and expert domains
- **17 Commands** - Slash commands for common tasks like commits, planning, and scaffolding
- **Hooks** - Automated enforcement of TDD, commit standards, and verification workflows

## Plugins

| Plugin | Purpose |
|--------|---------|
| **core** | Essential workflows: TDD enforcement, verification, brainstorming |
| **workflow** | Planning and execution: plans, subagents, worktrees, branch finishing |
| **review** | Code review: requesting reviews, receiving feedback, security analysis |
| **testing** | Test patterns: anti-patterns, condition-based waiting |
| **commit** | Git workflows with Conventional Commits, PR generation, branch organization |
| **python** | Python development with uv, pytest, FastAPI, Django, async patterns |
| **doc** | Documentation generation, API docs, tutorials, Amazon-style memos |
| **shell** | Shell scripting with Google Shell Style Guide |
| **debug** | Distributed systems debugging and log correlation |
| **meta** | Plugin development: writing skills, testing skills, marketplace analysis |

> **Note:** The `super` plugin has been split into focused modules: `core`, `workflow`, `review`, `testing`, and `debug`. See [MIGRATION.md](MIGRATION.md) for migration guide.

## Installation

### Prerequisites

```bash
# macOS - install system dependencies
brew install jq yq ripgrep fd coreutils

# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup

1. Clone the repository:

```bash
git clone https://github.com/pedroproenca/dot-claude.git
cd dot-claude
```

2. Install Python dependencies:

```bash
uv sync
```

3. Validate plugins:

```bash
uv run python scripts/validate-plugins.py
```

4. (Optional) Install pre-commit hooks for development:

```bash
uv run pre-commit install
```

5. Sync configuration (from within Claude Code):

```
/sync-claude-config
```

## Quick Start

### Using Skills

Skills are invoked automatically when relevant, or manually via the Skill tool:

```
# TDD workflow
skill: core:tdd

# Python project setup
skill: python:uv-package-manager

# Documentation writing
skill: doc:amazon-writing
```

### Using Commands

Slash commands expand to full prompts:

```
/workflow:plan       # Create implementation plan
/commit:new          # Create Conventional Commit
/python:refactor     # Refactor Python file
/doc:gen             # Generate documentation
```

### Using Agents

Agents are specialized subagents invoked via Task tool:

```python
# Code review
Task(subagent_type="review:code-reviewer", prompt="Review the authentication module")

# Python expertise
Task(subagent_type="python:python-expert", prompt="Optimize async database queries")

# Security analysis
Task(subagent_type="review:security-reviewer", prompt="Audit API endpoints for OWASP vulnerabilities")
```

## Key Features

### TDD Enforcement

The `core` plugin enforces test-driven development through multiple mechanisms:

1. **TDD Guard Hook** - Blocks production file edits unless test files are edited first
2. **Verification Hook** - Requires test/build evidence before completion claims
3. **core:tdd Skill** - Guides writing tests first, watching them fail, then implementing minimal code to pass

### Conventional Commits

The `commit` plugin validates git commits:

- Subject line format and length limits
- Type prefixes: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Body explains WHY, not WHAT
- One logical change per commit

### Workflow Automation

| Hook | Plugin | Type | Behavior |
|------|--------|------|----------|
| TDD Guard | core | PreToolUse | Blocks production file edits unless test files edited first |
| Verification | core | Stop | Requires test/build evidence before completion claims |
| Worktree Guard | workflow | PreToolUse | Warns about git worktree awareness |
| Git Safety | commit | PreToolUse | Validates git commands before execution |
| Commit Validation | commit | PostToolUse | Enforces Conventional Commits format |
| Shell Validation | shell | PreToolUse | Checks shell syntax before file creation |
| Context Preservation | shell | PreCompact | Preserves important context during compaction |

## Plugin Details

### core (Essential Workflows)

**Skills (3):**

- `tdd` - Write tests first, watch fail, write minimal code to pass
- `brainstorming` - Socratic method design refinement before implementation
- `verification` - Evidence-based success claims with test/build output

**Commands (1):**

- `/core:context` - Show project context for resuming work

**Hooks:**

- TDD Guard (PreToolUse) - Blocks production edits without test file changes first
- Verification (Stop) - Requires evidence before completion claims

### workflow (Planning & Execution)

**Skills (6):**

- `writing-plans` - Detailed implementation plans with exact file paths
- `executing-plans` - Execute plans in controlled batches with review checkpoints
- `git-worktrees` - Create isolated git worktrees for feature work
- `finish-branch` - Guide completion with merge/PR/cleanup options
- `subagent-dev` - Fresh subagent per task with code review gates
- `parallel-agents` - Concurrent agent deployment for independent failures

**Commands (2):**

- `/workflow:plan` - Create detailed implementation plan
- `/workflow:exec` - Execute plan with review checkpoints

**Hooks:**

- Worktree Guard (PreToolUse) - Warns about git worktree awareness

### review (Code Review)

**Skills (1):**

- `code-review` - Dispatch code-reviewer subagent and handle feedback with technical rigor

**Agents (2):**

- `code-reviewer` - Reviews code against plans and standards
- `security-reviewer` - Security vulnerability assessment (OWASP, CWE)

### testing (Test Patterns)

**Skills (2):**

- `anti-patterns` - Prevent testing mock behavior and production pollution
- `condition-wait` - Replace arbitrary timeouts with condition polling

### debug (Debugging)

**Skills (3):**

- `systematic` - Four-phase framework: investigate, analyze, hypothesize, implement
- `root-cause` - Trace bugs backward through call stack with instrumentation
- `defense-in-depth` - Validate at entry, business logic, and environment layers

**Agents (2):**

- `devops-troubleshooter` - Incident response and infrastructure debugging
- `error-detective` - Search logs and correlate errors across systems

### commit (Git Workflows)

**Skills (1):**

- `git-commit` - Safe commit wrapper with signed commits support

**Agents (1):**

- `commit-organizer` - Reorganizes commits following Conventional Commits

**Commands (3):**

- `/commit:new` - Create commit from staged changes
- `/commit:pr [base-branch]` - Generate PR title and description
- `/commit:reset` - Reset and reorganize commits

### python (Python Development)

**Skills (5):**

- `async-python-patterns` - asyncio and concurrent programming
- `python-packaging` - pyproject.toml, PyPI publishing
- `python-performance-optimization` - Profiling and optimization
- `python-testing-patterns` - pytest, fixtures, mocking
- `uv-package-manager` - Fast dependency management

**Agents (1):**

- `python-expert` - Python 3.12+ expert with FastAPI and Django knowledge

**Commands (1):**

- `/python:refactor` - Refactor Python file with ruff, mypy, and modern patterns

### doc (Documentation)

**Skills (1):**

- `amazon-writing` - Narrative writing (6-pagers, PRFAQs, memos)

**Agents (5):**

- `api-documenter` - OpenAPI/REST documentation
- `docs-architect` - Documentation strategy
- `mermaid-expert` - Diagrams and flowcharts
- `reference-builder` - Complete reference docs
- `tutorial-engineer` - Step-by-step tutorials

**Commands (7):**

- `/doc:explain` - Code explanation
- `/doc:rewrite [type]` - Rewrite following Amazon standards
- `/doc:gen` - Automated documentation generation
- `/doc:api-spec` - Generate OpenAPI specs and interactive API docs
- `/doc:architecture` - Create system architecture documentation
- `/doc:reference` - Create parameter and configuration references
- `/doc:tutorial` - Create step-by-step tutorials

### shell (Shell Scripting)

**Skills (2):**

- `google-shell-style` - Google Shell Style Guide enforcement
- `man` - Unix man page lookup

**Agents (1):**

- `shell-expert` - Shell scripting specialist

**Commands (1):**

- `/shell:refactor path/to/script.sh` - Refactor following Google style

### debug (Distributed Systems)

**Agents (2):**

- `devops-troubleshooter` - Log analysis and correlation
- `error-detective` - Stack trace analysis

**Commands (1):**

- `/debug:trace` - Debug and trace configuration

### meta (Plugin Development)

**Skills (3):**

- `writing-skills` - Guide for creating effective skills with YAML frontmatter
- `testing-skills` - Test skills with subagents using RED-GREEN-REFACTOR
- `marketplace-analysis` - Systematic DX, architecture, and capability analysis

**Agents (3):**

- `capability-analyzer` - Analyze plugin capabilities and features
- `marketplace-orchestrator` - Orchestrate marketplace analysis workflows
- `structure-analyzer` - Analyze plugin structure and architecture

**Commands (1):**

- `/meta:marketplace` - Analyze plugin for marketplace quality standards

## Architecture

### Plugin Structure

```
plugins/<name>/
├── .claude-plugin/
│   └── plugin.json          # Metadata
├── skills/
│   └── <skill-name>/
│       └── SKILL.md         # YAML frontmatter + content
├── agents/
│   └── <name>.md            # Agent definitions
├── commands/
│   └── <name>.md            # Slash command prompts
└── hooks/
    ├── hooks.json           # Hook configuration
    └── *.sh, *.py           # Hook scripts
```

### Skill Format

Skills use YAML frontmatter with optional tool restrictions:

```yaml
---
name: skill-name
description: Use when [condition] - [what it does]
allowed-tools: Bash(pytest:*), Write, Edit, Read
---

# Skill content with instructions and examples
```

### Hook Configuration

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/worktree-guard.sh",
            "timeout": 3
          }
        ]
      }
    ]
  }
}
```

## Configuration

### Permissions

The `.claude/settings.json` file controls tool permissions:

```json
{
  "permissions": {
    "allow": ["Bash(git:*)", "Bash(uv:*)", "Skill(core:*)", "Skill(workflow:*)"],
    "ask": ["Bash(git push:*)", "Bash(rm:*)"]
  }
}
```

### Status Line

Custom status line shows session metrics:

```
[model] directory | duration | +lines -lines | $cost
```

## Development

### Creating Skills

1. Create `plugins/<plugin>/skills/<name>/SKILL.md`
2. Add YAML frontmatter with `name`, `description`, optional `allowed-tools`
3. Test with `meta:testing-skills` skill

### Creating Agents

1. Create `plugins/<plugin>/agents/<name>.md`
2. Define role, capabilities, and model preference
3. Register in plugin if needed

### Creating Hooks

1. Add configuration to `plugins/<plugin>/hooks/hooks.json`
2. Create hook script (`.sh` or `.py`)
3. Use `$CLAUDE_PLUGIN_ROOT` for relative paths
4. Return JSON with `permissionDecision` for PreToolUse hooks

### Validation

```bash
# Run full test suite
uv run pytest tests/

# Validate all plugins
uv run python scripts/validate-plugins.py

# Validate cross-references
uv run python scripts/validate-references.py

# Validate settings.json files
uv run python scripts/validate-settings.py
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make changes following existing patterns
4. Run validation: `uv run pytest tests/`
5. Submit a pull request

Use the `meta:writing-skills` skill when creating new skills for the marketplace.

## License

MIT

## Author

Pedro Proenca (pedro@10xengs.com)
