---
title: Never Use eval with Untrusted Input
impact: LOW-MEDIUM
impactDescription: Prevents code injection
tags: security, eval, exec, injection
---

## Never Use eval with Untrusted Input

Never use `eval()`, `exec()`, or `compile()` with untrusted input.

**Incorrect (using eval with user input):**

```python
def calculate(expression: str) -> float:
    return eval(expression)  # DANGER: Arbitrary code execution!

# Attacker input: "__import__('os').system('rm -rf /')"
```

**Correct (safe alternatives):**

```python
import operator
import ast

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

def safe_calculate(expression: str) -> float:
    tree = ast.parse(expression, mode='eval')
    return _eval_node(tree.body)

def _eval_node(node):
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return OPERATORS[type(node.op)](left, right)
    raise ValueError(f"Unsupported: {type(node)}")
```

Reference: [Security Considerations](https://docs.python.org/3/library/security_warnings.html)
