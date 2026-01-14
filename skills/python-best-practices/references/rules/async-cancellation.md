---
title: Handle Task Cancellation Properly
impact: CRITICAL
impactDescription: Prevents connection leaks, orphaned transactions, corrupted state
tags: async, cancellation, cleanup, error-handling, graceful-shutdown, aioredis
---

## Handle Task Cancellation Properly

Improper cancellation handling causes resource leaks (database connections, file handles, Redis connections) and corrupted state (partial writes, uncommitted transactions). A cancelled task without cleanup can leak 1-10 connections per occurrence, exhausting connection pools in minutes under load.

**Incorrect (ignoring cancellation):**

```python
# PROBLEM: Resources leak when task is cancelled mid-operation
import asyncio
import aioredis

async def process_stream():
    """Process messages - leaks Redis connection on cancellation."""
    redis = await aioredis.from_url("redis://localhost")
    # If cancelled here, Redis connection is never closed!
    while True:
        data = await redis.lpop("queue")
        if data:
            await process_data(data)  # If cancelled here, data is lost!
        await asyncio.sleep(0.1)

async def update_database():
    """Update with transaction - leaves uncommitted on cancellation."""
    async with db.transaction():
        await db.execute("UPDATE users SET active = true WHERE id = ?", user_id)
        # If cancelled before commit, transaction hangs!
        await db.execute("INSERT INTO audit_log VALUES (?)", user_id)

async def worker():
    """Worker that swallows cancellation - breaks graceful shutdown."""
    try:
        while True:
            await do_work()
    except asyncio.CancelledError:
        pass  # WRONG: Swallowing prevents clean shutdown!
```

**Correct (proper cancellation handling):**

```python
# SOLUTION: Clean up resources, re-raise CancelledError, handle partial work
import asyncio
import aioredis

async def process_stream():
    """Process messages with proper cleanup on cancellation."""
    redis = await aioredis.from_url("redis://localhost")
    current_data = None
    try:
        while True:
            current_data = await redis.lpop("queue")
            if current_data:
                await process_data(current_data)
                current_data = None  # Mark as processed
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        # Return unprocessed data to queue before shutdown
        if current_data is not None:
            await redis.lpush("queue", current_data)
        raise  # ALWAYS re-raise CancelledError
    finally:
        # Clean up regardless of how we exit
        await redis.close()

async def update_database():
    """Update with proper transaction handling."""
    async with db.transaction() as txn:
        try:
            await db.execute("UPDATE users SET active = true WHERE id = ?", user_id)
            await db.execute("INSERT INTO audit_log VALUES (?)", user_id)
            await txn.commit()  # Explicit commit
        except asyncio.CancelledError:
            await txn.rollback()  # Explicit rollback on cancellation
            raise

async def worker():
    """Worker with graceful shutdown support."""
    try:
        while True:
            await do_work()
    except asyncio.CancelledError:
        # Log, flush buffers, close connections
        logger.info("Worker shutting down gracefully")
        await flush_pending_work()
        raise  # Let the cancellation propagate
```

**Alternative (shielding critical sections):**

```python
# When you absolutely must complete an operation before cancellation
import asyncio

async def critical_update():
    """Update that must complete even if cancelled."""
    try:
        await asyncio.shield(commit_to_database())
    except asyncio.CancelledError:
        # The shielded coroutine continues even after cancellation
        # But we must still propagate the cancellation
        raise
```

**When to use:** In any long-running async function that acquires resources (connections, files, locks) or maintains state. Essential for workers, stream processors, and server handlers.

**When NOT to use:** For simple, stateless coroutines that don't acquire resources, explicit cancellation handling may be unnecessary. The `finally` block alone may suffice.

Reference: [Task Cancellation](https://docs.python.org/3/library/asyncio-task.html#task-cancellation)
