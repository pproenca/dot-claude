---
name: reset-commits
description: Reset branch commits to branch point and recreate clean, organized commits following best practices
argument-hint: ""
allowed-tools: [Bash, Read, AskUserQuestion, TodoWrite]
---

# Commit History Reset and Organization

You are helping the user reorganize their git commit history following Google's and Anthropic's commit best practices.

## Workflow Overview

Follow these steps exactly:

1. **Safety check and backup**
2. **Identify branch point**
3. **Analyze changes**
4. **Suggest commit groupings**
5. **Guide commit creation**

## Step 1: Safety Check and Backup

First, verify the repository state and create a backup:

```bash
# Check we're in a git repository
git rev-parse --git-dir

# Check current branch name
git branch --show-current

# Check for uncommitted changes
git status --porcelain
```

**If there are uncommitted changes**:
- STOP and inform the user they must commit or stash changes first
- Do not proceed

**Create backup branch**:
```bash
# Create backup with timestamp
BACKUP_BRANCH="backup/$(git branch --show-current)-$(date +%Y%m%d-%H%M%S)"
git branch $BACKUP_BRANCH
echo "Created backup branch: $BACKUP_BRANCH"
```

## Step 2: Identify Branch Point

Find where the current branch diverged from main/master:

```bash
# Determine main branch name
MAIN_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')

# Find merge base (branch point)
BRANCH_POINT=$(git merge-base HEAD origin/$MAIN_BRANCH)

# Show branch point info
git log --oneline -1 $BRANCH_POINT
```

**Ask user for confirmation**:
Use AskUserQuestion to confirm:
- "I found the branch point at commit: [commit hash] [commit message]"
- "I will reset to this point. Proceed?"
- Options: "Yes, reset to this point" / "No, let me specify a different commit"

If user selects "No", ask them to provide the commit hash to reset to.

## Step 3: Analyze Changes

Get the full diff and changed files:

```bash
# Get all changed files
git diff --name-only $BRANCH_POINT HEAD

# Get detailed diff stats
git diff --stat $BRANCH_POINT HEAD

# Get full diff for analysis
git diff $BRANCH_POINT HEAD
```

**Analyze the changes** and categorize by:
- **File types**: Source code, tests, docs, config, assets
- **Change types**: New features, bug fixes, refactoring, documentation
- **Logical grouping**: Related files that change together
- **Dependencies**: Changes that must be committed together

## Step 4: Suggest Commit Groupings

Based on your analysis, create a commit organization plan following these principles:

### Google Commit Best Practices:
- **Atomic commits**: Each commit should be a single logical change
- **Small commits**: Easier to review, debug, and revert
- **Descriptive messages**: Clear subject line (50 chars), detailed body if needed
- **Type prefixes**: feat:, fix:, docs:, refactor:, test:, chore:
- **One concern per commit**: Don't mix features with bug fixes

### Anthropic Commit Best Practices:
- **Why over what**: Explain the reasoning, not just the changes
- **Context matters**: Include ticket/issue references
- **Test with commits**: Include tests in the same commit as the feature
- **Reviewability**: Each commit should be independently reviewable

**Present suggested groupings** as a numbered list:
```
Suggested commit organization:

1. [type]: [Brief description]
   Files: file1.ts, file2.ts
   Reason: [Why these belong together]

2. [type]: [Brief description]
   Files: file3.ts, test/file3.test.ts
   Reason: [Why these belong together]

...
```

**Ask user**: Use AskUserQuestion with options:
- "Use this organization as-is"
- "Let me adjust the groupings"
- "Show me the diff for group [number]"

If user wants adjustments, iterate until satisfied.

## Step 5: Guide Commit Creation

Once the plan is approved:

1. **Create TodoWrite list** with each commit as a todo item

2. **Perform soft reset**:
```bash
git reset --soft $BRANCH_POINT
```

3. **For each commit group**, guide the user:

```bash
# Add specific files for this commit
git add [files for this commit]

# Show what will be committed
git status

# Create commit with proper message
git commit -m "[type]: [subject line]

[Optional body explaining why, context, ticket refs]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Commit message format**:
- **Subject line**: `[type]: [imperative mood description]` (50 chars max)
- **Types**: feat, fix, docs, refactor, test, chore, perf, style
- **Body** (if needed):
  - Why this change is necessary
  - What problem it solves
  - Any context or ticket references
  - Blank line between subject and body
- **Footer**: Include Claude Code attribution

**Example commit messages**:

```
feat: add user authentication middleware

Implements JWT-based authentication to secure API endpoints.
This addresses security requirements from ticket AUTH-123.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

```
fix: resolve race condition in data loader

The concurrent requests were causing duplicate database entries.
Added mutex lock to ensure atomic operations.

Fixes #456

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

```
refactor: extract validation logic into separate module

Improves code organization and makes validators reusable across
different API endpoints. No functional changes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

4. **Mark todo complete** after each commit is created

5. **Final verification**:
```bash
# Show the new commit history
git log --oneline HEAD..origin/$MAIN_BRANCH

# Verify all changes are committed
git status
```

## Important Notes

- **Do not push automatically**: Let user review commits before pushing
- **Preserve attribution**: Always include Claude Code attribution
- **Safety first**: Backup branch is critical - never skip
- **User control**: Get user confirmation at key decision points
- **Explain reasoning**: Help user understand why commits are grouped this way

## Error Handling

**If branch point detection fails**:
- Ask user to specify the base branch or commit manually
- Show recent commits to help them identify the right point

**If there are conflicts or issues**:
- User can always recover from backup branch: `git reset --hard $BACKUP_BRANCH`
- Provide clear instructions for recovery

**If user wants to abort**:
- Reset to backup: `git reset --hard $BACKUP_BRANCH`
- Delete current work: `git branch -D $(git branch --show-current)`
- Checkout backup: `git checkout $BACKUP_BRANCH`

## Tips for Best Commit Messages

- **Start with verb**: "Add", "Fix", "Update", "Remove", "Refactor"
- **Be specific**: "Fix login timeout" not "Fix bug"
- **Present tense**: "Add feature" not "Added feature"
- **No period**: Subject line doesn't end with period
- **Wrap body at 72 chars**: For better readability in git log
- **Link issues**: Include ticket/issue references when relevant
