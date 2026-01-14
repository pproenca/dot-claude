---
title: Use Queue Shutdown for Graceful Termination
impact: CRITICAL
impactDescription: Clean shutdown without sentinel values
tags: async, queue, shutdown, python313
---

## Use Queue Shutdown for Graceful Termination

Python 3.13+ adds `asyncio.Queue.shutdown()` for graceful queue termination.

**Incorrect (manual shutdown signaling):**

```python
async def producer(queue):
    for i in range(10):
        await queue.put(i)
    await queue.put(None)  # Sentinel

async def consumer(queue):
    while (item := await queue.get()) is not None:
        await process(item)
```

**Correct (using Queue.shutdown):**

```python
import asyncio

async def producer(queue):
    for i in range(10):
        await queue.put(i)
    queue.shutdown()

async def consumer(queue):
    try:
        while True:
            item = await queue.get()
            await process(item)
    except asyncio.QueueShutDown:
        pass
```

Reference: [What's New in Python 3.13](https://docs.python.org/3/whatsnew/3.13.html)
