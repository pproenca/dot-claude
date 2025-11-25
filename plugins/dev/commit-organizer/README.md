# Commit Organizer Plugin

Organize messy commit history into clean, logical commits following Google and Anthropic best practices.

## Overview

This plugin helps you transform a branch with many Work-In-Progress (WIP) commits into a clean, well-organized commit history that's easy to review and understand.

## Features

- **Safe reset workflow**: Automatically creates backup branch before any destructive operations
- **Smart branch point detection**: Finds where your branch diverged from main/master
- **Intelligent grouping**: Analyzes changes and suggests logical commit groupings
- **Best practices enforcement**: Follows Google's and Anthropic's commit message conventions
- **Guided workflow**: Step-by-step process with confirmation at key points
- **Todo tracking**: Visual progress tracking through commit creation

## Installation

### Via Marketplace

```bash
# Clone the 10x-claude-skills marketplace
git clone https://github.com/pedroproenca/10x-claude-skills.git

# Add to Claude Code config (~/.claude/config.json)
{
  "pluginMarketplaces": [
    "/path/to/10x-claude-skills"
  ]
}
```

### Direct Installation

```bash
cc --plugin-dir /path/to/10x-claude-skills/plugins/commit-organizer
```

## Usage

### Basic Workflow

1. **Complete your work**: Finish your feature/fix with messy WIP commits
2. **Run the command**: `/reset-commits`
3. **Follow the guided process**:
   - Backup branch is created automatically
   - Branch point is detected and confirmed
   - Changes are analyzed and grouped logically
   - You review and approve the grouping plan
   - Commits are recreated one by one with proper messages

### Example Scenario

**Before**: 20 commits like:
```
- wip
- fix
- more changes
- update
- fix typo
- refactor stuff
- add feature
...
```

**After**: 3 clean commits:
```
feat: add user authentication middleware

Implements JWT-based authentication to secure API endpoints.
This addresses security requirements from ticket AUTH-123.

---

test: add authentication middleware test coverage

Includes unit tests for token validation, expiry checks,
and error handling scenarios.

---

docs: update API documentation for authentication

Added authentication section to API docs with examples
of header format and error responses.
```

## Commit Message Format

This plugin enforces industry-standard commit message format:

### Structure

```
[type]: [subject line - 50 chars max]

[Optional body explaining why, context, ticket refs]
[Wrapped at 72 characters]

[Optional footer with issue references]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **refactor**: Code refactoring (no functional changes)
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (deps, configs, etc.)
- **perf**: Performance improvements
- **style**: Code style changes (formatting, etc.)

### Best Practices

1. **Atomic commits**: Each commit = one logical change
2. **Why over what**: Explain reasoning, not just changes
3. **Small and focused**: Easier to review and revert
4. **Tests included**: Tests go with the feature/fix
5. **Descriptive subjects**: Clear, imperative mood
6. **Context provided**: Link tickets/issues when relevant

## Workflow Steps

### 1. Safety Check
- Verifies clean working directory
- Creates timestamped backup branch (`backup/your-branch-20240324-143022`)

### 2. Branch Point Detection
- Finds merge base with main/master
- Shows commit info for confirmation
- Allows manual commit specification if needed

### 3. Change Analysis
- Catalogs all changed files
- Identifies change types and patterns
- Groups related changes logically

### 4. Commit Planning
- Presents suggested commit groupings
- Explains rationale for each group
- Allows user to adjust before execution

### 5. Commit Creation
- Soft resets to branch point
- Guides through creating each commit
- Enforces proper commit message format
- Tracks progress with todos

### 6. Verification
- Shows final commit history
- Confirms all changes are committed
- Ready for review before push

## Safety Features

- **Automatic backup**: Every run creates a backup branch
- **Confirmation points**: User confirms branch point and grouping plan
- **Recovery instructions**: Clear steps if anything goes wrong
- **No auto-push**: User reviews before pushing

### Recovery

If something goes wrong:

```bash
# View backup branches
git branch --list 'backup/*'

# Restore from backup
git reset --hard backup/your-branch-timestamp

# Or checkout backup
git checkout backup/your-branch-timestamp
```

## Examples

### Feature Development

**Before**: 15 WIP commits while building a feature

**After**:
```
feat: implement data caching layer
test: add cache invalidation tests
docs: document caching configuration
```

### Bug Fix

**Before**: 8 commits debugging and fixing

**After**:
```
fix: resolve race condition in user session management

The concurrent requests were causing session data corruption.
Added mutex lock to ensure atomic session operations.

Fixes #789
```

### Refactoring

**Before**: Multiple commits moving code around

**After**:
```
refactor: extract validation logic into dedicated service

Improves code organization and makes validators reusable
across API endpoints. No functional changes.
```

## Tips

1. **Run before creating PR**: Clean up commits before requesting review
2. **Group by purpose**: Features, fixes, and docs in separate commits
3. **Include context**: Reference tickets/issues in commit bodies
4. **Review the plan**: Check suggested groupings before executing
5. **Test between commits**: Each commit should leave codebase working

## Troubleshooting

### "Can't find branch point"
- Ensure you've fetched latest from origin
- Manually specify base commit when prompted
- Check that main/master branch exists

### "Uncommitted changes detected"
- Commit or stash your changes first
- Run `git status` to see what's uncommitted

### "Backup branch already exists"
- Previous backup exists - safe to continue
- Or delete old backup: `git branch -D backup/old-branch-name`

## Requirements

- Git repository with remote (origin)
- Clean working directory (no uncommitted changes)
- Branch diverged from main/master

## Philosophy

Good commit history is:
- **Readable**: Easy to understand what changed and why
- **Reviewable**: Each commit can be reviewed independently
- **Debuggable**: Makes bisecting and reverting straightforward
- **Professional**: Demonstrates attention to quality

This plugin helps you achieve that standard effortlessly.

## Contributing

Found a bug or have a suggestion? Open an issue at:
https://github.com/pedroproenca/10x-claude-skills/issues

## License

MIT
