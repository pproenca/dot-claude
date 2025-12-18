# Pythonic Style Guide

> "Code is read far more often than it is written." - Guido Van Rossum, PEP 8

**Authoritative Sources:**

- [PEP 8](https://peps.python.org/pep-0008/) - Style Guide for Python Code
- [PEP 703](https://peps.python.org/pep-0703/) - Making the GIL Optional (Sam Gross)

## Guido's Core Philosophy

**The Overriding Principle:** Readability counts.

### Consistency Hierarchy

1. Within a function/module (most important)
2. Within a project
3. With PEP 8 (least important)

Know when to break rules—rigid adherence creates worse code than thoughtful deviation.

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| modules/packages | `lowercase_underscores` | `my_module` |
| Classes | `CapWords` | `MyClass` |
| functions/variables | `lowercase_underscores` | `get_user` |
| Constants | `ALL_CAPS` | `MAX_RETRIES` |
| Type variables | Short `CapWords` | `T`, `AnyStr` |

**Never use:** `l`, `O`, or `I` as single-character names (indistinguishable from numerals).

### Underscore Semantics

- `_single_leading`: "internal use" signal
- `__double_leading`: name mangling for subclass protection
- `single_trailing_`: avoid keyword conflicts (`class_`)

### Expression Clarity

```python
# None comparisons
if x is None:     # correct
if x is not None: # correct
if x == None:     # wrong

# Type checking
if isinstance(x, int):  # correct
if type(x) == int:      # wrong

# Boolean testing
if x:           # correct
if x == True:   # wrong
if x is True:   # only for sentinel comparisons

# Lambda vs def
def double(x): return x * 2  # correct
double = lambda x: x * 2     # wrong - use def for named functions
```

### Comments

> "Code tells you *how*. Comments tell you *why*."

For the complete philosophy, see [decision-based-comments.md](./decision-based-comments.md).

**Quick Reference:**

| Scenario | Action |
|----------|--------|
| Standard Python idiom | DELETE comment |
| Type information | Use type hints instead |
| Non-obvious/intentional code | REQUIRED - explain WHY |
| Workaround for external bug | REQUIRED - include ticket |

```python
# BAD: Translation comment (describes WHAT)
i += 1  # Increment i by 1

# GOOD: Decision comment (explains WHY)
# Skip the header row which contains column names, not data
i += 1

# BAD: Missing context for weird code
time.sleep(2)

# GOOD: Prevents future "optimization" that would break things
# Legacy auth server race condition requires delay before reconnect.
# See JIRA-402, fixed in auth-server v3.2+
time.sleep(2)
```

## Modern Type Hints (3.10+)

```python
# Modern (3.10+)
def process(items: list[str]) -> dict[str, int]: ...
def get_user(id: int) -> User | None: ...

# Legacy (avoid unless targeting < 3.10)
from typing import List, Dict, Optional
def process(items: List[str]) -> Dict[str, int]: ...
def get_user(id: int) -> Optional[User]: ...
```

## Data Container Selection

| Use Case | Container | Example |
|----------|-----------|---------|
| Simple data holder | `dataclass` | Internal DTOs |
| External data validation | `Pydantic` | API requests/responses |
| Dict schema (no validation) | `TypedDict` | JSON structure hints |
| Immutable record | `NamedTuple` | Database rows |

```python
from dataclasses import dataclass
from pydantic import BaseModel
from typing import TypedDict, NamedTuple

@dataclass
class Config:
    host: str
    port: int = 8080

class UserRequest(BaseModel):
    email: str
    age: int

class UserDict(TypedDict):
    id: int
    name: str

class Point(NamedTuple):
    x: float
    y: float
```

## Sam Gross's Free-Threaded Python (3.13+)

### Concurrency Pattern Selection

| Workload | GIL Python | nogil Python (3.13+) |
|----------|------------|----------------------|
| I/O-bound | async/await | async/await |
| CPU-bound | multiprocessing | threading (new option) |
| Mixed | async + ProcessPoolExecutor | async + ThreadPoolExecutor |

### Thread-Safe Design

When targeting free-threaded Python:

```python
# Thread-safe: immutable data
from dataclasses import dataclass, field
from typing import FrozenSet

@dataclass(frozen=True)
class Config:
    hosts: tuple[str, ...]
    tags: FrozenSet[str] = field(default_factory=frozenset)

# Thread-safe: explicit synchronization
import threading

class Counter:
    def __init__(self) -> None:
        self._value = 0
        self._lock = threading.Lock()

    def increment(self) -> int:
        with self._lock:
            self._value += 1
            return self._value
```

## 2024/2025 Ecosystem

| Task | Tool | Notes |
|------|------|-------|
| Package management | `uv` | 10-100x faster than pip |
| Linting/formatting | `ruff` | Replaces black, isort, flake8 |
| Type checking | `mypy` or `pyright` | Use strict mode |
| Testing | `pytest` | Not unittest |
| Project config | `pyproject.toml` | Not setup.py |

## Anti-Patterns

### Import Violations

```python
# Wrong
from os import *  # wildcard import

# Correct
from os import path, getcwd
```

### Exception Handling

```python
# Wrong
try:
    risky_operation()
except:  # bare except
    pass

# Correct
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

### Mutable Default Arguments

```python
# Wrong - shared mutable default
def append_to(item, target=[]):
    target.append(item)
    return target

# Correct - None sentinel
def append_to(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

### String Building

```python
# Wrong - O(n²) concatenation
result = ""
for item in items:
    result += str(item)

# Correct - O(n) join
result = "".join(str(item) for item in items)
```
