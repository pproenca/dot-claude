# Advanced Optimization Patterns

## NumPy for Numerical Work

```python
import numpy as np

# Python loop: O(n) with Python overhead per element
def python_sum(data: list[float]) -> float:
    return sum(x**2 for x in data)

# NumPy: C loop, vectorized operations
def numpy_sum(data: np.ndarray) -> float:
    return np.sum(data**2)

# NumPy is 10-100x faster for numerical operations
```

## Database Query Optimization

```python
# BAD: N+1 queries
users = session.query(User).all()
for user in users:
    print(user.orders)  # Query per user!

# GOOD: Eager loading
users = session.query(User).options(joinedload(User.orders)).all()
for user in users:
    print(user.orders)  # Already loaded

# GOOD: Batch operations
session.execute(
    User.__table__.update().where(User.active == True).values(verified=True)
)
```

## Memory Optimization with __slots__

```python
class WithSlots:
    __slots__ = ('x', 'y', 'z')

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

# Uses ~50% less memory than regular class with __dict__
```

## Weak References for Caches

```python
import weakref

class Cache:
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()

    def get(self, key):
        return self._cache.get(key)

    def set(self, key, value):
        self._cache[key] = value
        # Values can be garbage collected when no other references exist
```

## Memory-Mapped Files

```python
import mmap

with open("large_file.bin", "r+b") as f:
    # Map file into memory - OS handles paging
    mm = mmap.mmap(f.fileno(), 0)
    data = mm[1000:2000]  # Only load what you need
    mm.close()
```

## Struct for Binary Data

```python
import struct

# Pack data efficiently
packed = struct.pack('3i2f', 1, 2, 3, 4.0, 5.0)  # 20 bytes

# Unpack
values = struct.unpack('3i2f', packed)  # (1, 2, 3, 4.0, 5.0)
```

## Batch Processing

```python
def process_in_batches(items: list, batch_size: int = 1000):
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        yield process_batch(batch)

# Better for memory and can show progress
for result in process_in_batches(large_list):
    save(result)
```

## Lazy Evaluation

```python
class LazyProperty:
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = self.func(obj)
        setattr(obj, self.func.__name__, value)
        return value

class ExpensiveObject:
    @LazyProperty
    def computed_value(self):
        return expensive_computation()  # Only called once, on first access
```

## Avoiding Copies

```python
import numpy as np

# Creates copy
subset = array[1:10].copy()

# View (no copy, shares memory)
view = array[1:10]

# Check if view or copy
print(view.base is array)  # True if view
```

## Inlining Hot Paths

```python
# Before: function call overhead in tight loop
def helper(x):
    return x * 2 + 1

for i in range(1_000_000):
    result = helper(i)

# After: inlined
for i in range(1_000_000):
    result = i * 2 + 1  # ~30% faster
```

## Preallocating Lists

```python
# Slow: list grows dynamically
result = []
for i in range(10000):
    result.append(compute(i))

# Faster: preallocate if size is known
result = [None] * 10000
for i in range(10000):
    result[i] = compute(i)

# Best: comprehension
result = [compute(i) for i in range(10000)]
```

## Using __contains__ Effectively

```python
# Define custom __contains__ for faster membership testing
class Range:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def __contains__(self, x):
        return self.start <= x < self.stop  # O(1)

# 5 in Range(0, 10) is O(1), not O(n)
```
