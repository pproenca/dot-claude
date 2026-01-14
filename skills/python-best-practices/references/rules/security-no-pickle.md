---
title: Avoid Pickle with Untrusted Data
impact: LOW-MEDIUM
impactDescription: Prevents deserialization attacks
tags: security, pickle, serialization, json
---

## Avoid Pickle with Untrusted Data

Never unpickle data from untrusted sources.

**Incorrect (unpickling untrusted data):**

```python
import pickle

def load_user_data(data: bytes) -> dict:
    return pickle.loads(data)  # DANGER: Code execution!
```

**Correct (use JSON or safe alternatives):**

```python
import json
from typing import TypedDict

class UserData(TypedDict):
    name: str
    age: int

def load_user_data(data: bytes) -> UserData:
    return json.loads(data)

# If you must use pickle, restrict classes
import pickle

class RestrictedUnpickler(pickle.Unpickler):
    ALLOWED = {("datetime", "datetime")}

    def find_class(self, module: str, name: str):
        if (module, name) in self.ALLOWED:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"Forbidden: {module}.{name}")
```

Reference: [Security Considerations](https://docs.python.org/3/library/security_warnings.html)
