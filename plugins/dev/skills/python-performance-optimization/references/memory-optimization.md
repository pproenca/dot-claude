# Memory Optimization

## Table of Contents
- [Pattern 13: Using __slots__ for Memory](#pattern-13-using-__slots__-for-memory)
- [Pattern 18: Detecting Memory Leaks](#pattern-18-detecting-memory-leaks)
- [Pattern 19: Iterators vs Lists](#pattern-19-iterators-vs-lists)
- [Pattern 20: Weakref for Caches](#pattern-20-weakref-for-caches)

## Pattern 13: Using __slots__ for Memory

```python
import sys

class RegularClass:
    """Each instance has __dict__ (56+ bytes overhead)."""
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class SlottedClass:
    """No __dict__, attributes stored in fixed-size array."""
    __slots__ = ['x', 'y', 'z']

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

regular = RegularClass(1, 2, 3)
slotted = SlottedClass(1, 2, 3)

print(f"Regular class size: {sys.getsizeof(regular)} bytes")
print(f"Slotted class size: {sys.getsizeof(slotted)} bytes")

regular_objects = [RegularClass(i, i+1, i+2) for i in range(10000)]
slotted_objects = [SlottedClass(i, i+1, i+2) for i in range(10000)]

print(f"\nMemory for 10000 regular objects: ~{sys.getsizeof(regular) * 10000} bytes")
print(f"Memory for 10000 slotted objects: ~{sys.getsizeof(slotted) * 10000} bytes")
```

## Pattern 18: Detecting Memory Leaks

```python
import tracemalloc
import gc

def memory_leak_example():
    leaked_objects = []
    for i in range(100000):
        leaked_objects.append([i] * 100)

def track_memory_usage():
    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()
    memory_leak_example()
    snapshot2 = tracemalloc.take_snapshot()
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')

    print("Top 10 memory allocations:")
    for stat in top_stats[:10]:
        print(stat)

    tracemalloc.stop()

track_memory_usage()
gc.collect()
```

## Pattern 19: Iterators vs Lists

```python
import sys

def process_file_list(filename):
    """O(n) memory - entire file in RAM."""
    with open(filename) as f:
        lines = f.readlines()
        return sum(1 for line in lines if line.strip())

def process_file_iterator(filename):
    """O(1) memory - one line at a time."""
    with open(filename) as f:
        return sum(1 for line in f if line.strip())
```

## Pattern 20: Weakref for Caches

```python
import weakref

class CachedResource:
    def __init__(self, data):
        self.data = data

# Strong reference prevents GC
regular_cache = {}

def get_resource_regular(key):
    if key not in regular_cache:
        regular_cache[key] = CachedResource(f"Data for {key}")
    return regular_cache[key]

# Weak reference allows GC when no other refs exist
weak_cache = weakref.WeakValueDictionary()

def get_resource_weak(key):
    resource = weak_cache.get(key)
    if resource is None:
        resource = CachedResource(f"Data for {key}")
        weak_cache[key] = resource
    return resource
```
