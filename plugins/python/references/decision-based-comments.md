# Decision-Based Commenting Philosophy

This guide establishes the commenting philosophy for Python code. Comments exist to prevent breaking changes by documenting decisions, not to describe what code does.

> **"Code tells you *how*. Comments tell you *why*."**
> — Guido van Rossum

## The Core Principle

Developers can read Python. Comments that describe syntax insult their intelligence. Instead, describe the **business logic** or **engineering constraint** that forced the code to be written this way.

Comments serve one purpose: **preventing future breakage** by preserving context that the code cannot express.

---

## The 3 Tenets

### 1. The "Why", Not the "What"

Document the reasoning behind decisions, not the mechanics of what the code does.

```python
# BAD: Describes what the code does
for user in users:  # Iterating through the list of users
    process(user)

# GOOD: Explains the engineering decision
# Manual iteration preserves insertion order, which the downstream
# notification service requires for correct message threading.
for user in users:
    process(user)
```

### 2. Chesterton's Fence (Preventing Breaking Changes)

Comments exist to stop future developers from "optimizing" or "fixing" code that looks suboptimal but is intentional.

```python
# BAD: States the obvious
time.sleep(2)  # Sleeping for 2 seconds

# GOOD: Prevents a future "optimization" that would break things
# The legacy auth server has a race condition if we reconnect
# immediately after disconnect. This delay prevents socket hangups.
# See: JIRA-402, fixed in auth-server v3.2+
time.sleep(2)
```

### 3. Decision Records

When choosing between approaches, document why you picked the winner. This prevents circular refactoring where someone later switches to the "obvious" approach that actually failed.

```python
# BAD: States what was chosen
parser = PythonParser()  # Use the slow parser

# GOOD: Documents the trade-off analysis
# We use the pure-Python parser instead of the C extension because
# the C extension causes segfaults in Alpine Linux containers.
# Benchmark: 200ms vs 50ms per file, acceptable for our batch size.
parser = PythonParser()
```

---

## Decision Table: When to Comment

| Scenario | Comment? | Rationale |
|----------|----------|-----------|
| Standard Python idiom | DELETE | Trust developers to read Python |
| Obvious variable names | DELETE | `user_count = len(users)` is self-documenting |
| Type information | DELETE | Use type hints instead |
| Weird but intentional code | REQUIRED | Prevent "fixes" that break things |
| Performance trade-off | REQUIRED | Document why slower/faster approach was chosen |
| Business rule embedded in code | REQUIRED | Logic may outlive tribal knowledge |
| Workaround for external bug | REQUIRED | Include ticket/version for future removal |
| Magic numbers | REQUIRED | Explain derivation or source |
| Empty except/pass blocks | REQUIRED | Explain why silence is intentional |

---

## Anti-Patterns to Avoid

### Translation Comments

Comments that restate the code in English provide no value.

```python
# DELETE THESE:
i += 1  # Increment i by 1
users = []  # Initialize empty list
if x > 0:  # Check if x is greater than zero
```

### Type Comments

Modern Python has type hints. Remove comments that duplicate type information.

```python
# BAD: Type as comment
user = get_user()  # Returns a User object

# GOOD: Type hint
def get_user() -> User:
    ...
```

### Changelog Comments

Version control tracks changes. Comments should not.

```python
# BAD: Changelog in code
# Modified 2024-01-15: Added retry logic
# Modified 2024-02-01: Increased timeout

# GOOD: Git commit message handles this
```

### Obvious Function Docstrings

Docstrings that repeat the function name waste screen space.

```python
# BAD: Repeats the obvious
def calculate_total(items: list[Item]) -> float:
    """Calculates the total of items."""

# GOOD: Explains non-obvious behavior
def calculate_total(items: list[Item]) -> float:
    """
    Sum item prices with quantity discounts applied.

    Items with quantity > 10 receive 15% discount per company policy.
    Returns 0.0 for empty lists rather than raising.
    """
```

---

## Python-Specific Patterns

### Module-Level Comments

Use module docstrings for architectural context, not file listings.

```python
# BAD: Lists contents
"""
This module contains User, UserManager, and UserValidator classes.
"""

# GOOD: Explains architectural decisions
"""
User domain models with validation.

Separated from persistence layer to allow testing without database.
UserValidator uses the company's standard email regex (RFC 5321 subset)
rather than strict RFC 5322 to match legacy system behavior.
"""
```

### Inline Comments for Non-Obvious Code

Place decision comments on the line before, not inline.

```python
# GOOD: Comment before explains the decision
# Using bitwise AND for performance in hot loop (3x faster than modulo)
if n & 1:
    process_odd(n)

# ACCEPTABLE: Short clarification inline
timeout = 45  # Max Lambda execution (60s) minus cleanup buffer
```

### TODO/FIXME/HACK Markers

Use standard markers with context and ownership.

```python
# GOOD: Actionable with context
# TODO(team-auth): Remove after auth-server 3.2 rollout (Q2 2025)
# HACK: Workaround for upstream bug github.com/lib/issue/123
# FIXME: Race condition under high load, needs mutex
```

---

## Transforming Existing Comments

When reviewing code, apply this filter:

| Original Comment | Problem | Rewritten |
|-----------------|---------|-----------|
| `# Loop through items` | Translation | DELETE |
| `# Returns None` | Type info | Use `-> None` type hint |
| `# Slow but works` | Missing context | `# O(n²) acceptable here: max 50 items per API contract` |
| `# Don't change this` | Missing WHY | `# Order matters: auth must complete before session init` |
| `# Magic number` | Vague | `# 86400 = seconds per day, used for cache TTL` |

---

## Integration with Code Review

When reviewing Python code, verify:

1. **No translation comments** - Delete comments that restate the code
2. **Decision documentation** - Non-obvious code has context
3. **Workarounds are tracked** - External bugs reference tickets
4. **Magic values explained** - Numbers have derivation comments
5. **Empty blocks justified** - `pass` and bare `except` have rationale

---

## Summary

Write comments that answer: *"What would prevent a future developer from breaking this?"*

- **Delete** comments that describe WHAT the code does
- **Keep** comments that explain WHY the code exists this way
- **Add** comments that prevent future "optimizations" from breaking things
