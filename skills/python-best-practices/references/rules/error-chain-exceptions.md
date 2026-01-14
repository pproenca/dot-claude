---
title: Chain Exceptions Properly
impact: MEDIUM
impactDescription: Preserves exception context
tags: error, exception-chaining, raise-from, debugging
---

## Chain Exceptions Properly

Always use `raise ... from` to properly chain exceptions and preserve context.

**Incorrect (losing exception context):**

```python
def process_config(path: str) -> dict:
    try:
        with open(path) as f:
            return parse_config(f.read())
    except FileNotFoundError:
        raise ConfigError("Config file not found")  # Loses traceback
```

**Correct (properly chaining exceptions):**

```python
def process_config(path: str) -> dict:
    try:
        with open(path) as f:
            return parse_config(f.read())
    except FileNotFoundError as e:
        raise ConfigError(f"Config not found: {path}") from e
    except ParseError as e:
        raise ConfigError("Invalid config format") from e
    except Exception as e:
        # Use 'from None' to explicitly suppress chain
        raise ConfigError("Unexpected error") from None
```

Reference: [Exception Chaining](https://docs.python.org/3/tutorial/errors.html#exception-chaining)
