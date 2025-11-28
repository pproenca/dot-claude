# dot-claude

A collection of Claude Code plugins providing skills, agents, commands, and hooks for software engineering workflows.

## Overview

dot-claude extends Claude Code with specialized workflows for:

- **TDD and verification** - Enforced test-driven development and completion verification
- **Debugging** - Systematic debugging, root cause analysis, log correlation
- **Git workflows** - Google-style commits, PR creation, branch management
- **Documentation** - API docs, tutorials, Amazon-style memos, Mermaid diagrams
- **Python development** - Modern Python with uv, FastAPI, Django, async patterns
- **Shell scripting** - Google Shell Style Guide refactoring

## Installation

### Option 1: Clone and symlink (recommended for development)

```bash
git clone https://github.com/pedroproenca/dot-claude.git
cd dot-claude

# Symlink each plugin to Claude Code
for plugin in plugins/*/; do
  ln -sf "$(pwd)/$plugin" ~/.claude/plugins/
done
```

### Option 2: Add to project settings

Add to your project's `.claude/settings.json`:

```json
{
  "plugins": [
    "/path/to/dot-claude/plugins/super",
    "/path/to/dot-claude/plugins/commit",
    "/path/to/dot-claude/plugins/dev"
  ]
}
```

## Plugins

| Plugin | Description |
|--------|-------------|
| [**super**](docs/PLUGINS.md#super) | Core skills: TDD, debugging, code review, brainstorming |
| [**commit**](docs/PLUGINS.md#commit) | Git workflows: commits, PRs, branch organization |
| [**dev**](docs/PLUGINS.md#dev) | Python: uv, async, FastAPI, Django, testing |
| [**doc**](docs/PLUGINS.md#doc) | Documentation: API docs, tutorials, diagrams |
| [**shell**](docs/PLUGINS.md#shell) | Shell scripting with Google Style Guide |
| [**debug**](docs/PLUGINS.md#debug) | Distributed systems debugging |
| [**agent**](docs/PLUGINS.md#agent) | Multi-agent orchestration |

## Quick Start

### Using Skills

Skills are reusable techniques. Invoke with the Skill tool:

```
I'm using the brainstorming skill to design this feature.
```

Common skills:
- `super:brainstorming` - Design before coding
- `super:test-driven-development` - RED-GREEN-REFACTOR cycle
- `super:systematic-debugging` - Four-phase investigation
- `dev:python-testing-patterns` - pytest and mocking

### Using Commands

Slash commands expand to full prompts:

```
/super:plan           # Create implementation plan
/commit:new           # Create Google-style commit
/doc:gen              # Generate documentation
/shell:refactor path  # Refactor shell script
```

### Using Agents

Agents are specialized subagents:

```
Use the code-reviewer agent to review this implementation.
Use the fastapi-pro agent to build this API.
```

## Key Workflows

### TDD Enforcement

The `super` plugin enforces test-driven development:

1. **PreToolUse hook** blocks writing production code without tests
2. Writing test files is always allowed
3. Production code requires recent test runs

### Verification Before Completion

The `super` plugin requires evidence before claiming "done":

1. **Stop hook** checks if verification commands were run
2. Blocks completion without test/build output
3. Ensures claims match actual results

### Brainstorming Before Coding

Design before implementation:

1. Use `super:brainstorming` skill
2. Collaborative design refinement
3. Explore alternatives before committing

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and component relationships
- [Plugin Reference](docs/PLUGINS.md) - Complete plugin documentation
- [Getting Started](docs/GETTING-STARTED.md) - Installation and first steps

## Plugin Structure

Each plugin follows this layout:

```
plugins/<name>/
  .claude-plugin/
    plugin.json          # Metadata
  skills/
    <skill-name>/
      SKILL.md           # Skill document
  agents/
    <name>.md            # Agent definitions
  commands/
    <name>.md            # Slash commands
  hooks/
    hooks.json           # Hook configuration
    *.sh                 # Hook scripts
```

## Creating Skills

1. Create `plugins/<plugin>/skills/<name>/SKILL.md`
2. Add YAML frontmatter:

```yaml
---
name: skill-name
description: Use when [condition] - [what it does]
---

# Skill Content
```

3. Test with subagents (see `super:testing-skills-with-subagents`)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow TDD: write tests first
4. Submit a pull request

See `super:sharing-skills` for contributing skills upstream.

## License

MIT
