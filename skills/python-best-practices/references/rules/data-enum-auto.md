---
title: Use Enum with Auto
impact: MEDIUM
impactDescription: Type-safe constants
tags: data, enum, auto, constants
---

## Use Enum with Auto

Use `Enum` with `auto()` for enumerated constants.

**Incorrect (using string/int constants):**

```python
STATUS_PENDING = "pending"
STATUS_ACTIVE = "active"
STATUS_COMPLETED = "completed"

def get_status(order) -> str:
    if order.shipped:
        return STATUS_COMPLETED
    return STATUS_PENDING
```

**Correct (using Enum with auto):**

```python
from enum import Enum, auto, StrEnum

class Status(Enum):
    PENDING = auto()
    ACTIVE = auto()
    COMPLETED = auto()

# For string values, use StrEnum (3.11+)
class Status(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"

def get_status(order) -> Status:
    if order.shipped:
        return Status.COMPLETED
    return Status.PENDING
```

Reference: [enum module](https://docs.python.org/3/library/enum.html)
