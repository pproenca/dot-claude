---
title: Use None Instead of Optional
impact: CRITICAL
impactDescription: Simpler syntax, no imports
tags: typing, optional, none, type-hints
---

## Use None Instead of Optional

Replace `Optional[X]` with `X | None`. The `Optional` type from typing is now considered legacy syntax and the pipe syntax is preferred.

**Incorrect (using Optional):**

```python
from typing import Optional

def find_user(user_id: int) -> Optional[dict]:
    """Find a user by ID."""
    users = {"1": {"name": "Alice"}}
    return users.get(str(user_id))

def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get configuration value."""
    config = {"debug": "true"}
    return config.get(key, default)
```

**Correct (using X | None):**

```python
def find_user(user_id: int) -> dict | None:
    """Find a user by ID."""
    users = {"1": {"name": "Alice"}}
    return users.get(str(user_id))

def get_config(key: str, default: str | None = None) -> str | None:
    """Get configuration value."""
    config = {"debug": "true"}
    return config.get(key, default)
```

Reference: [Typing Best Practices](https://typing.python.org/en/latest/reference/best_practices.html)
