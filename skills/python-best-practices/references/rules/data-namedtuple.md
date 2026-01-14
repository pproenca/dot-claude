---
title: Use NamedTuple Over Plain Tuples
impact: MEDIUM
impactDescription: Self-documenting code
tags: data, namedtuple, tuple, typing
---

## Use NamedTuple Over Plain Tuples

Use `NamedTuple` for tuples with named fields.

**Incorrect (plain tuples with unclear indices):**

```python
def get_user_info() -> tuple[str, int, bool]:
    return ("Alice", 30, True)

info = get_user_info()
name = info[0]  # Unclear what index 0 means
age = info[1]
```

**Correct (using NamedTuple):**

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

Reference: [typing.NamedTuple](https://docs.python.org/3/library/typing.html#typing.NamedTuple)
