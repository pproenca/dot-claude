---
name: finishing-a-development-branch
description: Guide completion of development work by presenting merge/PR options. Use when "I'm done", "merge this", "create PR", "finish up", or when implementation is complete and tests pass.
allowed-tools: Read, Bash, AskUserQuestion, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*
---

# Finishing a Development Branch

Guide completion of development work by presenting clear options.

## When Invoked

After code review passes, tests pass, work is ready to integrate.

**Invoked by:**
- Post-swarm actions (after ExitPlanMode completes)
- Direct user request ("I'm done", "merge this", "create PR")

## Step 1: Verify Tests

```bash
npm test  # or cargo test / pytest / go test ./...
```

If tests fail: Stop. Cannot proceed until tests pass.

## Step 2: Determine Base Branch

```bash
git merge-base HEAD main 2>/dev/null && BASE="main" || \
git merge-base HEAD master 2>/dev/null && BASE="master" || \
BASE="unknown"
```

If unknown, ask user which branch.

## Step 3: Present Options

Use AskUserQuestion:

```claude
AskUserQuestion:
  header: "Integration"
  question: "Work complete. How to proceed?"
  multiSelect: false
  options:
    - label: "Merge locally"
      description: "Merge to base branch and delete feature branch"
    - label: "Create PR"
      description: "Push branch and create Pull Request"
    - label: "Keep as-is"
      description: "Preserve branch and worktree for later"
    - label: "Discard"
      description: "Delete branch and all commits"
```

## Step 4: Execute Choice

### Option: Merge locally

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/worktree-manager.sh"

FEATURE="$(git branch --show-current)"

# Safety check
if [ -n "$(git status --porcelain)" ]; then
  echo "Error: Uncommitted changes. Commit first."
  exit 1
fi

# Get main repo path
MAIN_REPO="$(get_main_worktree)"

# If in worktree, go to main repo
if ! is_main_repo; then
  cd "$MAIN_REPO"
fi

# Checkout base and merge
git checkout "$BASE"
git pull origin "$BASE" 2>/dev/null || true
git merge "$FEATURE"

npm test  # verify merged result
```

If tests pass and was in worktree:

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/worktree-manager.sh"
# Clean up worktree if we were in one
if [[ -n "${WORKTREE_PATH:-}" ]]; then
  git worktree remove --force "$WORKTREE_PATH" 2>/dev/null || true
fi
git branch -d "$FEATURE"
```

Skip to Step 5.

### Option: Create PR

```bash
FEATURE=$(git branch --show-current)
git push -u origin $FEATURE
gh pr create --title "[title]" --body "## Summary\n[changes]\n\n## Tests\n- All passing"
```

Proceed to Step 5.

### Option: Keep as-is

Report branch and worktree location. Skip Step 5. Return.

### Option: Discard

Confirm with AskUserQuestion first:

```claude
AskUserQuestion:
  header: "Confirm"
  question: "Discard all work on this branch?"
  multiSelect: false
  options:
    - label: "Yes, discard"
      description: "Delete branch and all commits permanently"
    - label: "Cancel"
      description: "Return to integration options"
```

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/worktree-manager.sh"

# If in worktree, remove it first
if ! is_main_repo; then
  remove_worktree
else
  git checkout $BASE
  git branch -D $FEATURE
fi
```

Proceed to Step 5.

## Step 5: Report Completion

Report:

```text
Branch finished:
- Action: [Merged / PR created / Discarded]
- Branch: [name]
- Worktree: [cleaned up / preserved]
```

Return to caller.
