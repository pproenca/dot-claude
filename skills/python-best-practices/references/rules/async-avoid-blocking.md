---
title: Avoid Blocking Calls in Async Functions
impact: CRITICAL
impactDescription: Prevents 100% CPU lockup, missed deadlines from event loop blocking
tags: async, blocking, executor, performance, httpx, requests, pillow
---

## Avoid Blocking Calls in Async Functions

A single blocking call in an async function can freeze the entire event loop, causing 100% CPU usage and missed deadlines for all concurrent operations. A 100ms `requests.get()` call blocks 100+ other coroutines waiting on the same event loop.

**Incorrect (blocking calls in async function):**

```python
# PROBLEM: Each blocking call freezes ALL concurrent tasks, 100% CPU lockup
import asyncio
import requests  # Blocking HTTP client!
import time
from PIL import Image  # Blocking image processing!

async def fetch_and_process():
    """Fetch data and process it."""
    # DANGER: Blocks event loop for 100-5000ms depending on network
    response = requests.get("https://api.example.com/data")

    # DANGER: Blocks event loop for exactly 1000ms
    time.sleep(1)

    return response.json()

async def process_image(image_path: str):
    """Process an uploaded image."""
    # DANGER: CPU-bound operation, blocks for 50-500ms per image
    img = Image.open(image_path)
    img = img.resize((800, 600))  # Blocks!
    img.save(image_path)

async def handler(request):
    """FastAPI handler that blocks the event loop."""
    # While this runs, no other requests are processed!
    await fetch_and_process()  # 1-6 seconds of blocking
    await process_image("/tmp/upload.jpg")  # 50-500ms of blocking
```

**Correct (using async alternatives or executors):**

```python
# SOLUTION: Async I/O for network, executor for CPU-bound work
import asyncio
from concurrent.futures import ThreadPoolExecutor
import httpx
from PIL import Image

# Create a dedicated executor for CPU-bound work
cpu_executor = ThreadPoolExecutor(max_workers=4)

async def fetch_and_process():
    """Fetch data without blocking the event loop."""
    # httpx is fully async - yields control while waiting
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")

    # asyncio.sleep yields to other coroutines
    await asyncio.sleep(1)

    return response.json()

async def process_image(image_path: str):
    """Process image in thread pool to avoid blocking."""
    loop = asyncio.get_running_loop()

    def _resize_image():
        """CPU-bound work runs in thread pool."""
        img = Image.open(image_path)
        img = img.resize((800, 600))
        img.save(image_path)

    # Run blocking code in executor, yields control to event loop
    await loop.run_in_executor(cpu_executor, _resize_image)

async def handler(request):
    """FastAPI handler that never blocks."""
    await fetch_and_process()  # Yields during network I/O
    await process_image("/tmp/upload.jpg")  # Yields during CPU work
```

**Alternative (using asyncio.to_thread for simple cases):**

```python
# Python 3.9+ shorthand for run_in_executor with default executor
import asyncio

async def read_large_file(path: str) -> bytes:
    """Read file without blocking - uses default thread pool."""
    def _read():
        with open(path, "rb") as f:
            return f.read()
    return await asyncio.to_thread(_read)
```

**When to use:** Always use async I/O libraries (httpx, aiofiles, asyncpg) in async code. Use `run_in_executor` or `to_thread` for unavoidable blocking operations like file I/O, image processing, or legacy library calls.

**When NOT to use:** In synchronous code, blocking calls are fine. Don't wrap every function in an executor - only blocking I/O and CPU-intensive operations need this treatment.

Reference: [Executing code in thread or process pools](https://docs.python.org/3/library/asyncio-eventloop.html#executing-code-in-thread-or-process-pools)
