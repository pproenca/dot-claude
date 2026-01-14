---
title: Use asyncio.timeout Context Manager
impact: CRITICAL
impactDescription: Enables deadline rescheduling, scoped timeouts for multiple operations
tags: async, timeout, context-manager, python311, httpx, deadline
---

## Use asyncio.timeout Context Manager

The `asyncio.timeout()` context manager provides scoped timeouts that can cover multiple operations and supports deadline rescheduling - features impossible with `wait_for()`. It also catches the standard `TimeoutError` instead of `asyncio.TimeoutError`.

**Incorrect (using wait_for):**

```python
# PROBLEM: Can't reschedule, can't scope multiple operations, wrong exception class
import asyncio
import httpx

async def fetch_with_timeout():
    """Single operation timeout - no flexibility."""
    try:
        result = await asyncio.wait_for(fetch_data(), timeout=5.0)
        return result
    except asyncio.TimeoutError:  # Different from built-in TimeoutError
        return None

async def fetch_multiple_with_timeout():
    """Multiple operations - must wrap each individually."""
    try:
        users = await asyncio.wait_for(fetch_users(), timeout=3.0)
        orders = await asyncio.wait_for(fetch_orders(), timeout=3.0)
        # Total time could be 6 seconds, not 3!
        return users, orders
    except asyncio.TimeoutError:
        return None, None

async def fetch_with_retry():
    """Can't extend timeout on retry."""
    for attempt in range(3):
        try:
            return await asyncio.wait_for(fetch_data(), timeout=5.0)
        except asyncio.TimeoutError:
            pass  # No way to extend deadline for next attempt
    return None
```

**Correct (using timeout context manager):**

```python
# SOLUTION: Scoped timeouts, reschedule support, standard TimeoutError
import asyncio
import httpx

async def fetch_with_timeout():
    """Single operation with standard exception handling."""
    try:
        async with asyncio.timeout(5.0):
            return await fetch_data()
    except TimeoutError:  # Standard built-in exception
        return None

async def fetch_multiple_with_timeout():
    """Multiple operations share a single 3-second deadline."""
    try:
        async with asyncio.timeout(3.0):
            # Total time for both calls must be under 3 seconds
            users = await fetch_users()
            orders = await fetch_orders()
            return users, orders
    except TimeoutError:
        return None, None

async def fetch_with_adaptive_timeout():
    """Reschedule deadline based on server response."""
    try:
        async with asyncio.timeout(5.0) as timeout_ctx:
            response = await initial_request()

            # Server says "try again in 2 seconds" - extend deadline
            if response.status_code == 429:
                retry_after = float(response.headers.get("Retry-After", 2))
                timeout_ctx.reschedule(asyncio.get_event_loop().time() + retry_after + 1)
                await asyncio.sleep(retry_after)
                response = await initial_request()

            return response.json()
    except TimeoutError:
        return None
```

**Alternative (asyncio.timeout_at for absolute deadlines):**

```python
# When you need to coordinate with external deadlines
import asyncio

async def process_with_deadline(deadline: float):
    """Process until absolute deadline (e.g., from HTTP request)."""
    try:
        async with asyncio.timeout_at(deadline):
            result = await long_running_process()
            return result
    except TimeoutError:
        return partial_result()
```

**When to use:** For all timeout scenarios in Python 3.11+. Use `timeout()` for relative timeouts and `timeout_at()` for absolute deadlines. The context manager is especially valuable when multiple operations share a deadline.

**When NOT to use:** When targeting Python 3.10 or earlier (use `wait_for` with `asyncio.TimeoutError`). For simple single-operation timeouts where you don't need rescheduling, `wait_for` is acceptable.

Reference: [asyncio.timeout](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout)
