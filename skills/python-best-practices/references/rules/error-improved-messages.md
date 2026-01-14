---
title: Leverage Improved Error Messages
impact: MEDIUM
impactDescription: Better debugging experience
tags: error, error-messages, debugging, python311
---

## Leverage Improved Error Messages

Take advantage of Python 3.11+ improved error messages by writing clear code.

**Python 3.11+ improvements:**

```python
# Shows exact location of errors
d = {"users": {"alice": {"age": 30}}}
print(d["users"]["bob"]["age"])
# KeyError: 'bob'
#     print(d["users"]["bob"]["age"])
#           ~~~~~~~~~~~~^^^^^^^

# Suggests similar names for typos
class User:
    def get_name(self): pass

user = User()
user.getname()  # Did you mean: 'get_name'?

# Module shadow warnings
# If you have random.py in your directory:
import random
random.randint(1, 10)
# AttributeError: ... (consider renaming '/path/random.py')
```

**Best practices for clear errors:**

```python
# Use descriptive variable names
user_data = fetch_user(user_id)  # Clear in traceback

# Break complex expressions into steps
config = load_config()
settings = config["app"]["settings"]  # Easier to debug
timeout = settings["timeout"]
```

Reference: [What's New in Python 3.11](https://docs.python.org/3/whatsnew/3.11.html)
