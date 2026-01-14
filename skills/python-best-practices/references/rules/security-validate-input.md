---
title: Validate External Input
impact: LOW-MEDIUM
impactDescription: Prevents injection attacks
tags: security, validation, input, pydantic
---

## Validate External Input

Always validate and sanitize input from external sources.

**Incorrect (trusting external input):**

```python
def get_user(user_id: str) -> User:
    return database.query(f"SELECT * FROM users WHERE id = {user_id}")
```

**Correct (validating input):**

```python
from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    user_id: int = Field(gt=0)

def get_user(request: UserRequest) -> User:
    return database.query(
        "SELECT * FROM users WHERE id = ?",
        (request.user_id,)
    )
```

Reference: [Pydantic](https://docs.pydantic.dev/)
