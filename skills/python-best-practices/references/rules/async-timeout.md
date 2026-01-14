---
title: Use asyncio.timeout Context Manager
impact: CRITICAL
impactDescription: Cleaner timeout handling
tags: async, timeout, context-manager, python311
---

## Use asyncio.timeout Context Manager

Use `asyncio.timeout()` context manager instead of `asyncio.wait_for()`.

**Incorrect (using wait_for):**

```python
import asyncio

async def fetch_with_timeout():
    try:
        result = await asyncio.wait_for(fetch_data(), timeout=5.0)
        return result
    except asyncio.TimeoutError:
        return None
```

**Correct (using timeout context manager):**

```python
import asyncio

async def fetch_with_timeout():
    try:
        async with asyncio.timeout(5.0):
            return await fetch_data()
    except TimeoutError:
        return None
```

Reference: [asyncio.timeout](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout)
