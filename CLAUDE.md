# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

dot-claude is a collection of Claude Code plugins providing skills, agents, commands, and hooks for software engineering workflows. It extends Claude Code with specialized capabilities for TDD, debugging, git workflows, documentation, Python development, and shell scripting.

## Commands

### Plugin Validation
```bash
./scripts/validate-plugins.sh
```
Validates all plugins using `claude plugin validate`.

### Configuration Sync
```
/sync-claude-config
```
Syncs settings, statusline, and hookify files between project `.claude/` and `~/.claude/`.

## Architecture

### Plugin Structure

Each plugin follows this layout:
```
plugins/<name>/
  .claude-plugin/
    plugin.json          # Metadata (name, version, description)
  skills/
    <skill-name>/
      SKILL.md           # Skill document with YAML frontmatter
  agents/
    <name>.md            # Agent definitions
  commands/
    <name>.md            # Slash command prompts
  hooks/
    hooks.json           # Hook configuration
    *.sh, *.py           # Hook scripts
```

### Plugins

| Plugin | Purpose |
|--------|---------|
| **super** | Core workflows: TDD enforcement, verification, brainstorming, debugging, code review |
| **commit** | Git: Conventional Commits, PR creation, branch organization |
| **dev** | Python: uv, async, FastAPI, Django, testing patterns |
| **doc** | Documentation: API docs, tutorials, Amazon-style memos, Mermaid |
| **shell** | Shell scripting with Google Shell Style Guide |
| **debug** | Distributed systems debugging and log correlation |
| **agent** | Multi-agent orchestration |
| **analyze** | Marketplace plugin analyzer for quality standards |
| **blackbox** | Flight recorder hooks for telemetry |

### Hook System

Hooks enforce workflows via JSON configuration in `hooks/hooks.json`. Four hook types:
- **SessionStart** - Runs on conversation start/resume/clear/compact
- **PreToolUse** - Runs before tool execution (can block with `deny`)
- **PostToolUse** - Runs after tool execution
- **Stop** - Runs when conversation ends (can block completion)

Key enforced behaviors:
- **TDD Guard** (`super`): Blocks production file edits unless test file edited first
- **Worktree Guard** (`super`): Warns about git worktree awareness
- **Verification** (`super`): Blocks completion claims without test/build evidence
- **Commit Safety** (`commit`): Validates commits against Conventional Commits

### Skills

Skills are SKILL.md files with YAML frontmatter:
```yaml
---
name: skill-name
description: Use when [condition] - [what it does]
allowed-tools: Bash(pytest:*), Write, Edit, Read
---
```

The `allowed-tools` field restricts which tools the skill can use.

### Agents

Agents are subagent definitions in `agents/*.md`. They're invoked via the Task tool with `subagent_type` matching the agent name.

### Commands

Slash commands in `commands/*.md` expand to full prompts. Invoke with `/plugin:command` syntax (e.g., `/super:plan`, `/commit:new`).

## Key Workflows

### Verification Before Completion (super plugin)

The Stop hook prompt checks:
1. Claims of "complete/fixed/passing/done" require verification command output
2. Plan execution requires `finishing-a-development-branch` skill usage

### Commit Validation (commit plugin)

PostToolUse hooks validate git commits against Conventional Commits:
- Subject line format and length
- Body explains WHY not WHAT
- One logical change per commit
- No mixed refactoring with features

## Development

### Prerequisites
```bash
# macOS
brew install jq yq ripgrep fd coreutils
```

### Creating Skills

1. Create `plugins/<plugin>/skills/<name>/SKILL.md`
2. Add YAML frontmatter with `name`, `description`, and optional `allowed-tools`
3. Test with `super:testing-skills-with-subagents` skill

### Creating Agents

1. Create `plugins/<plugin>/agents/<name>.md`
2. Define the agent's role and capabilities
3. Register in plugin if needed

### Creating Hooks

1. Add hook configuration to `plugins/<plugin>/hooks/hooks.json`
2. Create hook script (`.sh` or `.py`)
3. Use `$CLAUDE_PLUGIN_ROOT` for relative paths
4. Return JSON with `hookSpecificOutput.permissionDecision` for PreToolUse hooks

## Configuration

Project settings in `.claude/settings.json`:
- `permissions.allow` - Auto-approved tool patterns
- `permissions.deny` - Blocked tool patterns
- `permissions.ask` - Require user approval
- `statusLine` - Custom status line command

## Contributing

Use `super:sharing-skills` skill for contributing skills upstream via PR.
- Remember to make worktrees local to the project