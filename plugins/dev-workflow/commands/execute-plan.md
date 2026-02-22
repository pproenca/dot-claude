---
description: Execute implementation plan with progress tracking
argument-hint: [plan-file]
allowed-tools: Read, Write, Bash, TaskCreate, TaskUpdate, TaskList, TaskGet, Task, Skill, AskUserQuestion
---

# Execute Plan

Execute implementation plan with TaskCreate/TaskUpdate tracking and mandatory post-completion actions.

## Input

$ARGUMENTS

If empty or file not found: stop with error "Plan file not found or not specified."

## Step 1: Worktree Decision

Check if working in main repo or already in a worktree:

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/worktree-manager.sh"

if is_main_repo; then
  echo "IN_MAIN_REPO=true"
else
  echo "IN_MAIN_REPO=false"
  echo "Already in worktree: $(basename "$(pwd)")"
fi
```

**If already in worktree:** skip creation, proceed to Step 2.

**If in main repo:**

```claude
AskUserQuestion:
  header: "Worktree"
  question: "Create isolated worktree for this work?"
  multiSelect: false
  options:
    - label: "Yes (Recommended)"
      description: "Creates ../repo--branch, switches current session to it"
    - label: "No"
      description: "Work directly in main repo"
```

If yes, create worktree:

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/worktree-manager.sh"
PLAN_FILE="$ARGUMENTS"
PLAN_BASENAME="${PLAN_FILE##*/}"
PLAN_BASENAME="${PLAN_BASENAME%.md}"
BRANCH_NAME="$(echo "$PLAN_BASENAME" | sed 's/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-//')"
WORKTREE_PATH="$(create_worktree "$BRANCH_NAME")"
cd "$WORKTREE_PATH" && pwd
```

**Role: Orchestrator.** You coordinate task execution via Task agents, collect results, and run reviews. You do not implement tasks directly. If you find yourself writing implementation code, stop — dispatch a Task agent instead.

## Step 2: Read Plan and Create Tasks

```bash
PLAN_FILE="$ARGUMENTS"
if [[ ! -f "$PLAN_FILE" ]]; then
  echo "ERROR: Plan file not found: $PLAN_FILE"
  exit 1
fi
grep -E "^### Task [0-9]+(\.[0-9]+)?:" "$PLAN_FILE" | sed 's/^### Task \([0-9.]*\): \(.*\)/Task \1: \2/'
```

Create a task for each plan task using TaskCreate, plus "Code Review" and "Finish Branch" at the end.

Set dependencies with TaskUpdate `addBlockedBy`: tasks touching the same files must have the later blocked by the earlier. Tasks with no file overlap run in parallel.

## Step 3: Execute Tasks

### 3a. Find Executable Tasks

```claude
TaskList  # Shows status and blockedBy for all tasks
```

Identify tasks that are `pending` with all blockers completed.

### 3b. Launch Parallel Tasks

Launch all unblocked tasks in ONE message with `run_in_background: true`:

```claude
Task:
  subagent_type: general-purpose
  model: opus
  description: "Execute Task 1"
  prompt: "[Task content + instructions from template below]"
  run_in_background: true

Task:
  subagent_type: general-purpose
  model: opus
  description: "Execute Task 3"
  prompt: "[Task content + instructions from template below]"
  run_in_background: true
```

Mark launched tasks `in_progress` via TaskUpdate.

### 3c. Collect Results

After launching all tasks, collect results:

```claude
TaskOutput:
  task_id: task_1_id
  block: true

TaskOutput:
  task_id: task_3_id
  block: true
```

### 3d. Review and Mark Complete

Review each agent's report. If the report shows clear issues (missing requirements, test failures), dispatch the agent again to fix.

Mark reviewed tasks `completed` via TaskUpdate.

Check TaskList — previously blocked tasks may now be unblocked. Repeat from 3a until all implementation tasks complete.

### Task Agent Prompt Template

If a worktree was created, include `WORKTREE_PATH` so the agent works in the right directory.

```claude
Task:
  subagent_type: general-purpose
  model: opus
  description: "Execute Task [N]"
  prompt: |
    Execute Task [N] from the implementation plan.

    ## Working Directory

    WORKTREE_PATH="{{WORKTREE_PATH}}"

    All bash commands: `cd "$WORKTREE_PATH" && <command>`
    All file paths: absolute, e.g., `{{WORKTREE_PATH}}/src/file.py`

    If WORKTREE_PATH is empty, work in the current directory.

    ## Task Instructions

    [Full task content from plan file]

    ## How to Work

    1. Follow each step exactly as written
    2. After each test step, verify expected output matches
    3. Commit after tests pass
    4. If anything is unclear, ask for clarification — don't guess

    Do not add features not in the spec. Do not skip verification steps.

    ## Self-Review (before reporting back)

    Before reporting, check:

    **Spec compliance:**
    - Did I implement every requirement from the task spec?
    - Did I add anything NOT in the spec?
    - Do test assertions match spec expectations?

    **Code quality:**
    - Functions focused and single-purpose?
    - Names describe WHAT, not HOW?
    - Tests verify behavior, not mocks?
    - Follows existing codebase patterns?

    Fix any issues before reporting.

    ## Report Format

    - What you implemented (specific changes)
    - Files changed (with paths)
    - Test results (command and output)
    - Self-review findings and fixes
  run_in_background: true
```

## Step 4: Post-Completion Actions

After all implementation tasks complete:

### 4a. Code Review

Mark "Code Review" task `in_progress`.

```claude
Task:
  subagent_type: dev-workflow:code-reviewer
  model: opus
  run_in_background: true
  description: "Review all changes"
  prompt: "Review all changes from plan execution. Run: git diff main..HEAD. Focus on cross-cutting concerns and consistency."
```

Collect results with TaskOutput. Process feedback with `Skill("dev-workflow:receiving-code-review")`.

Mark "Code Review" `completed`.

### 4b. Finish Branch

Mark "Finish Branch" task `in_progress`.

Use `Skill("dev-workflow:finishing-a-development-branch")`.

Mark "Finish Branch" `completed`.

## Blocker Handling

If a task fails:

```claude
AskUserQuestion:
  header: "Blocker"
  question: "Task N failed. What to do?"
  multiSelect: false
  options:
    - label: "Retry"
      description: "Re-run the failed task"
    - label: "Skip"
      description: "Continue to next task"
    - label: "Stop"
      description: "Pause workflow, resume later"
```

## Resume

If session ends: re-run `/dev-workflow:execute-plan [plan-file]`. TaskList shows which tasks are complete. Skip completed, continue from first unblocked pending.

- `/dev-workflow:resume` — continue from task state
- `/dev-workflow:abandon` — mark all tasks deleted
