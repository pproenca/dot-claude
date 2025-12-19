# Harness Integration Implementation Plan

> **Execution:** Use `/dev-workflow:execute-plan docs/plans/2025-12-19-harness-integration.md` to implement task-by-task.

**Goal:** Replace dot-claude's shell-based state management with harness's thread-safe Python daemon for atomic task coordination.

**Architecture:** The integration adds a thin shell layer in dot-claude that calls `harness` CLI commands. SessionStart hook queries harness daemon for active workflows. Background agents claim/complete tasks via `harness task claim/complete`. The harness daemon handles DAG scheduling, idempotent retries, and timeout reclaim.

**Tech Stack:** Bash (hooks/scripts), Python 3.13t (harness daemon), JSON-over-Unix-socket IPC, jq for JSON parsing

---

## Parallel Groups

| Task Group | Tasks | Rationale |
|------------|-------|-----------|
| Group 1 | 1, 2 | Independent scripts, no file overlap |
| Group 2 | 3 | Depends on ensure-harness.sh from Task 1 |
| Group 3 | 4 | Depends on session-start.sh from Task 3 |
| Group 4 | 5, 6 | Independent commands, no file overlap |
| Group 5 | 7 | Depends on execute-plan from Task 5 |
| Group 6 | 8 | Integration tests depend on all prior tasks |
| Group 7 | 9 | Code review |

---

### Task 1: Create ensure-harness.sh Script

**Effort:** simple (5-8 tool calls)

**Files:**
- Create: `plugins/dev-workflow/scripts/ensure-harness.sh`
- Test: `plugins/dev-workflow/tests/ensure-harness.bats`

**Step 1: Write the failing test** (2-5 min)

Create `plugins/dev-workflow/tests/ensure-harness.bats`:

```bash
#!/usr/bin/env bats

setup() {
  load '../scripts/ensure-harness.sh'
  # Mock harness command
  export PATH="$BATS_TEST_DIRNAME/mocks:$PATH"
}

@test "ensure_harness returns 0 when daemon responds to ping" {
  # Mock harness ping succeeds
  echo '#!/bin/bash
echo "pong"
exit 0' > "$BATS_TEST_DIRNAME/mocks/harness"
  chmod +x "$BATS_TEST_DIRNAME/mocks/harness"

  run ensure_harness
  [ "$status" -eq 0 ]
}

@test "ensure_harness spawns daemon when ping fails then succeeds" {
  # First ping fails, second succeeds (daemon started)
  echo '#!/bin/bash
if [[ "$1" == "ping" ]]; then
  if [[ ! -f /tmp/harness-started ]]; then
    touch /tmp/harness-started
    exit 1
  fi
  echo "pong"
  exit 0
fi
exit 0' > "$BATS_TEST_DIRNAME/mocks/harness"
  chmod +x "$BATS_TEST_DIRNAME/mocks/harness"

  run ensure_harness
  [ "$status" -eq 0 ]
  rm -f /tmp/harness-started
}

@test "ensure_harness fails after timeout when daemon never starts" {
  echo '#!/bin/bash
exit 1' > "$BATS_TEST_DIRNAME/mocks/harness"
  chmod +x "$BATS_TEST_DIRNAME/mocks/harness"

  HARNESS_TIMEOUT=1 run ensure_harness
  [ "$status" -eq 1 ]
}
```

**Step 2: Create mocks directory and run test to verify it fails** (30 sec)

```bash
mkdir -p plugins/dev-workflow/tests/mocks
cd /Users/pedroproenca/Documents/Projects/dot-claude && bats plugins/dev-workflow/tests/ensure-harness.bats
```

Expected: FAIL with `ensure_harness: command not found` or similar

**Step 3: Write minimal implementation** (2-5 min)

Create `plugins/dev-workflow/scripts/ensure-harness.sh`:

```bash
#!/usr/bin/env bash
# ensure-harness.sh - Ensure harness daemon is running
# Returns 0 if daemon is running, 1 if failed to start

set -euo pipefail

HARNESS_TIMEOUT="${HARNESS_TIMEOUT:-5}"

ensure_harness() {
  # Check if daemon responds to ping
  if harness ping >/dev/null 2>&1; then
    return 0
  fi

  # Daemon not running, spawn it (harness client auto-spawns daemon)
  harness get-state >/dev/null 2>&1 || true

  # Wait for daemon to be ready
  local elapsed=0
  while ! harness ping >/dev/null 2>&1; do
    sleep 0.5
    elapsed=$((elapsed + 1))
    if [[ $elapsed -ge $((HARNESS_TIMEOUT * 2)) ]]; then
      echo "ERROR: harness daemon failed to start within ${HARNESS_TIMEOUT}s" >&2
      return 1
    fi
  done

  return 0
}

# Allow sourcing without execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  ensure_harness "$@"
fi
```

**Step 4: Run test to verify it passes** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && bats plugins/dev-workflow/tests/ensure-harness.bats
```

Expected: PASS (3 passed)

**Step 5: Commit** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && git add plugins/dev-workflow/scripts/ensure-harness.sh plugins/dev-workflow/tests/ensure-harness.bats plugins/dev-workflow/tests/mocks && git commit -m "feat(harness): add ensure-harness.sh daemon spawn script"
```

---

### Task 2: Create plan-to-harness.sh Converter Script

**Effort:** standard (10-15 tool calls)

**Files:**
- Create: `plugins/dev-workflow/scripts/plan-to-harness.sh`
- Test: `plugins/dev-workflow/tests/plan-to-harness.bats`

**Step 1: Write the failing test** (2-5 min)

Create `plugins/dev-workflow/tests/plan-to-harness.bats`:

```bash
#!/usr/bin/env bats

setup() {
  export SCRIPT_DIR="$BATS_TEST_DIRNAME/../scripts"
  export TEST_PLAN="$BATS_TEST_TMPDIR/test-plan.md"
}

@test "plan_to_harness extracts goal from plan header" {
  cat > "$TEST_PLAN" << 'EOF'
# User Authentication Implementation Plan

**Goal:** Add JWT-based user authentication to the API

---

### Task 1: Create User Model
EOF

  run bash "$SCRIPT_DIR/plan-to-harness.sh" "$TEST_PLAN"
  [ "$status" -eq 0 ]
  echo "$output" | jq -e '.goal == "Add JWT-based user authentication to the API"'
}

@test "plan_to_harness extracts tasks with descriptions" {
  cat > "$TEST_PLAN" << 'EOF'
# Feature Plan

**Goal:** Build feature

---

### Task 1: Create User Model

**Files:**
- Create: src/models/user.py

**Step 1: Write test**

### Task 2: Add API Endpoint

**Files:**
- Modify: src/api/routes.py

**Dependencies:** Task 1

**Step 1: Write test**
EOF

  run bash "$SCRIPT_DIR/plan-to-harness.sh" "$TEST_PLAN"
  [ "$status" -eq 0 ]

  # Check task count
  task_count=$(echo "$output" | jq '.tasks | length')
  [ "$task_count" -eq 2 ]

  # Check task descriptions
  echo "$output" | jq -e '.tasks["task-1"].description == "Create User Model"'
  echo "$output" | jq -e '.tasks["task-2"].description == "Add API Endpoint"'
}

@test "plan_to_harness parses dependencies" {
  cat > "$TEST_PLAN" << 'EOF'
# Feature Plan

**Goal:** Build feature

---

### Task 1: First Task

**Step 1: Do something**

### Task 2: Second Task

**Dependencies:** Task 1

**Step 1: Do something**

### Task 3: Third Task

**Dependencies:** Task 1, Task 2

**Step 1: Do something**
EOF

  run bash "$SCRIPT_DIR/plan-to-harness.sh" "$TEST_PLAN"
  [ "$status" -eq 0 ]

  # Task 1 has no dependencies
  deps1=$(echo "$output" | jq '.tasks["task-1"].dependencies | length')
  [ "$deps1" -eq 0 ]

  # Task 2 depends on task-1
  echo "$output" | jq -e '.tasks["task-2"].dependencies | contains(["task-1"])'

  # Task 3 depends on task-1 and task-2
  deps3=$(echo "$output" | jq '.tasks["task-3"].dependencies | length')
  [ "$deps3" -eq 2 ]
}

@test "plan_to_harness extracts instructions from steps" {
  cat > "$TEST_PLAN" << 'EOF'
# Feature Plan

**Goal:** Build feature

---

### Task 1: Create Model

**Step 1: Write the failing test** (2-5 min)

```python
def test_user_model():
    user = User(name="test")
    assert user.name == "test"
```

**Step 2: Run test** (30 sec)

```bash
pytest tests/test_user.py -v
```

**Step 3: Implement** (2-5 min)

```python
class User:
    def __init__(self, name):
        self.name = name
```
EOF

  run bash "$SCRIPT_DIR/plan-to-harness.sh" "$TEST_PLAN"
  [ "$status" -eq 0 ]

  # Instructions should contain the steps
  instructions=$(echo "$output" | jq -r '.tasks["task-1"].instructions')
  [[ "$instructions" == *"Write the failing test"* ]]
  [[ "$instructions" == *"def test_user_model"* ]]
}
```

**Step 2: Run test to verify it fails** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && bats plugins/dev-workflow/tests/plan-to-harness.bats
```

Expected: FAIL with `No such file or directory` for plan-to-harness.sh

**Step 3: Write minimal implementation** (2-5 min)

Create `plugins/dev-workflow/scripts/plan-to-harness.sh`:

```bash
#!/usr/bin/env bash
# plan-to-harness.sh - Convert markdown plan to harness JSON format
# Usage: plan-to-harness.sh <plan-file.md>

set -euo pipefail

plan_to_harness() {
  local plan_file="$1"

  if [[ ! -f "$plan_file" ]]; then
    echo "ERROR: Plan file not found: $plan_file" >&2
    return 1
  fi

  local content
  content=$(cat "$plan_file")

  # Extract goal from **Goal:** line
  local goal
  goal=$(echo "$content" | grep -E '^\*\*Goal:\*\*' | sed 's/\*\*Goal:\*\* *//' | head -1)

  # Initialize JSON structure
  local json='{"goal":"'"$goal"'","tasks":{}}'

  # Extract tasks using awk
  local task_num=0
  local current_task=""
  local current_desc=""
  local current_deps=""
  local current_instructions=""
  local in_task=false

  while IFS= read -r line; do
    # Check for task header: ### Task N: Description
    if [[ "$line" =~ ^###[[:space:]]+Task[[:space:]]+([0-9]+):[[:space:]]*(.*) ]]; then
      # Save previous task if exists
      if [[ -n "$current_task" ]]; then
        local deps_array="[]"
        if [[ -n "$current_deps" ]]; then
          deps_array=$(echo "$current_deps" | tr ',' '\n' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | \
            sed 's/Task /task-/g' | jq -R . | jq -s .)
        fi
        # Escape instructions for JSON
        local escaped_instructions
        escaped_instructions=$(echo "$current_instructions" | jq -Rs .)
        json=$(echo "$json" | jq --arg id "$current_task" --arg desc "$current_desc" \
          --argjson deps "$deps_array" --argjson instr "$escaped_instructions" \
          '.tasks[$id] = {description: $desc, dependencies: $deps, timeout_seconds: 600, instructions: $instr, role: "backend"}')
      fi

      task_num="${BASH_REMATCH[1]}"
      current_task="task-$task_num"
      current_desc="${BASH_REMATCH[2]}"
      current_deps=""
      current_instructions=""
      in_task=true
    # Check for dependencies line
    elif [[ "$in_task" == true && "$line" =~ ^\*\*Dependencies:\*\*[[:space:]]*(.*) ]]; then
      current_deps="${BASH_REMATCH[1]}"
    # Collect instructions (everything after **Step lines)
    elif [[ "$in_task" == true && "$line" =~ ^\*\*Step ]]; then
      current_instructions+="$line"$'\n'
    elif [[ "$in_task" == true && -n "$current_instructions" ]]; then
      current_instructions+="$line"$'\n'
    fi
  done <<< "$content"

  # Save last task
  if [[ -n "$current_task" ]]; then
    local deps_array="[]"
    if [[ -n "$current_deps" ]]; then
      deps_array=$(echo "$current_deps" | tr ',' '\n' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | \
        sed 's/Task /task-/g' | jq -R . | jq -s .)
    fi
    local escaped_instructions
    escaped_instructions=$(echo "$current_instructions" | jq -Rs .)
    json=$(echo "$json" | jq --arg id "$current_task" --arg desc "$current_desc" \
      --argjson deps "$deps_array" --argjson instr "$escaped_instructions" \
      '.tasks[$id] = {description: $desc, dependencies: $deps, timeout_seconds: 600, instructions: $instr, role: "backend"}')
  fi

  echo "$json"
}

# Allow sourcing or direct execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <plan-file.md>" >&2
    exit 1
  fi
  plan_to_harness "$1"
fi
```

**Step 4: Run test to verify it passes** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && bats plugins/dev-workflow/tests/plan-to-harness.bats
```

Expected: PASS (4 passed)

**Step 5: Commit** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && git add plugins/dev-workflow/scripts/plan-to-harness.sh plugins/dev-workflow/tests/plan-to-harness.bats && git commit -m "feat(harness): add plan-to-harness.sh markdown converter"
```

---

### Task 3: Modify session-start.sh Hook

**Effort:** standard (10-15 tool calls)

**Files:**
- Modify: `plugins/dev-workflow/hooks/session-start.sh`
- Test: `plugins/dev-workflow/tests/session-start.bats`

**Dependencies:** Task 1

**Step 1: Read the existing session-start.sh** (1 min)

```bash
cat plugins/dev-workflow/hooks/session-start.sh
```

Note the current structure for integration.

**Step 2: Write the failing test** (2-5 min)

Add to `plugins/dev-workflow/tests/session-start.bats`:

```bash
@test "session-start detects active harness workflow" {
  # Mock harness get-state to return active workflow
  mkdir -p "$BATS_TEST_DIRNAME/mocks"
  cat > "$BATS_TEST_DIRNAME/mocks/harness" << 'EOF'
#!/bin/bash
if [[ "$1" == "ping" ]]; then
  echo "pong"
  exit 0
fi
if [[ "$1" == "get-state" ]]; then
  echo '{"tasks":{"task-1":{"status":"completed"},"task-2":{"status":"pending"}}}'
  exit 0
fi
exit 0
EOF
  chmod +x "$BATS_TEST_DIRNAME/mocks/harness"
  export PATH="$BATS_TEST_DIRNAME/mocks:$PATH"

  run bash "$BATS_TEST_DIRNAME/../hooks/session-start.sh"

  [[ "$output" == *"ACTIVE WORKFLOW DETECTED"* ]]
  [[ "$output" == *"Progress: 1/2"* ]]
}

@test "session-start shows no workflow when harness state empty" {
  mkdir -p "$BATS_TEST_DIRNAME/mocks"
  cat > "$BATS_TEST_DIRNAME/mocks/harness" << 'EOF'
#!/bin/bash
if [[ "$1" == "ping" ]]; then
  echo "pong"
  exit 0
fi
if [[ "$1" == "get-state" ]]; then
  echo '{"tasks":{}}'
  exit 0
fi
exit 0
EOF
  chmod +x "$BATS_TEST_DIRNAME/mocks/harness"
  export PATH="$BATS_TEST_DIRNAME/mocks:$PATH"

  run bash "$BATS_TEST_DIRNAME/../hooks/session-start.sh"

  [[ "$output" != *"ACTIVE WORKFLOW"* ]]
}
```

**Step 3: Run test to verify it fails** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && bats plugins/dev-workflow/tests/session-start.bats
```

Expected: FAIL (current session-start.sh doesn't query harness)

**Step 4: Modify session-start.sh to integrate harness** (2-5 min)

Replace the state file checking logic with harness queries:

```bash
#!/usr/bin/env bash
# session-start.sh - SessionStart hook for dev-workflow plugin
# Queries harness daemon for active workflow state

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/ensure-harness.sh"

main() {
  # Ensure harness daemon is running
  if ! ensure_harness; then
    echo "WARNING: harness daemon not available" >&2
    # Fall through to load getting-started skill
  else
    # Query harness for active workflow
    local state
    state=$(harness get-state 2>/dev/null || echo '{}')

    local task_count
    task_count=$(echo "$state" | jq '.tasks | length')

    if [[ "$task_count" -gt 0 ]]; then
      local completed
      completed=$(echo "$state" | jq '[.tasks[] | select(.status == "completed")] | length')
      local pending
      pending=$(echo "$state" | jq '[.tasks[] | select(.status == "pending")] | length')
      local running
      running=$(echo "$state" | jq '[.tasks[] | select(.status == "running")] | length')

      cat << EOF
ACTIVE WORKFLOW DETECTED

Progress: $completed/$task_count tasks completed
- Pending: $pending
- Running: $running

Commands:
- /dev-workflow:resume - Continue execution
- /dev-workflow:abandon - Discard workflow state
EOF
      return 0
    fi
  fi

  # No active workflow - load getting-started skill
  cat << 'EOF'
dev-workflow skills available.

**Getting Started:**
- Use `/dev-workflow:brainstorm` to refine ideas
- Use `/dev-workflow:write-plan` to create implementation plans
- Use `/dev-workflow:execute-plan` to execute plans

Skills are loaded automatically based on task context.
EOF
}

main "$@"
```

**Step 5: Run test to verify it passes** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && bats plugins/dev-workflow/tests/session-start.bats
```

Expected: PASS (2 passed)

**Step 6: Commit** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && git add plugins/dev-workflow/hooks/session-start.sh plugins/dev-workflow/tests/session-start.bats && git commit -m "feat(harness): integrate session-start hook with harness daemon"
```

---

### Task 4: Add harness Wrappers to hook-helpers.sh

**Effort:** simple (5-8 tool calls)

**Files:**
- Modify: `plugins/dev-workflow/scripts/hook-helpers.sh`
- Test: `plugins/dev-workflow/tests/hook-helpers.bats`

**Dependencies:** Task 3

**Step 1: Read existing hook-helpers.sh** (1 min)

```bash
cat plugins/dev-workflow/scripts/hook-helpers.sh
```

Note existing functions to preserve.

**Step 2: Write the failing test** (2-5 min)

Add to `plugins/dev-workflow/tests/hook-helpers.bats`:

```bash
@test "harness_get_progress returns task counts" {
  mkdir -p "$BATS_TEST_DIRNAME/mocks"
  cat > "$BATS_TEST_DIRNAME/mocks/harness" << 'EOF'
#!/bin/bash
echo '{"tasks":{"t1":{"status":"completed"},"t2":{"status":"pending"},"t3":{"status":"running"}}}'
EOF
  chmod +x "$BATS_TEST_DIRNAME/mocks/harness"
  export PATH="$BATS_TEST_DIRNAME/mocks:$PATH"

  source "$BATS_TEST_DIRNAME/../scripts/hook-helpers.sh"

  result=$(harness_get_progress)
  total=$(echo "$result" | jq '.total')
  completed=$(echo "$result" | jq '.completed')

  [ "$total" -eq 3 ]
  [ "$completed" -eq 1 ]
}

@test "harness_is_workflow_active returns true when tasks exist" {
  mkdir -p "$BATS_TEST_DIRNAME/mocks"
  cat > "$BATS_TEST_DIRNAME/mocks/harness" << 'EOF'
#!/bin/bash
echo '{"tasks":{"t1":{"status":"pending"}}}'
EOF
  chmod +x "$BATS_TEST_DIRNAME/mocks/harness"
  export PATH="$BATS_TEST_DIRNAME/mocks:$PATH"

  source "$BATS_TEST_DIRNAME/../scripts/hook-helpers.sh"

  run harness_is_workflow_active
  [ "$status" -eq 0 ]
}

@test "harness_is_workflow_active returns false when no tasks" {
  mkdir -p "$BATS_TEST_DIRNAME/mocks"
  cat > "$BATS_TEST_DIRNAME/mocks/harness" << 'EOF'
#!/bin/bash
echo '{"tasks":{}}'
EOF
  chmod +x "$BATS_TEST_DIRNAME/mocks/harness"
  export PATH="$BATS_TEST_DIRNAME/mocks:$PATH"

  source "$BATS_TEST_DIRNAME/../scripts/hook-helpers.sh"

  run harness_is_workflow_active
  [ "$status" -eq 1 ]
}
```

**Step 3: Run test to verify it fails** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && bats plugins/dev-workflow/tests/hook-helpers.bats
```

Expected: FAIL (functions don't exist yet)

**Step 4: Add harness wrapper functions to hook-helpers.sh** (2-5 min)

Append to `plugins/dev-workflow/scripts/hook-helpers.sh`:

```bash
# =============================================================================
# Harness Integration Functions
# =============================================================================

# Get workflow progress as JSON: {total, completed, pending, running}
harness_get_progress() {
  local state
  state=$(harness get-state 2>/dev/null || echo '{"tasks":{}}')

  echo "$state" | jq '{
    total: .tasks | length,
    completed: [.tasks[] | select(.status == "completed")] | length,
    pending: [.tasks[] | select(.status == "pending")] | length,
    running: [.tasks[] | select(.status == "running")] | length
  }'
}

# Check if a workflow is active (has any tasks)
harness_is_workflow_active() {
  local state
  state=$(harness get-state 2>/dev/null || echo '{"tasks":{}}')

  local count
  count=$(echo "$state" | jq '.tasks | length')

  [[ "$count" -gt 0 ]]
}

# Import a plan file into harness
harness_import_plan() {
  local plan_file="$1"
  local json

  # Convert markdown plan to harness JSON
  json=$("$SCRIPT_DIR/plan-to-harness.sh" "$plan_file")

  # Import into harness
  echo "$json" | harness plan import --stdin
}

# Claim next available task for current worker
harness_claim_task() {
  harness task claim
}

# Complete a task
harness_complete_task() {
  local task_id="$1"
  harness task complete --id "$task_id"
}
```

**Step 5: Run test to verify it passes** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && bats plugins/dev-workflow/tests/hook-helpers.bats
```

Expected: PASS (3 passed)

**Step 6: Commit** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && git add plugins/dev-workflow/scripts/hook-helpers.sh plugins/dev-workflow/tests/hook-helpers.bats && git commit -m "feat(harness): add harness wrapper functions to hook-helpers.sh"
```

---

### Task 5: Modify execute-plan.md Command

**Effort:** standard (10-15 tool calls)

**Files:**
- Modify: `plugins/dev-workflow/commands/execute-plan.md`

**Dependencies:** Task 2, Task 4

**Step 1: Read existing execute-plan.md** (1 min)

```bash
cat plugins/dev-workflow/commands/execute-plan.md
```

Note the current execution flow.

**Step 2: Update execute-plan.md to use harness task claiming** (5 min)

The command should:
1. Call `harness_import_plan` to load the plan into harness
2. Dispatch agents that call `harness task claim` at start
3. Agents call `harness task complete --id <id>` when done
4. Remove shell-based state tracking (frontmatter_set calls)

Key changes to the command prompt:

```markdown
## Execution Flow (with harness)

### Step 1: Import Plan
```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
harness_import_plan "$PLAN_FILE"
```

### Step 2: Dispatch Agents

For each task group, dispatch agents in parallel:

```claude
Task:
  subagent_type: dev-workflow:task-executor
  run_in_background: true
  description: "Execute [task-id]"
  prompt: |
    You are executing a task from a harness-managed workflow.

    1. Claim your task:
       ```bash
       TASK=$(harness task claim)
       ```

    2. Parse task details:
       ```bash
       TASK_ID=$(echo "$TASK" | jq -r '.task.id')
       INSTRUCTIONS=$(echo "$TASK" | jq -r '.task.instructions')
       ```

    3. Execute the instructions exactly as written

    4. Complete the task:
       ```bash
       harness task complete --id "$TASK_ID"
       ```
```

### Step 3: Wait for Completion

```claude
TaskOutput:
  task_id: <agent-id>
  block: true
```

No manual state tracking needed - harness daemon tracks all task states.
```

**Step 3: Verify the changes are syntactically correct** (30 sec)

Read the modified file and ensure markdown is valid.

**Step 4: Commit** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && git add plugins/dev-workflow/commands/execute-plan.md && git commit -m "feat(harness): update execute-plan to use harness task claiming"
```

---

### Task 6: Modify resume.md Command

**Effort:** simple (5-8 tool calls)

**Files:**
- Modify: `plugins/dev-workflow/commands/resume.md`

**Dependencies:** Task 4

**Step 1: Read existing resume.md** (1 min)

```bash
cat plugins/dev-workflow/commands/resume.md
```

**Step 2: Update resume.md to use harness state** (3 min)

The command should:
1. Query `harness get-state` for incomplete tasks
2. Re-dispatch agents (they call `task claim` and get uncompleted work)
3. Remove frontmatter-based state tracking

Key changes:

```markdown
## Resume Flow (with harness)

### Step 1: Check Workflow State

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
PROGRESS=$(harness_get_progress)
PENDING=$(echo "$PROGRESS" | jq '.pending')
RUNNING=$(echo "$PROGRESS" | jq '.running')

if [[ "$PENDING" -eq 0 && "$RUNNING" -eq 0 ]]; then
  echo "No pending tasks. Workflow complete."
  exit 0
fi
```

### Step 2: Re-dispatch Agents

Agents call `harness task claim` - the daemon returns the next available task.
Running tasks that timed out will be automatically reclaimed.

No state file manipulation needed - harness handles everything.
```

**Step 3: Commit** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && git add plugins/dev-workflow/commands/resume.md && git commit -m "feat(harness): update resume command to use harness state"
```

---

### Task 7: Modify write-plan.md Command

**Effort:** simple (5-8 tool calls)

**Files:**
- Modify: `plugins/dev-workflow/commands/write-plan.md`

**Dependencies:** Task 5

**Step 1: Read existing write-plan.md** (1 min)

```bash
cat plugins/dev-workflow/commands/write-plan.md
```

**Step 2: Update write-plan.md to import plan into harness** (3 min)

Add to the end of the plan creation flow:

```markdown
## Step 5: Import Plan into Harness

After saving the plan file, import it into harness:

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
harness_import_plan "$PLAN_FILE"
```

This validates the DAG (cycle detection, missing dependencies) and creates
atomic state with all tasks pending.

If import fails, fix the plan and retry.
```

**Step 3: Remove frontmatter state creation** (2 min)

Remove any `create_state_file` or `frontmatter_set` calls that track workflow state.
Harness now manages all task state.

**Step 4: Commit** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && git add plugins/dev-workflow/commands/write-plan.md && git commit -m "feat(harness): update write-plan to import plan into harness"
```

---

### Task 8: Create Integration Tests

**Effort:** standard (10-15 tool calls)

**Files:**
- Create: `plugins/dev-workflow/tests/harness-integration.bats`

**Dependencies:** Task 1, Task 2, Task 3, Task 4

**Step 1: Write integration tests** (5 min)

Create `plugins/dev-workflow/tests/harness-integration.bats`:

```bash
#!/usr/bin/env bats

setup() {
  export SCRIPT_DIR="$BATS_TEST_DIRNAME/../scripts"
  export TEST_PLAN="$BATS_TEST_TMPDIR/test-plan.md"

  # Create a test plan
  cat > "$TEST_PLAN" << 'EOF'
# Test Feature Implementation Plan

**Goal:** Test harness integration

---

### Task 1: First Task

**Step 1: Do something**

### Task 2: Second Task

**Dependencies:** Task 1

**Step 1: Do something else**
EOF
}

teardown() {
  # Clean up any harness state
  harness shutdown 2>/dev/null || true
}

@test "full workflow: convert, import, claim, complete" {
  # Skip if harness not installed
  if ! command -v harness &>/dev/null; then
    skip "harness not installed"
  fi

  # Convert plan to JSON
  json=$(bash "$SCRIPT_DIR/plan-to-harness.sh" "$TEST_PLAN")

  # Verify JSON structure
  [ "$(echo "$json" | jq '.tasks | length')" -eq 2 ]

  # Import into harness (this starts daemon if needed)
  echo "$json" | harness plan import --stdin

  # Verify state
  state=$(harness get-state)
  [ "$(echo "$state" | jq '.tasks | length')" -eq 2 ]
  [ "$(echo "$state" | jq '.tasks["task-1"].status')" == '"pending"' ]

  # Claim first task
  claim=$(harness task claim)
  task_id=$(echo "$claim" | jq -r '.task.id')
  [ "$task_id" == "task-1" ]

  # Complete first task
  harness task complete --id "$task_id"

  # Verify task-1 completed
  state=$(harness get-state)
  [ "$(echo "$state" | jq '.tasks["task-1"].status')" == '"completed"' ]

  # Now task-2 should be claimable (dependency satisfied)
  claim=$(harness task claim)
  task_id=$(echo "$claim" | jq -r '.task.id')
  [ "$task_id" == "task-2" ]
}

@test "parallel claims return different tasks" {
  if ! command -v harness &>/dev/null; then
    skip "harness not installed"
  fi

  # Create plan with parallel tasks
  cat > "$TEST_PLAN" << 'EOF'
# Parallel Tasks

**Goal:** Test parallel claiming

---

### Task 1: Independent A

**Step 1: Do A**

### Task 2: Independent B

**Step 1: Do B**

### Task 3: Independent C

**Step 1: Do C**
EOF

  json=$(bash "$SCRIPT_DIR/plan-to-harness.sh" "$TEST_PLAN")
  echo "$json" | harness plan import --stdin

  # Claim tasks with different worker IDs
  export HARNESS_WORKER_ID="worker-1"
  claim1=$(harness task claim)
  task1=$(echo "$claim1" | jq -r '.task.id')

  export HARNESS_WORKER_ID="worker-2"
  claim2=$(harness task claim)
  task2=$(echo "$claim2" | jq -r '.task.id')

  export HARNESS_WORKER_ID="worker-3"
  claim3=$(harness task claim)
  task3=$(echo "$claim3" | jq -r '.task.id')

  # All tasks should be different
  [ "$task1" != "$task2" ]
  [ "$task2" != "$task3" ]
  [ "$task1" != "$task3" ]
}
```

**Step 2: Run integration tests** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && bats plugins/dev-workflow/tests/harness-integration.bats
```

Expected: PASS (or skip if harness not installed)

**Step 3: Commit** (30 sec)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && git add plugins/dev-workflow/tests/harness-integration.bats && git commit -m "test(harness): add integration tests for harness workflow"
```

---

### Task 9: Code Review

**Effort:** simple (3-5 tool calls)

**Files:**
- Review all modified files

**Dependencies:** Task 1-8

**Step 1: Run full test suite** (2 min)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && make test
```

**Step 2: Run linting** (1 min)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && make lint
```

**Step 3: Review changes** (5 min)

```bash
cd /Users/pedroproenca/Documents/Projects/dot-claude && git diff main..HEAD --stat
git log main..HEAD --oneline
```

Verify:
- [ ] All tests pass
- [ ] No linting errors
- [ ] Commit messages follow conventional format
- [ ] No debug code left in
- [ ] Error handling for missing harness binary

**Step 4: Final commit summary**

After review passes, the integration is complete.
