---
title: Use Slots for Memory-Efficient Classes
impact: HIGH
impactDescription: 30-50% memory reduction per instance
tags: perf, slots, memory, optimization
---

## Use Slots for Memory-Efficient Classes

Use `__slots__` to prevent creation of `__dict__` for instances, reducing memory significantly.

**Incorrect (class without slots):**

```python
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

# Each instance has ~100-200 bytes __dict__ overhead
points = [Point(i, i) for i in range(1_000_000)]
```

**Correct (using __slots__):**

```python
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

# Each instance is ~40 bytes instead of ~150 bytes
points = [Point(i, i) for i in range(1_000_000)]
```

Note: Slots prevent adding dynamic attributes at runtime.

Reference: [__slots__ documentation](https://docs.python.org/3/reference/datamodel.html#slots)
