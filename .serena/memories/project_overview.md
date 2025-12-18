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
└── dev-workflow/      # TDD, debugging, planning skills
    ├── agents/        # Subagent definitions
    ├── commands/      # Slash commands (/brainstorm, /write-plan, etc.)
    ├── hooks/         # Event hooks (session-start, stop, etc.)
    ├── scripts/       # Bash helper scripts
    ├── skills/        # Skills (TDD, debugging, etc.)
    ├── references/    # Shared docs
    └── tests/         # Bats test files

domain_plugins/
├── dev-python/        # Python 3.12+ development plugin
│   ├── agents/
│   ├── commands/
│   ├── hooks/
│   ├── references/
│   └── skills/
└── shell/             # Shell scripting plugin
    ├── agents/
    ├── commands/
    └── skills/

scripts/               # Marketplace validation scripts
├── lib/               # Common shell functions
├── level-1-syntax.sh  # JSON/YAML syntax validation
├── level-2-frontmatter.sh
├── level-4-arguments.sh
├── level-5-file-refs.sh
├── level-6-bash.sh
├── level-7-integration.sh
└── validate-all.sh    # Orchestrates all levels

.claude-plugin/        # Marketplace manifest
Makefile               # Build automation
pyproject.toml         # Python/uv config
.pre-commit-config.yaml # Git hooks
```

## Plugin Organization
- **`plugins/`**: Core workflow plugins (language-agnostic)
- **`domain_plugins/`**: Language/domain-specific plugins

## Plugin Architecture
Each plugin follows the Claude Code plugin structure:
- `.claude-plugin/plugin.json` - Plugin manifest
- `agents/*.md` - Subagent definitions
- `commands/*.md` - Slash command definitions
- `skills/*/SKILL.md` - Skill definitions with frontmatter
- `hooks/hooks.json` - Event hook registrations
- `scripts/*.sh` - Helper bash scripts
