# Task Completion Checklist

## Before Committing

### 1. Lint
```bash
make lint
```
Ensures all bash scripts pass shellcheck.

### 2. Validate Plugins
```bash
make validate
```
Validates both `plugins/` and `domain_plugins/` directories:
- JSON syntax in plugin.json files
- Frontmatter in markdown files
- Script permissions

### 3. Run Tests
```bash
make test
```
Runs all bats test suites.

### 4. Full Check (Recommended)
```bash
make check
```
Runs marketplace validation levels 1-7 plus BATS tests:
- Level 1: JSON/YAML syntax
- Level 2: YAML frontmatter
- Level 4: Command arguments
- Level 5: File references
- Level 6: Bash syntax in markdown
- Level 7: Integration tests
- BATS: Unit tests

## Pre-commit Hooks
When you commit, pre-commit automatically runs:
- `trailing-whitespace` - removes trailing whitespace
- `end-of-file-fixer` - ensures files end with newline
- `check-yaml` - validates YAML syntax
- `check-json` - validates JSON syntax
- `shellcheck` - lints bash scripts

## After Task Completion
1. Ensure `make check` passes
2. Commit with conventional commit format:
   - `feat(plugin): description` - new feature
   - `fix(plugin): description` - bug fix
   - `chore(plugin): description` - maintenance
   - `docs(plugin): description` - documentation
3. Pre-commit hooks run automatically
4. If hooks modify files, stage and re-commit
