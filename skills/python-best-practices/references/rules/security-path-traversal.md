---
title: Prevent Directory Traversal
impact: LOW-MEDIUM
impactDescription: Prevents file system attacks
tags: security, path, traversal, pathlib
---

## Prevent Directory Traversal

Validate file paths to prevent directory traversal attacks.

**Incorrect (unvalidated file paths):**

```python
def read_file(filename: str) -> str:
    with open(f"/data/{filename}") as f:  # DANGER: ../../../etc/passwd
        return f.read()
```

**Correct (path validation):**

```python
from pathlib import Path

BASE_DIR = Path("/data").resolve()

def read_file(filename: str) -> str:
    # Resolve the full path
    file_path = (BASE_DIR / filename).resolve()

    # Ensure it's within the base directory
    if not file_path.is_relative_to(BASE_DIR):
        raise ValueError("Access denied: path traversal detected")

    with open(file_path) as f:
        return f.read()
```

Reference: [pathlib](https://docs.python.org/3/library/pathlib.html)
