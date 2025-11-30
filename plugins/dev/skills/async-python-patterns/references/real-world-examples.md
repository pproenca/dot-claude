# Real-World Async Examples

## Table of Contents
- [Web Scraping with aiohttp](#web-scraping-with-aiohttp)
- [Async Database Operations](#async-database-operations)
- [WebSocket Server](#websocket-server)
- [Performance Best Practices](#performance-best-practices)

## Web Scraping with aiohttp

```python
import asyncio
import aiohttp
from typing import List, Dict

async def fetch_url(session: aiohttp.ClientSession, url: str) -> Dict:
    """Returns dict with url, status, length or error key."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            text = await response.text()
            return {
                "url": url,
                "status": response.status,
                "length": len(text)
            }
    except Exception as e:
        return {"url": url, "error": str(e)}

async def scrape_urls(urls: List[str]) -> List[Dict]:
    """All URLs fetched concurrently, reuses single session."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

async def main():
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/status/404",
    ]

    results = await scrape_urls(urls)
    for result in results:
        print(result)

asyncio.run(main())
```

## Async Database Operations

```python
import asyncio
from typing import List, Optional

class AsyncDB:
    async def execute(self, query: str) -> List[dict]:
        await asyncio.sleep(0.1)
        return [{"id": 1, "name": "Example"}]

    async def fetch_one(self, query: str) -> Optional[dict]:
        await asyncio.sleep(0.1)
        return {"id": 1, "name": "Example"}

async def get_user_data(db: AsyncDB, user_id: int) -> dict:
    """Runs user, orders, profile queries concurrently."""
    user_task = db.fetch_one(f"SELECT * FROM users WHERE id = {user_id}")
    orders_task = db.execute(f"SELECT * FROM orders WHERE user_id = {user_id}")
    profile_task = db.fetch_one(f"SELECT * FROM profiles WHERE user_id = {user_id}")

    user, orders, profile = await asyncio.gather(user_task, orders_task, profile_task)

    return {
        "user": user,
        "orders": orders,
        "profile": profile
    }

async def main():
    db = AsyncDB()
    user_data = await get_user_data(db, 1)
    print(user_data)

asyncio.run(main())
```

## WebSocket Server

```python
import asyncio
from typing import Set

class WebSocket:
    def __init__(self, client_id: str):
        self.client_id = client_id

    async def send(self, message: str):
        print(f"Sending to {self.client_id}: {message}")
        await asyncio.sleep(0.01)

    async def recv(self) -> str:
        await asyncio.sleep(1)
        return f"Message from {self.client_id}"

class WebSocketServer:
    def __init__(self):
        self.clients: Set[WebSocket] = set()

    async def register(self, websocket: WebSocket):
        self.clients.add(websocket)
        print(f"Client {websocket.client_id} connected")

    async def unregister(self, websocket: WebSocket):
        self.clients.remove(websocket)
        print(f"Client {websocket.client_id} disconnected")

    async def broadcast(self, message: str):
        if self.clients:
            tasks = [client.send(message) for client in self.clients]
            await asyncio.gather(*tasks)

    async def handle_client(self, websocket: WebSocket):
        await self.register(websocket)
        try:
            async for message in self.message_iterator(websocket):
                await self.broadcast(f"{websocket.client_id}: {message}")
        finally:
            await self.unregister(websocket)

    async def message_iterator(self, websocket: WebSocket):
        for _ in range(3):
            yield await websocket.recv()
```

## Performance Best Practices

### Use Connection Pools

```python
import asyncio
import aiohttp

async def with_connection_pool():
    """Reuses TCP connections instead of creating new ones."""
    connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [session.get(f"https://api.example.com/item/{i}") for i in range(50)]
        responses = await asyncio.gather(*tasks)
        return responses
```

### Batch Operations

```python
async def batch_process(items: List[str], batch_size: int = 10):
    """Limits concurrent tasks to prevent resource exhaustion."""
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        tasks = [process_item(item) for item in batch]
        await asyncio.gather(*tasks)
        print(f"Processed batch {i // batch_size + 1}")

async def process_item(item: str):
    await asyncio.sleep(0.1)
    return f"Processed: {item}"
```

### Avoid Blocking Operations

```python
import asyncio
import concurrent.futures
from typing import Any

def blocking_operation(data: Any) -> Any:
    import time
    time.sleep(1)
    return data * 2

async def run_in_executor(data: Any) -> Any:
    """Offloads blocking work to thread pool, keeps event loop free."""
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, blocking_operation, data)
        return result

async def main():
    results = await asyncio.gather(*[run_in_executor(i) for i in range(5)])
    print(results)

asyncio.run(main())
```
