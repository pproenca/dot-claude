---
title: Use Built-in Generics
impact: CRITICAL
impactDescription: Eliminates 4-6 typing imports per module, 20% shorter annotations
tags: typing, generics, list, dict, set, tuple, collections-abc, fastapi
---

## Use Built-in Generics

Built-in generics eliminate 4-6 imports from `typing` per module and make annotations 20% shorter. A typical FastAPI application with 50 endpoint functions saves ~200 import statements across the codebase.

**Incorrect (importing from typing):**

```python
# PROBLEM: 6 imports from typing, uppercase names feel like Java
from typing import List, Dict, Set, Tuple, Type, FrozenSet

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class UserResponse(BaseModel):
    tags: List[str]
    metadata: Dict[str, str]

@router.get("/users")
async def list_users() -> List[UserResponse]:
    """List all users."""
    return await fetch_users()

@router.get("/stats")
async def get_stats() -> Dict[str, int]:
    """Get usage statistics."""
    return {"active": 100, "total": 500}

def get_unique_tags(users: List[UserResponse]) -> Set[str]:
    """Extract unique tags from users."""
    return {tag for user in users for tag in user.tags}

def get_coordinates() -> Tuple[float, float, float]:
    """Return 3D coordinates."""
    return (1.0, 2.0, 3.0)
```

**Correct (using built-in generics):**

```python
# SOLUTION: No typing imports needed, lowercase matches Python builtins
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class UserResponse(BaseModel):
    tags: list[str]
    metadata: dict[str, str]

@router.get("/users")
async def list_users() -> list[UserResponse]:
    """List all users."""
    return await fetch_users()

@router.get("/stats")
async def get_stats() -> dict[str, int]:
    """Get usage statistics."""
    return {"active": 100, "total": 500}

def get_unique_tags(users: list[UserResponse]) -> set[str]:
    """Extract unique tags from users."""
    return {tag for user in users for tag in user.tags}

def get_coordinates() -> tuple[float, float, float]:
    """Return 3D coordinates."""
    return (1.0, 2.0, 3.0)
```

**Alternative (collections.abc for abstract types):**

```python
# For abstract types, use collections.abc instead of typing
from collections.abc import Sequence, Mapping, Iterable, Iterator, Callable

def process_any_sequence(items: Sequence[str]) -> int:
    """Works with list, tuple, or any sequence type."""
    return len(items)

def process_any_mapping(data: Mapping[str, int]) -> list[str]:
    """Works with dict, OrderedDict, or any mapping type."""
    return list(data.keys())
```

**When to use:** Always use lowercase built-in generics in Python 3.9+ codebases. Use `collections.abc` for abstract types when you want to accept multiple concrete implementations.

**When NOT to use:** For Python 3.8 and earlier, you must use typing module imports. Use `from __future__ import annotations` to enable PEP 585 syntax in 3.7-3.9.

Reference: [Typing Best Practices](https://typing.python.org/en/latest/reference/best_practices.html)
