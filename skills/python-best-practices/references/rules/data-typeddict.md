---
title: Use TypedDict for Dictionary Schemas
impact: MEDIUM
impactDescription: Type-safe dictionary access
tags: data, typeddict, typing, dictionary
---

## Use TypedDict for Dictionary Schemas

Use `TypedDict` for dictionaries with a fixed set of string keys.

**Incorrect (using dict without type structure):**

```python
def create_user(name: str, age: int) -> dict:
    return {"name": name, "age": age, "active": True}

def process_user(user: dict) -> str:
    # No type checking for key access
    return f"{user['name']} is {user['age']} years old"
```

**Correct (using TypedDict):**

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
    return f"{user['name']} is {user['age']} years old"
```

Reference: [typing.TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict)
