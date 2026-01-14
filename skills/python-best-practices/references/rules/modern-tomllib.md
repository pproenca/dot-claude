---
title: Use tomllib for TOML Parsing
impact: MEDIUM-HIGH
impactDescription: No external dependencies needed
tags: modern, tomllib, toml, config, python311
---

## Use tomllib for TOML Parsing

Use the built-in `tomllib` module (Python 3.11+) for parsing TOML files.

**Incorrect (using third-party library):**

```python
# Requires: pip install toml
import toml

def load_config(path: str) -> dict:
    with open(path) as f:
        return toml.load(f)
```

**Correct (using built-in tomllib):**

```python
import tomllib

def load_config(path: str) -> dict:
    with open(path, "rb") as f:  # Binary mode required
        return tomllib.load(f)

# For parsing TOML strings
def parse_toml_string(content: str) -> dict:
    return tomllib.loads(content)
```

Note: `tomllib` only supports reading TOML. Use `tomli-w` for writing.

Reference: [tomllib documentation](https://docs.python.org/3/library/tomllib.html)
