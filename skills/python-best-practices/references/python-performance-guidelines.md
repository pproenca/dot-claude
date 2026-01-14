# Python 3.11-3.14 Best Practices

**Version 0.1.0**
Official Python Docs & Community Best Practices
January 2026

> **Note:**
> This document is mainly for agents and LLMs to follow when maintaining,
> generating, or refactoring Python codebases. Humans
> may also find it useful, but guidance here is optimized for automation
> and consistency by AI-assisted workflows.

---

## Abstract

Comprehensive performance optimization guide for Python 3.11-3.14 applications, designed for AI agents and LLMs. Contains 43+ rules across 8 categories, prioritized by impact from critical (eliminating type annotation boilerplate by 50% and 5+ import statements per file, preventing async deadlocks and event loop blocking) to incremental (consolidating project configuration into single pyproject.toml). Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct implementations, and specific impact metrics to guide automated refactoring and code generation.

---

## Table of Contents

1. [Modern Type Annotations](#1-modern-type-annotations) — **CRITICAL**
   - 1.1 [Use Union Pipe Syntax](#11-use-union-pipe-syntax)
   - 1.2 [Use None Instead of Optional](#12-use-none-instead-of-optional)
   - 1.3 [Use PEP 695 Type Parameter Syntax](#13-use-pep-695-type-parameter-syntax)
   - 1.4 [Use Built-in Generics](#14-use-built-in-generics)
   - 1.5 [Use Type Statement for Aliases](#15-use-type-statement-for-aliases)
2. [Async & Concurrency Patterns](#2-async--concurrency-patterns) — **CRITICAL**
   - 2.1 [Use TaskGroup for Structured Concurrency](#21-use-taskgroup-for-structured-concurrency)
   - 2.2 [Use asyncio.timeout Context Manager](#22-use-asynciotimeout-context-manager)
   - 2.3 [Handle Task Cancellation Properly](#23-handle-task-cancellation-properly)
   - 2.4 [Use Queue Shutdown for Graceful Termination](#24-use-queue-shutdown-for-graceful-termination)
   - 2.5 [Avoid Blocking Calls in Async Functions](#25-avoid-blocking-calls-in-async-functions)
3. [Memory & Performance Optimization](#3-memory--performance-optimization) — **HIGH**
   - 3.1 [Use Slots for Memory-Efficient Classes](#31-use-slots-for-memory-efficient-classes)
   - 3.2 [Use Generators for Large Datasets](#32-use-generators-for-large-datasets)
   - 3.3 [Cache Expensive Computations](#33-cache-expensive-computations)
   - 3.4 [Use Local Variable Caching](#34-use-local-variable-caching)
4. [Modern Python Idioms](#4-modern-python-idioms) — **MEDIUM-HIGH**
   - 4.1 [Use Structural Pattern Matching](#41-use-structural-pattern-matching)
   - 4.2 [Use F-String Debug Specifier](#42-use-f-string-debug-specifier)
   - 4.3 [Use tomllib for TOML Parsing](#43-use-tomllib-for-toml-parsing)
5. [Error Handling & Exceptions](#5-error-handling--exceptions) — **MEDIUM**
   - 5.1 [Use Exception Groups](#51-use-exception-groups)
   - 5.2 [Chain Exceptions Properly](#52-chain-exceptions-properly)
   - 5.3 [Use Context Managers for Cleanup](#53-use-context-managers-for-cleanup)
   - 5.4 [Create Custom Exceptions Properly](#54-create-custom-exceptions-properly)
   - 5.5 [Use Self Type for Method Chaining](#55-use-self-type-for-method-chaining)
   - 5.6 [Leverage Improved Error Messages](#56-leverage-improved-error-messages)
6. [Data Structures & Classes](#6-data-structures--classes) — **MEDIUM**
   - 6.1 [Use Dataclass with Slots](#61-use-dataclass-with-slots)
   - 6.2 [Use TypedDict for Dictionary Schemas](#62-use-typeddict-for-dictionary-schemas)
   - 6.3 [Use NamedTuple Over Plain Tuples](#63-use-namedtuple-over-plain-tuples)
   - 6.4 [Use Enum with Auto](#64-use-enum-with-auto)
   - 6.5 [Use Frozen Dataclass for Immutability](#65-use-frozen-dataclass-for-immutability)
   - 6.6 [Use copy.replace for Updates](#66-use-copyreplace-for-updates)
   - 6.7 [Use Field Default Factory](#67-use-field-default-factory)
7. [Security & Safety Patterns](#7-security--safety-patterns) — **LOW-MEDIUM**
   - 7.1 [Never Use eval with Untrusted Input](#71-never-use-eval-with-untrusted-input)
   - 7.2 [Use literal_eval for Safe Parsing](#72-use-literal_eval-for-safe-parsing)
   - 7.3 [Avoid Pickle with Untrusted Data](#73-avoid-pickle-with-untrusted-data)
   - 7.4 [Validate External Input](#74-validate-external-input)
   - 7.5 [Use secrets Module for Security](#75-use-secrets-module-for-security)
   - 7.6 [Avoid shell=True in Subprocess](#76-avoid-shelltrue-in-subprocess)
   - 7.7 [Use Parameterized Database Queries](#77-use-parameterized-database-queries)
   - 7.8 [Store Secrets in Environment Variables](#78-store-secrets-in-environment-variables)
   - 7.9 [Use Proper Hashing Algorithms](#79-use-proper-hashing-algorithms)
   - 7.10 [Prevent Directory Traversal](#710-prevent-directory-traversal)
8. [Tooling & Configuration](#8-tooling--configuration) — **LOW**
   - 8.1 [Use pyproject.toml as Single Source](#81-use-pyprojecttoml-as-single-source)
   - 8.2 [Configure Ruff for Linting](#82-configure-ruff-for-linting)
   - 8.3 [Enable Strict Mypy Mode](#83-enable-strict-mypy-mode)

---

## 1. Modern Type Annotations

**Impact: CRITICAL**

Modern type syntax reduces annotation boilerplate by 50% and eliminates 5+ import statements per file. Type checkers catch 3-5 type errors per 1000 LoC at development time - errors that would otherwise become runtime bugs in production.

### 1.1 Use Union Pipe Syntax

Use the `|` operator for union types instead of importing `Union` from the typing module. This syntax is cleaner and requires no imports for Python 3.10+.

**Incorrect: Using Union from typing module**

```python
from typing import Union

def process_value(value: Union[int, str, float]) -> Union[str, None]:
    """Process a numeric or string value."""
    if isinstance(value, (int, float)):
        return str(value * 2)
    return value.upper()

def get_user_id(user: Union[dict, None]) -> Union[int, None]:
    if user is None:
        return None
    return user.get("id")
```

**Correct: Using pipe operator for unions**

```python
def process_value(value: int | str | float) -> str | None:
    """Process a numeric or string value."""
    if isinstance(value, (int, float)):
        return str(value * 2)
    return value.upper()

def get_user_id(user: dict | None) -> int | None:
    if user is None:
        return None
    return user.get("id")
```

The pipe syntax is more readable and reduces import clutter. None should always be the last element in a union.

### 1.2 Use None Instead of Optional

Replace `Optional[X]` with `X | None`. The `Optional` type from typing is now considered legacy syntax.

**Incorrect: Using Optional from typing**

```python
from typing import Optional

def find_user(user_id: int) -> Optional[dict]:
    """Find a user by ID."""
    users = {"1": {"name": "Alice"}, "2": {"name": "Bob"}}
    return users.get(str(user_id))

def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get configuration value."""
    config = {"debug": "true", "timeout": "30"}
    return config.get(key, default)
```

**Correct: Using X | None syntax**

```python
def find_user(user_id: int) -> dict | None:
    """Find a user by ID."""
    users = {"1": {"name": "Alice"}, "2": {"name": "Bob"}}
    return users.get(str(user_id))

def get_config(key: str, default: str | None = None) -> str | None:
    """Get configuration value."""
    config = {"debug": "true", "timeout": "30"}
    return config.get(key, default)
```

### 1.3 Use PEP 695 Type Parameter Syntax

Python 3.12+ introduces a new syntax for generic functions and classes that eliminates the need for `TypeVar` declarations.

**Incorrect: Using TypeVar for generics (pre-3.12 style)**

```python
from typing import TypeVar, Sequence, Callable

T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")
V = TypeVar("V")

def first(items: Sequence[T]) -> T:
    """Return the first item in a sequence."""
    return items[0]

def map_items(items: list[T], func: Callable[[T], U]) -> list[U]:
    """Apply a function to each item."""
    return [func(item) for item in items]

class Stack(list[T]):
    """A simple stack implementation."""
    def push(self, item: T) -> None:
        self.append(item)

    def pop_item(self) -> T:
        return self.pop()
```

**Correct: Using PEP 695 type parameter syntax (3.12+)**

```python
from collections.abc import Sequence, Callable

def first[T](items: Sequence[T]) -> T:
    """Return the first item in a sequence."""
    return items[0]

def map_items[T, U](items: list[T], func: Callable[[T], U]) -> list[U]:
    """Apply a function to each item."""
    return [func(item) for item in items]

class Stack[T](list[T]):
    """A simple stack implementation."""
    def push(self, item: T) -> None:
        self.append(item)

    def pop_item(self) -> T:
        return self.pop()
```

The new syntax is more concise, eliminates redundant name strings, and provides automatic variance inference.

### 1.4 Use Built-in Generics

Use built-in collection types directly as generics instead of importing from `typing`.

**Incorrect: Importing generic types from typing**

```python
from typing import List, Dict, Set, Tuple, Type, FrozenSet

def process_items(items: List[str]) -> Dict[str, int]:
    """Count occurrences of each item."""
    result: Dict[str, int] = {}
    for item in items:
        result[item] = result.get(item, 0) + 1
    return result

def get_unique(items: List[str]) -> Set[str]:
    """Get unique items."""
    return set(items)

def get_coordinates() -> Tuple[float, float, float]:
    """Return 3D coordinates."""
    return (1.0, 2.0, 3.0)

def create_instance(cls: Type[object]) -> object:
    """Create an instance of a class."""
    return cls()
```

**Correct: Using built-in generics**

```python
def process_items(items: list[str]) -> dict[str, int]:
    """Count occurrences of each item."""
    result: dict[str, int] = {}
    for item in items:
        result[item] = result.get(item, 0) + 1
    return result

def get_unique(items: list[str]) -> set[str]:
    """Get unique items."""
    return set(items)

def get_coordinates() -> tuple[float, float, float]:
    """Return 3D coordinates."""
    return (1.0, 2.0, 3.0)

def create_instance(cls: type[object]) -> object:
    """Create an instance of a class."""
    return cls()
```

For abstract types, import from `collections.abc` instead of `typing`.

### 1.5 Use Type Statement for Aliases

Python 3.12+ introduces the `type` statement for type aliases, replacing `TypeAlias` annotation.

**Incorrect: Using TypeAlias annotation**

```python
from typing import TypeAlias

UserId: TypeAlias = int
UserData: TypeAlias = dict[str, str | int | None]
Callback: TypeAlias = Callable[[str, int], bool]

# Forward references require string quotes
TreeNode: TypeAlias = "dict[str, TreeNode | int]"
```

**Correct: Using type statement (3.12+)**

```python
from collections.abc import Callable

type UserId = int
type UserData = dict[str, str | int | None]
type Callback = Callable[[str, int], bool]

# Forward references work naturally
type TreeNode = dict[str, TreeNode | int]
```

The `type` statement creates `TypeAliasType` instances and natively supports forward references without quotes.

---

## 2. Async & Concurrency Patterns

**Impact: CRITICAL**

Blocking calls in async code cause 100% CPU lockup and missed deadlines for all concurrent operations. TaskGroup eliminates 10-15 lines of manual cleanup code per concurrent operation and guarantees no orphaned tasks on exceptions.

### 2.1 Use TaskGroup for Structured Concurrency

Use `asyncio.TaskGroup` instead of manually managing tasks with `gather()` or `create_task()`. TaskGroup ensures proper cleanup and exception propagation.

**Incorrect: Manual task management with gather**

```python
import asyncio

async def fetch_all_data():
    """Fetch data from multiple sources."""
    task1 = asyncio.create_task(fetch_users())
    task2 = asyncio.create_task(fetch_orders())
    task3 = asyncio.create_task(fetch_products())

    try:
        results = await asyncio.gather(task1, task2, task3)
        return results
    except Exception:
        # Manual cleanup required
        task1.cancel()
        task2.cancel()
        task3.cancel()
        raise
```

**Correct: Using TaskGroup for structured concurrency**

```python
import asyncio

async def fetch_all_data():
    """Fetch data from multiple sources."""
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_users())
        task2 = tg.create_task(fetch_orders())
        task3 = tg.create_task(fetch_products())

    # All tasks completed successfully here
    return (task1.result(), task2.result(), task3.result())
```

TaskGroup automatically cancels remaining tasks if one fails and properly propagates exceptions.

### 2.2 Use asyncio.timeout Context Manager

Use `asyncio.timeout()` context manager instead of `asyncio.wait_for()` for cleaner timeout handling.

**Incorrect: Using wait_for for timeouts**

```python
import asyncio

async def fetch_with_timeout():
    """Fetch data with a timeout."""
    try:
        result = await asyncio.wait_for(fetch_data(), timeout=5.0)
        return result
    except asyncio.TimeoutError:
        return None

async def process_with_multiple_timeouts():
    """Multiple operations with different timeouts."""
    data1 = await asyncio.wait_for(fetch_users(), timeout=3.0)
    data2 = await asyncio.wait_for(fetch_orders(), timeout=5.0)
    return data1, data2
```

**Correct: Using timeout context manager (3.11+)**

```python
import asyncio

async def fetch_with_timeout():
    """Fetch data with a timeout."""
    try:
        async with asyncio.timeout(5.0):
            result = await fetch_data()
            return result
    except TimeoutError:
        return None

async def process_with_multiple_timeouts():
    """Multiple operations with different timeouts."""
    async with asyncio.timeout(3.0):
        data1 = await fetch_users()
    async with asyncio.timeout(5.0):
        data2 = await fetch_orders()
    return data1, data2
```

The context manager approach allows for deadline rescheduling with `timeout.reschedule()`.

### 2.3 Handle Task Cancellation Properly

Always handle `CancelledError` to ensure proper cleanup when tasks are cancelled.

**Incorrect: Ignoring cancellation handling**

```python
import asyncio

async def process_stream():
    """Process a data stream."""
    while True:
        data = await receive_data()
        await process_data(data)
        # If cancelled during processing, resources may leak
```

**Correct: Proper cancellation handling**

```python
import asyncio

async def process_stream():
    """Process a data stream with proper cleanup."""
    resource = await acquire_resource()
    try:
        while True:
            data = await receive_data()
            await process_data(data)
    except asyncio.CancelledError:
        # Perform cleanup before re-raising
        await cleanup_partial_work()
        raise  # Always re-raise CancelledError
    finally:
        await release_resource(resource)
```

Never suppress `CancelledError` - always re-raise it after cleanup.

### 2.4 Use Queue Shutdown for Graceful Termination

Python 3.13+ adds `asyncio.Queue.shutdown()` for graceful queue termination.

**Incorrect: Manual shutdown signaling**

```python
import asyncio

async def producer(queue: asyncio.Queue):
    for i in range(10):
        await queue.put(i)
    await queue.put(None)  # Sentinel value

async def consumer(queue: asyncio.Queue):
    while True:
        item = await queue.get()
        if item is None:  # Check for sentinel
            break
        await process(item)
        queue.task_done()
```

**Correct: Using Queue.shutdown() (3.13+)**

```python
import asyncio

async def producer(queue: asyncio.Queue):
    for i in range(10):
        await queue.put(i)
    queue.shutdown()  # Signal no more items

async def consumer(queue: asyncio.Queue):
    try:
        while True:
            item = await queue.get()
            await process(item)
            queue.task_done()
    except asyncio.QueueShutDown:
        pass  # Queue was shut down
```

### 2.5 Avoid Blocking Calls in Async Functions

Never call blocking I/O or CPU-intensive operations directly in async functions.

**Incorrect: Blocking calls in async function**

```python
import asyncio
import requests
import time

async def fetch_and_process():
    """Fetch data and process it."""
    # WRONG: This blocks the event loop!
    response = requests.get("https://api.example.com/data")

    # WRONG: This also blocks the event loop!
    time.sleep(1)

    return response.json()
```

**Correct: Using async alternatives or executors**

```python
import asyncio
import httpx

async def fetch_and_process():
    """Fetch data and process it."""
    # Use async HTTP client
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")

    # Use asyncio.sleep for delays
    await asyncio.sleep(1)

    return response.json()

# For unavoidable blocking calls, use run_in_executor
async def process_with_blocking():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, blocking_function)
    return result
```

---

## 3. Memory & Performance Optimization

**Impact: HIGH**

`__slots__` reduces instance memory by 73% (150 bytes to 40 bytes per instance). For 1 million objects, this saves 110MB of RAM. Generators process 10GB+ files with constant memory instead of loading entire datasets.

### 3.1 Use Slots for Memory-Efficient Classes

Use `__slots__` to prevent creation of `__dict__` for instances, reducing memory by 30-50%.

**Incorrect: Class without slots (default behavior)**

```python
class Point:
    """A 2D point without slots."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

# Each instance has a __dict__ with ~100-200 bytes overhead
points = [Point(i, i) for i in range(1_000_000)]
```

**Correct: Using __slots__ for memory efficiency**

```python
class Point:
    """A 2D point with slots for memory efficiency."""
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

# Each instance is ~40 bytes instead of ~150 bytes
points = [Point(i, i) for i in range(1_000_000)]
```

Use slots when creating many instances of a class. Be aware that slots prevent adding dynamic attributes.

### 3.2 Use Generators for Large Datasets

Use generator expressions instead of list comprehensions when iterating once over large datasets.

**Incorrect: Creating large intermediate lists**

```python
def process_large_file(filename: str) -> int:
    """Count valid lines in a large file."""
    with open(filename) as f:
        # Creates entire list in memory!
        lines = [line.strip() for line in f]
        valid_lines = [line for line in lines if is_valid(line)]
        return len(valid_lines)

def get_squares_sum(n: int) -> int:
    """Sum of squares up to n."""
    # Creates list of 1 million items!
    squares = [x ** 2 for x in range(n)]
    return sum(squares)
```

**Correct: Using generators for memory efficiency**

```python
def process_large_file(filename: str) -> int:
    """Count valid lines in a large file."""
    with open(filename) as f:
        # Generator - processes one line at a time
        valid_count = sum(1 for line in f if is_valid(line.strip()))
        return valid_count

def get_squares_sum(n: int) -> int:
    """Sum of squares up to n."""
    # Generator expression - no list created
    return sum(x ** 2 for x in range(n))
```

Generators are single-use; create a new generator if you need to iterate again.

### 3.3 Cache Expensive Computations

Use `functools.cache` or `functools.lru_cache` for memoizing expensive function calls.

**Incorrect: Recomputing expensive results**

```python
def fibonacci(n: int) -> int:
    """Calculate fibonacci number."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)  # Exponential time!

def fetch_user_data(user_id: int) -> dict:
    """Fetch user data from database."""
    # Called multiple times with same ID
    return database.query(f"SELECT * FROM users WHERE id = {user_id}")
```

**Correct: Using functools.cache for memoization**

```python
from functools import cache, lru_cache

@cache  # Unlimited cache (Python 3.9+)
def fibonacci(n: int) -> int:
    """Calculate fibonacci number with memoization."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)  # O(n) time now

@lru_cache(maxsize=128)  # Limited cache, evicts least-recently-used
def fetch_user_data(user_id: int) -> dict:
    """Fetch user data with caching."""
    return database.query(f"SELECT * FROM users WHERE id = {user_id}")

# Clear cache when needed
fetch_user_data.cache_clear()
```

Use `@cache` for unlimited caching and `@lru_cache(maxsize=N)` for bounded caching.

### 3.4 Use Local Variable Caching

Cache attribute lookups and method calls in local variables within tight loops.

**Incorrect: Repeated attribute lookups in loop**

```python
import math

def calculate_distances(points: list[tuple[float, float]]) -> list[float]:
    """Calculate distance from origin for all points."""
    distances = []
    for x, y in points:
        # math.sqrt looked up on every iteration
        distances.append(math.sqrt(x ** 2 + y ** 2))
    return distances

class Processor:
    def process_all(self, items: list[str]) -> list[str]:
        results = []
        for item in items:
            # self.transform looked up on every iteration
            results.append(self.transform(item))
        return results
```

**Correct: Caching lookups in local variables**

```python
import math

def calculate_distances(points: list[tuple[float, float]]) -> list[float]:
    """Calculate distance from origin for all points."""
    sqrt = math.sqrt  # Cache the function lookup
    distances = []
    for x, y in points:
        distances.append(sqrt(x ** 2 + y ** 2))
    return distances

class Processor:
    def process_all(self, items: list[str]) -> list[str]:
        transform = self.transform  # Cache method lookup
        results = []
        for item in items:
            results.append(transform(item))
        return results
```

This optimization is most impactful in tight loops processing millions of items.

---

## 4. Modern Python Idioms

**Impact: MEDIUM-HIGH**

Pattern matching replaces 10-20 line if/elif chains with 5-8 line match statements. The f-string debug specifier (`f"{x=}"`) saves 50% typing in debug statements while being self-documenting.

### 4.1 Use Structural Pattern Matching

Use `match`/`case` statements for complex conditional logic instead of if/elif chains.

**Incorrect: Long if/elif chains**

```python
def handle_command(command: dict) -> str:
    """Handle a command based on its type."""
    if command.get("type") == "move":
        direction = command.get("direction")
        if direction == "north":
            return move_north()
        elif direction == "south":
            return move_south()
        else:
            return "Invalid direction"
    elif command.get("type") == "attack":
        target = command.get("target")
        if target is not None:
            return attack(target)
        else:
            return "No target specified"
    elif command.get("type") == "quit":
        return quit_game()
    else:
        return "Unknown command"
```

**Correct: Using structural pattern matching (3.10+)**

```python
def handle_command(command: dict) -> str:
    """Handle a command using pattern matching."""
    match command:
        case {"type": "move", "direction": "north"}:
            return move_north()
        case {"type": "move", "direction": "south"}:
            return move_south()
        case {"type": "move", "direction": direction}:
            return f"Invalid direction: {direction}"
        case {"type": "attack", "target": target} if target is not None:
            return attack(target)
        case {"type": "attack"}:
            return "No target specified"
        case {"type": "quit"}:
            return quit_game()
        case _:
            return "Unknown command"
```

Pattern matching is especially powerful for matching nested structures and using guards.

### 4.2 Use F-String Debug Specifier

Use the `=` specifier in f-strings for quick debugging output.

**Incorrect: Manually formatting debug output**

```python
def debug_calculation(x: int, y: int) -> int:
    """Calculate with debug output."""
    result = x * y + 10
    print(f"x={x}, y={y}, result={result}")

    intermediate = x ** 2
    print(f"intermediate={intermediate}")

    return result
```

**Correct: Using f-string = specifier**

```python
def debug_calculation(x: int, y: int) -> int:
    """Calculate with debug output."""
    result = x * y + 10
    print(f"{x=}, {y=}, {result=}")  # Output: x=5, y=3, result=25

    intermediate = x ** 2
    print(f"{intermediate=}")  # Output: intermediate=25

    # Also works with expressions
    print(f"{x + y=}")  # Output: x + y=8

    return result
```

The `=` specifier automatically includes the variable name/expression in the output.

### 4.3 Use tomllib for TOML Parsing

Use the built-in `tomllib` module (Python 3.11+) for parsing TOML files instead of third-party libraries.

**Incorrect: Using third-party TOML library**

```python
# Requires: pip install toml
import toml

def load_config(path: str) -> dict:
    """Load configuration from TOML file."""
    with open(path) as f:
        return toml.load(f)
```

**Correct: Using built-in tomllib (3.11+)**

```python
import tomllib

def load_config(path: str) -> dict:
    """Load configuration from TOML file."""
    with open(path, "rb") as f:  # Note: binary mode required
        return tomllib.load(f)

# For parsing TOML strings
def parse_toml_string(content: str) -> dict:
    """Parse TOML from a string."""
    return tomllib.loads(content)
```

Note that `tomllib` only supports reading TOML, not writing. Use `tomli-w` for writing.

---

## 5. Error Handling & Exceptions

**Impact: MEDIUM**

Proper exception handling improves code robustness and debugging experience.

### 5.1 Use Exception Groups

Use `ExceptionGroup` and `except*` for handling multiple simultaneous exceptions (Python 3.11+).

**Incorrect: Losing exceptions in concurrent operations**

```python
async def fetch_all_with_errors():
    """Fetch from multiple sources, only catching first error."""
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

**Correct: Using exception groups (3.11+)**

```python
async def fetch_all_with_errors():
    """Fetch from multiple sources, handling all errors."""
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fetch_users())
            tg.create_task(fetch_orders())
            tg.create_task(fetch_products())
    except* ValueError as eg:
        # Handle all ValueError exceptions
        for exc in eg.exceptions:
            print(f"Validation error: {exc}")
    except* ConnectionError as eg:
        # Handle all ConnectionError exceptions
        for exc in eg.exceptions:
            print(f"Connection error: {exc}")
```

The `except*` syntax allows handling different exception types from an exception group.

### 5.2 Chain Exceptions Properly

Always use `raise ... from` to properly chain exceptions and preserve context.

**Incorrect: Losing exception context**

```python
def process_config(path: str) -> dict:
    """Process configuration file."""
    try:
        with open(path) as f:
            return parse_config(f.read())
    except FileNotFoundError:
        raise ConfigError("Config file not found")  # Loses original traceback

def fetch_data(url: str) -> dict:
    try:
        return make_request(url)
    except Exception:
        raise DataError("Failed to fetch data")  # Loses original exception
```

**Correct: Properly chaining exceptions**

```python
def process_config(path: str) -> dict:
    """Process configuration file."""
    try:
        with open(path) as f:
            return parse_config(f.read())
    except FileNotFoundError as e:
        raise ConfigError(f"Config file not found: {path}") from e

def fetch_data(url: str) -> dict:
    try:
        return make_request(url)
    except RequestError as e:
        raise DataError(f"Failed to fetch data from {url}") from e
    except Exception as e:
        # Use 'from None' to explicitly suppress chain if needed
        raise DataError("Unexpected error") from None
```

### 5.3 Use Context Managers for Cleanup

Use context managers to ensure resources are properly cleaned up.

**Incorrect: Manual resource management**

```python
def process_file(path: str) -> list[str]:
    """Process a file."""
    f = open(path)
    try:
        lines = f.readlines()
        return [line.strip() for line in lines]
    finally:
        f.close()

def use_database():
    """Use a database connection."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()
        finally:
            cursor.close()
    finally:
        conn.close()
```

**Correct: Using context managers**

```python
def process_file(path: str) -> list[str]:
    """Process a file."""
    with open(path) as f:
        return [line.strip() for line in f]

def use_database():
    """Use a database connection."""
    with create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()
```

### 5.4 Create Custom Exceptions Properly

Create custom exceptions that inherit from appropriate base classes.

**Incorrect: Poor exception design**

```python
class Error(Exception):
    pass

class ConfigError(Error):
    def __init__(self, msg):
        self.msg = msg

class NetworkError:  # Not inheriting from Exception!
    pass
```

**Correct: Well-designed custom exceptions**

```python
class ApplicationError(Exception):
    """Base exception for application errors."""
    pass

class ConfigError(ApplicationError):
    """Configuration-related errors."""
    def __init__(self, message: str, path: str | None = None):
        self.path = path
        super().__init__(message)

class NetworkError(ApplicationError):
    """Network-related errors."""
    def __init__(self, message: str, url: str, status_code: int | None = None):
        self.url = url
        self.status_code = status_code
        super().__init__(message)
```

### 5.5 Use Self Type for Method Chaining

Use `Self` type for methods that return the instance itself (Python 3.11+).

**Incorrect: Using class name or Any for return type**

```python
from typing import Any

class Builder:
    def set_name(self, name: str) -> "Builder":  # String annotation
        self.name = name
        return self

    def set_value(self, value: int) -> Any:  # Too permissive
        self.value = value
        return self
```

**Correct: Using Self type (3.11+)**

```python
from typing import Self

class Builder:
    def set_name(self, name: str) -> Self:
        self.name = name
        return self

    def set_value(self, value: int) -> Self:
        self.value = value
        return self

class ExtendedBuilder(Builder):
    def set_extra(self, extra: str) -> Self:  # Returns ExtendedBuilder
        self.extra = extra
        return self
```

### 5.6 Leverage Improved Error Messages

Take advantage of Python 3.11+ improved error messages by writing clear code.

**Example: Python 3.11+ error message improvements**

```python
# Python 3.11+ shows exact location of errors
d = {"users": {"alice": {"age": 30}}}
print(d["users"]["bob"]["age"])
# KeyError: 'bob'
#     print(d["users"]["bob"]["age"])
#           ~~~~~~~~~~~~^^^^^^^

# Suggest similar names for typos
class User:
    def get_name(self): pass

user = User()
user.getname()  # Did you mean: 'get_name'?

# Module shadow warnings
# If you have random.py in your directory:
import random
random.randint(1, 10)
# AttributeError: ... (consider renaming '/path/random.py')
```

---

## 6. Data Structures & Classes

**Impact: MEDIUM**

Modern data structure patterns improve code clarity and reduce boilerplate.

### 6.1 Use Dataclass with Slots

Use `@dataclass(slots=True)` for memory-efficient dataclasses (Python 3.10+).

**Incorrect: Dataclass without slots**

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    z: float

# Each instance has __dict__ overhead
```

**Correct: Dataclass with slots**

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    x: float
    y: float
    z: float

# ~30-50% memory reduction per instance
```

### 6.2 Use TypedDict for Dictionary Schemas

Use `TypedDict` for dictionaries with a fixed set of string keys.

**Incorrect: Using dict without type structure**

```python
def create_user(name: str, age: int) -> dict:
    return {"name": name, "age": age, "active": True}

def process_user(user: dict) -> str:
    # No type checking for key access
    return f"{user['name']} is {user['age']} years old"
```

**Correct: Using TypedDict**

```python
from typing import TypedDict, NotRequired

class User(TypedDict):
    name: str
    age: int
    active: bool
    email: NotRequired[str]  # Optional key

def create_user(name: str, age: int) -> User:
    return {"name": name, "age": age, "active": True}

def process_user(user: User) -> str:
    # Type checker knows about keys and their types
    return f"{user['name']} is {user['age']} years old"
```

### 6.3 Use NamedTuple Over Plain Tuples

Use `NamedTuple` for tuples with named fields.

**Incorrect: Plain tuples with unclear indices**

```python
def get_user_info() -> tuple[str, int, bool]:
    return ("Alice", 30, True)

info = get_user_info()
name = info[0]  # Unclear what index 0 means
age = info[1]
```

**Correct: Using NamedTuple**

```python
from typing import NamedTuple

class UserInfo(NamedTuple):
    name: str
    age: int
    active: bool

def get_user_info() -> UserInfo:
    return UserInfo("Alice", 30, True)

info = get_user_info()
name = info.name  # Clear and self-documenting
age = info.age
# Still supports indexing: info[0]
```

### 6.4 Use Enum with Auto

Use `Enum` with `auto()` for enumerated constants.

**Incorrect: Using string/int constants**

```python
STATUS_PENDING = "pending"
STATUS_ACTIVE = "active"
STATUS_COMPLETED = "completed"

def get_status(order: Order) -> str:
    if order.shipped:
        return STATUS_COMPLETED
    return STATUS_PENDING
```

**Correct: Using Enum with auto**

```python
from enum import Enum, auto

class Status(Enum):
    PENDING = auto()
    ACTIVE = auto()
    COMPLETED = auto()

def get_status(order: Order) -> Status:
    if order.shipped:
        return Status.COMPLETED
    return Status.PENDING

# For string values, use StrEnum (3.11+)
from enum import StrEnum

class Status(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
```

### 6.5 Use Frozen Dataclass for Immutability

Use `@dataclass(frozen=True)` for immutable data objects.

**Incorrect: Mutable dataclass used as hashable**

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

p = Point(1, 2)
p.x = 3  # Mutation allowed
# hash(p)  # TypeError: unhashable
```

**Correct: Frozen dataclass for immutability**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float

p = Point(1, 2)
# p.x = 3  # FrozenInstanceError
hash(p)  # Works! Can use as dict key or in sets

# Combine with slots for efficiency
@dataclass(frozen=True, slots=True)
class ImmutablePoint:
    x: float
    y: float
```

### 6.6 Use copy.replace for Updates

Use `copy.replace()` for creating modified copies of dataclasses (Python 3.13+).

**Incorrect: Manual copy and modify**

```python
from dataclasses import dataclass
import copy

@dataclass
class Config:
    host: str
    port: int
    debug: bool

config = Config("localhost", 8080, False)
new_config = copy.copy(config)
new_config.debug = True
```

**Correct: Using copy.replace (3.13+)**

```python
from dataclasses import dataclass
from copy import replace

@dataclass
class Config:
    host: str
    port: int
    debug: bool

config = Config("localhost", 8080, False)
new_config = replace(config, debug=True)  # Clean functional update
```

### 6.7 Use Field Default Factory

Use `field(default_factory=...)` for mutable default values.

**Incorrect: Mutable default value**

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    tags: list[str] = []  # DANGER: Shared between all instances!
```

**Correct: Using default_factory**

```python
from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    # With initial values
    roles: list[str] = field(default_factory=lambda: ["user"])
```

---

## 7. Security & Safety Patterns

**Impact: LOW-MEDIUM**

Security best practices prevent common vulnerabilities in Python applications.

### 7.1 Never Use eval with Untrusted Input

Never use `eval()`, `exec()`, or `compile()` with untrusted input.

**Incorrect: Using eval with user input**

```python
def calculate(expression: str) -> float:
    """Calculate a mathematical expression."""
    return eval(expression)  # DANGER: Arbitrary code execution!

# Attacker input: "__import__('os').system('rm -rf /')"
```

**Correct: Safe alternatives**

```python
import operator
import ast

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

def safe_calculate(expression: str) -> float:
    """Safely evaluate a mathematical expression."""
    tree = ast.parse(expression, mode='eval')
    return _eval_node(tree.body)

def _eval_node(node):
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return OPERATORS[type(node.op)](left, right)
    else:
        raise ValueError(f"Unsupported operation: {type(node)}")
```

### 7.2 Use literal_eval for Safe Parsing

Use `ast.literal_eval()` for parsing Python literals from strings.

**Incorrect: Using eval for literal parsing**

```python
def parse_config(value: str) -> any:
    """Parse a configuration value."""
    return eval(value)  # DANGER!
```

**Correct: Using ast.literal_eval**

```python
import ast

def parse_config(value: str) -> any:
    """Safely parse a Python literal from string."""
    return ast.literal_eval(value)

# Only supports: strings, bytes, numbers, tuples, lists, dicts, sets, booleans, None
parse_config("[1, 2, 3]")  # [1, 2, 3]
parse_config("{'key': 'value'}")  # {'key': 'value'}
# parse_config("__import__('os')")  # ValueError: malformed node
```

### 7.3 Avoid Pickle with Untrusted Data

Never unpickle data from untrusted sources.

**Incorrect: Unpickling untrusted data**

```python
import pickle

def load_user_data(data: bytes) -> dict:
    """Load user data from bytes."""
    return pickle.loads(data)  # DANGER: Arbitrary code execution!
```

**Correct: Use JSON or safe alternatives**

```python
import json
from typing import TypedDict

class UserData(TypedDict):
    name: str
    age: int

def load_user_data(data: bytes) -> UserData:
    """Safely load user data from JSON."""
    return json.loads(data)

# If you must use pickle, restrict classes
import pickle

class RestrictedUnpickler(pickle.Unpickler):
    ALLOWED_CLASSES = {
        ("collections", "OrderedDict"),
        ("datetime", "datetime"),
    }

    def find_class(self, module: str, name: str):
        if (module, name) in self.ALLOWED_CLASSES:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"Forbidden: {module}.{name}")
```

### 7.4 Validate External Input

Always validate and sanitize input from external sources.

**Incorrect: Trusting external input**

```python
def get_user(user_id: str) -> User:
    """Get a user by ID."""
    return database.query(f"SELECT * FROM users WHERE id = {user_id}")
```

**Correct: Validating input**

```python
from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    user_id: int = Field(gt=0)

def get_user(request: UserRequest) -> User:
    """Get a user by ID with validation."""
    return database.query(
        "SELECT * FROM users WHERE id = ?",
        (request.user_id,)
    )
```

### 7.5 Use secrets Module for Security

Use `secrets` module for cryptographic randomness, not `random`.

**Incorrect: Using random for security**

```python
import random
import string

def generate_token() -> str:
    """Generate an authentication token."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(32))
```

**Correct: Using secrets module**

```python
import secrets
import string

def generate_token() -> str:
    """Generate a cryptographically secure token."""
    return secrets.token_urlsafe(32)

def generate_password(length: int = 16) -> str:
    """Generate a secure password."""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))

# For comparing secrets (timing-attack safe)
def verify_token(provided: str, expected: str) -> bool:
    return secrets.compare_digest(provided, expected)
```

### 7.6 Avoid shell=True in Subprocess

Avoid `shell=True` in subprocess calls to prevent shell injection.

**Incorrect: Using shell=True**

```python
import subprocess

def list_files(directory: str) -> str:
    """List files in a directory."""
    result = subprocess.run(
        f"ls -la {directory}",  # DANGER: Shell injection!
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout
```

**Correct: Pass arguments as list**

```python
import subprocess
from pathlib import Path

def list_files(directory: str) -> str:
    """Safely list files in a directory."""
    path = Path(directory).resolve()
    result = subprocess.run(
        ["ls", "-la", str(path)],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout
```

### 7.7 Use Parameterized Database Queries

Always use parameterized queries to prevent SQL injection.

**Incorrect: String formatting in queries**

```python
def get_user(username: str) -> dict:
    """Get user by username."""
    cursor.execute(f"SELECT * FROM users WHERE name = '{username}'")
    return cursor.fetchone()
```

**Correct: Parameterized queries**

```python
def get_user(username: str) -> dict:
    """Safely get user by username."""
    cursor.execute(
        "SELECT * FROM users WHERE name = ?",
        (username,)
    )
    return cursor.fetchone()

# For named parameters
def search_users(name: str, age: int) -> list:
    cursor.execute(
        "SELECT * FROM users WHERE name = :name AND age > :age",
        {"name": name, "age": age}
    )
    return cursor.fetchall()
```

### 7.8 Store Secrets in Environment Variables

Never hardcode secrets in source code.

**Incorrect: Hardcoded secrets**

```python
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://user:password@localhost/db"
```

**Correct: Environment variables**

```python
import os

API_KEY = os.environ["API_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]

# With defaults for optional settings
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# Using pydantic-settings for validation
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    database_url: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

### 7.9 Use Proper Hashing Algorithms

Use appropriate hashing algorithms for security-sensitive operations.

**Incorrect: Weak hashing**

```python
import hashlib

def hash_password(password: str) -> str:
    """Hash a password."""
    return hashlib.md5(password.encode()).hexdigest()  # WEAK!
```

**Correct: Proper password hashing**

```python
import hashlib
import secrets

def hash_password(password: str) -> str:
    """Securely hash a password."""
    salt = secrets.token_bytes(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        iterations=100_000
    )
    return salt.hex() + key.hex()

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against stored hash."""
    salt = bytes.fromhex(stored_hash[:64])
    stored_key = stored_hash[64:]
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        iterations=100_000
    )
    return secrets.compare_digest(key.hex(), stored_key)
```

### 7.10 Prevent Directory Traversal

Validate file paths to prevent directory traversal attacks.

**Incorrect: Unvalidated file paths**

```python
def read_file(filename: str) -> str:
    """Read a file."""
    with open(f"/data/{filename}") as f:  # DANGER: ../../../etc/passwd
        return f.read()
```

**Correct: Path validation**

```python
from pathlib import Path

BASE_DIR = Path("/data").resolve()

def read_file(filename: str) -> str:
    """Safely read a file from the data directory."""
    # Resolve the full path
    file_path = (BASE_DIR / filename).resolve()

    # Ensure it's within the base directory
    if not file_path.is_relative_to(BASE_DIR):
        raise ValueError("Access denied: path traversal detected")

    with open(file_path) as f:
        return f.read()
```

---

## 8. Tooling & Configuration

**Impact: LOW**

Modern Python project configuration improves developer experience and CI/CD integration.

### 8.1 Use pyproject.toml as Single Source

Consolidate all tool configuration in `pyproject.toml`.

**Incorrect: Multiple configuration files**

```
myproject/
├── setup.py
├── setup.cfg
├── mypy.ini
├── .isort.cfg
├── .flake8
├── pytest.ini
└── requirements.txt
```

**Correct: Single pyproject.toml**

```toml
[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.25.0",
    "pydantic>=2.0.0",
]

[dependency-groups]
dev = [
    "mypy>=1.8.0",
    "ruff>=0.2.0",
    "pytest>=8.0.0",
]

[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### 8.2 Configure Ruff for Linting

Use Ruff as an all-in-one linter and formatter.

**Correct: Comprehensive ruff configuration**

```toml
[tool.ruff]
target-version = "py311"
line-length = 88
exclude = [".venv", "build", "dist"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "F",      # Pyflakes
    "I",      # isort
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "SIM",    # flake8-simplify
    "RUF",    # Ruff-specific
]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]  # Allow assert in tests

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### 8.3 Enable Strict Mypy Mode

Configure mypy in strict mode for maximum type safety.

**Correct: Strict mypy configuration**

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
show_error_codes = true
enable_error_code = ["ignore-without-code", "truthy-bool"]

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = ["third_party.*"]
ignore_missing_imports = true
```

---

## References

1. [Python Official Documentation](https://docs.python.org/3/)
2. [PEP 695 - Type Parameter Syntax](https://peps.python.org/pep-0695/)
3. [PEP 636 - Structural Pattern Matching Tutorial](https://peps.python.org/pep-0636/)
4. [Typing Best Practices](https://typing.python.org/en/latest/reference/best_practices.html)
5. [Real Python - Python 3.13 Features](https://realpython.com/python313-new-features/)
6. [Ruff Documentation](https://docs.astral.sh/ruff/)
