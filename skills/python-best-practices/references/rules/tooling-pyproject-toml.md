---
title: Use pyproject.toml as Single Source
impact: LOW
impactDescription: Consolidated configuration
tags: tooling, pyproject, configuration, packaging
---

## Use pyproject.toml as Single Source

Consolidate all tool configuration in `pyproject.toml`.

**Incorrect (multiple configuration files):**

```
myproject/
├── setup.py
├── setup.cfg
├── mypy.ini
├── .isort.cfg
├── .flake8
├── pytest.ini
└── requirements.txt
```

**Correct (single pyproject.toml):**

```toml
[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.25.0",
    "pydantic>=2.0.0",
]

[dependency-groups]
dev = [
    "mypy>=1.8.0",
    "ruff>=0.2.0",
    "pytest>=8.0.0",
]

[tool.ruff]
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Reference: [pyproject.toml specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
