#!/usr/bin/env bats
# Note: harness was renamed to hyh, accessed via 'uvx hyh'

setup() {
  export TEST_PLAN="$BATS_TEST_TMPDIR/test-plan.md"

  # Create a test plan matching hyh expected format
  cat > "$TEST_PLAN" << 'EOF'
# Test Feature Implementation Plan

> **Execution:** Use `/dev-workflow:execute-plan` to implement.

**Goal:** Test hyh integration

---

## Task Groups

| Task Group | Tasks | Rationale |
|------------|-------|-----------|
| Group 1    | 1     | First task |
| Group 2    | 2     | Second task (depends on Group 1) |

---

### Task 1: First Task

**Files:**
- Create: `src/first.py`

**Step 1: Do something**
Implement the first task.

### Task 2: Second Task

**Files:**
- Create: `src/second.py`

**Step 1: Do something else**
Implement the second task.
EOF
}

teardown() {
  # Clean up any hyh state
  uvx hyh shutdown 2>/dev/null || true
}

@test "full workflow: convert, import, claim, complete" {
  # Skip if uvx not installed (required for hyh)
  if ! command -v uvx &>/dev/null; then
    skip "hyh not installed"
  fi

  # Import markdown plan directly into hyh (this starts daemon if needed)
  uvx hyh plan import --file "$TEST_PLAN"

  # Verify state
  state=$(uvx hyh get-state)
  [ "$(echo "$state" | jq '.tasks | length')" -eq 2 ]
  [ "$(echo "$state" | jq '.tasks["1"].status')" == '"pending"' ]

  # Claim first task
  claim=$(uvx hyh task claim)
  task_id=$(echo "$claim" | jq -r '.task.id')
  [ "$task_id" == "1" ]

  # Complete first task
  uvx hyh task complete --id "$task_id"

  # Verify task 1 completed
  state=$(uvx hyh get-state)
  [ "$(echo "$state" | jq '.tasks["1"].status')" == '"completed"' ]

  # Now task 2 should be claimable (dependency satisfied)
  claim=$(uvx hyh task claim)
  task_id=$(echo "$claim" | jq -r '.task.id')
  [ "$task_id" == "2" ]
}

@test "sequential claims return different tasks after completion" {
  if ! command -v uvx &>/dev/null; then
    skip "hyh not installed"
  fi

  # Ensure clean state - shutdown any existing daemon
  uvx hyh shutdown 2>/dev/null || true
  sleep 0.5

  # Create plan with parallel tasks (all in same group = no dependencies)
  cat > "$TEST_PLAN" << 'EOF'
# Parallel Tasks

> **Execution:** Use `/dev-workflow:execute-plan` to implement.

**Goal:** Test parallel claiming

---

## Task Groups

| Task Group | Tasks | Rationale |
|------------|-------|-----------|
| Group 1    | 1, 2, 3 | All independent tasks (parallel) |

---

### Task 1: Independent A

**Files:**
- Create: `src/a.py`

**Step 1: Do A**
Implement task A.

### Task 2: Independent B

**Files:**
- Create: `src/b.py`

**Step 1: Do B**
Implement task B.

### Task 3: Independent C

**Files:**
- Create: `src/c.py`

**Step 1: Do C**
Implement task C.
EOF

  # Import markdown plan directly into hyh
  uvx hyh plan import --file "$TEST_PLAN"

  # Claim first task
  claim1=$(uvx hyh task claim)
  id1=$(echo "$claim1" | jq -r '.task.id')

  # Complete first task so we can claim a second one
  uvx hyh task complete --id "$id1"

  # Claim second task (should be different)
  claim2=$(uvx hyh task claim)
  id2=$(echo "$claim2" | jq -r '.task.id')

  # Complete second task
  uvx hyh task complete --id "$id2"

  # Claim third task (should be different from both)
  claim3=$(uvx hyh task claim)
  id3=$(echo "$claim3" | jq -r '.task.id')

  # All IDs should be different
  [ "$id1" != "$id2" ]
  [ "$id2" != "$id3" ]
  [ "$id1" != "$id3" ]
}
