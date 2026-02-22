---
description: Execute implementation plan with progress tracking
argument-hint: [plan-file]
allowed-tools: Read, Write, Bash, TaskCreate, TaskUpdate, TaskList, TaskGet, Task, Skill, AskUserQuestion
---

# Execute Plan

Execute implementation plan with TaskCreate/TaskUpdate tracking and mandatory post-completion actions.

**Model Requirements:**
- Orchestrator (this command): **Opus 4.6** - handles planning decisions, coordination
- Task execution agents: **Opus 4.6** - handles individual task implementation (TDD cycles)

## Input

$ARGUMENTS

**If empty or file not found:** Stop with error "Plan file not found or not specified"

## Step 1: Worktree Decision

Check if working in main repo or already in a worktree:

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/worktree-manager.sh"

# Check if in main repo (not already in a worktree)
if is_main_repo; then
  echo "IN_MAIN_REPO=true"
else
  echo "IN_MAIN_REPO=false"
  CURRENT_DIR="$(pwd)"
  echo "Already in worktree: ${CURRENT_DIR##*/}"
fi
```

### If IN_MAIN_REPO=false (Already in Worktree)

Skip worktree creation. The current session is the isolated executor.
Proceed to **Step 1b: Orchestrator Role**.

### If IN_MAIN_REPO=true

```claude
AskUserQuestion:
  header: "Worktree"
  question: "Create isolated worktree session for this work?"
  multiSelect: false
  options:
    - label: "Yes - create worktree (Recommended)"
      description: "Creates ../repo--branch, switches to it in current session"
    - label: "No - work in main repo"
      description: "Execute directly in main repo (not recommended)"
```

**If user selects "Yes - create worktree":**

Create worktree and switch to it in current session:

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/worktree-manager.sh"
PLAN_FILE="$ARGUMENTS"

# Extract filename from path (avoid nested command substitutions)
PLAN_BASENAME="${PLAN_FILE##*/}"
PLAN_BASENAME="${PLAN_BASENAME%.md}"

# Remove date prefix using sed
BRANCH_NAME="$(echo "$PLAN_BASENAME" | sed 's/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-//')"

# Create sibling worktree
WORKTREE_PATH="$(create_worktree "$BRANCH_NAME")"
echo "Created worktree: $WORKTREE_PATH"
echo "Branch: $BRANCH_NAME"

# Change to worktree (plan file accessible via shared .git)
cd "$WORKTREE_PATH" && pwd
```

**Report and CONTINUE to Step 1b:**

```text
Worktree created and activated.

Location: $WORKTREE_PATH
Branch: $BRANCH_NAME

Proceeding with plan execution in current session...
```

**CONTINUE to Step 1b.** The current session continues as orchestrator.

**If user selects "No - work in main repo":**

Continue in current directory. Proceed to Step 1b.

## Step 1b: Orchestrator Role

**ROLE: ORCHESTRATOR**

You are the **ORCHESTRATOR** for this plan execution.

Your responsibilities:
- Coordinate task execution via Task agents
- Collect results via TaskOutput
- Run code reviews
- **YOU DO NOT IMPLEMENT TASKS DIRECTLY**

If you find yourself writing implementation code, STOP.
Implementation is done by Task agents, not by you.

Proceed to Step 2.

## Step 2: Read Plan and Create Tasks

Read the plan file and extract tasks:

```bash
PLAN_FILE="$ARGUMENTS"

# Verify plan exists
if [[ ! -f "$PLAN_FILE" ]]; then
  echo "ERROR: Plan file not found: $PLAN_FILE"
  exit 1
fi

# Extract task list from plan
grep -E "^### Task [0-9]+(\.[0-9]+)?:" "$PLAN_FILE" | sed 's/^### Task \([0-9.]*\): \(.*\)/Task \1: \2/'
```

Create a task for each plan task using TaskCreate, plus "Code Review" and "Finish Branch" at the end.

**Dependency setup:** After creating all tasks, use TaskUpdate with `addBlockedBy` to express file-overlap dependencies:
- Tasks that touch the same files MUST have the later task blocked by the earlier one
- Tasks with NO file overlap can run in parallel (no blockedBy needed)

Example:
```claude
# Task 1: Create user model (src/user.py)
TaskCreate:
  subject: "Task 1: Create user model"
  description: "[full task content from plan]"
  activeForm: "Implementing user model"

# Task 2: Extend user model (src/user.py) - OVERLAPS with Task 1
TaskCreate:
  subject: "Task 2: Extend user model"
  description: "[full task content from plan]"
  activeForm: "Extending user model"

# Task 3: Create product model (src/product.py) - INDEPENDENT
TaskCreate:
  subject: "Task 3: Create product model"
  description: "[full task content from plan]"
  activeForm: "Implementing product model"

# Set dependency: Task 2 blocked by Task 1 (file overlap)
TaskUpdate:
  taskId: "2"
  addBlockedBy: ["1"]
```

## Step 3: Execute Tasks

Use TaskList to find unblocked pending tasks and execute them in parallel.

### 3a. Find Executable Tasks

```claude
TaskList  # Shows all tasks with status and blockedBy
```

Identify tasks that are `pending` with empty `blockedBy` (or all blockers completed).

### 3b. Launch Parallel Tasks

Launch ALL unblocked tasks in ONE message with `run_in_background: true`:

```claude
# Launch ALL unblocked tasks in SINGLE message for true parallelism

Task:
  subagent_type: general-purpose
  model: opus
  description: "Execute Task 1"
  prompt: |
    [Task content from plan]

    ## Instructions
    [Same instructions as Task Agent Prompt Template below]
  run_in_background: true

Task:
  subagent_type: general-purpose
  model: opus
  description: "Execute Task 3"
  prompt: |
    [Task content from plan]

    ## Instructions
    [Same instructions as below]
  run_in_background: true
```

Mark launched tasks as `in_progress`:

```claude
TaskUpdate:
  taskId: "1"
  status: "in_progress"

TaskUpdate:
  taskId: "3"
  status: "in_progress"
```

### 3c. Collect Results

**AFTER launching all**, collect results with TaskOutput:

```claude
# Collect results (order doesn't matter - all run in parallel)
TaskOutput:
  task_id: task_1_id
  block: true

TaskOutput:
  task_id: task_3_id
  block: true
```

### 3d. Two-Stage Review (MANDATORY)

Run two-stage review for each completed task (see below).

### 3e. Mark Complete and Continue

Mark reviewed tasks as `completed`:

```claude
TaskUpdate:
  taskId: "1"
  status: "completed"

TaskUpdate:
  taskId: "3"
  status: "completed"
```

Check TaskList again — previously blocked tasks (like Task 2) are now unblocked. Repeat from 3a.

**Continue until all implementation tasks are completed.**

### Task Agent Prompt Template

**IMPORTANT:** If a worktree was created, include the `WORKTREE_PATH` in the prompt so the agent knows where to execute commands.

```claude
Task:
  subagent_type: general-purpose
  model: opus
  description: "Execute Task [N]"
  prompt: |
    Execute Task [N] from the implementation plan.

    ## Working Directory

    WORKTREE_PATH="{{WORKTREE_PATH}}"

    **CRITICAL:** All bash commands MUST use this pattern:
    ```bash
    cd "$WORKTREE_PATH" && <your-command>
    ```

    All file paths should be absolute, e.g., `{{WORKTREE_PATH}}/src/file.py`

    If WORKTREE_PATH is empty or not set, work in the current directory.

    ## Task Instructions

    [Read task section from plan file and include here]

    ## Before You Begin
    If anything is unclear about requirements, approach, or dependencies:
    **Ask questions now.** Raise concerns before starting work.

    ## Your Job
    1. Follow each Step exactly as written in the task instructions
    2. After each "Run test" step, verify the expected output matches
    3. Commit after tests pass

    ## While Working
    If you encounter something unexpected or blockers, **ask for clarification**.
    It's always OK to pause and clarify rather than guess.

    **DO NOT:**
    - Guess at unclear requirements
    - Make assumptions about intent
    - Add features not in the spec
    - Skip verification steps

    ## Before Reporting Back: Self-Review (MANDATORY)

    **Completeness:**
    - Did I fully implement everything in the spec?
    - Did I miss any requirements?

    **Quality:**
    - Is this my best work?
    - Are names clear and accurate?

    **Discipline:**
    - Did I avoid overbuilding (YAGNI)?
    - Did I follow existing patterns?

    **Testing:**
    - Do tests verify BEHAVIOR, not mocks?
    - Did I watch each test fail first?

    **Fix any issues before reporting.**

    ## Report Format
    - Task completed
    - What you implemented (specific changes)
    - Files changed (with paths)
    - Test results (command and output)
    - Self-review findings
  run_in_background: true
```

### WRONG Pattern (Functionally Sequential)

```claude
# DON'T DO THIS - defeats parallelism!
for each task:
  task_id = Task(agent, run_in_background: true)
  result = TaskOutput(task_id, block: true)  # Blocks immediately!
```

### CORRECT Pattern (True Parallel)

```claude
# DO THIS - launch all, then collect all
task_1_id = Task(agent, Task 1, run_in_background: true)
task_2_id = Task(agent, Task 2, run_in_background: true)
task_3_id = Task(agent, Task 3, run_in_background: true)
# All three running simultaneously

result_1 = TaskOutput(task_1_id, block: true)
result_2 = TaskOutput(task_2_id, block: true)
result_3 = TaskOutput(task_3_id, block: true)
```

### Two-Stage Review (MANDATORY)

After implementer completes, run two-stage review before marking task complete.

**Stage 1: Spec Compliance Review**

Verify implementer built exactly what was requested.

```claude
Task:
  subagent_type: general-purpose
  model: opus
  description: "Spec review Task [N]"
  prompt: |
    You are reviewing whether an implementation matches its specification.

    ## What Was Requested
    [Task content from plan]

    ## What Implementer Claims They Built
    [From implementer's report]

    ## CRITICAL: Do Not Trust the Report

    **DO:**
    - Read the actual code they wrote
    - Compare implementation to requirements line by line
    - Check for missing pieces
    - Look for extra features not requested

    ## Report

    ✅ SPEC COMPLIANT - All requirements met, no extras, no missing items.

    ❌ SPEC ISSUES - List specifically:
    - Missing: [requirement] not implemented
    - Extra: [feature] added but not in spec
```

**If spec issues found:** Dispatch implementer to fix, then re-run spec review.

**Stage 2: Code Quality Review**

After spec compliance passes:

```claude
Task:
  subagent_type: general-purpose
  model: opus
  description: "Quality review Task [N]"
  prompt: |
    Review code quality for Task [N]. Spec compliance already verified.

    ## Quality Criteria

    **Code Structure:**
    - Functions focused and single-purpose?
    - Follows existing codebase patterns?

    **Naming:**
    - Names describe WHAT, not HOW?

    **Testing:**
    - Tests verify BEHAVIOR, not mocks?

    ## Report

    ✅ APPROVED - No critical or important issues.

    ⚠️ ISSUES FOUND:
    - Critical: [issue] at [file:line]
    - Important: [issue] at [file:line]
```

**If critical/important issues found:** Dispatch implementer to fix, then re-run quality review.

---

## Step 4: Post-Completion Actions (MANDATORY)

After ALL implementation tasks complete:

### 4a. Code Review

Mark "Code Review" task `in_progress` via TaskUpdate.

```claude
Task:
  subagent_type: dev-workflow:code-reviewer
  model: opus
  run_in_background: true
  description: "Review all changes"
  prompt: |
    Review all changes from plan execution.
    Run: git diff main..HEAD
    Focus on cross-cutting concerns and consistency.
```

Wait for results:

```claude
TaskOutput:
  task_id: <code-reviewer-task-id>
  block: true
```

Use `Skill("dev-workflow:receiving-code-review")` to process feedback.

Mark "Code Review" `completed` via TaskUpdate.

### 4b. Finish Branch

Mark "Finish Branch" task `in_progress` via TaskUpdate.

Use `Skill("dev-workflow:finishing-a-development-branch")`.

Mark "Finish Branch" `completed` via TaskUpdate.

---

## Blocker Handling

If a task fails:

```claude
AskUserQuestion:
  header: "Blocker"
  question: "Task N failed. What to do?"
  multiSelect: false
  options:
    - label: "Skip"
      description: "Continue to next task"
    - label: "Retry"
      description: "Re-run the failed task"
    - label: "Stop"
      description: "Pause workflow, resume later"
```

---

## Resume Capability

If session ends unexpectedly:

1. Re-run `/dev-workflow:execute-plan [plan-file]`
2. TaskList will show which tasks are complete/pending/blocked
3. Skip completed tasks, continue from first unblocked pending
4. Previously expressed blockedBy dependencies are preserved

Commands:
- /dev-workflow:resume - Continue execution from task state
- /dev-workflow:abandon - Mark all tasks deleted and stop
