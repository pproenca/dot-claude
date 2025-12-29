---
description: Execute implementation plan with progress tracking and post-completion actions
argument-hint: [plan-file]
allowed-tools: Read, Write, Bash, TodoWrite, Task, Skill, AskUserQuestion, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*
---

# Execute Plan

Execute implementation plan with state tracking and mandatory post-completion actions.

**Model Requirements:**
- Orchestrator (this command): **Opus 4.5** - handles planning decisions, state management, coordination
- Task execution agents: **Sonnet** - handles individual task implementation (TDD cycles)

## Input

$ARGUMENTS

**If empty or file not found:** Stop with error "Plan file not found or not specified"

## Step 1: Initialize State

Read plan and import into hyh:

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
PLAN_FILE="$ARGUMENTS"

# Verify plan exists
if [[ ! -f "$PLAN_FILE" ]]; then
  echo "ERROR: Plan file not found: $PLAN_FILE"
  exit 1
fi

# Import plan into hyh daemon
hyh_import_plan "$PLAN_FILE"

# Get workflow state from hyh
PROGRESS=$(hyh_get_progress)
TOTAL=$(echo "$PROGRESS" | jq -r '.total')
echo "HYH WORKFLOW IMPORTED"
echo "TOTAL_TASKS: $TOTAL"
```

**If TOTAL is 0:** Stop with error "No tasks found in plan. Tasks must use format: ### Task N: [Name]"

## Step 2: Setup TodoWrite

Extract task titles and create TodoWrite items:

```bash
grep -E "^### Task [0-9]+(\.[0-9]+)?:" "$PLAN_FILE" | sed 's/^### Task \([0-9.]*\): \(.*\)/Task \1: \2/'
```

Create TodoWrite with:
- All tasks from plan as `pending`
- "Code Review" as `pending`
- "Finish Branch" as `pending`

## Step 3: Choose Execution Mode

```claude
AskUserQuestion:
  header: "Mode"
  question: "How should tasks be executed?"
  multiSelect: false
  options:
    - label: "Sequential"
      description: "Execute tasks one by one with full TDD cycle"
    - label: "Parallel (Recommended)"
      description: "Run independent tasks concurrently via background agents"
```

---

## Sequential Execution

Execute tasks one by one using background agents with two-stage review after each task.

### Process Flow

```dot
digraph sequential {
    rankdir=TB;
    "Dispatch Implementer" -> "Wait for Completion";
    "Wait for Completion" -> "Spec Compliance Review";
    "Spec Compliance Review" -> "Spec Issues?" [shape=diamond];
    "Spec Issues?" -> "Implementer Fixes Spec Issues" [label="yes"];
    "Implementer Fixes Spec Issues" -> "Spec Compliance Review";
    "Spec Issues?" -> "Code Quality Review" [label="no"];
    "Code Quality Review" -> "Quality Issues?" [shape=diamond];
    "Quality Issues?" -> "Implementer Fixes Quality Issues" [label="yes"];
    "Implementer Fixes Quality Issues" -> "Code Quality Review";
    "Quality Issues?" -> "Mark Task Complete" [label="no"];
    "Mark Task Complete" -> "Next Task";
}
```

### 3a. Check for Interrupted Dispatch (Compact Recovery)

Check if a previous task was interrupted by checking hyh state:

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
PROGRESS=$(hyh_get_progress)
RUNNING=$(echo "$PROGRESS" | jq -r '.running')

if [[ "$RUNNING" -gt 0 ]]; then
  echo "RECOVERING: Found $RUNNING running task(s) in hyh"
fi
```

If tasks are running, they will be automatically reclaimed or resumed by hyh. No manual recovery needed.

### 3b. Execute Each Task

Mark task `in_progress` in TodoWrite.

Launch task in background:

```claude
Task:
  subagent_type: general-purpose
  model: sonnet
  description: "Execute next task from hyh"
  prompt: |
    Execute a task from the hyh-managed workflow.

    ## Step 1: Claim Your Task

    ```bash
    source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
    TASK=$(hyh_claim_task)
    TASK_ID=$(echo "$TASK" | jq -r '.task.id')
    INSTRUCTIONS=$(echo "$TASK" | jq -r '.task.instructions')

    echo "CLAIMED TASK: $TASK_ID"
    echo "INSTRUCTIONS:"
    echo "$INSTRUCTIONS"
    ```

    ## Step 2: Execute the Instructions

    Follow the instructions exactly as written in the task.

    ## Before You Begin
    If anything is unclear about requirements, approach, or dependencies:
    **Ask questions now.** Raise concerns before starting work.

    Questions to consider:
    - Are the requirements clear?
    - Do I understand the approach?
    - Are there dependencies I need to know about?
    - Anything ambiguous in the task description?

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

    Review your work with fresh eyes before reporting.

    **Completeness:**
    - Did I fully implement everything in the spec?
    - Did I miss any requirements?
    - Are there edge cases I didn't handle?

    **Quality:**
    - Is this my best work?
    - Are names clear and accurate (describe WHAT, not HOW)?
    - Is the code clean and maintainable?

    **Discipline:**
    - Did I avoid overbuilding (YAGNI)?
    - Did I only build what was requested?
    - Did I follow existing patterns in the codebase?

    **Testing:**
    - Do tests verify BEHAVIOR, not mock behavior?
    - Did I watch each test fail before implementing?
    - Are tests comprehensive for the requirements?

    **If you find issues during self-review, fix them now before reporting.**

    ## Step 3: Complete the Task

    After successfully implementing and verifying:

    ```bash
    source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
    hyh_complete_task "$TASK_ID"
    echo "TASK COMPLETED: $TASK_ID"
    ```

    ## Report Format

    When done, report:
    - Task ID completed
    - What you implemented (specific changes)
    - Files changed (with paths)
    - Test results (command and output)
    - Self-review findings (any issues found and fixed)
    - Any concerns or blockers
  run_in_background: true
```

Wait for completion:

```claude
TaskOutput:
  task_id: [agent_id]
  block: true
```

### 3c. Two-Stage Review (MANDATORY)

After implementer completes, run two-stage review before marking task complete.

**Stage 1: Spec Compliance Review**

Verify implementer built exactly what was requested (nothing more, nothing less).

```claude
Task:
  subagent_type: general-purpose
  model: sonnet
  description: "Spec review Task [N]"
  prompt: |
    You are reviewing whether an implementation matches its specification.

    ## What Was Requested
    [Task content from plan]

    ## What Implementer Claims They Built
    [From implementer's report]

    ## CRITICAL: Do Not Trust the Report

    The implementer may have been incomplete, inaccurate, or optimistic.
    You MUST verify everything independently.

    **DO NOT:**
    - Take their word for what they implemented
    - Trust their claims about completeness
    - Assume tests passing means spec is met

    **DO:**
    - Read the actual code they wrote
    - Compare implementation to requirements line by line
    - Check for missing pieces
    - Look for extra features not requested

    ## Your Job

    **Missing requirements:**
    - Did they implement everything requested?
    - Are there requirements they skipped?
    - Did they claim something but not implement it?

    **Extra/unneeded work:**
    - Did they build things not requested?
    - Did they over-engineer or add unnecessary features?

    **Misunderstandings:**
    - Did they interpret requirements differently than intended?
    - Did they solve the wrong problem?

    ## Report

    Report ONE of:

    ✅ SPEC COMPLIANT - All requirements met, no extras, no missing items.

    ❌ SPEC ISSUES - List specifically:
    - Missing: [requirement] not implemented
    - Extra: [feature] added but not in spec
    - Misunderstood: [requirement] interpreted as [wrong thing]
```

**If spec issues found:** Dispatch implementer to fix, then re-run spec review.

```claude
Task:
  subagent_type: general-purpose
  model: sonnet
  description: "Fix spec issues Task [N]"
  prompt: |
    Fix the following spec compliance issues for Task [N]:

    [Issues from spec reviewer]

    Fix each issue. Do not add anything else.
    Report what you fixed.
```

Loop until spec compliance passes.

**Stage 2: Code Quality Review**

After spec compliance passes, review implementation quality.

```claude
Task:
  subagent_type: general-purpose
  model: sonnet
  description: "Quality review Task [N]"
  prompt: |
    Review code quality for Task [N]. Spec compliance already verified.

    ## Changes to Review
    [Files from implementer report]

    ## Quality Criteria

    **Code Structure:**
    - Functions focused and single-purpose?
    - Complexity appropriate (not over-engineered)?
    - Follows existing codebase patterns?

    **Naming:**
    - Names describe WHAT, not HOW?
    - Names accurate and consistent?

    **Testing:**
    - Tests verify BEHAVIOR, not mocks?
    - Test setup minimal and clear?
    - Test names descriptive?

    ## Severity Levels

    **Critical** - Must fix: Security issues, data corruption, tests that don't test behavior
    **Important** - Should fix: Unclear naming, over-engineering, maintainability issues
    **Minor** - Nice to fix: Style, verbosity

    ## Report

    ✅ APPROVED - No critical or important issues.

    ⚠️ ISSUES FOUND:
    - Critical: [issue] at [file:line] - [fix needed]
    - Important: [issue] at [file:line] - [fix needed]
```

**If critical/important issues found:** Dispatch implementer to fix, then re-run quality review.

Loop until quality review passes.

### 3d. Update State After Each Task

Only after BOTH reviews pass:

Mark task `completed` in TodoWrite. Task is already marked complete in hyh by the agent. Continue to next task.

---

## Parallel Execution (Background Agents)

Uses `Task(run_in_background)` + `TaskOutput` pattern with two-stage review after each group.

**Note:** In parallel mode, review happens after group completion (not per-task) to maximize parallelism while maintaining quality gates.

### 3a. Check for Interrupted Dispatch (Compact Recovery)

Check hyh state for any running tasks:

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
PROGRESS=$(hyh_get_progress)
RUNNING=$(echo "$PROGRESS" | jq -r '.running')

echo "RUNNING TASKS: $RUNNING"
```

If tasks are running, they will be automatically reclaimed or resumed by hyh. No manual recovery needed.

### 3b. Analyze Task Groups

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
PLAN_FILE="$ARGUMENTS"

# Group tasks by file dependencies
# Tasks in same group have NO file overlap → can run parallel
# Groups execute serially (group1 completes before group2 starts)
TASK_GROUPS=$(group_tasks_by_dependency "$PLAN_FILE" 5)
MAX_PARALLEL=$(get_max_parallel_from_groups "$TASK_GROUPS")

echo "TASK_GROUPS: $TASK_GROUPS"
echo "MAX_PARALLEL: $MAX_PARALLEL"
```

### 3c. Execute Groups Serially, Tasks in Parallel

For each group in `TASK_GROUPS` (split by `|`):

**If group has multiple tasks** (e.g., `group1:1,2,3`):

1. Launch ALL agents in the group simultaneously using `Task(run_in_background: true)`:

```claude
# Launch in SINGLE message for true parallelism
Task:
  subagent_type: general-purpose
  model: sonnet
  description: "Execute task from hyh (agent 1)"
  prompt: |
    Execute a task from the hyh-managed workflow.

    ## Step 1: Claim Your Task

    ```bash
    source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
    TASK=$(hyh_claim_task)
    TASK_ID=$(echo "$TASK" | jq -r '.task.id')
    INSTRUCTIONS=$(echo "$TASK" | jq -r '.task.instructions')

    echo "CLAIMED TASK: $TASK_ID"
    echo "INSTRUCTIONS:"
    echo "$INSTRUCTIONS"
    ```

    ## Step 2: Execute the Instructions

    Follow the instructions exactly as written in the task.

    ## Before You Begin
    If anything is unclear: **Ask questions now.** Raise concerns before starting.

    Questions to consider:
    - Are the requirements clear?
    - Do I understand the approach?
    - Are there dependencies I need to know about?

    ## Your Job
    1. Follow each Step exactly as written in the task instructions
    2. After each "Run test" step, verify expected output matches
    3. Commit after tests pass

    ## While Working
    If blocked or unexpected, **ask for clarification** rather than guess.

    **DO NOT:**
    - Guess at unclear requirements
    - Make assumptions about intent
    - Add features not in the spec
    - Skip verification steps

    ## Before Reporting Back: Self-Review (MANDATORY)

    **Completeness:**
    - Did I fully implement everything in the spec?
    - Did I miss any requirements?
    - Are there edge cases I didn't handle?

    **Quality:**
    - Is this my best work?
    - Are names clear and accurate?

    **Discipline:**
    - Did I avoid overbuilding (YAGNI)?
    - Did I only build what was requested?
    - Did I follow existing patterns?

    **Testing:**
    - Do tests verify BEHAVIOR, not mocks?
    - Did I watch each test fail first?

    **Fix any issues before reporting.**

    ## Step 3: Complete the Task

    After successfully implementing and verifying:

    ```bash
    source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
    hyh_complete_task "$TASK_ID"
    echo "TASK COMPLETED: $TASK_ID"
    ```

    ## Report Format
    - Task ID completed
    - What you implemented
    - Files changed (with paths)
    - Test results
    - Self-review findings
  run_in_background: true

Task:
  subagent_type: general-purpose
  model: sonnet
  description: "Execute task from hyh (agent 2)"
  prompt: |
    [Same comprehensive prompt structure as agent 1]
  run_in_background: true
```

2. Wait for ALL agents in the group to complete:

```claude
# Wait for all background agents
TaskOutput:
  task_id: [agent_id_1]
  block: true

TaskOutput:
  task_id: [agent_id_2]
  block: true
```

4. **Two-Stage Group Review**

After group implementation completes, run combined review for all tasks in the group.

**Stage 1: Spec Compliance Review (all tasks in group)**

```claude
Task:
  subagent_type: general-purpose
  model: sonnet
  description: "Spec review Group [N]"
  prompt: |
    Review spec compliance for Tasks [list] completed in this group.

    ## Requirements for Each Task
    [Task specs from plan]

    ## Implementer Reports
    [Reports from each implementer]

    ## CRITICAL: Do Not Trust Reports

    Verify each task independently:
    - Read actual code, not just reports
    - Check each requirement is met
    - Look for missing pieces or extras

    ## Report

    For EACH task, report:
    - ✅ Task N: SPEC COMPLIANT
    - ❌ Task N: ISSUES - [list missing/extra/misunderstood]
```

**If any task has spec issues:** Dispatch fix agents for those specific tasks, then re-review.

**Stage 2: Code Quality Review (all tasks in group)**

After spec compliance passes for all tasks:

```claude
Task:
  subagent_type: general-purpose
  model: sonnet
  description: "Quality review Group [N]"
  prompt: |
    Review code quality for Tasks [list]. Spec compliance verified.

    ## Quality Criteria
    - Code structure (focused, not over-engineered)
    - Naming (WHAT not HOW)
    - Testing (behavior not mocks)

    ## Report

    For EACH task:
    - ✅ Task N: APPROVED
    - ⚠️ Task N: ISSUES - [Critical/Important issues with file:line]
```

**If critical/important issues:** Dispatch fix agents, then re-review.

5. Mark completed tasks in TodoWrite.

Tasks are already marked complete in hyh by the agents. No state file updates needed.

**If group has single task** (e.g., `group3:5`):

Use same pattern as sequential execution (two-stage review per task).

### 3d. Why This Pattern Works

| Aspect | Benefit |
|--------|---------|
| **Dependencies respected** | hyh DAG ensures dependencies satisfied before claiming |
| **True parallelism** | Multiple agents claim tasks simultaneously |
| **Quality gates** | Two-stage review catches issues before next group |
| **No context leak** | Task content claimed from hyh, not loaded into orchestrator |
| **Accurate progress** | hyh daemon tracks state atomically |
| **Resume works** | hyh state survives crashes and session restarts |

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

### 4c. Cleanup State

No cleanup needed. hyh daemon maintains workflow state. If workflow should be cleared:

```bash
uvx hyh plan reset
echo "Workflow complete. State cleared."
```

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
      description: "Pause workflow, resume later with /dev-workflow:resume"
```

---

## Resume Capability

If session ends unexpectedly, hyh daemon maintains workflow state. Resume by:

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
PROGRESS=$(hyh_get_progress)
echo "WORKFLOW STATUS:"
echo "$PROGRESS" | jq '.'

# Resume execution by continuing to dispatch agents
# They will claim the next available tasks from hyh
```

Commands:
- /dev-workflow:resume - Continue execution (dispatch more agents)
- /dev-workflow:abandon - Clear state via `uvx hyh plan reset`
