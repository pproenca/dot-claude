---
title: Use Frozen Dataclass for Immutability
impact: MEDIUM
impactDescription: Hashable, immutable objects
tags: data, dataclass, frozen, immutable
---

## Use Frozen Dataclass for Immutability

Use `@dataclass(frozen=True)` for immutable data objects.

**Incorrect (mutable dataclass):**

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

p = Point(1, 2)
p.x = 3  # Mutation allowed
# hash(p)  # TypeError: unhashable
```

**Correct (frozen dataclass):**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float

p = Point(1, 2)
# p.x = 3  # FrozenInstanceError
hash(p)  # Works! Can use as dict key

# Combine with slots for efficiency
@dataclass(frozen=True, slots=True)
class ImmutablePoint:
    x: float
    y: float
```

Reference: [dataclasses](https://docs.python.org/3/library/dataclasses.html)
