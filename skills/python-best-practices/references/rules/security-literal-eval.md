---
title: Use literal_eval for Safe Parsing
impact: LOW-MEDIUM
impactDescription: Safe Python literal parsing
tags: security, literal-eval, ast, parsing
---

## Use literal_eval for Safe Parsing

Use `ast.literal_eval()` for parsing Python literals from strings.

**Incorrect (using eval for literal parsing):**

```python
def parse_config(value: str) -> any:
    return eval(value)  # DANGER!
```

**Correct (using ast.literal_eval):**

```python
import ast

def parse_config(value: str) -> any:
    return ast.literal_eval(value)

# Only supports: strings, bytes, numbers, tuples,
# lists, dicts, sets, booleans, None
parse_config("[1, 2, 3]")  # [1, 2, 3]
parse_config("{'key': 'value'}")  # {'key': 'value'}
# parse_config("__import__('os')")  # ValueError
```

Reference: [ast.literal_eval](https://docs.python.org/3/library/ast.html#ast.literal_eval)
