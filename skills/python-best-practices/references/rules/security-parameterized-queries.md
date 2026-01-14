---
title: Use Parameterized Database Queries
impact: LOW-MEDIUM
impactDescription: Prevents SQL injection
tags: security, sql, injection, database
---

## Use Parameterized Database Queries

Always use parameterized queries to prevent SQL injection.

**Incorrect (string formatting in queries):**

```python
def get_user(username: str) -> dict:
    cursor.execute(f"SELECT * FROM users WHERE name = '{username}'")
    return cursor.fetchone()
```

**Correct (parameterized queries):**

```python
def get_user(username: str) -> dict:
    cursor.execute(
        "SELECT * FROM users WHERE name = ?",
        (username,)
    )
    return cursor.fetchone()

# For named parameters
def search_users(name: str, age: int) -> list:
    cursor.execute(
        "SELECT * FROM users WHERE name = :name AND age > :age",
        {"name": name, "age": age}
    )
    return cursor.fetchall()
```

Reference: [sqlite3 security](https://docs.python.org/3/library/sqlite3.html)
