---
name: python-testing
description: Use when writing pytest tests, creating fixtures, mocking dependencies, or testing async code - provides patterns that verify actual behavior with proper fixtures and parametrization; prevents testing mocks instead of code (plugin:python@dot-claude)
allowed-tools: Bash(pytest:*), Read, Edit
---

# Python Testing Patterns

Robust testing with pytest.

## Before Writing Tests

1. Read `references/pythonic-style.md` for naming and style conventions
2. **TDD workflow**: Write failing test first, then implement
3. Test behavior, not implementation details

## Reference Files

| Topic | When to Load | File |
|-------|--------------|------|
| Pythonic style | Before writing code | `../references/pythonic-style.md` |
| Async, property-based, factories | Advanced patterns | `references/advanced-patterns.md` |
| SQLAlchemy, in-memory DBs | Database testing | `references/database-testing.md` |

## Basic Tests

```python
import pytest

def test_addition():
    assert 2 + 2 == 4

def test_exception_raised():
    with pytest.raises(ValueError, match="invalid"):
        raise ValueError("invalid input")
```

## Fixtures

```python
@pytest.fixture
def db():
    """
    Provides isolated database connection for test isolation.

    Using in-memory SQLite prevents test pollution across runs and
    guarantees each test starts with known state.
    """
    database = Database("sqlite:///:memory:")
    database.connect()
    yield database
    database.disconnect()

def test_query(db):
    results = db.query("SELECT * FROM users")
    assert len(results) >= 0

# Session scope shares fixture across all tests for expensive resources
# (e.g., one DB schema creation for all tests vs per-test).
@pytest.fixture(scope="session")
def app_config():
    return {"debug": True, "db_url": "sqlite:///:memory:"}
```

## Parametrized Tests

```python
@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("invalid.email", False),
    ("", False),
])
def test_email_validation(email, valid):
    assert is_valid_email(email) == valid

# With custom IDs
@pytest.mark.parametrize("value,expected", [
    pytest.param(1, True, id="positive"),
    pytest.param(0, False, id="zero"),
    pytest.param(-1, False, id="negative"),
])
def test_is_positive(value, expected):
    assert (value > 0) == expected
```

## Mocking

```python
from unittest.mock import Mock, patch

def test_api_call():
    mock_response = Mock()
    mock_response.json.return_value = {"id": 1, "name": "Test"}

    with patch("requests.get", return_value=mock_response) as mock_get:
        result = fetch_user(1)

        assert result["id"] == 1
        mock_get.assert_called_once_with("https://api.example.com/users/1")

# Decorator syntax
@patch("module.external_service")
def test_with_mock(mock_service):
    mock_service.return_value = "mocked"
    assert my_function() == "mocked"
```

## Async Testing

```python
import pytest

@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_data("https://api.example.com")
    assert result is not None

@pytest.mark.asyncio
async def test_timeout():
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(), timeout=0.1)

# Async fixture
@pytest.fixture
async def async_client():
    client = AsyncClient()
    await client.connect()
    yield client
    await client.disconnect()
```

## Test Organization

```
tests/
├── conftest.py           # Shared fixtures
├── test_unit/
│   ├── test_models.py
│   └── test_utils.py
├── test_integration/
│   └── test_api.py
└── test_e2e/
    └── test_workflows.py
```

## Naming Conventions

```python
# Good: describes behavior and expected outcome
def test_user_creation_with_valid_data_succeeds():
def test_login_fails_with_invalid_password():
def test_api_returns_404_for_missing_resource():

# Bad: vague or non-descriptive
def test_user():
def test_1():
```

## Markers

```python
@pytest.mark.slow
def test_slow_operation():
    ...

@pytest.mark.integration
def test_database():
    ...

@pytest.mark.skip(reason="Not implemented")
def test_future_feature():
    ...

@pytest.mark.xfail(reason="Known bug #123")
def test_known_bug():
    ...

# Run: pytest -m "not slow"
```

## Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-v", "--cov=myapp", "--cov-report=term-missing"]
markers = [
    "slow: marks tests as slow",
    "integration: marks integration tests",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*"]
```

## TDD Workflow

1. **RED**: Write failing test
2. **GREEN**: Write minimal code to pass
3. **REFACTOR**: Improve while keeping tests green

```python
# 1. Write test first
def test_calculate_total():
    cart = Cart([Item(10), Item(20)])
    assert cart.total() == 30

# 2. Run test - it fails (Cart doesn't exist)

# 3. Implement minimal code
class Cart:
    def __init__(self, items):
        self.items = items
    def total(self):
        return sum(item.price for item in self.items)

# 4. Run test - it passes

# 5. Refactor if needed (tests stay green)
```

## Workflow Integration

If the `core` plugin is installed, use these skills:

| Task | Skill |
|------|-------|
| Full TDD methodology | `core:tdd` |
| Debug test failures | `debug:systematic` |
| Before claiming done | `core:verification` |

## Best Practices

1. **One assertion per test** when possible
2. **Descriptive names** that explain behavior
3. **Independent tests** - no shared mutable state
4. **Use fixtures** for setup/teardown
5. **Mock external dependencies** appropriately
6. **Parametrize** to reduce duplication
7. **Test edge cases** and error conditions
8. **Run tests in CI** on every commit
9. **Measure coverage** but focus on quality
10. **Write tests first** (TDD) when possible
