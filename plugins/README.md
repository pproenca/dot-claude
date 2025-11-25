# Claude Code Plugin Marketplace

A curated collection of plugins for Claude Code, organized by capability domain.

## Namespaces

| Namespace | Purpose | Plugins |
|-----------|---------|---------|
| `dev/` | Development workflows | 3 |
| `sdk/` | Claude Code extensions | 5 |
| `docs/` | Documentation generation | 1 |
| `pm/` | Project management | 1 |

## Available Plugins

### dev/ — Development Workflows

Plugins for day-to-day coding tasks.

| Plugin | Description |
|--------|-------------|
| [commit-organizer](dev/commit-organizer/) | Organize messy commits into clean, logical commits following Google and Anthropic best practices |
| [feature-dev](dev/feature-dev/) | Feature development workflow with specialized agents for exploration, architecture, and review |
| [superpowers](dev/superpowers/) | Advanced methodologies: debugging, testing, planning, code review, agent-driven development |

### sdk/ — Claude Code Extensions

Build your own Claude Code plugins and tools.

| Plugin | Description |
|--------|-------------|
| [plugin-dev](sdk/plugin-dev/) | Comprehensive guidance for plugin development: commands, agents, hooks, MCP, skills |
| [agent-sdk-dev](sdk/agent-sdk-dev/) | Claude Agent SDK development support |
| [skill-creator](sdk/skill-creator/) | Create effective Claude Code skills with progressive disclosure |
| [mcp-builder](sdk/mcp-builder/) | Build MCP servers in TypeScript or Python |
| [hookify](sdk/hookify/) | Create hooks to prevent unwanted behaviors |

### docs/ — Documentation

Generate and maintain technical documentation.

| Plugin | Description |
|--------|-------------|
| [doc-generator](docs/doc-generator/) | Generate API docs, architecture diagrams, tutorials, and references |

### pm/ — Project Management

Personal and team productivity.

| Plugin | Description |
|--------|-------------|
| [priority-manager](pm/priority-manager/) | Git-based priority management with daily/weekly rituals |

## Installation

### Install entire marketplace

```bash
claude --add-plugin /path/to/plugins
```

### Install single plugin

```bash
claude --add-plugin /path/to/plugins/dev/superpowers
```

### Install by namespace

```bash
claude --add-plugin /path/to/plugins/dev
```

## Structure

```
plugins/
├── dev/                    # Development workflows
│   ├── commit-organizer/
│   ├── feature-dev/
│   └── superpowers/
├── sdk/                    # Claude Code SDK & extensions
│   ├── plugin-dev/
│   ├── agent-sdk-dev/
│   ├── skill-creator/
│   ├── mcp-builder/
│   └── hookify/
├── docs/                   # Documentation generation
│   └── doc-generator/
├── pm/                     # Project management
│   └── priority-manager/
└── comms/                  # Communications
    └── internal-comms/
```

## Contributing

Each plugin follows Claude Code's standard structure:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json         # Required manifest
├── commands/               # Slash commands
├── agents/                 # Subagent definitions
├── skills/                 # Auto-activating skills
│   └── skill-name/
│       └── SKILL.md
└── hooks/                  # Event handlers
    └── hooks.json
```

See [sdk/plugin-dev](sdk/plugin-dev/) for comprehensive plugin development guidance.
