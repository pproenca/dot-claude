# Upgrade dev-workflow to Claude Code 2.1.39 + Opus 4.6

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Modernize the dev-workflow plugin to use Claude Code 2.1.39 primitives and Opus 4.6 model references.

**Architecture:** Replace TodoWrite with TaskCreate/TaskUpdate/TaskList/TaskGet in all frontmatter and command bodies. Remove deprecated tools (LS, NotebookRead, KillShell, SlashCommand). Update ExitPlanMode usage (swarm params removed). Clean Serena MCP references. Delete stale reference docs (tools.md, hooks.md). Update marketplace-level validation constants.

**Tech Stack:** Bash (bats tests), Markdown (skills/commands/agents), JSON (hooks.json), Shell (validation scripts)

---

### Task 1: Update marketplace-level validation constants

**Files:**
- Modify: `scripts/lib/constants.sh:14-33`
- Modify: `plugins/dev-workflow/scripts/validate.sh:101`

**Step 1: Update constants.sh valid tools list**

In `scripts/lib/constants.sh`, replace the `VALID_BUILTIN_TOOLS` array (lines 14-33) with the updated list:

```bash
# Built-in Claude Code tools
VALID_BUILTIN_TOOLS=(
  "AskUserQuestion"
  "Bash"
  "Edit"
  "EnterPlanMode"
  "ExitPlanMode"
  "Glob"
  "Grep"
  "NotebookEdit"
  "Read"
  "Skill"
  "Task"
  "TaskCreate"
  "TaskGet"
  "TaskList"
  "TaskOutput"
  "TaskStop"
  "TaskUpdate"
  "WebFetch"
  "WebSearch"
  "Write"
)
```

Removed: `BashOutput`, `KillShell`, `LSP`, `SlashCommand`, `TodoWrite`
Added: `EnterPlanMode`, `ExitPlanMode`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskOutput`, `TaskStop`, `TaskUpdate`

**Step 2: Update validate.sh valid tools list**

In `plugins/dev-workflow/scripts/validate.sh`, replace line 101:

```bash
VALID_TOOLS="Read|Write|Edit|Bash|Glob|Grep|Task|TaskCreate|TaskUpdate|TaskList|TaskGet|TaskStop|TaskOutput|AskUserQuestion|Skill|WebFetch|WebSearch|NotebookEdit"
```

Removed: `TodoWrite`, `NotebookRead`, `LS`
Added: `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet`, `TaskStop`, `TaskOutput`

**Step 3: Add haiku to valid models**

In `scripts/lib/constants.sh`, update `VALID_MODELS`:

```bash
VALID_MODELS=(
  "haiku"
  "sonnet"
  "opus"
)
```

**Step 4: Run validation to confirm constants work**

Run: `./plugins/dev-workflow/scripts/validate.sh`
Expected: Some failures (tools not yet updated in frontmatter) — that's expected. Just verify the script itself runs without bash errors.

**Step 5: Commit**

```bash
git add scripts/lib/constants.sh plugins/dev-workflow/scripts/validate.sh
git commit -m "chore: update valid tools for Claude Code 2.1.39"
```

---

### Task 2: Delete stale reference docs

**Files:**
- Delete: `plugins/dev-workflow/tools.md`
- Delete: `plugins/dev-workflow/hooks.md`

**Step 1: Delete the files**

```bash
rm plugins/dev-workflow/tools.md plugins/dev-workflow/hooks.md
```

**Step 2: Verify no critical references exist**

Search for references to these files:

```bash
grep -r "tools\.md\|hooks\.md" plugins/dev-workflow/ --include="*.md" --include="*.sh" --include="*.json" | grep -v ".git"
```

If any references found, note them — they'll be cleaned in later tasks when those files are edited.

**Step 3: Commit**

```bash
git add -A plugins/dev-workflow/tools.md plugins/dev-workflow/hooks.md
git commit -m "chore: remove stale tools.md and hooks.md reference docs"
```

---

### Task 3: Update all skill frontmatter (remove Serena, swap TodoWrite)

**Files:**
- Modify: `plugins/dev-workflow/skills/getting-started/SKILL.md:4`
- Modify: `plugins/dev-workflow/skills/test-driven-development/SKILL.md:4`
- Modify: `plugins/dev-workflow/skills/systematic-debugging/SKILL.md:4`
- Modify: `plugins/dev-workflow/skills/receiving-code-review/SKILL.md:4`
- Modify: `plugins/dev-workflow/skills/finishing-a-development-branch/SKILL.md:4`
- Modify: `plugins/dev-workflow/skills/root-cause-tracing/SKILL.md:4`
- Modify: `plugins/dev-workflow/skills/condition-based-waiting/SKILL.md:4`
- Modify: `plugins/dev-workflow/skills/testing-anti-patterns/SKILL.md:4`

**Step 1: Update getting-started frontmatter**

In `plugins/dev-workflow/skills/getting-started/SKILL.md`, change line 4:
```yaml
allowed-tools: Read, Skill, TaskCreate, TaskUpdate, TaskList
```
(Was: `Read, Skill, TodoWrite, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*`)

**Step 2: Update test-driven-development frontmatter**

In `plugins/dev-workflow/skills/test-driven-development/SKILL.md`, change line 4:
```yaml
allowed-tools: Read, Edit, Bash
```
(Was: `Read, Edit, Bash, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*`)

**Step 3: Update systematic-debugging frontmatter**

In `plugins/dev-workflow/skills/systematic-debugging/SKILL.md`, change line 4:
```yaml
allowed-tools: Read, Bash, Grep, Skill
```
(Was: `Read, Bash, Grep, Skill, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*`)

**Step 4: Update receiving-code-review frontmatter**

In `plugins/dev-workflow/skills/receiving-code-review/SKILL.md`, change line 4:
```yaml
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Skill
```
(Was: `Read, Write, Edit, Bash, Grep, Glob, Skill, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*`)

**Step 5: Update finishing-a-development-branch frontmatter**

In `plugins/dev-workflow/skills/finishing-a-development-branch/SKILL.md`, change line 4:
```yaml
allowed-tools: Read, Bash, AskUserQuestion
```
(Was: `Read, Bash, AskUserQuestion, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*`)

**Step 6: Update root-cause-tracing frontmatter**

In `plugins/dev-workflow/skills/root-cause-tracing/SKILL.md`, change line 4:
```yaml
allowed-tools: Read, Bash, Grep, Glob
```
(Was: `Read, Bash, Grep, Glob, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*`)

**Step 7: Update condition-based-waiting frontmatter**

In `plugins/dev-workflow/skills/condition-based-waiting/SKILL.md`, change line 4:
```yaml
allowed-tools: Read, Bash
```
(Was: `Read, Bash, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*`)

**Step 8: Update testing-anti-patterns frontmatter**

In `plugins/dev-workflow/skills/testing-anti-patterns/SKILL.md`, change line 4:
```yaml
allowed-tools: Read, Grep, Glob
```
(Was: `Read, Grep, Glob, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*`)

**Step 9: Run validation**

Run: `./plugins/dev-workflow/scripts/validate.sh`
Expected: Skills section should all PASS.

**Step 10: Commit**

```bash
git add plugins/dev-workflow/skills/
git commit -m "chore(skills): remove Serena refs, swap TodoWrite for TaskCreate/Update"
```

---

### Task 4: Update all command frontmatter (remove Serena, swap TodoWrite)

**Files:**
- Modify: `plugins/dev-workflow/commands/execute-plan.md:4`
- Modify: `plugins/dev-workflow/commands/write-plan.md:4`
- Modify: `plugins/dev-workflow/commands/resume.md:4`
- Modify: `plugins/dev-workflow/commands/abandon.md:4`
- Modify: `plugins/dev-workflow/commands/brainstorm.md:4`
- Modify: `plugins/dev-workflow/commands/user-story.md:4`

**Step 1: Update execute-plan frontmatter**

In `plugins/dev-workflow/commands/execute-plan.md`, change line 4:
```yaml
allowed-tools: Read, Write, Bash, TaskCreate, TaskUpdate, TaskList, TaskGet, Task, Skill, AskUserQuestion
```
(Was: `Read, Write, Bash, TodoWrite, Task, Skill, AskUserQuestion, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*`)

**Step 2: Update write-plan frontmatter**

In `plugins/dev-workflow/commands/write-plan.md`, change line 4:
```yaml
allowed-tools: Read, Write, Grep, Glob, Bash, TaskCreate, TaskUpdate, TaskList, AskUserQuestion, Task
```
(Was: `Read, Write, Grep, Glob, Bash, TodoWrite, AskUserQuestion, Task, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*`)

**Step 3: Update resume frontmatter**

In `plugins/dev-workflow/commands/resume.md`, change line 4:
```yaml
allowed-tools: Read, Bash, TaskList, TaskGet, TaskUpdate, Task, Skill, AskUserQuestion
```
(Was: `Read, Bash, TodoWrite, Task, Skill, AskUserQuestion, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*`)

**Step 4: Update abandon frontmatter**

In `plugins/dev-workflow/commands/abandon.md`, change line 4:
```yaml
allowed-tools: Bash, TaskList, TaskUpdate, AskUserQuestion
```
(Was: `Bash, TodoWrite, AskUserQuestion, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*`)

**Step 5: Update brainstorm frontmatter**

In `plugins/dev-workflow/commands/brainstorm.md`, change line 4:
```yaml
allowed-tools: Read, Write, Bash, Grep, Glob, AskUserQuestion
```
(Was: `Read, Write, Bash, Grep, Glob, AskUserQuestion, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*`)

**Step 6: Update user-story frontmatter**

In `plugins/dev-workflow/commands/user-story.md`, change line 4:
```yaml
allowed-tools: Read, Write, Bash, Grep, Glob, AskUserQuestion, TaskCreate, TaskUpdate, TaskList, Task
```
(Was: `Read, Write, Bash, Grep, Glob, AskUserQuestion, TodoWrite, Task`)

**Step 7: Run validation**

Run: `./plugins/dev-workflow/scripts/validate.sh`
Expected: Commands section should all PASS.

**Step 8: Commit**

```bash
git add plugins/dev-workflow/commands/
git commit -m "chore(commands): remove Serena refs, swap TodoWrite for TaskCreate/Update"
```

---

### Task 5: Update agent definitions (remove LS, update body text)

**Files:**
- Modify: `plugins/dev-workflow/agents/code-architect.md:50`
- Modify: `plugins/dev-workflow/agents/code-explorer.md:47,78`

**Step 1: Verify code-architect tools**

Read `plugins/dev-workflow/agents/code-architect.md` line 50:
```yaml
tools: Glob, Grep, Read, WebFetch, WebSearch
```
No LS present — already clean. No change needed.

**Step 2: Verify code-explorer tools**

Read `plugins/dev-workflow/agents/code-explorer.md` line 47:
```yaml
tools: Glob, Grep, Read
```
No LS in frontmatter — already clean. No change needed in frontmatter.

**Step 3: Update code-explorer body text**

In `plugins/dev-workflow/agents/code-explorer.md`, line 78 says:
```markdown
Use the LS and Glob tools to understand project layout:
```

Change to:
```markdown
Use Glob and Bash (ls) to understand project layout:
```

**Step 4: Verify code-reviewer tools**

Read `plugins/dev-workflow/agents/code-reviewer.md` line 49:
```yaml
tools: Glob, Grep, Read, Bash
```
Already clean. No change needed.

**Step 5: Run validation**

Run: `./plugins/dev-workflow/scripts/validate.sh`
Expected: Agents section should all PASS.

**Step 6: Commit**

```bash
git add plugins/dev-workflow/agents/
git commit -m "chore(agents): remove LS references"
```

---

### Task 6: Rewrite execute-plan command body

This is the biggest change — replacing TodoWrite with TaskCreate/TaskUpdate and removing swarm/group_tasks_by_dependency.

**Files:**
- Modify: `plugins/dev-workflow/commands/execute-plan.md:9-474`

**Step 1: Rewrite execute-plan.md**

Replace the entire body (lines 9 onwards) of `plugins/dev-workflow/commands/execute-plan.md` with:

````markdown
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
````

**Step 2: Run validation**

Run: `./plugins/dev-workflow/scripts/validate.sh`
Expected: execute-plan should PASS (valid frontmatter, valid tools).

**Step 3: Commit**

```bash
git add plugins/dev-workflow/commands/execute-plan.md
git commit -m "feat(execute-plan): rewrite for Claude 2.1.39 task primitives"
```

---

### Task 7: Update getting-started skill body

**Files:**
- Modify: `plugins/dev-workflow/skills/getting-started/SKILL.md:72-163`

**Step 1: Replace TodoWrite references in body**

In `plugins/dev-workflow/skills/getting-started/SKILL.md`:

Change line 72-75 (section "Skills with Checklists"):
```markdown
## Skills with Checklists

If a skill contains a checklist, create tasks using TaskCreate for each step.

Mental tracking of checklists leads to skipped steps. TaskCreate/TaskUpdate makes progress visible.
```
(Was: references to TodoWrite)

**Step 2: Update Planning Workflows section**

Replace lines 127-145 (parallel execution description):

```markdown
### How Parallel Execution Works

The `/dev-workflow:execute-plan` command uses background agents for parallelism:

```
1. Create tasks with TaskCreate, expressing dependencies via addBlockedBy
2. FOR each round of unblocked tasks:
   a. Launch tasks with Task(run_in_background: true)
   b. Wait for all with TaskOutput(block: true)
   c. Mark completed with TaskUpdate
   d. Check TaskList for newly unblocked tasks
3. Proceed to post-completion actions
```

This approach:
- Preserves plan in `docs/plans/` for version control
- Respects task dependencies (blockedBy ensures correct ordering)
- No context leak (task content passed to agents only)
- Accurate progress tracking (TaskList shows real-time state)
```

**Step 3: Remove swarm references**

Replace lines 296-310 (Swarm Execution section):

```markdown
### Parallel Execution

Use `ExitPlanMode` to finish planning. For parallel execution, use the plugin commands flow:

```
/dev-workflow:write-plan → /dev-workflow:execute-plan
```

The execute-plan command handles parallelism via Task agents with `run_in_background: true`. Dependencies expressed via `addBlockedBy` ensure correct ordering.
```

**Step 4: Update State Persistence section**

Replace lines 313-326:

```markdown
### State Persistence (Resume Capability)

**State is managed by TaskCreate/TaskUpdate.** Tasks are tracked as pending/in_progress/completed with dependency tracking via blockedBy.

The plan file in `docs/plans/` is the source of truth for task definitions.

**If session ends unexpectedly:**
1. Re-run `/dev-workflow:execute-plan [plan-file]`
2. TaskList shows which tasks are complete
3. Skip completed tasks, continue from first unblocked pending

Commands:
- /dev-workflow:resume - Continue execution from task state
- /dev-workflow:abandon - Mark tasks deleted and stop
```

**Step 5: Update Post-Execution Actions**

In the Post-Execution Actions section, the TaskOutput usage is already correct. Just update the text "TodoWrite" → "TaskUpdate" if present.

**Step 6: Run validation**

Run: `./plugins/dev-workflow/scripts/validate.sh`
Expected: PASS for getting-started skill.

**Step 7: Commit**

```bash
git add plugins/dev-workflow/skills/getting-started/SKILL.md
git commit -m "feat(getting-started): update for Claude 2.1.39 task primitives"
```

---

### Task 8: Update resume and abandon command bodies

**Files:**
- Modify: `plugins/dev-workflow/commands/resume.md:9-66`
- Modify: `plugins/dev-workflow/commands/abandon.md:9-76`

**Step 1: Rewrite resume.md body**

Replace lines 9 onwards of `plugins/dev-workflow/commands/resume.md`:

````markdown
# Resume Workflow

Resume execution of an interrupted plan from where it left off.

## Step 1: Check Current State

Check task state for current progress:

```claude
TaskList  # Shows all tasks with status, blockedBy, and ownership
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
      description: "Resume execution from first unblocked pending task"
    - label: "Review first"
      description: "Show completed work before continuing"
```

## Step 3: Execute

**If Continue:**

1. Read the original plan file
2. Check TaskList for pending unblocked tasks
3. Continue with `/dev-workflow:execute-plan [plan-file]`
4. The command will detect completed tasks via TaskList and skip them

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
````

**Step 2: Rewrite abandon.md body**

Replace lines 9 onwards of `plugins/dev-workflow/commands/abandon.md`:

````markdown
# Abandon Workflow

Discard the active workflow state. Use this when you want to start fresh or the previous plan is no longer relevant.

## Step 1: Show Current State and Check for Unpushed Work

Check task state for current progress:

```claude
TaskList  # Shows all tasks with status
```

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
  echo "WARNING: Branch '$CURRENT_BRANCH' has NEVER been pushed to remote!"
  echo "    Abandoning may result in loss of work if worktree is deleted."
  echo "    Recommend: git push -u origin $CURRENT_BRANCH"
else
  # Check for unpushed commits
  UNPUSHED=$(git log "origin/$CURRENT_BRANCH..$CURRENT_BRANCH" --oneline 2>/dev/null || echo "")
  if [[ -n "$UNPUSHED" ]]; then
    echo ""
    echo "WARNING: You have unpushed commits on '$CURRENT_BRANCH':"
    echo "$UNPUSHED"
    echo ""
    echo "    Recommend pushing first: git push origin $CURRENT_BRANCH"
  else
    echo "Branch is up to date with remote."
  fi
fi
```

## Step 2: Confirm

Use AskUserQuestion:

```claude
AskUserQuestion:
  header: "Confirm"
  question: "Clear all tasks and abandon workflow? Completed commits will remain, but tracking will be lost."
  multiSelect: false
  options:
    - label: "Yes, abandon"
      description: "Delete all tasks and start fresh"
    - label: "Cancel"
      description: "Keep workflow for later resume"
```

## Step 3: Clear State

**If Yes, abandon:**

Mark all pending/in_progress tasks as deleted:

```claude
# For each task in TaskList that is not completed:
TaskUpdate:
  taskId: "<id>"
  status: "deleted"
```

Report: "Workflow abandoned. You can start a new workflow with /dev-workflow:brainstorm or EnterPlanMode."

**If Cancel:**

Report: "Workflow preserved. Use /dev-workflow:resume to continue."
````

**Step 3: Run validation**

Run: `./plugins/dev-workflow/scripts/validate.sh`
Expected: PASS for resume and abandon commands.

**Step 4: Commit**

```bash
git add plugins/dev-workflow/commands/resume.md plugins/dev-workflow/commands/abandon.md
git commit -m "feat(resume,abandon): update for Claude 2.1.39 task primitives"
```

---

### Task 9: Update write-plan command body (remove swarm, update model refs)

**Files:**
- Modify: `plugins/dev-workflow/commands/write-plan.md:132,296-310`

**Step 1: Update model reference in write-plan context**

No explicit model reference in write-plan.md body — the model refs are in execute-plan (already updated in Task 6). Verify no "Opus 4.5" text exists:

```bash
grep -n "Opus 4.5\|opus 4.5" plugins/dev-workflow/commands/write-plan.md
```

**Step 2: Remove TodoWrite reference in body**

In write-plan.md, the body text at line 132 says "Create TodoWrite with all tasks as `pending`". Search and update any such references to use TaskCreate terminology instead. The plan-writing command instructs the *plan author* to write plans with task structure — it doesn't actually call TodoWrite itself. No body changes needed beyond frontmatter (already done in Task 4).

**Step 3: Verify and commit if changes were made**

If no body changes needed, skip commit. Otherwise:

```bash
git add plugins/dev-workflow/commands/write-plan.md
git commit -m "chore(write-plan): remove stale TodoWrite/swarm references"
```

---

### Task 10: Update CLAUDE.md

**Files:**
- Modify: `plugins/dev-workflow/CLAUDE.md`

**Step 1: Update valid tools list**

In `plugins/dev-workflow/CLAUDE.md`, find the line:
```
**Valid tools:** `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `Task`, `TodoWrite`, `AskUserQuestion`, `Skill`, `WebFetch`, `WebSearch`, `NotebookEdit`
```

Replace with:
```
**Valid tools:** `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `Task`, `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet`, `TaskStop`, `TaskOutput`, `AskUserQuestion`, `Skill`, `WebFetch`, `WebSearch`, `NotebookEdit`
```

**Step 2: Update plugin flow diagram**

Find the flow diagram:
```text
/dev-workflow:brainstorm (optional) → EnterPlanMode → ExitPlanMode(launchSwarm: true)
```

Replace with:
```text
/dev-workflow:brainstorm (optional) → /dev-workflow:write-plan → /dev-workflow:execute-plan
```

**Step 3: Update "Skills with checklists" line**

Find:
```
Skills with checklists require TodoWrite tracking.
```

Replace with:
```
Skills with checklists require TaskCreate/TaskUpdate tracking.
```

**Step 4: Remove tools.md/hooks.md from Directory Structure**

These files no longer exist. Remove them if listed in the directory structure section.

**Step 5: Run validation**

Run: `./plugins/dev-workflow/scripts/validate.sh`
Expected: Full PASS.

**Step 6: Commit**

```bash
git add plugins/dev-workflow/CLAUDE.md
git commit -m "docs(CLAUDE.md): update for Claude 2.1.39 primitives"
```

---

### Task 11: Run full validation and fix any remaining issues

**Files:**
- All modified files

**Step 1: Run plugin-level validation**

```bash
./plugins/dev-workflow/scripts/validate.sh
```

Expected: Full PASS (0 errors).

**Step 2: Run marketplace-level validation**

```bash
make check
```

OR if make not configured:

```bash
./scripts/validate-all.sh --quick
```

Expected: No errors related to dev-workflow plugin.

**Step 3: Run bats tests**

```bash
bats plugins/dev-workflow/tests/
```

Expected: All tests pass. The `hook-helpers.bats` tests should still pass since `get_task_files`, `get_task_numbers`, `get_next_task_number`, and `group_tasks_by_dependency` functions are still present in `hook-helpers.sh` (we keep them — they're still valid utility functions even if execute-plan no longer calls `group_tasks_by_dependency` directly).

**Step 4: Grep for any remaining stale references**

```bash
grep -rn "TodoWrite\|mcp__plugin_serena\|Opus 4\.5\|KillShell\|NotebookRead\b\|SlashCommand" plugins/dev-workflow/ --include="*.md" --include="*.sh" --include="*.json"
```

Fix any remaining references found.

**Step 5: Commit any fixes**

```bash
git add plugins/dev-workflow/
git commit -m "fix: resolve remaining stale references from 2.1.39 upgrade"
```

---

### Task 12: Code Review

Final quality gate. Dispatch code-reviewer agent to review all changes since this work began.

---

| Task Group | Tasks | Rationale |
|------------|-------|-----------|
| Group 1 | 1, 2, 3, 4, 5 | Independent: constants, deletions, skill frontmatter, command frontmatter, agents |
| Group 2 | 6, 7, 8, 9, 10 | Command/skill bodies depend on frontmatter being correct |
| Group 3 | 11 | Validation depends on all changes being in place |
| Group 4 | 12 | Code review after all changes |
