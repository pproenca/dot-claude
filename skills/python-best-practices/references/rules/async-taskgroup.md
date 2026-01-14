---
title: Use TaskGroup for Structured Concurrency
impact: CRITICAL
impactDescription: Eliminates 10+ lines of manual cleanup code, guarantees no orphaned tasks
tags: async, taskgroup, concurrency, python311, httpx, aiohttp
---

## Use TaskGroup for Structured Concurrency

TaskGroup eliminates 10-15 lines of manual task cleanup code per concurrent operation and guarantees that no tasks are orphaned on exceptions. Without TaskGroup, failing to cancel tasks properly can leak connections, file handles, and memory - a common source of production issues.

**Incorrect (manual task management):**

```python
# PROBLEM: 15+ lines of error-prone cleanup code, easy to miss edge cases
import asyncio
import httpx

async def fetch_all_data():
    """Fetch data from multiple APIs - manual cleanup required."""
    tasks = []
    try:
        async with httpx.AsyncClient() as client:
            task1 = asyncio.create_task(client.get("https://api.example.com/users"))
            task2 = asyncio.create_task(client.get("https://api.example.com/orders"))
            task3 = asyncio.create_task(client.get("https://api.example.com/products"))
            tasks = [task1, task2, task3]

            results = await asyncio.gather(*tasks)
            return [r.json() for r in results]
    except Exception:
        # Manual cleanup - easy to forget or do incorrectly
        for task in tasks:
            if not task.done():
                task.cancel()
        # Must await cancelled tasks to prevent warnings
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
    # What if httpx.AsyncClient.__aexit__ raises? Tasks may leak!
```

**Correct (using TaskGroup):**

```python
# SOLUTION: Automatic cleanup, no orphaned tasks, all exceptions captured
import asyncio
import httpx

async def fetch_all_data():
    """Fetch data from multiple APIs with structured concurrency."""
    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:
            task_users = tg.create_task(client.get("https://api.example.com/users"))
            task_orders = tg.create_task(client.get("https://api.example.com/orders"))
            task_products = tg.create_task(client.get("https://api.example.com/products"))

        # All tasks guaranteed complete here
        return [
            task_users.result().json(),
            task_orders.result().json(),
            task_products.result().json(),
        ]

# Handle multiple failures gracefully with except*
async def fetch_with_error_handling():
    """Fetch with granular error handling for different failure types."""
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fetch_users())
            tg.create_task(fetch_orders())
    except* httpx.ConnectError as eg:
        # Handle all connection errors from any task
        for exc in eg.exceptions:
            logger.error(f"Connection failed: {exc}")
    except* httpx.TimeoutException as eg:
        # Handle all timeout errors from any task
        for exc in eg.exceptions:
            logger.error(f"Request timed out: {exc}")
```

**Alternative (gather with return_exceptions for partial results):**

```python
# When you need partial results even if some tasks fail
async def fetch_best_effort():
    """Fetch data, returning partial results on failures."""
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            client.get("https://api.example.com/users"),
            client.get("https://api.example.com/orders"),
            return_exceptions=True,  # Don't raise, return exceptions in list
        )
        # Filter out failures
        return [r.json() for r in results if not isinstance(r, Exception)]
```

**When to use:** For all concurrent async operations in Python 3.11+. TaskGroup should be the default choice for running multiple coroutines concurrently.

**When NOT to use:** When you need partial results from a set of tasks (use `gather(return_exceptions=True)`), or when targeting Python 3.10 or earlier.

Reference: [asyncio TaskGroup](https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup)
