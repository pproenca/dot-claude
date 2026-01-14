---
title: Use Type Statement for Aliases
impact: CRITICAL
impactDescription: Native forward reference support
tags: typing, type-alias, pep695, python312
---

## Use Type Statement for Aliases

Python 3.12+ introduces the `type` statement for type aliases.

**Incorrect (using TypeAlias annotation):**

```python
from typing import TypeAlias

UserId: TypeAlias = int
TreeNode: TypeAlias = "dict[str, TreeNode | int]"
```

**Correct (using type statement):**

```python
type UserId = int
type TreeNode = dict[str, TreeNode | int]  # No quotes needed
```

Reference: [PEP 695 - Type Parameter Syntax](https://peps.python.org/pep-0695/)
