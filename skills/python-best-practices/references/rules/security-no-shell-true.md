---
title: Avoid shell=True in Subprocess
impact: LOW-MEDIUM
impactDescription: Prevents shell injection
tags: security, subprocess, shell, injection
---

## Avoid shell=True in Subprocess

Avoid `shell=True` in subprocess calls to prevent shell injection.

**Incorrect (using shell=True):**

```python
import subprocess

def list_files(directory: str) -> str:
    result = subprocess.run(
        f"ls -la {directory}",  # DANGER: Shell injection!
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout
```

**Correct (pass arguments as list):**

```python
import subprocess
from pathlib import Path

def list_files(directory: str) -> str:
    path = Path(directory).resolve()
    result = subprocess.run(
        ["ls", "-la", str(path)],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout
```

Reference: [subprocess security](https://docs.python.org/3/library/subprocess.html#security-considerations)
