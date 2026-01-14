---
title: Use Proper Hashing Algorithms
impact: LOW-MEDIUM
impactDescription: Secure password storage
tags: security, hashing, passwords, hashlib
---

## Use Proper Hashing Algorithms

Use appropriate hashing algorithms for security-sensitive operations.

**Incorrect (weak hashing):**

```python
import hashlib

def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()  # WEAK!
```

**Correct (proper password hashing):**

```python
import hashlib
import secrets

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        iterations=100_000
    )
    return salt.hex() + key.hex()

def verify_password(password: str, stored_hash: str) -> bool:
    salt = bytes.fromhex(stored_hash[:64])
    stored_key = stored_hash[64:]
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        iterations=100_000
    )
    return secrets.compare_digest(key.hex(), stored_key)
```

Reference: [hashlib](https://docs.python.org/3/library/hashlib.html)
