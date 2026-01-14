---
title: Use copy.replace for Updates
impact: MEDIUM
impactDescription: Clean functional updates
tags: data, copy, replace, dataclass, python313
---

## Use copy.replace for Updates

Use `copy.replace()` for creating modified copies of dataclasses (Python 3.13+).

**Incorrect (manual copy and modify):**

```python
from dataclasses import dataclass
import copy

@dataclass
class Config:
    host: str
    port: int
    debug: bool

config = Config("localhost", 8080, False)
new_config = copy.copy(config)
new_config.debug = True
```

**Correct (using copy.replace):**

```python
from dataclasses import dataclass
from copy import replace

@dataclass
class Config:
    host: str
    port: int
    debug: bool

config = Config("localhost", 8080, False)
new_config = replace(config, debug=True)  # Clean functional update
```

Reference: [copy.replace](https://docs.python.org/3/library/copy.html#copy.replace)
