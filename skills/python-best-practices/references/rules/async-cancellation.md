---
title: Handle Task Cancellation Properly
impact: CRITICAL
impactDescription: Prevents resource leaks
tags: async, cancellation, cleanup, error-handling
---

## Handle Task Cancellation Properly

Always handle `CancelledError` to ensure proper cleanup. Never suppress it.

**Incorrect (ignoring cancellation):**

```python
async def process_stream():
    while True:
        data = await receive_data()
        await process_data(data)
```

**Correct (proper cancellation handling):**

```python
import asyncio

async def process_stream():
    resource = await acquire_resource()
    try:
        while True:
            data = await receive_data()
            await process_data(data)
    except asyncio.CancelledError:
        await cleanup_partial_work()
        raise  # Always re-raise
    finally:
        await release_resource(resource)
```

Reference: [Task Cancellation](https://docs.python.org/3/library/asyncio-task.html#task-cancellation)
