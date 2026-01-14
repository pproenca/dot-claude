---
title: Use Slots for Memory-Efficient Classes
impact: HIGH
impactDescription: 73% memory reduction (150 bytes to 40 bytes per instance)
tags: perf, slots, memory, optimization, pandas, numpy
---

## Use Slots for Memory-Efficient Classes

`__slots__` reduces instance memory by 73% (from ~150 bytes to ~40 bytes) by eliminating the per-instance `__dict__`. For 1 million objects, this saves 110MB of RAM. Use slots for data-heavy classes in ETL pipelines, scientific computing, and any application creating many instances.

**Incorrect (class without slots):**

```python
# PROBLEM: Each instance has ~150 bytes overhead from __dict__
import sys

class Point:
    """2D point without slots."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class TradeRecord:
    """Financial trade record - 8 fields, ~280 bytes per instance."""
    def __init__(self, symbol: str, price: float, quantity: int,
                 timestamp: float, side: str, order_id: str,
                 account: str, exchange: str):
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp
        self.side = side
        self.order_id = order_id
        self.account = account
        self.exchange = exchange

# 1 million points = ~150MB of RAM (just for __dict__ overhead!)
points = [Point(i, i) for i in range(1_000_000)]
print(f"Memory: {sys.getsizeof(points[0].__dict__)} bytes per __dict__")
```

**Correct (using __slots__):**

```python
# SOLUTION: 73% memory reduction, ~40 bytes per instance
import sys

class Point:
    """2D point with slots - memory efficient."""
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class TradeRecord:
    """Trade record with slots - ~100 bytes per instance (64% reduction)."""
    __slots__ = ("symbol", "price", "quantity", "timestamp",
                 "side", "order_id", "account", "exchange")

    def __init__(self, symbol: str, price: float, quantity: int,
                 timestamp: float, side: str, order_id: str,
                 account: str, exchange: str):
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp
        self.side = side
        self.order_id = order_id
        self.account = account
        self.exchange = exchange

# 1 million points = ~40MB of RAM (110MB saved!)
points = [Point(i, i) for i in range(1_000_000)]
# points[0].z = 3  # AttributeError: 'Point' object has no attribute 'z'
```

**Alternative (slots with inheritance):**

```python
# When inheriting, child must also define __slots__
class Point2D:
    __slots__ = ("x", "y")
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class Point3D(Point2D):
    __slots__ = ("z",)  # Only new attributes, not inherited ones
    def __init__(self, x: float, y: float, z: float):
        super().__init__(x, y)
        self.z = z
```

**When to use:** For classes where you create many instances (1000+): data records, points/vectors, tree nodes, graph edges, ORM-like objects. Essential in data pipelines, scientific computing, and games.

**When NOT to use:** For classes that need dynamic attributes (`setattr`), use `__weakref__`, or are subclassed frequently. Also avoid for small numbers of instances where memory savings are negligible.

Reference: [__slots__ documentation](https://docs.python.org/3/reference/datamodel.html#slots)
