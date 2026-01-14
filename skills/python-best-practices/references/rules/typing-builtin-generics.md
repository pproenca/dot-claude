---
title: Use Built-in Generics
impact: CRITICAL
impactDescription: Reduces imports, cleaner code
tags: typing, generics, list, dict, set, tuple
---

## Use Built-in Generics

Use built-in collection types directly as generics instead of importing from `typing`.

**Incorrect (importing from typing):**

```python
from typing import List, Dict, Set, Tuple

def process_items(items: List[str]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for item in items:
        result[item] = result.get(item, 0) + 1
    return result
```

**Correct (using built-in generics):**

```python
def process_items(items: list[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in items:
        result[item] = result.get(item, 0) + 1
    return result
```

For abstract types, import from `collections.abc`.

Reference: [Typing Best Practices](https://typing.python.org/en/latest/reference/best_practices.html)
