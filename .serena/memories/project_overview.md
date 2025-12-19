# Project Overview

## Purpose
`dot-claude` is a personal Claude Code plugins marketplace containing custom plugins for development workflows.

## Tech Stack
- **Shell/Bash**: Primary scripting language for hooks and scripts
- **Python**: Managed via uv for dev dependencies (pre-commit)
- **Markdown**: Plugin skills, commands, and documentation

## Plugins

| Plugin | Location | Description |
|--------|----------|-------------|
| dev-workflow | `plugins/dev-workflow/` | TDD, debugging, planning skills (11 skills) |
| dev-python | `domain_plugins/dev-python/` | Python 3.12+ development with uv, ruff, pydantic, FastAPI, Django |
| shell | `domain_plugins/shell/` | Shell scripting with Google Style Guide |

## Workflow

The primary workflow uses native Claude Code plan mode:

```
/dev-workflow:brainstorm (optional) → EnterPlanMode → ExitPlanMode(launchSwarm: true)
                                           ↓
                              SessionStart injects methodology:
                              - TDD task structure
                              - Pragmatic architecture
                              - Parallel grouping
                              - Post-swarm actions
```

**SessionStart hook** loads `getting-started` skill which establishes:
- Skill check protocol before any task
- Planning methodology for native plan mode
- Post-completion actions (code review, finish branch)

## Structure
```
plugins/
└── dev-workflow/              # Core workflow plugin
    ├── .claude-plugin/        # Plugin manifest
    ├── agents/                # code-reviewer, code-explorer, code-architect
    ├── commands/              # /brainstorm, /write-plan, /execute-plan, /resume, /abandon
    ├── hooks/                 # SessionStart, stop hooks
    ├── scripts/               # Bash helpers (hook-helpers.sh, validate.sh)
    ├── skills/                # 11 skills (TDD, debugging, verification, etc.)
    ├── references/            # Shared docs (skill-integration, planning-philosophy)
    └── tests/                 # Bats test files

domain_plugins/
├── dev-python/                # Python domain plugin
│   ├── .claude-plugin/
│   ├── agents/                # python-expert, async-python-specialist, django-specialist
│   ├── commands/              # /refactor
│   ├── hooks/                 # detect-python-version, pytest-runner
│   ├── references/            # Style guides, version features
│   └── skills/                # python-project, python-testing, python-performance
└── shell/                     # Shell domain plugin
    ├── .claude-plugin/
    ├── agents/                # shell-expert
    ├── commands/              # /refactor
    └── skills/                # google-shell-style

scripts/                       # Marketplace validation scripts
├── lib/                       # Common shell functions
├── level-1-syntax.sh          # JSON/YAML syntax validation
├── level-2-frontmatter.sh     # YAML frontmatter
├── level-4-arguments.sh       # Command arguments
├── level-5-file-refs.sh       # File references
├── level-6-bash.sh            # Bash syntax in markdown
├── level-7-integration.sh     # Integration tests
└── validate-all.sh            # Orchestrates all levels

Makefile                       # Build automation
pyproject.toml                 # Python/uv config
.pre-commit-config.yaml        # Git hooks
```

## Plugin Architecture
Each plugin follows the Claude Code plugin structure:
- `.claude-plugin/plugin.json` - Plugin manifest
- `agents/*.md` - Subagent definitions
- `commands/*.md` - Slash command definitions
- `skills/*/SKILL.md` - Skill definitions with frontmatter
- `hooks/hooks.json` - Event hook registrations
- `scripts/*.sh` - Helper bash scripts

## dev-workflow Skills (11)

| Category | Skills |
|----------|--------|
| Methodology | `test-driven-development`, `systematic-debugging`, `root-cause-tracing` |
| Quality | `verification-before-completion`, `testing-anti-patterns`, `defense-in-depth` |
| Collaboration | `receiving-code-review` |
| Workflow | `finishing-a-development-branch`, `condition-based-waiting` |
| Session | `getting-started`, `pragmatic-architecture` |
