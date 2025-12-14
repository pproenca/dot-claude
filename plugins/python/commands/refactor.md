---
name: refactor
description: Modernize a Python file with ruff, mypy, and expert review for Python 3.12+ patterns
argument-hint: <file_path>
allowed-tools: Bash(ruff:*), Bash(mypy:*), Bash(uv:*), Bash(python:*), Read, Edit, Task, Glob
---

# Refactor Python File

Modernize a Python file using automated tools and expert review.

## Workflow

### Step 1: Locate Target File

If `$ARGUMENTS` is provided, use that file path. Otherwise:

1. Use Glob to find Python files in the current directory
2. Ask the user which file to refactor using AskUserQuestion

### Step 2: Run Analysis (Parallel)

Run these checks concurrently:

1. **Ruff Analysis**
   ```bash
   uv run ruff check <file> --output-format=json
   uv run ruff format <file> --check --diff
   ```

2. **Mypy Type Check**
   ```bash
   uv run mypy <file> --show-error-codes
   ```

3. **Python Expert Task**
   Use the Task tool with `python:python-expert` agent to analyze:
   - Modern Python 3.12+ patterns that could be applied
   - Pythonic idioms that could improve readability
   - Type hint improvements

4. **Comment Review**
   Check comments against `references/decision-based-comments.md`:
   - Flag translation comments (describe WHAT) for removal
   - Verify non-obvious code has decision comments (explain WHY)
   - Ensure workarounds reference external tickets

### Step 3: Present Findings

Consolidate all findings and present to user:

```
## Refactoring Analysis for <file>

### Critical Issues (ruff errors, type errors)
- Issue 1
- Issue 2

### Style Improvements (ruff suggestions)
- Suggestion 1
- Suggestion 2

### Modernization Opportunities (3.12+ patterns)
- Pattern 1
- Pattern 2

### Comment Quality
- Comments to remove: X
- Missing decision comments: Y
```

Ask user: "Apply all changes, critical fixes only, or cancel?"

### Step 4: Apply Changes

Based on user choice:

**All changes:**
1. Apply ruff fixes: `uv run ruff check <file> --fix`
2. Apply ruff format: `uv run ruff format <file>`
3. Apply comment improvements via Edit tool
4. Apply modernization patterns via Edit tool

**Critical only:**
1. Apply only ruff error fixes (not style suggestions)
2. Apply type fixes

### Step 5: Verify

After applying changes:

1. Run syntax check: `python -m py_compile <file>`
2. Run ruff again to confirm no new issues
3. Run mypy again to confirm type improvements

Report:
```
## Refactoring Complete

Before: X issues
After: Y issues

Changes applied:
- Ruff fixes: N
- Format changes: Y/N
- Comment updates: N
- Pattern modernizations: N
```

## Comment Philosophy

When reviewing comments, apply Guido's philosophy:

> "Code tells you *how*. Comments tell you *why*."

**Remove:**
- `i += 1  # Increment i by 1` (translation comment)
- `# Loop through users` (obvious from code)
- Type information in comments (use type hints)

**Keep/Add:**
- Why a non-obvious approach was chosen
- Workarounds with ticket references
- Business logic that may outlive tribal knowledge
- Magic numbers with derivation

## Modern Patterns to Apply

### Type Hints (3.10+)
```python
# Old
from typing import List, Dict, Optional
def func(items: List[str]) -> Optional[Dict[str, int]]: ...

# New
def func(items: list[str]) -> dict[str, int] | None: ...
```

### Match Statements (3.10+)
```python
# Old
if status == "pending":
    ...
elif status == "active":
    ...

# New
match status:
    case "pending":
        ...
    case "active":
        ...
```

### Dataclasses
```python
# Old
class Config:
    def __init__(self, host, port):
        self.host = host
        self.port = port

# New
from dataclasses import dataclass

@dataclass
class Config:
    host: str
    port: int = 8080
```

### F-strings
```python
# Old
"Hello, {}".format(name)
"Hello, %s" % name

# New
f"Hello, {name}"
```

## Safety

- Always verify syntax after changes
- Run existing tests if available
- Create backup recommendation for large changes
- Don't change public API signatures without explicit approval
