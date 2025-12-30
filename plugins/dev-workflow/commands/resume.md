---
description: Resume interrupted plan execution
allowed-tools: Read, Bash, TodoWrite, Task, Skill, AskUserQuestion, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*
---

# Resume Workflow

Resume execution of an interrupted plan from where it left off.

## Step 1: Check Current State

Check TodoWrite for current progress:

```claude
# Check TodoWrite state - the existing todo list shows current progress
# Pending tasks are those not yet completed
# Count completed vs total to show progress
```

Check git log for recent work:

```bash
git log --oneline --since="1 day ago" | head -20
```

## Step 2: Ask User

Use AskUserQuestion:

```claude
AskUserQuestion:
  header: "Resume"
  question: "Continue workflow execution?"
  multiSelect: false
  options:
    - label: "Continue"
      description: "Resume execution from first pending task"
    - label: "Review first"
      description: "Show completed work before continuing"
```

## Step 3: Execute

**If Continue:**

1. Read the original plan file
2. Check TodoWrite for pending tasks
3. Continue with `/dev-workflow:execute-plan [plan-file]`
4. The command will detect completed tasks in TodoWrite and skip them

**If Review first:**

1. Show git log with diff summary:
   ```bash
   git log --oneline --stat --since="1 day ago"
   ```
2. Then ask again if ready to continue

## Step 4: Complete Workflow

After all tasks done:

1. Run code review (Task tool with dev-workflow:code-reviewer)
2. Use Skill("dev-workflow:receiving-code-review")
3. Use Skill("dev-workflow:finishing-a-development-branch")
