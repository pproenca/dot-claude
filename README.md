# dot-claude

Personal Claude Code plugins marketplace.

## Plugins

| Plugin | Description | Version |
|--------|-------------|---------|
| [python](plugins/python) | Modern Python 3.12+ development with uv, ruff, pydantic, FastAPI, Django | 1.0.0 |
| [dev-workflow](plugins/dev-workflow) | Development workflow with TDD, debugging, and collaboration skills | 2.4.2 |

## Installation

Add this marketplace to Claude Code:

```bash
claude plugins add-marketplace pproenca/dot-claude
```

Then install individual plugins:

```bash
# Install Python plugin
claude plugins install pproenca/python

# Install dev-workflow plugin
claude plugins install pproenca/dev-workflow
```

## Plugin Details

### python

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
