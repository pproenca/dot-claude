---
title: Use Union Pipe Syntax
impact: CRITICAL
impactDescription: Eliminates 1 import + 30% shorter annotations per file
tags: typing, union, type-hints, python310, pydantic
---

## Use Union Pipe Syntax

The pipe syntax for union types eliminates the `from typing import Union` import and makes type annotations 30% shorter on average. In a typical 500-line module with 20+ type annotations, this saves 1 import statement and ~100 characters of boilerplate.

**Incorrect (importing Union from typing):**

```python
# PROBLEM: Requires import, verbose syntax, ~45 chars per annotation
from typing import Union

from pydantic import BaseModel

class UserResponse(BaseModel):
    """API response model for user data."""
    user_id: Union[int, str]  # Supports both numeric and string IDs
    name: Union[str, None]
    email: Union[str, None]
    metadata: Union[dict[str, str], None]

def process_value(value: Union[int, str, float]) -> Union[str, None]:
    """Process a numeric or string value."""
    if isinstance(value, (int, float)):
        return str(value * 2)
    return value.upper()

def fetch_user(user_id: Union[int, str]) -> Union[dict, None]:
    """Fetch user by ID from database."""
    # Union[X, None] is verbose compared to X | None
    return db.query(user_id)
```

**Correct (using pipe operator):**

```python
# SOLUTION: No import needed, ~30 chars per annotation (30% shorter)
from pydantic import BaseModel

class UserResponse(BaseModel):
    """API response model for user data."""
    user_id: int | str  # Supports both numeric and string IDs
    name: str | None
    email: str | None
    metadata: dict[str, str] | None

def process_value(value: int | str | float) -> str | None:
    """Process a numeric or string value."""
    if isinstance(value, (int, float)):
        return str(value * 2)
    return value.upper()

def fetch_user(user_id: int | str) -> dict | None:
    """Fetch user by ID from database."""
    # Cleaner, more readable
    return db.query(user_id)
```

**Alternative (using TypeAlias for complex unions):**

```python
# When you reuse the same union type multiple times
type JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]

def parse_json(data: bytes) -> JsonValue:
    """Parse JSON data into Python objects."""
    import json
    return json.loads(data)
```

**When to use:** Always prefer pipe syntax for Python 3.10+ codebases. Use it in function signatures, variable annotations, and Pydantic/dataclass field types.

**When NOT to use:** When maintaining compatibility with Python 3.9 or earlier, you must use `Union` from typing. Consider using `from __future__ import annotations` as a bridge.

Reference: [Typing Best Practices](https://typing.python.org/en/latest/reference/best_practices.html)
