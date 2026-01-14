---
title: Avoid Blocking Calls in Async Functions
impact: CRITICAL
impactDescription: Prevents event loop blocking
tags: async, blocking, executor, performance
---

## Avoid Blocking Calls in Async Functions

Never call blocking I/O or CPU-intensive operations directly in async functions. Use async alternatives or run blocking code in an executor.

**Incorrect (blocking calls in async function):**

```python
import asyncio
import requests
import time

async def fetch_and_process():
    """Fetch data and process it."""
    # WRONG: This blocks the event loop!
    response = requests.get("https://api.example.com/data")

    # WRONG: This also blocks the event loop!
    time.sleep(1)

    return response.json()
```

**Correct (using async alternatives or executors):**

```python
import asyncio
import httpx

async def fetch_and_process():
    """Fetch data and process it."""
    # Use async HTTP client
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")

    # Use asyncio.sleep for delays
    await asyncio.sleep(1)

    return response.json()

# For unavoidable blocking calls, use run_in_executor
async def process_with_blocking():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, blocking_function)
    return result
```

Reference: [Executing code in thread or process pools](https://docs.python.org/3/library/asyncio-eventloop.html#executing-code-in-thread-or-process-pools)
