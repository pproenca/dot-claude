---
title: Use Self Type for Method Chaining
impact: MEDIUM
impactDescription: Correct typing for fluent interfaces
tags: error, self-type, typing, method-chaining, python311
---

## Use Self Type for Method Chaining

Use `Self` type for methods that return the instance itself (Python 3.11+).

**Incorrect (using class name or Any):**

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

**Correct (using Self type):**

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

Reference: [typing.Self](https://docs.python.org/3/library/typing.html#typing.Self)
