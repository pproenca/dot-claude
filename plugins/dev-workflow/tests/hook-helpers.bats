#!/usr/bin/env bats

load test_helper

SCRIPT="$PLUGIN_ROOT/scripts/hook-helpers.sh"

setup() {
  setup_test_dir
  # shellcheck source=../scripts/hook-helpers.sh disable=SC1091
  source "$SCRIPT"
}

teardown() {
  teardown_test_dir
}

# ============================================================================
# get_task_files() tests
# ============================================================================

@test "get_task_files: extracts files from task section" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: Create user model

**Files:**
- Create: `src/models/user.py`
- Test: `tests/test_user.py`

### Task 2: Next task
EOF

  result=$(get_task_files "$TEST_DIR/plan.md" "1")
  echo "$result" | grep -q "src/models/user.py"
  echo "$result" | grep -q "tests/test_user.py"
}

@test "get_task_files: handles Modify files" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: Update config

**Files:**
- Modify: `src/config.py:10-20`
- Test: `tests/test_config.py`

### Task 2: Next task
EOF

  result=$(get_task_files "$TEST_DIR/plan.md" "1")
  echo "$result" | grep -q "src/config.py:10-20"
}

@test "get_task_files: returns empty for task with no files" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: Documentation only

Just update README.

### Task 2: Next task
EOF

  result=$(get_task_files "$TEST_DIR/plan.md" "1")
  [[ -z "$result" ]]
}

# ============================================================================
# group_tasks_by_dependency() tests
# ============================================================================

@test "group_tasks_by_dependency: independent tasks in same group" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: User model

**Files:**
- Create: `src/user.py`
- Test: `tests/test_user.py`

### Task 2: Product model

**Files:**
- Create: `src/product.py`
- Test: `tests/test_product.py`

### Task 3: Order model

**Files:**
- Create: `src/order.py`
- Test: `tests/test_order.py`
EOF

  result=$(group_tasks_by_dependency "$TEST_DIR/plan.md" 5)
  # All three tasks should be in one group (no overlap)
  [[ "$result" == "group1:1,2,3" ]]
}

@test "group_tasks_by_dependency: overlapping tasks in different groups" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: Create base

**Files:**
- Create: `src/base.py`

### Task 2: Extend base

**Files:**
- Modify: `src/base.py`
- Create: `src/extended.py`

### Task 3: Independent

**Files:**
- Create: `src/other.py`
EOF

  result=$(group_tasks_by_dependency "$TEST_DIR/plan.md" 5)
  # Task 1 and 2 overlap on src/base.py, so should be in different groups
  echo "$result" | grep -q "group1:1"
  echo "$result" | grep -q "group2:2"
}

@test "group_tasks_by_dependency: respects max group size" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: A
**Files:**
- Create: `a.py`

### Task 2: B
**Files:**
- Create: `b.py`

### Task 3: C
**Files:**
- Create: `c.py`

### Task 4: D
**Files:**
- Create: `d.py`
EOF

  # Max group size of 2
  result=$(group_tasks_by_dependency "$TEST_DIR/plan.md" 2)
  # Should split into two groups of 2
  echo "$result" | grep -q "group1:1,2"
  echo "$result" | grep -q "group2:3,4"
}

# ============================================================================
# Decimal task number support tests
# ============================================================================

@test "get_task_numbers: extracts integer task numbers" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: First
Content

### Task 2: Second
Content

### Task 3: Third
Content
EOF

  result=$(get_task_numbers "$TEST_DIR/plan.md")
  [[ "$result" == "1 2 3" ]]
}

@test "get_task_numbers: extracts decimal task numbers" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: Main task
Content

### Task 1.1: Subtask A
Content

### Task 1.2: Subtask B
Content

### Task 2: Another main task
Content
EOF

  result=$(get_task_numbers "$TEST_DIR/plan.md")
  [[ "$result" == "1 1.1 1.2 2" ]]
}

@test "get_task_numbers: handles mixed integer and decimal" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: First
### Task 1.1: Sub
### Task 2: Second
### Task 2.1: Sub A
### Task 2.2: Sub B
### Task 3: Third
EOF

  result=$(get_task_numbers "$TEST_DIR/plan.md")
  [[ "$result" == "1 1.1 2 2.1 2.2 3" ]]
}

@test "get_next_task_number: returns next integer" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: First
### Task 2: Second
### Task 3: Third
EOF

  result=$(get_next_task_number "$TEST_DIR/plan.md" "1")
  [[ "$result" == "2" ]]
}

@test "get_next_task_number: returns subtask after main task" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: Main
### Task 1.1: Sub
### Task 2: Next main
EOF

  result=$(get_next_task_number "$TEST_DIR/plan.md" "1")
  [[ "$result" == "1.1" ]]
}

@test "get_next_task_number: returns main task after subtask" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: Main
### Task 1.1: Sub
### Task 2: Next main
EOF

  result=$(get_next_task_number "$TEST_DIR/plan.md" "1.1")
  [[ "$result" == "2" ]]
}

@test "get_next_task_number: returns empty for last task" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: First
### Task 2: Last
EOF

  result=$(get_next_task_number "$TEST_DIR/plan.md" "2")
  [[ -z "$result" ]]
}

@test "get_task_files: extracts files from decimal task" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: Main task

**Files:**
- Create: `src/main.py`

### Task 1.1: Subtask

**Files:**
- Create: `src/sub.py`
- Test: `tests/test_sub.py`

### Task 2: Next main

**Files:**
- Create: `src/next.py`
EOF

  result=$(get_task_files "$TEST_DIR/plan.md" "1.1")
  echo "$result" | grep -q "src/sub.py"
  echo "$result" | grep -q "tests/test_sub.py"
  # Should NOT include files from other tasks
  ! echo "$result" | grep -q "src/main.py"
  ! echo "$result" | grep -q "src/next.py"
}

@test "group_tasks_by_dependency: handles decimal tasks with no overlap" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: Main

**Files:**
- Create: `src/a.py`

### Task 1.1: Sub A

**Files:**
- Create: `src/b.py`

### Task 1.2: Sub B

**Files:**
- Create: `src/c.py`
EOF

  result=$(group_tasks_by_dependency "$TEST_DIR/plan.md" 5)
  # All tasks independent, should be in same group
  [[ "$result" == "group1:1,1.1,1.2" ]]
}

@test "group_tasks_by_dependency: handles decimal tasks with overlap" {
  cat > "$TEST_DIR/plan.md" << 'EOF'
### Task 1: Create base

**Files:**
- Create: `src/base.py`

### Task 1.1: Extend base

**Files:**
- Modify: `src/base.py`
- Create: `src/extended.py`

### Task 2: Independent

**Files:**
- Create: `src/other.py`
EOF

  result=$(group_tasks_by_dependency "$TEST_DIR/plan.md" 5)
  # Task 1 and 1.1 overlap on base.py, should be in different groups
  echo "$result" | grep -q "group1:1"
  echo "$result" | grep -q "group2:1.1"
}

# ============================================================================
# Hyh Integration Functions - Note: accessed via 'uvx hyh'
# ============================================================================

@test "hyh_get_progress returns task counts" {
  mkdir -p "$BATS_TEST_DIRNAME/mocks"
  cat > "$BATS_TEST_DIRNAME/mocks/uvx" << 'EOF'
#!/bin/bash
# uvx receives: hyh <command>
if [[ "$1" == "hyh" && "$2" == "get-state" ]]; then
  echo '{"tasks":{"t1":{"status":"completed"},"t2":{"status":"pending"},"t3":{"status":"running"}}}'
  exit 0
fi
exit 0
EOF
  chmod +x "$BATS_TEST_DIRNAME/mocks/uvx"
  export PATH="$BATS_TEST_DIRNAME/mocks:$PATH"

  source "$BATS_TEST_DIRNAME/../scripts/hook-helpers.sh"

  result=$(hyh_get_progress)
  total=$(echo "$result" | jq '.total')
  completed=$(echo "$result" | jq '.completed')

  [ "$total" -eq 3 ]
  [ "$completed" -eq 1 ]
}
