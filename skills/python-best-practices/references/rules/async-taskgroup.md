---
title: Use TaskGroup for Structured Concurrency
impact: CRITICAL
impactDescription: Automatic cleanup and exception propagation
tags: async, taskgroup, concurrency, python311
---

## Use TaskGroup for Structured Concurrency

Use `asyncio.TaskGroup` instead of manually managing tasks with `gather()`.

**Incorrect (manual task management):**

```python
import asyncio

async def fetch_all_data():
    task1 = asyncio.create_task(fetch_users())
    task2 = asyncio.create_task(fetch_orders())
    try:
        results = await asyncio.gather(task1, task2)
        return results
    except Exception:
        task1.cancel()
        task2.cancel()
        raise
```

**Correct (using TaskGroup):**

```python
import asyncio

async def fetch_all_data():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_users())
        task2 = tg.create_task(fetch_orders())
    return (task1.result(), task2.result())
```

Reference: [asyncio TaskGroup](https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup)
