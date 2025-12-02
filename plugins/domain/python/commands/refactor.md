---
description: Refactor a Python file using ruff, mypy, and modern patterns
argument-hint: "<path/to/file.py>"
allowed-tools: [Bash, Read, Edit, Glob, AskUserQuestion, Task, Skill]
---

# Refactor Python File

Refactor the specified Python file to follow modern Python patterns and best practices.

## Progress Tracking

Create TodoWrite with each step:
1. Identify and read target file
2. Analyze (ruff + mypy + python-expert in parallel)
3. Propose changes
4. Apply refactoring
5. Verify and report

## Step 1: Identify and Read Target File

If `$ARGUMENTS` is provided, use it as the target file path.

Otherwise, find Python files and prompt user:

```bash
fd -e py --type f 2>/dev/null | head -20
```

Use AskUserQuestion:
- Header: "File"
- Question: "Which Python file would you like to refactor?"
- Options: [up to 4 files from fd results]

Read the file content to understand its structure.

## Step 2: Analyze

Run these in parallel:

### Ruff check
```bash
ruff check "<target_file_path>" 2>&1 || true
```

### Ruff format diff
```bash
ruff format --diff "<target_file_path>" 2>&1 || true
```

### Mypy (if installed)
```bash
mypy "<target_file_path>" --ignore-missing-imports 2>&1 || true
```

### Python-expert dispatch
```
Task tool with:
- subagent_type: "python:python-expert"
- prompt: "REVIEW the Python file at <target_file_path> for modern Python 3.12+ patterns, type hints, async patterns if applicable, and overall code quality"
```

Combine findings. For each issue note:
- Line number
- Current code
- Recommended fix
- Rule reference (ruff code or pattern name)

## Step 3: Propose Changes

Present summary:
- Total issues: N
- Ruff violations: N
- Type errors: N
- Pattern improvements: N

Use AskUserQuestion:
- Header: "Refactor"
- Question: "How would you like to proceed?"
- Options:
  - Apply all: Apply all changes
  - Critical only: Only apply ruff errors and type fixes
  - Cancel: Do not make changes

## Step 4: Apply Refactoring

Use Edit tool to apply approved changes in order:
1. Critical fixes (type errors, security issues)
2. Ruff auto-fixes (formatting, linting)
3. Pattern improvements (modern Python idioms)

## Step 5: Verify and Report

### Syntax check
```bash
python -m py_compile "<target_file_path>"
```

### Ruff comparison
```bash
ruff check "<target_file_path>" 2>&1 || true
```

### Final Report

```
## Refactoring Complete

**File:** [path]

### Changes Applied
- [key changes by category]

### Ruff Comparison
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Errors | N | N | -N |
| Warnings | N | N | -N |

### Verification
- Syntax check: [PASS/FAIL]
- Ruff delta: [Improved/Same/Regressed]

### Python Expert Assessment
- **Initial Review:** [summary]
- **Recommendation:** [PASS/NEEDS_FIXES]
```
