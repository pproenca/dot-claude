---
description: Abandon active workflow and clear TodoWrite
allowed-tools: Bash, TodoWrite, AskUserQuestion, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*
---

# Abandon Workflow

Discard the active workflow state. Use this when you want to start fresh or the previous plan is no longer relevant.

## Step 1: Show Current State and Check for Unpushed Work

Check TodoWrite for current progress and show summary.

```bash
# Check git for recent work
git log --oneline --since="1 day ago" | head -10

# SAFETY: Check for unpushed commits
CURRENT_BRANCH=$(git branch --show-current)
echo ""
echo "Current branch: $CURRENT_BRANCH"

# Check if branch exists on remote
if ! git ls-remote --heads origin "$CURRENT_BRANCH" 2>/dev/null | grep -q .; then
  echo ""
  echo "⚠️  WARNING: Branch '$CURRENT_BRANCH' has NEVER been pushed to remote!"
  echo "    Abandoning may result in loss of work if worktree is deleted."
  echo "    Recommend: git push -u origin $CURRENT_BRANCH"
else
  # Check for unpushed commits
  UNPUSHED=$(git log "origin/$CURRENT_BRANCH..$CURRENT_BRANCH" --oneline 2>/dev/null || echo "")
  if [[ -n "$UNPUSHED" ]]; then
    echo ""
    echo "⚠️  WARNING: You have unpushed commits on '$CURRENT_BRANCH':"
    echo "$UNPUSHED"
    echo ""
    echo "    Recommend pushing first: git push origin $CURRENT_BRANCH"
  else
    echo "✓ Branch is up to date with remote."
  fi
fi
```

## Step 2: Confirm

Use AskUserQuestion:

```claude
AskUserQuestion:
  header: "Confirm"
  question: "Clear TodoWrite and abandon workflow? Completed commits will remain, but tracking will be lost."
  multiSelect: false
  options:
    - label: "Yes, abandon"
      description: "Clear TodoWrite and start fresh"
    - label: "Cancel"
      description: "Keep workflow for later resume"
```

## Step 3: Clear State

**If Yes, abandon:**

Clear TodoWrite by setting an empty list:

```claude
TodoWrite:
  todos: []
```

Report: "Workflow abandoned. You can start a new workflow with /dev-workflow:brainstorm or EnterPlanMode."

**If Cancel:**

Report: "Workflow preserved. Use /dev-workflow:resume to continue."
