---
title: Cache Expensive Computations
impact: HIGH
impactDescription: O(1) for repeated calls
tags: perf, cache, memoization, functools
---

## Cache Expensive Computations

Use `functools.cache` or `functools.lru_cache` for memoizing expensive function calls.

**Incorrect (recomputing expensive results):**

```python
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)  # Exponential time!

def fetch_user_data(user_id: int) -> dict:
    # Called multiple times with same ID
    return database.query(f"SELECT * FROM users WHERE id = {user_id}")
```

**Correct (using functools.cache):**

```python
from functools import cache, lru_cache

@cache  # Unlimited cache
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)  # O(n) now

@lru_cache(maxsize=128)  # Bounded cache
def fetch_user_data(user_id: int) -> dict:
    return database.query(f"SELECT * FROM users WHERE id = {user_id}")

# Clear cache when needed
fetch_user_data.cache_clear()
```

Reference: [functools.cache](https://docs.python.org/3/library/functools.html#functools.cache)
