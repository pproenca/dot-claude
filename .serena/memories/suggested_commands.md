# Suggested Commands

## Development Setup
```bash
# Install dependencies (bats, shellcheck, pre-commit)
make install

# Check dependency status
make deps
```

## Testing
```bash
# Run all bats tests
make test

# Run tests with verbose output
make test-verbose

# Run specific test file
bats plugins/dev-workflow/tests/hook-helpers.bats
```

## Linting
```bash
# Lint all bash scripts with shellcheck
make lint

# Lint single file
shellcheck -x plugins/dev-workflow/scripts/hook-helpers.sh
```

## Validation
```bash
# Validate all plugins (JSON, frontmatter, permissions)
make validate

# Validate single plugin
claude plugin validate plugins/dev-workflow/
```

## Full Check
```bash
# Run lint + validate + test
make check
```

## Cleanup
```bash
# Remove generated files and caches
make clean
```

## Git
```bash
# Standard git commands work
git status
git diff
git log --oneline

# Pre-commit runs automatically on commit
git commit -m "message"
```

## Python/uv
```bash
# Sync dependencies
uv sync

# Run pre-commit manually
uv run pre-commit run --all-files
```

## Darwin (macOS) Specific
- Use `brew install` for bats-core and shellcheck
- Note: `mapfile`/`readarray` not available, use alternatives
