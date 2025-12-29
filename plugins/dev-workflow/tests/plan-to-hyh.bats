#!/usr/bin/env bats

setup() {
  export SCRIPT_DIR="$BATS_TEST_DIRNAME/../scripts"
  export TEST_PLAN="$BATS_TEST_TMPDIR/test-plan.md"
}

@test "plan_to_hyh extracts goal from plan header" {
  cat > "$TEST_PLAN" << 'EOF'
# User Authentication Implementation Plan

**Goal:** Add JWT-based user authentication to the API

---

### Task 1: Create User Model
EOF

  run bash "$SCRIPT_DIR/plan-to-hyh.sh" "$TEST_PLAN"
  [ "$status" -eq 0 ]
  echo "$output" | jq -e '.goal == "Add JWT-based user authentication to the API"'
}

@test "plan_to_hyh extracts tasks with descriptions" {
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

  run bash "$SCRIPT_DIR/plan-to-hyh.sh" "$TEST_PLAN"
  [ "$status" -eq 0 ]

  # Check task count
  task_count=$(echo "$output" | jq '.tasks | length')
  [ "$task_count" -eq 2 ]

  # Check task descriptions
  echo "$output" | jq -e '.tasks["task-1"].description == "Create User Model"'
  echo "$output" | jq -e '.tasks["task-2"].description == "Add API Endpoint"'
}

@test "plan_to_hyh parses dependencies" {
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

  run bash "$SCRIPT_DIR/plan-to-hyh.sh" "$TEST_PLAN"
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

@test "plan_to_hyh handles decimal task numbers" {
  cat > "$TEST_PLAN" << 'EOF'
# Feature Plan

**Goal:** Build feature with subtasks

---

### Task 1: Main Task

**Step 1: Setup**

### Task 1.1: Subtask A

**Dependencies:** Task 1

**Step 1: Do subtask A**

### Task 1.2: Subtask B

**Dependencies:** Task 1.1

**Step 1: Do subtask B**

### Task 2: Final Task

**Dependencies:** Task 1.2

**Step 1: Finish**
EOF

  run bash "$SCRIPT_DIR/plan-to-hyh.sh" "$TEST_PLAN"
  [ "$status" -eq 0 ]

  # Should have 4 tasks including subtasks
  task_count=$(echo "$output" | jq '.tasks | length')
  [ "$task_count" -eq 4 ]

  # Check subtask IDs and descriptions
  echo "$output" | jq -e '.tasks["task-1.1"].description == "Subtask A"'
  echo "$output" | jq -e '.tasks["task-1.2"].description == "Subtask B"'

  # Check subtask dependencies
  echo "$output" | jq -e '.tasks["task-1.1"].dependencies | contains(["task-1"])'
  echo "$output" | jq -e '.tasks["task-1.2"].dependencies | contains(["task-1.1"])'
}

@test "plan_to_hyh extracts instructions from steps" {
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

  run bash "$SCRIPT_DIR/plan-to-hyh.sh" "$TEST_PLAN"
  [ "$status" -eq 0 ]

  # Instructions should contain the steps
  instructions=$(echo "$output" | jq -r '.tasks["task-1"].instructions')
  [[ "$instructions" == *"Write the failing test"* ]]
  [[ "$instructions" == *"def test_user_model"* ]]
}
