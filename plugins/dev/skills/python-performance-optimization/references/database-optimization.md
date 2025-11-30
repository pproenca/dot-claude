# Database Optimization

## Table of Contents
- [Pattern 16: Batch Database Operations](#pattern-16-batch-database-operations)
- [Pattern 17: Query Optimization](#pattern-17-query-optimization)

## Pattern 16: Batch Database Operations

```python
import sqlite3
import time

def create_db():
    """Create test database."""
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    return conn

def slow_inserts(conn, count):
    """Insert records one at a time."""
    start = time.time()
    cursor = conn.cursor()
    for i in range(count):
        cursor.execute("INSERT INTO users (name) VALUES (?)", (f"User {i}",))
        conn.commit()  # Commit each insert
    elapsed = time.time() - start
    return elapsed

def fast_inserts(conn, count):
    """Batch insert with single commit."""
    start = time.time()
    cursor = conn.cursor()
    data = [(f"User {i}",) for i in range(count)]
    cursor.executemany("INSERT INTO users (name) VALUES (?)", data)
    conn.commit()  # Single commit
    elapsed = time.time() - start
    return elapsed

# Benchmark
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
# Use indexes for frequently queried columns
"""
-- Slow: No index
SELECT * FROM users WHERE email = 'user@example.com';

-- Fast: With index
CREATE INDEX idx_users_email ON users(email);
SELECT * FROM users WHERE email = 'user@example.com';
"""

# Use query planning
import sqlite3

conn = sqlite3.connect("example.db")
cursor = conn.cursor()

# Analyze query performance
cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = ?", ("test@example.com",))
print(cursor.fetchall())

# Use SELECT only needed columns
# Slow: SELECT *
# Fast: SELECT id, name
```
