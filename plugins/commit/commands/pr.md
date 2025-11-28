---
description: Generate PR title and description following Conventional Commits
argument-hint: "[base-branch]"
allowed-tools: [Bash, Read, AskUserQuestion]
---

# Generate PR Description

Create a PR title and description from branch commits following Conventional Commits format.

## Workflow

1. Analyze branch commits
2. Determine dominant commit type
3. Generate PR title
4. Generate PR description
5. Present for review

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

## Step 2: Determine Dominant Commit Type

Analyze the commits to determine the primary type for the PR title.

**Type priority** (use the most significant):
1. `feat` - Any new feature makes this a feature PR
2. `fix` - Bug fixes if no features
3. `refactor` - Restructuring if no features/fixes
4. `perf` - Performance improvements
5. `docs` - Documentation changes
6. `test` - Test additions
7. `build`/`ci` - Build/CI changes
8. `chore` - Maintenance

**Breaking change**: If ANY commit has `!` or `BREAKING CHANGE:`, the PR title should include `!`.

**Single commit**: Use that commit's type and subject directly.

**Multiple commits with same type**: Use that type, summarize the changes.

**Multiple commits with different types**: Use the highest priority type, describe the overall change.

---

## Step 3: Generate PR Title

The PR title should follow Conventional Commits format:

```
<type>[!]: <summary of changes>
```

**Rules:**
- Use dominant type from Step 2
- Include `!` if any commit is a breaking change
- Imperative mood ("add", not "adding")
- 50-72 chars ideal
- No period at end

**Examples:**

| Commits | PR Title |
|---------|----------|
| Single `feat: add user preferences` | `feat: add user preferences` |
| `feat: add auth`, `feat: add sessions` | `feat: add authentication system` |
| `feat: add API`, `fix: handle errors` | `feat: add API with error handling` |
| `refactor: extract service`, `test: add tests` | `refactor: extract service with tests` |
| `feat!: remove v1 API` | `feat!: remove v1 API` |

---

## Step 4: Generate PR Description

Structure the description following this template:

```markdown
## Summary

[1-3 sentences explaining WHAT this PR does and WHY]

## Changes

[Bullet list of commits/changes, grouped logically by type]

### Features
- [feat commits]

### Bug Fixes
- [fix commits]

### Other Changes
- [refactor/chore/etc commits]

## Context

[Background that helps reviewers understand the change]

- Problem being solved
- Why this approach was chosen
- Any tradeoffs or limitations

## Breaking Changes

[If any commits have breaking changes, list them here]

- [Description of breaking change and migration path]

## Test Plan

[How to verify this works]

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing: [steps if applicable]
```

**Note:** Omit empty sections (e.g., if no breaking changes, omit that section).

---

## Step 5: Present for Review

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
- If branch has unorganized commits, suggest running `/commit:reset` first
- The description should provide enough context that links may become inaccessible
- PR title must follow Conventional Commits format for release-please compatibility
