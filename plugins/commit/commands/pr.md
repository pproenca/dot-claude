---
description: Generate PR title and description following Google's practices
argument-hint: "[base-branch]"
allowed-tools: [Bash, Read, AskUserQuestion]
---

# Generate PR Description

Create a PR title and description from branch commits following Google's CL description guidelines.

## Workflow

1. Analyze branch commits
2. Generate PR title
3. Generate PR description
4. Present for review

---

## Step 1: Analyze Branch Commits

Determine base branch (default: origin/main or origin/master):

```bash
# Get default branch
DEFAULT_BRANCH=$(git remote show origin 2>/dev/null | grep 'HEAD branch' | cut -d' ' -f5)
BASE_BRANCH="${1:-$DEFAULT_BRANCH}"

# Get branch point
BRANCH_POINT=$(git merge-base HEAD origin/$BASE_BRANCH 2>/dev/null || git merge-base HEAD $BASE_BRANCH)

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)

echo "Current branch: $CURRENT_BRANCH"
echo "Base branch: $BASE_BRANCH"
echo "Branch point: $BRANCH_POINT"
```

Get all commits on this branch:

```bash
git log --oneline $BRANCH_POINT..HEAD
```

Get combined diff stats:

```bash
git diff --stat $BRANCH_POINT..HEAD
```

Read each commit message to understand the full scope of changes:

```bash
git log --format='%B---' $BRANCH_POINT..HEAD
```

---

## Step 2: Generate PR Title

The PR title should:
- **Summarize the primary change** in imperative mood
- **Be searchable** - future developers can find this PR
- **Stand alone** - understandable without reading the description
- **50-72 chars** ideal

**Single commit**: Use the commit subject as PR title.

**Multiple commits**: Identify the main theme/feature:
- "Add rate limiting to auth endpoint"
- "Fix authentication edge cases"
- "Refactor validation into separate service"

---

## Step 3: Generate PR Description

Structure the description following Google's guidelines:

```markdown
## Summary

[1-3 sentences explaining WHAT this PR does and WHY]

## Changes

[Bullet list of commits/changes, grouped logically]

- [Change 1]
- [Change 2]
- [Change 3]

## Context

[Background that helps reviewers understand the change]

- Problem being solved
- Why this approach was chosen
- Any tradeoffs or limitations

## Test Plan

[How to verify this works]

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing: [steps if applicable]
```

---

## Step 4: Present for Review

Present the generated title and description, then validate with AskUserQuestion:

### PR Validation
- Header: "PR"
- Question: "Does this PR title and description accurately describe your changes?"
- Options:
  - Looks good: Use this title and description as-is
  - Edit title: I want to adjust the PR title
  - Edit description: I want to modify the description or test plan
  - Major changes: Significant rewrites needed to both

Output the final PR content formatted for copy-paste:

```
## PR Title
[title]

## PR Description
[full description]
```

---

## Notes

- This command generates PR content but does NOT create the PR
- Use `gh pr create --title "..." --body "..."` to create the PR
- If branch has unorganized commits, suggest running `/commits:reset` first
- The description should provide enough context that links may become inaccessible
