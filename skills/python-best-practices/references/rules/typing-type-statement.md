---
title: Use Type Statement for Aliases
impact: CRITICAL
impactDescription: Native forward references, no TypeAlias import, cleaner recursive types
tags: typing, type-alias, pep695, python312, json, recursive-types
---

## Use Type Statement for Aliases

The `type` statement eliminates the `TypeAlias` import and provides native support for forward references without string quotes. For recursive types like JSON schemas or tree structures, this removes the error-prone string-quoting requirement entirely.

**Incorrect (using TypeAlias annotation):**

```python
# PROBLEM: Requires import, forward references need string quotes (error-prone)
from typing import TypeAlias
from collections.abc import Callable

# Simple aliases still need import
UserId: TypeAlias = int
Email: TypeAlias = str

# Recursive types require string quotes - easy to forget or mistype
JsonValue: TypeAlias = "str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]"
TreeNode: TypeAlias = "dict[str, TreeNode | int]"

# Complex callback types are verbose
RequestHandler: TypeAlias = Callable[[str, dict[str, str]], tuple[int, dict[str, str]]]

# Generic aliases need separate TypeVar declarations
from typing import TypeVar
T = TypeVar("T")
Result: TypeAlias = tuple[T, str | None]  # Doesn't work as expected
```

**Correct (using type statement):**

```python
# SOLUTION: No import needed, native forward reference support
from collections.abc import Callable

# Simple aliases - clean and clear
type UserId = int
type Email = str

# Recursive types work naturally without quotes
type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]
type TreeNode = dict[str, TreeNode | int]

# Complex callback types are more readable
type RequestHandler = Callable[[str, dict[str, str]], tuple[int, dict[str, str]]]

# Generic type aliases with inline type parameters
type Result[T] = tuple[T, str | None]
type Pair[K, V] = tuple[K, V]
```

**Alternative (lazy evaluation for complex types):**

```python
# Type aliases are lazily evaluated, enabling complex cross-references
type Expression = Literal | BinaryOp | UnaryOp | Call
type Literal = int | float | str | bool
type BinaryOp = tuple[Expression, str, Expression]
type UnaryOp = tuple[str, Expression]
type Call = tuple[str, list[Expression]]

# This would have required complex forward reference handling with TypeAlias
```

**When to use:** For all type aliases in Python 3.12+ codebases. Especially valuable for recursive types (JSON, AST, tree structures) and generic aliases where forward references are needed.

**When NOT to use:** When targeting Python 3.11 or earlier. Use `TypeAlias` with string quotes for forward references in older codebases.

Reference: [PEP 695 - Type Parameter Syntax](https://peps.python.org/pep-0695/)
