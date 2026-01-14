---
title: Use Local Variable Caching
impact: HIGH
impactDescription: Faster attribute access in loops
tags: perf, local-variables, optimization, loops
---

## Use Local Variable Caching

Cache attribute lookups and method calls in local variables within tight loops.

**Incorrect (repeated attribute lookups):**

```python
import math

def calculate_distances(points: list[tuple[float, float]]) -> list[float]:
    distances = []
    for x, y in points:
        # math.sqrt looked up on every iteration
        distances.append(math.sqrt(x ** 2 + y ** 2))
    return distances

class Processor:
    def process_all(self, items: list[str]) -> list[str]:
        results = []
        for item in items:
            # self.transform looked up on every iteration
            results.append(self.transform(item))
        return results
```

**Correct (caching lookups in local variables):**

```python
import math

def calculate_distances(points: list[tuple[float, float]]) -> list[float]:
    sqrt = math.sqrt  # Cache the function lookup
    distances = []
    for x, y in points:
        distances.append(sqrt(x ** 2 + y ** 2))
    return distances

class Processor:
    def process_all(self, items: list[str]) -> list[str]:
        transform = self.transform  # Cache method lookup
        return [transform(item) for item in items]
```

This optimization is most impactful in tight loops processing millions of items.

Reference: [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
