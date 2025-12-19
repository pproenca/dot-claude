#!/usr/bin/env bats

setup() {
  export SCRIPT_DIR="$BATS_TEST_DIRNAME/../scripts"
  export TEST_PLAN="$BATS_TEST_TMPDIR/test-plan.md"
  export TEST_JSON="$BATS_TEST_TMPDIR/test-plan.json"

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

  # Write JSON to file wrapped in markdown code fence (harness expects this format)
  cat > "$TEST_JSON" << EOF
\`\`\`json
$json
\`\`\`
EOF

  # Import into harness (this starts daemon if needed)
  harness plan import --file "$TEST_JSON"

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

  # Ensure clean state - shutdown any existing daemon
  harness shutdown 2>/dev/null || true
  sleep 0.5

  # Create plan with parallel tasks (no dependencies)
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

  # Write JSON to file wrapped in markdown code fence (harness expects this format)
  cat > "$TEST_JSON" << EOF
\`\`\`json
$json
\`\`\`
EOF

  harness plan import --file "$TEST_JSON"

  # Claim first task
  claim1=$(harness task claim)
  id1=$(echo "$claim1" | jq -r '.task.id')

  # Complete first task so we can claim a second one
  harness task complete --id "$id1"

  # Claim second task (should be different)
  claim2=$(harness task claim)
  id2=$(echo "$claim2" | jq -r '.task.id')

  # Complete second task
  harness task complete --id "$id2"

  # Claim third task (should be different from both)
  claim3=$(harness task claim)
  id3=$(echo "$claim3" | jq -r '.task.id')

  # All IDs should be different
  [ "$id1" != "$id2" ]
  [ "$id2" != "$id3" ]
  [ "$id1" != "$id3" ]
}
