# Advanced Async Patterns

## Table of Contents
- [Pattern 6: Async Context Managers](#pattern-6-async-context-managers)
- [Pattern 7: Async Iterators and Generators](#pattern-7-async-iterators-and-generators)
- [Pattern 8: Producer-Consumer Pattern](#pattern-8-producer-consumer-pattern)
- [Pattern 9: Semaphore for Rate Limiting](#pattern-9-semaphore-for-rate-limiting)
- [Pattern 10: Async Locks and Synchronization](#pattern-10-async-locks-and-synchronization)

## Pattern 6: Async Context Managers

```python
import asyncio
from typing import Optional

class AsyncDatabaseConnection:
    """Manages connection lifecycle via async with."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.connection: Optional[object] = None

    async def __aenter__(self):
        print("Opening connection")
        await asyncio.sleep(0.1)
        self.connection = {"dsn": self.dsn, "connected": True}
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection")
        await asyncio.sleep(0.1)
        self.connection = None

async def query_database():
    async with AsyncDatabaseConnection("postgresql://localhost") as conn:
        print(f"Using connection: {conn}")
        await asyncio.sleep(0.2)
        return {"rows": 10}

asyncio.run(query_database())
```

## Pattern 7: Async Iterators and Generators

```python
import asyncio
from typing import AsyncIterator

async def async_range(start: int, end: int, delay: float = 0.1) -> AsyncIterator[int]:
    for i in range(start, end):
        await asyncio.sleep(delay)
        yield i

async def fetch_pages(url: str, max_pages: int) -> AsyncIterator[dict]:
    for page in range(1, max_pages + 1):
        await asyncio.sleep(0.2)
        yield {
            "page": page,
            "url": f"{url}?page={page}",
            "data": [f"item_{page}_{i}" for i in range(5)]
        }

async def consume_async_iterator():
    async for number in async_range(1, 5):
        print(f"Number: {number}")

    print("\nFetching pages:")
    async for page_data in fetch_pages("https://api.example.com/items", 3):
        print(f"Page {page_data['page']}: {len(page_data['data'])} items")

asyncio.run(consume_async_iterator())
```

## Pattern 8: Producer-Consumer Pattern

```python
import asyncio
from asyncio import Queue
from typing import Optional

async def producer(queue: Queue, producer_id: int, num_items: int):
    for i in range(num_items):
        item = f"Item-{producer_id}-{i}"
        await queue.put(item)
        print(f"Producer {producer_id} produced: {item}")
        await asyncio.sleep(0.1)
    await queue.put(None)  # Sentinel signals consumer to stop

async def consumer(queue: Queue, consumer_id: int):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break

        print(f"Consumer {consumer_id} processing: {item}")
        await asyncio.sleep(0.2)
        queue.task_done()

async def producer_consumer_example():
    queue = Queue(maxsize=10)

    producers = [
        asyncio.create_task(producer(queue, i, 5))
        for i in range(2)
    ]

    consumers = [
        asyncio.create_task(consumer(queue, i))
        for i in range(3)
    ]

    await asyncio.gather(*producers)
    await queue.join()

    for c in consumers:
        c.cancel()

asyncio.run(producer_consumer_example())
```

## Pattern 9: Semaphore for Rate Limiting

```python
import asyncio
from typing import List

async def api_call(url: str, semaphore: asyncio.Semaphore) -> dict:
    async with semaphore:
        print(f"Calling {url}")
        await asyncio.sleep(0.5)
        return {"url": url, "status": 200}

async def rate_limited_requests(urls: List[str], max_concurrent: int = 5):
    """Semaphore limits concurrent API calls to prevent rate limiting."""
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [api_call(url, semaphore) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

async def main():
    urls = [f"https://api.example.com/item/{i}" for i in range(20)]
    results = await rate_limited_requests(urls, max_concurrent=3)
    print(f"Completed {len(results)} requests")

asyncio.run(main())
```

## Pattern 10: Async Locks and Synchronization

```python
import asyncio

class AsyncCounter:
    """Lock prevents race conditions on concurrent increments."""

    def __init__(self):
        self.value = 0
        self.lock = asyncio.Lock()

    async def increment(self):
        async with self.lock:
            current = self.value
            await asyncio.sleep(0.01)
            self.value = current + 1

    async def get_value(self) -> int:
        async with self.lock:
            return self.value

async def worker(counter: AsyncCounter, worker_id: int):
    for _ in range(10):
        await counter.increment()
        print(f"Worker {worker_id} incremented")

async def test_counter():
    counter = AsyncCounter()

    workers = [asyncio.create_task(worker(counter, i)) for i in range(5)]
    await asyncio.gather(*workers)

    final_value = await counter.get_value()
    print(f"Final counter value: {final_value}")

asyncio.run(test_counter())
```
