# Suggested Commands

## Development Setup
```bash
make install          # Install dependencies (bats, shellcheck, pre-commit)
make deps             # Check dependency status
```

## Testing
```bash
make test             # Run all bats tests
make test-verbose     # Run tests with verbose output
bats plugins/dev-workflow/tests/  # Run specific test directory
```

## Linting
```bash
make lint             # Lint all bash scripts with shellcheck
shellcheck -x plugins/dev-workflow/scripts/hook-helpers.sh  # Single file
```

## Validation
```bash
make check            # Full validation (levels 1-7 + BATS tests) - recommended
make validate         # Validate plugins with Claude CLI

# Individual validation levels
scripts/level-1-syntax.sh       # JSON/YAML syntax
scripts/level-2-frontmatter.sh  # YAML frontmatter
scripts/level-4-arguments.sh    # Command arguments
scripts/level-5-file-refs.sh    # File references
scripts/level-6-bash.sh         # Bash syntax in markdown
scripts/level-7-integration.sh  # Integration tests
```

## Plugin-Specific Validation
```bash
# dev-workflow
plugins/dev-workflow/scripts/validate.sh

# All plugins
scripts/validate-all.sh
```

## Cleanup
```bash
make clean            # Remove generated files and caches
```

## Git
```bash
git status
git diff
git log --oneline

# Pre-commit runs automatically on commit
git commit -m "feat(scope): description"
```

## Python/uv
```bash
uv sync                              # Sync dependencies
uv run pre-commit run --all-files    # Run pre-commit manually
```

## Platform Notes (macOS)
- Use `brew install` for bats-core and shellcheck
- `mapfile`/`readarray` not available - use alternatives
