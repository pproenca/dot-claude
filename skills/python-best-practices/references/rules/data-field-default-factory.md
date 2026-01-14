---
title: Use Field Default Factory
impact: MEDIUM
impactDescription: Prevents shared mutable defaults
tags: data, dataclass, field, default-factory
---

## Use Field Default Factory

Use `field(default_factory=...)` for mutable default values.

**Incorrect (mutable default value):**

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    tags: list[str] = []  # DANGER: Shared between all instances!
```

**Correct (using default_factory):**

```python
from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    # With initial values
    roles: list[str] = field(default_factory=lambda: ["user"])
```

Reference: [dataclasses.field](https://docs.python.org/3/library/dataclasses.html#dataclasses.field)
