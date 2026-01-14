---
title: Use Generators for Large Datasets
impact: HIGH
impactDescription: O(1) memory instead of O(n)
tags: perf, generators, memory, iteration
---

## Use Generators for Large Datasets

Use generator expressions instead of list comprehensions when iterating once over large datasets.

**Incorrect (creating large intermediate lists):**

```python
def process_large_file(filename: str) -> int:
    with open(filename) as f:
        # Creates entire list in memory!
        lines = [line.strip() for line in f]
        valid_lines = [line for line in lines if is_valid(line)]
        return len(valid_lines)

def get_squares_sum(n: int) -> int:
    # Creates list of n items!
    squares = [x ** 2 for x in range(n)]
    return sum(squares)
```

**Correct (using generators):**

```python
def process_large_file(filename: str) -> int:
    with open(filename) as f:
        # Generator - processes one line at a time
        return sum(1 for line in f if is_valid(line.strip()))

def get_squares_sum(n: int) -> int:
    # Generator expression - no list created
    return sum(x ** 2 for x in range(n))
```

Note: Generators are single-use; create a new one to iterate again.

Reference: [Generator expressions](https://docs.python.org/3/reference/expressions.html#generator-expressions)
