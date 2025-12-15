# Project Overview

## Purpose
`dot-claude` is a personal Claude Code plugins marketplace containing custom plugins for development workflows.

## Tech Stack
- **Shell/Bash**: Primary scripting language for hooks and scripts
- **Python**: Managed via uv for dev dependencies (pre-commit)
- **Markdown**: Plugin skills, commands, and documentation

## Structure
```
plugins/
├── dev-workflow/      # TDD, debugging, planning skills (v2.4.2)
│   ├── agents/        # Subagent definitions
│   ├── commands/      # Slash commands (/brainstorm, /write-plan, etc.)
│   ├── hooks/         # Event hooks (session-start, stop, etc.)
│   ├── scripts/       # Bash helper scripts
│   ├── skills/        # Skills (TDD, debugging, etc.)
│   └── tests/         # Bats test files
├── dev-python/        # Python 3.12+ development plugin (v1.0.0)
│   ├── agents/
│   ├── commands/
│   ├── hooks/
│   └── skills/
└── shell/             # Shell scripting plugin
    ├── agents/
    ├── commands/
    └── skills/

Makefile               # Build automation
pyproject.toml         # Python/uv config
.pre-commit-config.yaml # Git hooks
```

## Plugin Architecture
Each plugin follows the Claude Code plugin structure:
- `.claude-plugin/plugin.json` - Plugin manifest
- `agents/*.md` - Subagent definitions
- `commands/*.md` - Slash command definitions
- `skills/*/SKILL.md` - Skill definitions with frontmatter
- `hooks/hooks.json` - Event hook registrations
- `scripts/*.sh` - Helper bash scripts
