# dot-claude

Personal Claude Code plugins marketplace.

## Plugins

| Plugin | Description |
|--------|-------------|
| [dev-python](domain_plugins/dev-python) | Modern Python 3.12+ development with uv, ruff, pydantic, FastAPI, Django |
| [dev-workflow](plugins/dev-workflow) | Development workflow with TDD, debugging, and collaboration skills |
| [shell](domain_plugins/shell) | Shell scripting with Google Style Guide expertise |

## Installation

Add this marketplace to Claude Code:

```bash
claude plugins add-marketplace pproenca/dot-claude
```

Then install individual plugins:

```bash
# Install Python plugin
claude plugins install pproenca/dev-python

# Install dev-workflow plugin
claude plugins install pproenca/dev-workflow
```

## Plugin Details

### dev-python

Modern Python development plugin with:
- uv package manager integration
- ruff linting and formatting
- pydantic, FastAPI, Django patterns
- Production-ready practices

### dev-workflow

Development methodology plugin with:
- Test-driven development (TDD) skills
- Systematic debugging
- Code review workflows
- Planning and brainstorming commands

## License

MIT
