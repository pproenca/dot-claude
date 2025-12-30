# Phase: DELEGATE

## Purpose
Spawn task-executor subagents to implement the plan. No direct coding by orchestrator.

## Prerequisites
- Phase file shows DELEGATE
- `.claude/plan-approved` exists
- plan.md is complete

## Verify Phase
```bash
cat "${STATE_DIR}/workflow-phase"      # Should show DELEGATE
cat "${STATE_DIR}/plan-approved"       # Should show approved
```

## Activities

### 1. Spawn Task Packet Writer
Instead of writing task packets inline, delegate to task-packet-writer:

```
Task(
  subagent_type: "agentic-workflow:task-packet-writer"
  prompt: |
    PLAN_PATH: .claude/plan.md
    OUTPUT_DIR: .claude/task-packets/
    WORKTREE_BASE: ~/.dot-claude-worktrees
    PROJECT_NAME: {project_name}
)
```

Result: List of task packet file paths.

### 2. Create Worktrees for Each Task
```bash
source "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/worktree-utils.sh"
WORKTREE_PATH=$(worktree_create "task-a-component")
echo "Created worktree at: $WORKTREE_PATH"
```

### 3. Spawn Task Executors

**Wave 1 (Parallel)**: Include multiple Task calls in SINGLE message:

```
# All in ONE assistant message for parallel execution
Task(
  subagent_type: "agentic-workflow:task-executor"
  prompt: "TASK_PACKET_PATH: .claude/task-packets/task-a-component.md"
  run_in_background: true
)
Task(
  subagent_type: "agentic-workflow:task-executor"
  prompt: "TASK_PACKET_PATH: .claude/task-packets/task-b-service.md"
  run_in_background: true
)
```

**Collect Results**:
```
result_a = TaskOutput(task_id: task_a_id, block: true)
result_b = TaskOutput(task_id: task_b_id, block: true)
```

**Wave 2+ (After Dependencies)**:
- Wait for Wave 1 to complete
- Read artifacts from completed tasks
- Spawn next wave with artifact context

### 4. Update State
After each wave completes:
```bash
# Update todo.md
echo "DONE Task A: Component" >> todo.md
# Update progress.txt
echo "Completed: Wave 1" >> progress.txt
```

And sync TodoWrite:
```
TodoWrite([{content: "Task A: Component", status: "completed", ...}])
```

## Constraints
- NO direct code modifications by orchestrator
- All implementation via task-executor subagents
- One task = one worktree = one branch
- Worktrees isolate parallel execution

## Duration
Target: All tasks spawned before context reaches 70% usage.

## Transition
When all task-executors complete, proceed to VERIFY:
```bash
echo "VERIFY" > "${STATE_DIR}/workflow-phase"
Read("${CLAUDE_PLUGIN_ROOT}/agents/references/phase-verify.md")
```
