# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **dot-claude**, a collection of Claude Code plugins providing skills, agents, commands, and hooks. Plugins extend Claude Code with specialized workflows for TDD, debugging, git, documentation, shell scripting, and Python development.

## Architecture

### Plugin Structure

Each plugin lives in `plugins/<name>/` with a standardized layout:

```
plugins/<name>/
  .claude-plugin/
    plugin.json          # Plugin metadata (name, version, description)
  agents/                # Subagent definitions (.md files with YAML frontmatter)
  commands/              # Slash commands (.md files with frontmatter)
  skills/
    <skill-name>/
      SKILL.md           # Main skill document (YAML frontmatter required)
      supporting-file.*  # Optional: heavy references, reusable scripts
  hooks/
    hooks.json           # Hook configuration (SessionStart, PreToolUse, PostToolUse, Stop)
    *.sh                 # Hook scripts
  cheatsheets/           # Reference documentation
  lib/                   # Shared JavaScript utilities
```

### Available Plugins

| Plugin | Purpose |
|--------|---------|
| **super** | Core skills: TDD, debugging, code review, brainstorming, verification workflows |
| **commit** | Git workflows: structured commits, PRs, branch organization (Google-style) |
| **dev** | Python development: uv, async patterns, FastAPI, Django, testing, packaging |
| **doc** | Documentation: API docs, tutorials, Mermaid diagrams, Amazon-style memos |
| **shell** | Shell scripting with Google Shell Style Guide refactoring |
| **debug** | Distributed systems debugging, log analysis, error correlation |
| **agent** | Context engineering and multi-agent orchestration |

### Key Concepts

**Skills** are reusable techniques in SKILL.md with YAML frontmatter:
```yaml
---
name: skill-name
description: Use when [condition] - [what it does]
---
```
- Description starts with "Use when..." for discoverability
- Skills document proven techniques, not narratives about past solutions
- Follow TDD for skill creation (see `super:writing-skills`)

**Agents** are subagent definitions with model, color, and prompt configuration

**Commands** are slash commands expanding to full prompts

**Hooks** intercept tool usage at SessionStart, PreToolUse, PostToolUse, and Stop events

### Core Workflows

The `super` plugin enforces critical patterns:
- **TDD (`test-driven-development`)**: RED-GREEN-REFACTOR cycle for all code
- **Verification (`verification-before-completion`)**: Run tests before claiming "done"
- **Brainstorming (`brainstorming`)**: Design before coding
- **Systematic debugging (`systematic-debugging`)**: Four-phase investigation

These are enforced via hooks in `super/hooks/hooks.json`.

## Development

### Adding a New Skill

1. Create `plugins/<plugin>/skills/<skill-name>/SKILL.md`
2. Include YAML frontmatter with `name` and `description` (max 1024 chars total)
3. Test skill with subagents before deployment (see `super:testing-skills-with-subagents`)
4. Follow RED-GREEN-REFACTOR: baseline test -> write skill -> close loopholes

### Adding a New Command

Create `plugins/<plugin>/commands/<name>.md` with frontmatter:
```yaml
---
description: One-line description
argument-hint: "optional args"
allowed-tools: [Bash, Read, Task]
---
```

### Adding a New Agent

Create `plugins/<plugin>/agents/<name>.md` with frontmatter:
```yaml
---
name: agent-name
description: |
  When to use examples with <example> tags
model: claude-opus-4-5-20251101
color: magenta
---
```

### Hook Configuration

Edit `plugins/<plugin>/hooks/hooks.json`:
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/hooks/script.sh"
      }]
    }]
  }
}
```

## Key Files

- `plugins/super/lib/skills-core.js` - Skill discovery and resolution logic
- `plugins/super/hooks/tdd-guard.sh` - Enforces TDD for Write/Edit operations
- `plugins/commit/cheatsheets/google-guidelines.md` - Commit message standards
- `.claude/settings.json` - Local Claude Code settings
- `.claude/statusline.sh` - Custom statusline configuration

## Shell Script Standards

When writing shell scripts (.sh files):

1. **Always include shebang:** `#!/bin/bash` or `#!/bin/sh`
2. **Use defensive header for bash scripts:**
   ```bash
   set -euo pipefail
   ```
3. **Quote all variables:** `"${var}"` not `$var`
4. **Use modern syntax:** `$(command)` not backticks, `[[ ]]` not `[ ]`
5. **PreToolUse hooks validate:** syntax (bash -n) and shellcheck if available
6. **Avoid Bash 4+ features:** Don't use `mapfile`/`readarray` (macOS has Bash 3.2). Use `while read` loops instead.

## Testing

Skills use subagent-based testing rather than traditional unit tests. See `super:testing-skills-with-subagents` for the methodology.
