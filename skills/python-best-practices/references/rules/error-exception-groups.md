---
title: Use Exception Groups
impact: MEDIUM
impactDescription: Handle multiple simultaneous exceptions
tags: error, exception-group, except-star, python311
---

## Use Exception Groups

Use `ExceptionGroup` and `except*` for handling multiple simultaneous exceptions (Python 3.11+).

**Incorrect (losing exceptions in concurrent operations):**

```python
async def fetch_all_with_errors():
    try:
        await asyncio.gather(
            fetch_users(),
            fetch_orders(),
            fetch_products(),
        )
    except Exception as e:
        # Only catches the first exception!
        print(f"Error: {e}")
```

**Correct (using exception groups):**

```python
async def fetch_all_with_errors():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fetch_users())
            tg.create_task(fetch_orders())
    except* ValueError as eg:
        for exc in eg.exceptions:
            print(f"Validation error: {exc}")
    except* ConnectionError as eg:
        for exc in eg.exceptions:
            print(f"Connection error: {exc}")
```

Reference: [Exception Groups](https://docs.python.org/3/library/exceptions.html#ExceptionGroup)
