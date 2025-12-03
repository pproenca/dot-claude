# Advanced Async Patterns

## Semaphores for Rate Limiting

```python
import asyncio

async def fetch_with_limit(url: str, semaphore: asyncio.Semaphore) -> dict:
    async with semaphore:  # Only N concurrent fetches
        return await fetch_data(url)

async def fetch_all_limited(urls: list[str], max_concurrent: int = 10):
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [fetch_with_limit(url, semaphore) for url in urls]
    return await asyncio.gather(*tasks)
```

## Locks for Shared State

```python
import asyncio

class AsyncCounter:
    def __init__(self):
        self._value = 0
        self._lock = asyncio.Lock()

    async def increment(self) -> int:
        async with self._lock:
            self._value += 1
            return self._value
```

## Producer-Consumer Pattern

```python
import asyncio

async def producer(queue: asyncio.Queue, items: list):
    for item in items:
        await queue.put(item)
    await queue.put(None)  # Sentinel to stop consumers

async def consumer(queue: asyncio.Queue, name: str):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        await process(item)
        queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=100)
    items = range(1000)

    producers = [asyncio.create_task(producer(queue, items))]
    consumers = [asyncio.create_task(consumer(queue, f"C{i}")) for i in range(5)]

    await asyncio.gather(*producers)
    await queue.join()
    for c in consumers:
        c.cancel()
```

## Async Context Managers

```python
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_resource():
    resource = await acquire_resource()
    try:
        yield resource
    finally:
        await release_resource(resource)

async def main():
    async with managed_resource() as r:
        await use_resource(r)
```

## Async Iterators

```python
class AsyncRange:
    def __init__(self, start: int, stop: int):
        self.start = start
        self.stop = stop

    def __aiter__(self):
        self.current = self.start
        return self

    async def __anext__(self):
        if self.current >= self.stop:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)  # Simulate async work
        value = self.current
        self.current += 1
        return value

async def main():
    async for i in AsyncRange(0, 5):
        print(i)
```

## Async Generators

```python
async def async_range(start: int, stop: int):
    for i in range(start, stop):
        await asyncio.sleep(0.1)
        yield i

async def main():
    async for i in async_range(0, 5):
        print(i)
```

## Task Groups (3.11+)

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch("url1"))
        task2 = tg.create_task(fetch("url2"))
    # All tasks complete or all are cancelled on first exception
    return task1.result(), task2.result()
```

## Cancellation Handling

```python
async def cancelable_task():
    try:
        while True:
            await asyncio.sleep(1)
            print("Working...")
    except asyncio.CancelledError:
        print("Cleaning up...")
        await cleanup()
        raise  # Re-raise to propagate

async def main():
    task = asyncio.create_task(cancelable_task())
    await asyncio.sleep(3)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Task was cancelled")
```

## Exception Groups (3.11+)

```python
async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(might_fail_1())
            tg.create_task(might_fail_2())
    except* ValueError as eg:
        for exc in eg.exceptions:
            print(f"ValueError: {exc}")
    except* TypeError as eg:
        for exc in eg.exceptions:
            print(f"TypeError: {exc}")
```

## Connection Pooling

```python
import aiohttp

async def fetch_with_session(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as response:
        return await response.json()

async def fetch_many(urls: list[str]):
    connector = aiohttp.TCPConnector(limit=100)  # Max 100 connections
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_with_session(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```
