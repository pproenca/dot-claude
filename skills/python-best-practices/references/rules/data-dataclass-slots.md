---
title: Use Dataclass with Slots
impact: MEDIUM
impactDescription: 30-50% memory reduction
tags: data, dataclass, slots, memory, python310
---

## Use Dataclass with Slots

Use `@dataclass(slots=True)` for memory-efficient dataclasses (Python 3.10+).

**Incorrect (dataclass without slots):**

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    z: float

# Each instance has __dict__ overhead
```

**Correct (dataclass with slots):**

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    x: float
    y: float
    z: float

# ~30-50% memory reduction per instance
```

Reference: [dataclasses](https://docs.python.org/3/library/dataclasses.html)
