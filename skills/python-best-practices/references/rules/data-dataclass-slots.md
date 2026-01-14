---
title: Use Dataclass with Slots
impact: MEDIUM
impactDescription: 30-50% memory reduction + zero-boilerplate class definition
tags: data, dataclass, slots, memory, python310, pydantic, sqlalchemy
---

## Use Dataclass with Slots

`@dataclass(slots=True)` combines the memory benefits of `__slots__` (30-50% reduction) with the zero-boilerplate of dataclasses. A single decorator replaces 15+ lines of `__init__`, `__repr__`, `__eq__`, and `__slots__` definitions.

**Incorrect (dataclass without slots):**

```python
# PROBLEM: Each instance has ~150 bytes __dict__ overhead
from dataclasses import dataclass

@dataclass
class Point:
    """3D point - 180 bytes per instance."""
    x: float
    y: float
    z: float

@dataclass
class TradeEvent:
    """Trade event - ~350 bytes per instance due to __dict__."""
    timestamp: float
    symbol: str
    price: float
    quantity: int
    side: str
    order_id: str
    exchange: str
    account_id: str

# Processing 1M trade events = 350MB just for __dict__ overhead
events = [TradeEvent(0.0, "AAPL", 150.0, 100, "buy", "123", "NYSE", "acc1")
          for _ in range(1_000_000)]
```

**Correct (dataclass with slots):**

```python
# SOLUTION: 30-50% memory reduction, same zero-boilerplate benefits
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    """3D point - ~56 bytes per instance (69% smaller)."""
    x: float
    y: float
    z: float

@dataclass(slots=True)
class TradeEvent:
    """Trade event - ~160 bytes per instance (54% smaller)."""
    timestamp: float
    symbol: str
    price: float
    quantity: int
    side: str
    order_id: str
    exchange: str
    account_id: str

# Processing 1M trade events = 160MB (190MB saved!)
events = [TradeEvent(0.0, "AAPL", 150.0, 100, "buy", "123", "NYSE", "acc1")
          for _ in range(1_000_000)]

# Combine with frozen for immutable + hashable
@dataclass(slots=True, frozen=True)
class CacheKey:
    """Immutable cache key - can be used in sets and as dict keys."""
    user_id: int
    resource_type: str
    resource_id: int

# Use as dict key
cache: dict[CacheKey, bytes] = {}
key = CacheKey(123, "image", 456)
cache[key] = b"..."
```

**Alternative (manual slots for Python 3.9):**

```python
# For Python 3.9, define __slots__ manually in dataclass
from dataclasses import dataclass

@dataclass
class Point:
    __slots__ = ("x", "y", "z")
    x: float
    y: float
    z: float
```

**When to use:** For all dataclasses where you create many instances (data records, DTOs, events). Especially valuable in data pipelines, event processing, and scientific computing.

**When NOT to use:** When you need dynamic attributes on instances, when inheriting from non-slotted classes, or when you need `__weakref__` support. Also avoid if the dataclass represents a one-off configuration object.

Reference: [dataclasses](https://docs.python.org/3/library/dataclasses.html)
