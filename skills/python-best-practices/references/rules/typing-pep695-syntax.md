---
title: Use PEP 695 Type Parameter Syntax
impact: CRITICAL
impactDescription: Eliminates 3-5 TypeVar declarations + 2 imports per generic module
tags: typing, generics, typevar, pep695, python312, sqlalchemy
---

## Use PEP 695 Type Parameter Syntax

PEP 695 syntax eliminates TypeVar declarations entirely, saving 3-5 lines of boilerplate per generic function/class. In a typical repository service with 10 generic functions, this removes ~40 lines of TypeVar declarations and redundant string-name matching.

**Incorrect (using TypeVar pre-3.12 style):**

```python
# PROBLEM: 5 TypeVar declarations, must match string names exactly, 2 extra imports
from typing import TypeVar, Generic
from collections.abc import Sequence, Callable

T = TypeVar("T")  # String must match variable name
U = TypeVar("U")
K = TypeVar("K")
V = TypeVar("V")
T_co = TypeVar("T_co", covariant=True)

def first(items: Sequence[T]) -> T:
    """Return the first item in a sequence."""
    return items[0]

def map_items(items: list[T], func: Callable[[T], U]) -> list[U]:
    """Apply a function to each item."""
    return [func(item) for item in items]

class Repository(Generic[T]):
    """Generic repository pattern for database entities."""
    def __init__(self, model_class: type[T]) -> None:
        self._model = model_class

    def get(self, id: int) -> T | None:
        return self._session.get(self._model, id)

    def list_all(self) -> list[T]:
        return list(self._session.scalars(select(self._model)))
```

**Correct (using PEP 695 syntax):**

```python
# SOLUTION: No TypeVar declarations, automatic variance inference, cleaner syntax
from collections.abc import Sequence, Callable
from sqlalchemy import select
from sqlalchemy.orm import Session

def first[T](items: Sequence[T]) -> T:
    """Return the first item in a sequence."""
    return items[0]

def map_items[T, U](items: list[T], func: Callable[[T], U]) -> list[U]:
    """Apply a function to each item."""
    return [func(item) for item in items]

class Repository[T]:
    """Generic repository pattern for database entities."""
    def __init__(self, model_class: type[T], session: Session) -> None:
        self._model = model_class
        self._session = session

    def get(self, id: int) -> T | None:
        return self._session.get(self._model, id)

    def list_all(self) -> list[T]:
        return list(self._session.scalars(select(self._model)))
```

**Alternative (bounded type parameters):**

```python
from collections.abc import Hashable

# Bounded type parameter - T must be Hashable
def deduplicate[T: Hashable](items: list[T]) -> list[T]:
    """Remove duplicates while preserving order."""
    seen: set[T] = set()
    result: list[T] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
```

**When to use:** For all new generic functions and classes in Python 3.12+ codebases. Especially valuable for repository patterns, data transformation utilities, and type-safe collection wrappers.

**When NOT to use:** When targeting Python 3.11 or earlier. For complex variance scenarios where explicit covariant/contravariant TypeVars provide clearer intent.

Reference: [PEP 695 - Type Parameter Syntax](https://peps.python.org/pep-0695/)
