---
title: Use Union Pipe Syntax
impact: CRITICAL
impactDescription: Cleaner code, no imports needed
tags: typing, union, type-hints, python310
---

## Use Union Pipe Syntax

Use the `|` operator for union types instead of importing `Union` from the typing module. This syntax is cleaner, requires no imports, and is the recommended approach for Python 3.10+.

**Incorrect (importing Union from typing):**

```python
from typing import Union

def process_value(value: Union[int, str, float]) -> Union[str, None]:
    """Process a numeric or string value."""
    if isinstance(value, (int, float)):
        return str(value * 2)
    return value.upper()
```

**Correct (using pipe operator):**

```python
def process_value(value: int | str | float) -> str | None:
    """Process a numeric or string value."""
    if isinstance(value, (int, float)):
        return str(value * 2)
    return value.upper()
```

Note: None should always be the last element in a union.

Reference: [Typing Best Practices](https://typing.python.org/en/latest/reference/best_practices.html)
