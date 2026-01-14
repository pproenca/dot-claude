---
title: Use Context Managers for Cleanup
impact: MEDIUM
impactDescription: Guarantees resource cleanup
tags: error, context-manager, with, resources
---

## Use Context Managers for Cleanup

Use context managers to ensure resources are properly cleaned up.

**Incorrect (manual resource management):**

```python
def process_file(path: str) -> list[str]:
    f = open(path)
    try:
        lines = f.readlines()
        return [line.strip() for line in lines]
    finally:
        f.close()

def use_database():
    conn = create_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()
        finally:
            cursor.close()
    finally:
        conn.close()
```

**Correct (using context managers):**

```python
def process_file(path: str) -> list[str]:
    with open(path) as f:
        return [line.strip() for line in f]

def use_database():
    with create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()
```

Reference: [Context Managers](https://docs.python.org/3/reference/datamodel.html#context-managers)
