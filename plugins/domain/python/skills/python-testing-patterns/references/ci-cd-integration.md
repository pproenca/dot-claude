# CI/CD Integration

## GitHub Actions Workflow with uv

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run tests
        run: uv run pytest --cov=myapp --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
```

## Coverage Reporting

```bash
# Ensure pytest-cov is in dev dependencies
uv add --dev pytest-cov

# Run tests with coverage
uv run pytest --cov=myapp tests/

# Generate HTML report
uv run pytest --cov=myapp --cov-report=html tests/

# Fail if coverage below threshold
uv run pytest --cov=myapp --cov-fail-under=80 tests/

# Show missing lines
uv run pytest --cov=myapp --cov-report=term-missing tests/
```
