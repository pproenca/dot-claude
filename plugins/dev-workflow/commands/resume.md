---
description: Resume interrupted plan execution
allowed-tools: Read, Bash, TodoWrite, Task, Skill, AskUserQuestion, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*
---

# Resume Workflow

Resume execution of an interrupted plan from where it left off.

## Step 1: Check Workflow State (with hyh)

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
PROGRESS=$(hyh_get_progress)
PENDING=$(echo "$PROGRESS" | jq '.pending')
RUNNING=$(echo "$PROGRESS" | jq '.running')
COMPLETED=$(echo "$PROGRESS" | jq '.completed')
TOTAL=$(echo "$PROGRESS" | jq '.total')

if [[ "$PENDING" -eq 0 && "$RUNNING" -eq 0 ]]; then
  echo "No pending tasks. Workflow complete."
  exit 0
fi

echo "Workflow status: $COMPLETED/$TOTAL completed, $RUNNING running, $PENDING pending"
```

## Step 2: Verify State

1. Query hyh for full state:
   ```bash
   uvx hyh get-state
   ```
2. Check git log to see completed work:
   ```bash
   git log --oneline --since="1 day ago"
   ```
3. Identify which tasks are completed vs pending

## Step 3: Ask User

Use AskUserQuestion:

```claude
AskUserQuestion:
  header: "Resume"
  question: "Continue workflow execution? ($COMPLETED/$TOTAL tasks completed, $PENDING pending, $RUNNING running)"
  multiSelect: false
  options:
    - label: "Continue"
      description: "Resume execution - agents will claim next available tasks"
    - label: "Review first"
      description: "Show completed work before continuing"
```

## Step 4: Execute (with hyh)

**If Continue:**
1. Re-dispatch agents - they will automatically claim uncompleted tasks
2. Agents call `uvx hyh task claim` to get their next task
3. Running tasks that timed out will be automatically reclaimed by hyh
4. No manual state file manipulation needed - hyh handles everything

**If Review first:**
1. Show git log with diff summary
2. Show hyh state with task statuses
3. Then ask again if ready to continue

## Step 5: Complete Workflow

After all tasks done:
1. Verify all tasks are completed:
   ```bash
   PROGRESS=$(hyh_get_progress)
   PENDING=$(echo "$PROGRESS" | jq '.pending')
   if [[ "$PENDING" -gt 0 ]]; then
     echo "Error: Workflow incomplete, $PENDING tasks pending"
     exit 1
   fi
   ```
2. Run code review (Task tool with dev-workflow:code-reviewer)
3. Use Skill("dev-workflow:receiving-code-review")
4. Use Skill("dev-workflow:finishing-a-development-branch")
5. No state file cleanup needed - hyh manages state lifecycle
