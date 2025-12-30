# Python TDD Example: User Repository

Complete example of TDD cycle for implementing a user repository.

## Step 1: RED - Write Failing Test

```python
# tests/repositories/test_user_repository.py
import pytest
from src.repositories.user_repository import UserRepository
from src.models.user import User

class TestUserRepository:
    def test_create_user_returns_user_with_id(self):
        """Creating a user should return the user with an assigned ID."""
        repo = UserRepository()
        user_data = {"email": "test@example.com", "name": "Test User"}

        created_user = repo.create(user_data)

        assert isinstance(created_user, User)
        assert created_user.id is not None
        assert created_user.email == "test@example.com"
        assert created_user.name == "Test User"
```

## Step 2: Run - Confirm Failure

```bash
$ uv run pytest tests/repositories/test_user_repository.py -v

FAILED - ModuleNotFoundError: No module named 'src.repositories.user_repository'
```

Test fails because module doesn't exist. This is correct.

## Step 3: Commit Test

```bash
git add tests/repositories/test_user_repository.py
git commit -m "test: add user repository create test"
```

## Step 4: GREEN - Minimal Implementation

```python
# src/repositories/user_repository.py
from uuid import uuid4
from src.models.user import User

class UserRepository:
    def create(self, user_data: dict) -> User:
        return User(
            id=str(uuid4()),
            email=user_data["email"],
            name=user_data["name"],
        )
```

```python
# src/models/user.py
from msgspec import Struct

class User(Struct):
    id: str
    email: str
    name: str
```

## Step 5: Run - Confirm Pass

```bash
$ uv run pytest tests/repositories/test_user_repository.py -v

PASSED
```

## Step 6: Add More Tests - Repeat Cycle

```python
# Add to test file
def test_get_user_by_id_returns_user(self):
    """Getting a user by ID should return the correct user."""
    repo = UserRepository()
    created = repo.create({"email": "test@example.com", "name": "Test"})

    found = repo.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id

def test_get_user_by_id_returns_none_for_unknown_id(self):
    """Getting unknown ID should return None."""
    repo = UserRepository()

    found = repo.get_by_id("unknown-id")

    assert found is None
```

Run tests (RED):
```bash
$ uv run pytest -v
FAILED - AttributeError: 'UserRepository' object has no attribute 'get_by_id'
```

Implement (GREEN):
```python
class UserRepository:
    def __init__(self):
        self._users: dict[str, User] = {}

    def create(self, user_data: dict) -> User:
        user = User(
            id=str(uuid4()),
            email=user_data["email"],
            name=user_data["name"],
        )
        self._users[user.id] = user
        return user

    def get_by_id(self, user_id: str) -> User | None:
        return self._users.get(user_id)
```

Run tests:
```bash
$ uv run pytest -v
3 passed
```

## Step 7: BLUE - Refactor

Now improve the code:

```python
# src/repositories/user_repository.py
from uuid import uuid4
from typing import Protocol
from src.models.user import User

class IdGenerator(Protocol):
    def __call__(self) -> str: ...

def default_id_generator() -> str:
    return str(uuid4())

class UserRepository:
    """In-memory user repository."""

    def __init__(self, id_generator: IdGenerator = default_id_generator):
        self._users: dict[str, User] = {}
        self._id_generator = id_generator

    def create(self, user_data: dict) -> User:
        """Create a new user with generated ID."""
        user = User(
            id=self._id_generator(),
            email=user_data["email"],
            name=user_data["name"],
        )
        self._users[user.id] = user
        return user

    def get_by_id(self, user_id: str) -> User | None:
        """Retrieve user by ID, or None if not found."""
        return self._users.get(user_id)
```

## Step 8: Confirm Tests Still Pass

```bash
$ uv run pytest -v
3 passed
```

## Commit Implementation

```bash
git add src/
git commit -m "feat: implement in-memory user repository"
```

---

## Key Takeaways

1. Test came first, implementation followed
2. Each test describes one behavior
3. Implementation is minimal to pass tests
4. Refactoring adds quality without changing behavior
5. Tests serve as living documentation
