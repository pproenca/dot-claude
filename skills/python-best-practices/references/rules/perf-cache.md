---
title: Cache Expensive Computations
impact: HIGH
impactDescription: O(2^n) to O(n) for recursive functions, 1000x speedup for repeated API calls
tags: perf, cache, memoization, functools, lru-cache, redis
---

## Cache Expensive Computations

`functools.cache` transforms exponential O(2^n) algorithms into linear O(n) and eliminates redundant API/database calls. `fibonacci(35)` takes 4 seconds without caching vs 0.00001 seconds with caching - a 400,000x speedup.

**Incorrect (recomputing expensive results):**

```python
# PROBLEM: O(2^n) complexity, fibonacci(35) takes ~4 seconds
import time

def fibonacci(n: int) -> int:
    """Exponential time - each call spawns 2 more calls."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# fibonacci(35) makes 29,860,703 function calls!
start = time.time()
result = fibonacci(35)  # Takes ~4 seconds
print(f"Time: {time.time() - start:.2f}s")

class UserService:
    """Service that repeatedly queries same users."""
    def get_user_orders(self, user_id: int) -> list:
        # Called 10 times per request with same user_id
        user = self._fetch_user(user_id)  # 50ms database query
        return self._fetch_orders(user_id)  # 100ms database query

    def _fetch_user(self, user_id: int) -> dict:
        return database.query("SELECT * FROM users WHERE id = ?", user_id)

    def _fetch_orders(self, user_id: int) -> list:
        return database.query("SELECT * FROM orders WHERE user_id = ?", user_id)
```

**Correct (using functools.cache):**

```python
# SOLUTION: O(n) complexity, fibonacci(35) takes 0.00001 seconds
from functools import cache, lru_cache
import time

@cache  # Unlimited cache - use for pure functions
def fibonacci(n: int) -> int:
    """Linear time with memoization."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# fibonacci(35) makes only 36 function calls!
start = time.time()
result = fibonacci(35)  # Takes 0.00001 seconds (400,000x faster)
print(f"Time: {time.time() - start:.6f}s")

class UserService:
    """Service with cached database queries."""

    @lru_cache(maxsize=256)  # Bounded cache - evicts least-recently-used
    def _fetch_user(self, user_id: int) -> dict:
        return database.query("SELECT * FROM users WHERE id = ?", user_id)

    @lru_cache(maxsize=256)
    def _fetch_orders(self, user_id: int) -> list:
        return database.query("SELECT * FROM orders WHERE user_id = ?", user_id)

    def get_user_orders(self, user_id: int) -> list:
        # Subsequent calls with same user_id return instantly
        user = self._fetch_user(user_id)  # First call: 50ms, subsequent: 0ms
        return self._fetch_orders(user_id)

    def invalidate_user(self, user_id: int) -> None:
        """Clear cache when user data changes."""
        self._fetch_user.cache_clear()
        self._fetch_orders.cache_clear()
```

**Alternative (TTL cache with cachetools):**

```python
# When you need time-based expiration
from cachetools import TTLCache
from cachetools.func import ttl_cache

# TTL cache that expires entries after 5 minutes
@ttl_cache(maxsize=100, ttl=300)
def fetch_exchange_rate(currency: str) -> float:
    """Fetch exchange rate - cache for 5 minutes."""
    return api.get_rate(currency)

# Manual TTL cache for more control
rate_cache: TTLCache[str, float] = TTLCache(maxsize=100, ttl=300)

def get_rate(currency: str) -> float:
    if currency in rate_cache:
        return rate_cache[currency]
    rate = api.get_rate(currency)
    rate_cache[currency] = rate
    return rate
```

**When to use:** For any pure function called repeatedly with same arguments: recursive algorithms, API calls, database queries, expensive computations. Use `@cache` for unlimited caching, `@lru_cache` for bounded memory.

**When NOT to use:** For functions with side effects, mutable arguments (use tuples instead of lists), or time-sensitive data (use TTL cache instead). Cache invalidation is hard - prefer short TTLs for frequently changing data.

Reference: [functools.cache](https://docs.python.org/3/library/functools.html#functools.cache)
