---
title: Use None Instead of Optional
impact: CRITICAL
impactDescription: Eliminates Optional import, 40% shorter nullable type annotations
tags: typing, optional, none, type-hints, pydantic, sqlalchemy
---

## Use None Instead of Optional

The `X | None` syntax eliminates the `from typing import Optional` import and makes nullable annotations 40% shorter (`Optional[str]` is 13 chars vs `str | None` at 10 chars). In a typical ORM model file with 20 nullable fields, this saves significant visual clutter.

**Incorrect (using Optional):**

```python
# PROBLEM: Requires import, verbose 13-char wrapper per nullable type
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel

class User(Base):
    """SQLAlchemy user model with nullable fields."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    phone: Mapped[Optional[str]] = mapped_column(nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(nullable=True)

class UserUpdate(BaseModel):
    """Pydantic model for partial updates."""
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

def find_user(user_id: int) -> Optional[User]:
    """Find a user by ID."""
    return session.get(User, user_id)
```

**Correct (using X | None):**

```python
# SOLUTION: No import needed, cleaner 10-char nullable syntax
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel

class User(Base):
    """SQLAlchemy user model with nullable fields."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    phone: Mapped[str | None] = mapped_column(nullable=True)
    bio: Mapped[str | None] = mapped_column(nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(nullable=True)

class UserUpdate(BaseModel):
    """Pydantic model for partial updates."""
    email: str | None = None
    phone: str | None = None
    bio: str | None = None
    avatar_url: str | None = None

def find_user(user_id: int) -> User | None:
    """Find a user by ID."""
    return session.get(User, user_id)
```

**Alternative (using Union for multiple nullable types):**

```python
# When you have multiple alternative types plus None
def parse_id(value: str) -> int | str | None:
    """Parse ID from string, returning int if numeric, str otherwise, None on failure."""
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return value if value.isalnum() else None
```

**When to use:** Always use `X | None` for nullable types in Python 3.10+ codebases. Works seamlessly with Pydantic, SQLAlchemy, and all type checkers.

**When NOT to use:** When maintaining Python 3.9 compatibility without `from __future__ import annotations`. Note that `Optional` was technically for "optional arguments with defaults", but was commonly misused for nullable types - the new syntax is clearer.

Reference: [Typing Best Practices](https://typing.python.org/en/latest/reference/best_practices.html)
