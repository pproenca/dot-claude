# dot-claude

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A collection of Claude Code plugins for structured development workflows, Python best practices, and shell scripting.

> **Note:** This is a personal project and is not affiliated with or endorsed by Anthropic. Use at your own discretion.

## Plugins

| Plugin | Description |
|--------|-------------|
| [dev-workflow](plugins/dev-workflow) | TDD, systematic debugging, and code review workflows |
| [dev-python](domain_plugins/dev-python) | Python 3.12+ with uv, ruff, pydantic, FastAPI, Django |
| [shell](domain_plugins/shell) | Shell scripting with Google Style Guide patterns |

## Requirements

- [Claude Code](https://github.com/anthropics/claude-code) CLI

## Installation

### Via Plugin Marketplace (Recommended)

Add the marketplace and install plugins from within Claude Code:

```
/plugin marketplace add pproenca/dot-claude
```

Then install individual plugins:

```
/plugin install dev-workflow@pproenca
/plugin install dev-python@pproenca
/plugin install shell@pproenca
```

### Manual Installation

Clone the repository and symlink the desired plugins:

```bash
git clone https://github.com/pproenca/dot-claude.git ~/.dot-claude

# Install dev-workflow
ln -s ~/.dot-claude/plugins/dev-workflow ~/.claude/plugins/dev-workflow

# Install dev-python
ln -s ~/.dot-claude/domain_plugins/dev-python ~/.claude/plugins/dev-python

# Install shell
ln -s ~/.dot-claude/domain_plugins/shell ~/.claude/plugins/shell
```

## Plugin Details

### [dev-workflow](plugins/dev-workflow)

Development methodology plugin enforcing discipline through architecture:

- **Skills**: TDD, systematic debugging, verification, code review
- **Commands**: `/brainstorm`, `/write-plan`, `/execute-plan`, `/resume`
- **Agents**: code-explorer, code-architect, code-reviewer

### [dev-python](domain_plugins/dev-python)

Modern Python development plugin:

- uv package manager integration
- ruff linting and formatting
- pydantic, FastAPI, Django patterns
- Python 3.12+ idioms

### [shell](domain_plugins/shell)

Shell scripting plugin:

- Google Shell Style Guide compliance
- Bash best practices
- Script structure patterns

## Contributing

Contributions are welcome. Please open an issue to discuss changes before submitting a pull request.

## Acknowledgments

Inspired by [anthropics/skills](https://github.com/anthropics/skills).

## License

[MIT](LICENSE)
