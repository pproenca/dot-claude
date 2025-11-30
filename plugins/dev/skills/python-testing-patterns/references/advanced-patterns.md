# Advanced Testing Patterns

## Table of Contents
- [Pattern 6: Testing Async Code](#pattern-6-testing-async-code)
- [Pattern 7: Monkeypatch for Testing](#pattern-7-monkeypatch-for-testing)
- [Pattern 8: Temporary Files and Directories](#pattern-8-temporary-files-and-directories)
- [Pattern 9: Custom Fixtures and Conftest](#pattern-9-custom-fixtures-and-conftest)
- [Pattern 10: Property-Based Testing](#pattern-10-property-based-testing)

## Pattern 6: Testing Async Code

```python
# test_async.py
import pytest
import asyncio

async def fetch_data(url: str) -> dict:
    await asyncio.sleep(0.1)
    return {"url": url, "data": "result"}


@pytest.mark.asyncio
async def test_fetch_data():
    result = await fetch_data("https://api.example.com")
    assert result["url"] == "https://api.example.com"
    assert "data" in result


@pytest.mark.asyncio
async def test_concurrent_fetches():
    urls = ["url1", "url2", "url3"]
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)

    assert len(results) == 3
    assert all("data" in r for r in results)


@pytest.fixture
async def async_client():
    client = {"connected": True}
    yield client
    client["connected"] = False


@pytest.mark.asyncio
async def test_with_async_fixture(async_client):
    assert async_client["connected"] is True
```

## Pattern 7: Monkeypatch for Testing

```python
# test_environment.py
import os
import pytest

def get_database_url() -> str:
    return os.environ.get("DATABASE_URL", "sqlite:///:memory:")


def test_database_url_default():
    url = get_database_url()
    assert url


def test_database_url_custom(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/test")
    assert get_database_url() == "postgresql://localhost/test"


def test_database_url_not_set(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert get_database_url() == "sqlite:///:memory:"


class Config:
    def __init__(self):
        self.api_key = "production-key"

    def get_api_key(self):
        return self.api_key


def test_monkeypatch_attribute(monkeypatch):
    config = Config()
    monkeypatch.setattr(config, "api_key", "test-key")
    assert config.get_api_key() == "test-key"
```

## Pattern 8: Temporary Files and Directories

```python
# test_file_operations.py
import pytest
from pathlib import Path

def save_data(filepath: Path, data: str):
    filepath.write_text(data)


def load_data(filepath: Path) -> str:
    return filepath.read_text()


def test_file_operations(tmp_path):
    test_file = tmp_path / "test_data.txt"
    save_data(test_file, "Hello, World!")
    assert test_file.exists()
    data = load_data(test_file)
    assert data == "Hello, World!"


def test_multiple_files(tmp_path):
    files = {
        "file1.txt": "Content 1",
        "file2.txt": "Content 2",
        "file3.txt": "Content 3"
    }

    for filename, content in files.items():
        filepath = tmp_path / filename
        save_data(filepath, content)

    assert len(list(tmp_path.iterdir())) == 3

    for filename, expected_content in files.items():
        filepath = tmp_path / filename
        assert load_data(filepath) == expected_content
```

## Pattern 9: Custom Fixtures and Conftest

```python
# conftest.py
import pytest

@pytest.fixture(scope="session")
def database_url():
    return "postgresql://localhost/test_db"


@pytest.fixture(autouse=True)
def reset_database(database_url):
    """Clears database before each test, logs completion after."""
    print(f"Clearing database: {database_url}")
    yield
    print("Test completed")


@pytest.fixture
def sample_user():
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com"
    }


@pytest.fixture
def sample_users():
    return [
        {"id": 1, "name": "User 1"},
        {"id": 2, "name": "User 2"},
        {"id": 3, "name": "User 3"},
    ]


@pytest.fixture(params=["sqlite", "postgresql", "mysql"])
def db_backend(request):
    """Runs tests with different database backends."""
    return request.param


def test_with_db_backend(db_backend):
    print(f"Testing with {db_backend}")
    assert db_backend in ["sqlite", "postgresql", "mysql"]
```

## Pattern 10: Property-Based Testing

```python
# test_properties.py
from hypothesis import given, strategies as st
import pytest

def reverse_string(s: str) -> str:
    return s[::-1]


@given(st.text())
def test_reverse_twice_is_original(s):
    assert reverse_string(reverse_string(s)) == s


@given(st.text())
def test_reverse_length(s):
    assert len(reverse_string(s)) == len(s)


@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    assert a + b == b + a


@given(st.lists(st.integers()))
def test_sorted_list_properties(lst):
    sorted_lst = sorted(lst)
    assert len(sorted_lst) == len(lst)
    assert set(sorted_lst) == set(lst)
    for i in range(len(sorted_lst) - 1):
        assert sorted_lst[i] <= sorted_lst[i + 1]
```
