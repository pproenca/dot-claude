---
title: Use F-String Debug Specifier
impact: MEDIUM-HIGH
impactDescription: Faster debugging output
tags: modern, fstring, debug, python38
---

## Use F-String Debug Specifier

Use the `=` specifier in f-strings for quick debugging output.

**Incorrect (manually formatting debug output):**

```python
def debug_calculation(x: int, y: int) -> int:
    result = x * y + 10
    print(f"x={x}, y={y}, result={result}")
    
    intermediate = x ** 2
    print(f"intermediate={intermediate}")
    
    return result
```

**Correct (using f-string = specifier):**

```python
def debug_calculation(x: int, y: int) -> int:
    result = x * y + 10
    print(f"{x=}, {y=}, {result=}")  # Output: x=5, y=3, result=25
    
    intermediate = x ** 2
    print(f"{intermediate=}")  # Output: intermediate=25
    
    # Also works with expressions
    print(f"{x + y=}")  # Output: x + y=8
    
    return result
```

Reference: [f-strings](https://docs.python.org/3/reference/lexical_analysis.html#f-strings)
