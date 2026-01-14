---
title: Create Custom Exceptions Properly
impact: MEDIUM
impactDescription: Better error handling and debugging
tags: error, custom-exceptions, exception-design
---

## Create Custom Exceptions Properly

Create custom exceptions that inherit from appropriate base classes.

**Incorrect (poor exception design):**

```python
class Error(Exception):
    pass

class ConfigError(Error):
    def __init__(self, msg):
        self.msg = msg

class NetworkError:  # Not inheriting from Exception!
    pass
```

**Correct (well-designed custom exceptions):**

```python
class ApplicationError(Exception):
    """Base exception for application errors."""
    pass

class ConfigError(ApplicationError):
    """Configuration-related errors."""
    def __init__(self, message: str, path: str | None = None):
        self.path = path
        super().__init__(message)

class NetworkError(ApplicationError):
    """Network-related errors."""
    def __init__(self, message: str, url: str, status_code: int | None = None):
        self.url = url
        self.status_code = status_code
        super().__init__(message)
```

Reference: [User-defined Exceptions](https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions)
