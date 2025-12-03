# Python Version Features Reference

Use this reference to adapt code patterns to the target Python version.

## Version Detection

Check these files in order:

1. `.python-version` (uv's pin file)
2. `pyproject.toml` → `requires-python`
3. `.claude/python-version` (stored preference)

## Python 3.14 (2025)

**Status:** Beta, nogil improvements

### Key Features

- **Improved free-threading performance** (PEP 703 Phase II)
- **Deferred evaluation of annotations** (PEP 649)
- **Template strings** (PEP 750, t-strings)

```python
# Template strings (3.14+)
from string import Template
name = "world"
t = t"Hello {name}"  # template string, not evaluated immediately

# Deferred annotations - no runtime cost
def process(data: list[ComplexType]) -> Result:
    ...  # ComplexType not evaluated unless inspected
```

## Python 3.13 (October 2024)

**Status:** Current stable with experimental features

### Key Features

- **Free-threaded build** (`--disable-gil`, experimental)
- **Experimental JIT compiler**
- **Improved error messages**
- **Deprecation of `getopt` module**

```python
# Check if running nogil build
import sys
if hasattr(sys, '_is_gil_enabled'):
    print(f"GIL enabled: {sys._is_gil_enabled()}")

# Use threading for CPU-bound work in nogil builds
import threading

def cpu_intensive(data):
    # In nogil Python, threads run in true parallel
    threads = [threading.Thread(target=process, args=(chunk,))
               for chunk in split_data(data)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
```

## Python 3.12 (October 2023)

**Status:** Recommended for new projects

### Key Features

- **Type parameter syntax** (PEP 695)
- **F-string improvements** (nested quotes, comments)
- **Per-interpreter GIL** (preparation for nogil)
- **Improved error messages**

```python
# Type parameter syntax (3.12+)
type Point = tuple[float, float]
type Vector[T] = list[T]

def first[T](items: list[T]) -> T:
    return items[0]

class Stack[T]:
    def push(self, item: T) -> None: ...
    def pop(self) -> T: ...

# Legacy (< 3.12)
from typing import TypeVar, Generic
T = TypeVar('T')
class Stack(Generic[T]):
    def push(self, item: T) -> None: ...

# F-string improvements (3.12+)
f"User: {user["name"]}"  # nested quotes allowed
f"{value:.2f  # with comment
}"  # multiline with comments
```

## Python 3.11 (October 2022)

**Status:** Widely deployed, safe default

### Key Features

- **Exception groups and `except*`** (PEP 654)
- **`tomllib` in stdlib** (TOML parsing)
- **Self type** (PEP 673)
- **10-60% faster than 3.10**
- **Fine-grained error locations**

```python
# Exception groups (3.11+)
async def fetch_all(urls):
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(url)) for url in urls]
    # All exceptions collected, raised as ExceptionGroup

try:
    await fetch_all(urls)
except* ConnectionError as eg:
    for exc in eg.exceptions:
        log_connection_error(exc)
except* TimeoutError as eg:
    for exc in eg.exceptions:
        log_timeout(exc)

# tomllib (3.11+, read-only)
import tomllib
with open("pyproject.toml", "rb") as f:
    config = tomllib.load(f)

# Self type (3.11+)
from typing import Self

class Builder:
    def with_name(self, name: str) -> Self:
        self.name = name
        return self
```

## Python 3.10 (October 2021)

**Status:** Minimum for modern type hints

### Key Features

- **Structural pattern matching** (`match`/`case`)
- **Union types with `|`** (PEP 604)
- **Parenthesized context managers**
- **Parameter specification variables**

```python
# Pattern matching (3.10+)
match command:
    case ["quit"]:
        return quit()
    case ["load", filename]:
        return load(filename)
    case ["save", filename] if filename.endswith('.json'):
        return save_json(filename)
    case _:
        return unknown_command()

# Union types (3.10+)
def process(value: int | str | None) -> str:
    ...

# Legacy (< 3.10)
from typing import Union, Optional
def process(value: Union[int, str, None]) -> str:
    ...

# Parenthesized context managers (3.10+)
with (
    open("input.txt") as infile,
    open("output.txt", "w") as outfile,
):
    outfile.write(infile.read())
```

## Compatibility Patterns

### Type Hints Compatibility

```python
from __future__ import annotations  # Defer evaluation (3.7+)
import sys

if sys.version_info >= (3, 10):
    # Modern syntax
    def func(x: int | None) -> list[str]: ...
else:
    # Legacy imports
    from typing import Optional, List
    def func(x: Optional[int]) -> List[str]: ...
```

### Feature Detection

```python
import sys

# Check Python version
if sys.version_info >= (3, 13):
    # Use free-threaded features
    pass

# Check for optional features
if hasattr(sys, '_is_gil_enabled'):
    # Running on nogil-capable build
    pass
```

## Version Recommendations

| Project Type | Minimum Version | Recommended |
|--------------|-----------------|-------------|
| New library | 3.10 | 3.12 |
| New application | 3.11 | 3.12 |
| Performance-critical | 3.11 | 3.13 (with JIT) |
| Parallel CPU-bound | 3.13 | 3.14 (nogil) |
| Legacy maintenance | 3.8 | 3.10 |
