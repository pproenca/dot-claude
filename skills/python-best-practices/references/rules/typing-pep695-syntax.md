---
title: Use PEP 695 Type Parameter Syntax
impact: CRITICAL
impactDescription: Eliminates TypeVar boilerplate
tags: typing, generics, typevar, pep695, python312
---

## Use PEP 695 Type Parameter Syntax

Python 3.12+ introduces a new syntax for generic functions and classes that eliminates the need for `TypeVar` declarations.

**Incorrect (using TypeVar pre-3.12 style):**

```python
from typing import TypeVar, Sequence

T = TypeVar("T")

def first(items: Sequence[T]) -> T:
    return items[0]

class Stack(list[T]):
    def push(self, item: T) -> None:
        self.append(item)
```

**Correct (using PEP 695 syntax):**

```python
from collections.abc import Sequence

def first[T](items: Sequence[T]) -> T:
    return items[0]

class Stack[T](list[T]):
    def push(self, item: T) -> None:
        self.append(item)
```

Reference: [PEP 695 - Type Parameter Syntax](https://peps.python.org/pep-0695/)
