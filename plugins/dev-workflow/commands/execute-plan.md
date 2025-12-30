---
description: Execute implementation plan with progress tracking and post-completion actions
argument-hint: [plan-file]
allowed-tools: Read, Write, Bash, TodoWrite, Task, Skill, AskUserQuestion, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*
---

# Execute Plan

Execute implementation plan with TodoWrite tracking and mandatory post-completion actions.

**Model Requirements:**
- Orchestrator (this command): **Opus 4.5** - handles planning decisions, coordination
- Task execution agents: **Opus 4.5** - handles individual task implementation (TDD cycles)

## Input

$ARGUMENTS

**If empty or file not found:** Stop with error "Plan file not found or not specified"

## Step 1: Worktree Setup

Check if working in main repo and offer to create isolated worktree:

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/worktree-manager.sh"

# Check if in main repo (not already in a worktree)
if is_main_repo; then
  echo "IN_MAIN_REPO=true"
else
  echo "IN_MAIN_REPO=false"
  echo "Already in worktree: $(basename "$(pwd)")"
fi
```

**If IN_MAIN_REPO=true:**

```claude
AskUserQuestion:
  header: "Worktree"
  question: "Create isolated worktree for this work?"
  multiSelect: false
  options:
    - label: "Yes (Recommended)"
      description: "Create worktree with feature branch - keeps main clean"
    - label: "No"
      description: "Work directly in main repo"
```

**If user selects "Yes":**

Derive branch name from plan file (e.g., `2024-01-15-auth-feature.md` → `auth-feature`):

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/worktree-manager.sh"
PLAN_FILE="$ARGUMENTS"

# Extract feature name from plan filename (remove date prefix and extension)
BRANCH_NAME=$(basename "$PLAN_FILE" .md | sed 's/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-//')

# Create worktree and switch to it
WORKTREE_PATH=$(create_worktree "$BRANCH_NAME")
echo "WORKTREE_CREATED: $WORKTREE_PATH"
echo "BRANCH: $BRANCH_NAME"

# Change to worktree directory
cd "$WORKTREE_PATH"
pwd
```

**If user selects "No":** Continue in current directory.

## Step 2: Read Plan and Setup TodoWrite

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

Create TodoWrite with all tasks as `pending`, plus "Code Review" and "Finish Branch" at the end.

## Step 3: Execute Tasks in Parallel Groups

Tasks are grouped by file dependencies - tasks with no file overlap can run in parallel.

### 3a. Parse Task Groups

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
PLAN_FILE="$ARGUMENTS"

# Group tasks by file dependencies (max 5 per group)
GROUPS=$(group_tasks_by_dependency "$PLAN_FILE" 5)
# Output format: "group1:1,2,3|group2:4,5|group3:6"

echo "Task groups: $GROUPS"
```

### 3b. Execute Groups (Groups Serial, Tasks Parallel)

FOR EACH group in GROUPS:

1. **Parse group tasks**: Extract task IDs from group string
2. **Mark all group tasks `in_progress`** in TodoWrite
3. **Launch ALL tasks in group in ONE message** with `run_in_background: true`:

```claude
# Launch ALL group tasks in SINGLE message for true parallelism
# Example: Group has tasks 1, 2, 3

Task:
  subagent_type: general-purpose
  model: opus
  description: "Execute Task 1"
  prompt: |
    [Task 1 content from plan]

    ## Instructions
    [Same instructions as below]
  run_in_background: true

Task:
  subagent_type: general-purpose
  model: opus
  description: "Execute Task 2"
  prompt: |
    [Task 2 content from plan]

    ## Instructions
    [Same instructions as below]
  run_in_background: true

Task:
  subagent_type: general-purpose
  model: opus
  description: "Execute Task 3"
  prompt: |
    [Task 3 content from plan]

    ## Instructions
    [Same instructions as below]
  run_in_background: true
```

4. **Store all task IDs** returned from Task calls
5. **AFTER launching all**, collect results with TaskOutput:

```claude
# Collect results (order doesn't matter - all run in parallel)
TaskOutput:
  task_id: task_1_id
  block: true

TaskOutput:
  task_id: task_2_id
  block: true

TaskOutput:
  task_id: task_3_id
  block: true
```

6. **Run two-stage review** for all completed tasks in the group
7. **Mark group tasks `completed`** in TodoWrite
8. **Proceed to next group**

### Task Agent Prompt Template

```claude
Task:
  subagent_type: general-purpose
  model: opus
  description: "Execute Task [N]"
  prompt: |
    Execute Task [N] from the implementation plan.

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

### 3b. Two-Stage Review (MANDATORY)

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

### 3c. Update TodoWrite

Mark task `completed` in TodoWrite. Continue to next task.

---

## Step 4: Post-Completion Actions (MANDATORY)

After ALL tasks complete:

### 4a. Code Review

Mark "Code Review" `in_progress` in TodoWrite.

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

Mark "Code Review" `completed`.

### 4b. Finish Branch

Mark "Finish Branch" `in_progress` in TodoWrite.

Use `Skill("dev-workflow:finishing-a-development-branch")`.

Mark "Finish Branch" `completed`.

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
2. TodoWrite will show which tasks are complete
3. Skip completed tasks, continue from first pending

Commands:
- /dev-workflow:resume - Continue execution from TodoWrite state
- /dev-workflow:abandon - Clear TodoWrite and stop
