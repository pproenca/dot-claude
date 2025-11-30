# dot-claude

Claude Code plugins for productivity workflows - skills, agents, commands, and hooks.

## Overview

dot-claude is a collection of plugins that extend Claude Code with specialized capabilities for software engineering workflows. It provides:

- **29 Skills** - Reusable workflow patterns for TDD, debugging, documentation, and more
- **16 Agents** - Specialized subagents for code review, security analysis, and expert domains
- **16 Commands** - Slash commands for common tasks like commits, planning, and scaffolding
- **Hooks** - Automated enforcement of TDD, commit standards, and verification workflows

## Plugins

| Plugin | Purpose |
|--------|---------|
| **super** | Core workflows: TDD enforcement, verification, brainstorming, debugging, code review |
| **commit** | Git workflows with Conventional Commits, PR generation, branch organization |
| **dev** | Python development with uv, pytest, FastAPI, Django, async patterns |
| **doc** | Documentation generation, API docs, tutorials, Amazon-style memos |
| **shell** | Shell scripting with Google Shell Style Guide |
| **debug** | Distributed systems debugging and log correlation |
| **agent** | Multi-agent orchestration and context management |
| **blackbox** | Flight recorder hooks for telemetry and recovery |

## Installation

### Prerequisites

```bash
# macOS
brew install jq yq ripgrep fd coreutils

# Python 3.8+ required (3.12+ recommended)
python3 --version
```

### Setup

1. Clone the repository:
```bash
git clone https://github.com/pedroproenca/dot-claude.git
cd dot-claude
```

2. Validate plugins:
```bash
./scripts/validate-plugins.sh
```

3. Sync configuration (from within Claude Code):
```
/sync-claude-config
```

## Quick Start

### Using Skills

Skills are invoked automatically when relevant, or manually via the Skill tool:

```
# TDD workflow
skill: super:test-driven-development

# Python project setup
skill: dev:uv-package-manager

# Documentation writing
skill: doc:amazon-writing
```

### Using Commands

Slash commands expand to full prompts:

```
/super:plan          # Create implementation plan
/commit:new          # Create Conventional Commit
/dev:scaffold        # Scaffold Python project
/doc:gen             # Generate documentation
```

### Using Agents

Agents are specialized subagents invoked via Task tool:

```python
# Code review
Task(subagent_type="super:code-reviewer", prompt="Review the authentication module")

# Python expertise
Task(subagent_type="dev:python-pro", prompt="Optimize async database queries")

# Security analysis
Task(subagent_type="super:security-reviewer", prompt="Audit API endpoints for OWASP vulnerabilities")
```

## Key Features

### TDD Enforcement

The `super` plugin enforces test-driven development:

1. **TDD Guard Hook** - Blocks production file edits unless test file edited first
2. **Verification Hook** - Requires test/build evidence before completion claims

### Conventional Commits

The `commit` plugin validates git commits:

- Subject line format and length limits
- Type prefixes: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Body explains WHY, not WHAT
- One logical change per commit

### Workflow Automation

| Hook | Plugin | Behavior |
|------|--------|----------|
| TDD Guard | super | Blocks code without tests |
| Worktree Guard | super | Warns about git worktree awareness |
| Verification | super | Requires test output for done claims |
| Commit Validation | commit | Enforces Conventional Commits |
| Shell Validation | shell | Checks syntax before file creation |

## Plugin Details

### super (Core Workflows)

**Skills:**
- `test-driven-development` - Write tests first, watch fail, write minimal code
- `systematic-debugging` - Four-phase debugging framework
- `brainstorming` - Socratic method design refinement
- `verification-before-completion` - Evidence-based success claims
- `writing-plans` - Detailed implementation plans
- `dispatching-parallel-agents` - Concurrent agent deployment

**Agents:**
- `code-reviewer` - Reviews code against plans and standards
- `diagram-generator` - Creates architecture diagrams
- `security-reviewer` - Security vulnerability assessment

**Commands:**
- `/super:plan` - Create implementation plan
- `/super:brainstorm` - Interactive design refinement
- `/super:exec` - Execute plan with review checkpoints
- `/super:context` - Show project context for resuming
- `/super:notes` - Add session notes to CLAUDE.md

### commit (Git Workflows)

**Skills:**
- `git-commit` - Safe commit wrapper with signed commits support

**Agents:**
- `commit-organizer` - Reorganizes commits following Conventional Commits

**Commands:**
- `/commit:new` - Create commit from staged changes
- `/commit:pr [base-branch]` - Generate PR title and description
- `/commit:reset` - Reset and reorganize commits

### dev (Python Development)

**Skills:**
- `uv-package-manager` - Fast dependency management
- `python-testing-patterns` - pytest, fixtures, mocking
- `python-packaging` - pyproject.toml, PyPI publishing
- `python-performance-optimization` - Profiling and optimization
- `async-python-patterns` - asyncio and concurrent programming

**Agents:**
- `python-pro` - Python 3.12+ expert
- `fastapi-pro` - FastAPI API development
- `django-pro` - Django web framework

**Commands:**
- `/dev:scaffold` - Python project scaffolding

### doc (Documentation)

**Skills:**
- `amazon-writing` - Narrative writing (6-pagers, PRFAQs, memos)

**Agents:**
- `api-documenter` - OpenAPI/REST documentation
- `docs-architect` - Documentation strategy
- `mermaid-expert` - Diagrams and flowcharts
- `reference-builder` - Complete reference docs
- `tutorial-engineer` - Step-by-step tutorials

**Commands:**
- `/doc:explain` - Code explanation
- `/doc:rewrite [type]` - Rewrite following Amazon standards
- `/doc:gen` - Automated documentation generation

### shell (Shell Scripting)

**Skills:**
- `google-shell-style` - Google Shell Style Guide enforcement
- `man` - Unix man page lookup

**Agents:**
- `shell-expert` - Shell scripting specialist

**Commands:**
- `/shell:refactor path/to/script.sh` - Refactor following Google style

### debug (Distributed Systems)

**Agents:**
- `error-detective` - Stack trace analysis
- `devops-troubleshooter` - Log analysis and correlation

**Commands:**
- `/debug:trace` - Debug and trace configuration

### agent (Orchestration)

**Agents:**
- `context-manager` - Multi-agent workflow orchestration

**Commands:**
- `/agent:improve` - Agent performance optimization
- `/agent:optimize` - Multi-agent optimization

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
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/tdd-guard.sh",
            "timeout": 5
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
    "allow": ["Bash(git:*)", "Bash(uv:*)", "Skill(super:*)"],
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
3. Test with `super:testing-skills-with-subagents` skill

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
# Validate all plugins
./scripts/validate-plugins.sh
```

## Contributing

Use the `super:sharing-skills` skill for contributing skills upstream via PR.

1. Fork the repository
2. Create a feature branch
3. Make changes following existing patterns
4. Run validation: `./scripts/validate-plugins.sh`
5. Submit a pull request

## License

MIT

## Author

Pedro Proenca (pedro@10xengs.com)
