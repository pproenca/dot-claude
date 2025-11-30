# Database Optimization

## Table of Contents
- [Pattern 16: Batch Database Operations](#pattern-16-batch-database-operations)
- [Pattern 17: Query Optimization](#pattern-17-query-optimization)

## Pattern 16: Batch Database Operations

```python
import sqlite3
import time

def create_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    return conn

def slow_inserts(conn, count):
    """N commits = N disk syncs, O(n) I/O operations."""
    start = time.time()
    cursor = conn.cursor()
    for i in range(count):
        cursor.execute("INSERT INTO users (name) VALUES (?)", (f"User {i}",))
        conn.commit()
    elapsed = time.time() - start
    return elapsed

def fast_inserts(conn, count):
    """Single commit = single disk sync, O(1) I/O operations."""
    start = time.time()
    cursor = conn.cursor()
    data = [(f"User {i}",) for i in range(count)]
    cursor.executemany("INSERT INTO users (name) VALUES (?)", data)
    conn.commit()
    elapsed = time.time() - start
    return elapsed

conn1 = create_db()
slow_time = slow_inserts(conn1, 1000)

conn2 = create_db()
fast_time = fast_inserts(conn2, 1000)

print(f"Individual inserts: {slow_time:.4f}s")
print(f"Batch insert: {fast_time:.4f}s")
print(f"Speedup: {slow_time/fast_time:.2f}x")
```

## Pattern 17: Query Optimization

```python
"""
-- O(n) full table scan without index
SELECT * FROM users WHERE email = 'user@example.com';

-- O(log n) B-tree lookup with index
CREATE INDEX idx_users_email ON users(email);
SELECT * FROM users WHERE email = 'user@example.com';
"""

import sqlite3

conn = sqlite3.connect("example.db")
cursor = conn.cursor()

cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = ?", ("test@example.com",))
print(cursor.fetchall())
```
