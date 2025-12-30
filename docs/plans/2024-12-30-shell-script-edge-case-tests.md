# Shell Script Edge Case Tests

> **Execution:** Use `/dev-workflow:execute-plan docs/plans/2024-12-30-shell-script-edge-case-tests.md` to implement task-by-task.

**Goal:** Add critical path tests for shell scripts that have gaps in coverage.

**Architecture:** New test file for `check-worktree-setup.sh`, extend existing test files for `hook-helpers.bats` and `worktree-manager.bats`.

**Tech Stack:** Bats (Bash Automated Testing System), test_helper.bash fixtures

---

## Task Groups

| Task Group | Tasks | Rationale |
|------------|-------|-----------|
| Group 1 | 1, 2, 3 | Independent test files, no file overlap |

---

### Task 1: Add check-worktree-setup.sh Tests

**Files:**
- Create: `plugins/dev-workflow/tests/check-worktree-setup.bats`

**Step 1: Write the test file** (5 min)

```bash
#!/usr/bin/env bats
# Tests for check-worktree-setup.sh

load test_helper

SCRIPT="$PLUGIN_ROOT/hooks/check-worktree-setup.sh"

setup() {
  setup_test_dir
  export CLAUDE_PROJECT_DIR="$TEST_DIR"
}

teardown() {
  teardown_test_dir
}

@test "is_configured returns false when settings file missing" {
  run "$SCRIPT"
  [ "$status" -eq 0 ]
  # Should output JSON warning
  echo "$output" | grep -q "hookSpecificOutput"
}

@test "is_configured returns false when settings has no additionalDirectories" {
  mkdir -p "$TEST_DIR/.claude"
  echo '{"permissions": {}}' > "$TEST_DIR/.claude/settings.json"

  run "$SCRIPT"
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "Worktree support not configured"
}

@test "is_configured returns true with tilde path" {
  mkdir -p "$TEST_DIR/.claude"
  cat > "$TEST_DIR/.claude/settings.json" << 'EOF'
{"permissions":{"additionalDirectories":["~/.dot-claude-worktrees"]}}
EOF

  run "$SCRIPT"
  [ "$status" -eq 0 ]
  # Should NOT output warning when configured
  [[ -z "$output" ]]
}

@test "is_configured returns true with expanded path" {
  mkdir -p "$TEST_DIR/.claude"
  cat > "$TEST_DIR/.claude/settings.json" << EOF
{"permissions":{"additionalDirectories":["$HOME/.dot-claude-worktrees"]}}
EOF

  run "$SCRIPT"
  [ "$status" -eq 0 ]
  [[ -z "$output" ]]
}

@test "outputs valid JSON when not configured" {
  run "$SCRIPT"
  [ "$status" -eq 0 ]
  assert_valid_json
}

@test "always exits with 0" {
  # Missing file
  run "$SCRIPT"
  [ "$status" -eq 0 ]

  # Invalid JSON in settings
  mkdir -p "$TEST_DIR/.claude"
  echo 'not json' > "$TEST_DIR/.claude/settings.json"
  run "$SCRIPT"
  [ "$status" -eq 0 ]
}
```

**Step 2: Run tests to verify they pass** (30 sec)

```bash
bats plugins/dev-workflow/tests/check-worktree-setup.bats
```

Expected: 6 passed

**Step 3: Commit** (30 sec)

```bash
git add plugins/dev-workflow/tests/check-worktree-setup.bats
git commit -m "test(dev-workflow): add check-worktree-setup tests"
```

---

### Task 2: Add get_max_parallel_from_groups Tests

**Files:**
- Modify: `plugins/dev-workflow/tests/hook-helpers.bats`

**Step 1: Write the tests** (3 min)

Add at end of file:

```bash
# ============================================================================
# get_max_parallel_from_groups() tests
# ============================================================================

@test "get_max_parallel_from_groups: returns largest group size" {
  result=$(get_max_parallel_from_groups "group1:1,2,3|group2:4,5|group3:6")
  [[ "$result" == "3" ]]
}

@test "get_max_parallel_from_groups: single group" {
  result=$(get_max_parallel_from_groups "group1:1,2")
  [[ "$result" == "2" ]]
}

@test "get_max_parallel_from_groups: single task groups" {
  result=$(get_max_parallel_from_groups "group1:1|group2:2|group3:3")
  [[ "$result" == "1" ]]
}

@test "get_max_parallel_from_groups: handles decimal task numbers" {
  result=$(get_max_parallel_from_groups "group1:1,1.1,1.2|group2:2")
  [[ "$result" == "3" ]]
}
```

**Step 2: Run tests to verify** (30 sec)

```bash
bats plugins/dev-workflow/tests/hook-helpers.bats
```

Expected: All tests pass (17 existing + 4 new = 21 total)

**Step 3: Commit** (30 sec)

```bash
git add plugins/dev-workflow/tests/hook-helpers.bats
git commit -m "test(dev-workflow): add get_max_parallel_from_groups tests"
```

---

### Task 3: Add Missing worktree-manager Edge Cases

**Files:**
- Modify: `plugins/dev-workflow/tests/worktree-manager.bats`

**Step 1: Write the tests** (3 min)

Add after existing tests:

```bash
@test "get_main_worktree returns correct path" {
  local main_repo
  main_repo="$(pwd)"

  result=$(get_main_worktree)
  [[ "$result" == "$main_repo" ]]
}

@test "get_main_worktree from within worktree returns main repo" {
  local main_repo repo_name
  main_repo="$(pwd)"
  repo_name="$(basename "$(git rev-parse --show-toplevel)")"

  create_worktree "feature-test"
  cd "${WORKTREE_BASE}/${repo_name}/feature-test"

  result=$(get_main_worktree)
  [[ "$result" == "$main_repo" ]]
}

@test "CLI: check-unpushed command with path argument" {
  local repo_name
  repo_name="$(basename "$(git rev-parse --show-toplevel)")"

  create_worktree "check-test"
  local worktree_path="${WORKTREE_BASE}/${repo_name}/check-test"

  # Make a commit (unpushed)
  cd "$worktree_path"
  echo "test" > test.txt
  git add test.txt
  git commit -m "test commit"
  cd -

  run "$SCRIPT" check-unpushed "$worktree_path"
  [ "$status" -eq 1 ]
}
```

**Step 2: Run tests to verify** (30 sec)

```bash
bats plugins/dev-workflow/tests/worktree-manager.bats
```

Expected: All tests pass (14 existing + 3 new = 17 total)

**Step 3: Commit** (30 sec)

```bash
git add plugins/dev-workflow/tests/worktree-manager.bats
git commit -m "test(dev-workflow): add worktree-manager edge case tests"
```

---

### Task 4: Code Review

**Files:**
- Review all changes from Tasks 1-3

**Step 1: Run full test suite** (30 sec)

```bash
bats plugins/dev-workflow/tests/
```

Expected: All tests pass

**Step 2: Run validation** (30 sec)

```bash
plugins/dev-workflow/scripts/validate.sh
```

Expected: Pass (may have pre-existing warnings for LSP in agents)
