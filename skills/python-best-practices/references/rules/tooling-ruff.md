---
title: Configure Ruff for Linting
impact: LOW
impactDescription: Fast, comprehensive linting
tags: tooling, ruff, linting, formatting
---

## Configure Ruff for Linting

Use Ruff as an all-in-one linter and formatter.

**Correct (comprehensive ruff configuration):**

```toml
[tool.ruff]
target-version = "py311"
line-length = 88
exclude = [".venv", "build", "dist"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "F",      # Pyflakes
    "I",      # isort
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "SIM",    # flake8-simplify
    "RUF",    # Ruff-specific
]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]  # Allow assert in tests

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

Run with: `ruff check .` and `ruff format .`

Reference: [Ruff documentation](https://docs.astral.sh/ruff/)
