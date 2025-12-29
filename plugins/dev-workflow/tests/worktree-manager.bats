#!/usr/bin/env bats
# Tests for worktree-manager.sh

load test_helper

SCRIPT="$PLUGIN_ROOT/scripts/worktree-manager.sh"

setup() {
  setup_git_repo
  source "$SCRIPT"
}

teardown() {
  teardown_git_repo
}

@test "create_worktree creates worktree with branch" {
  result=$(create_worktree "feature-test")

  # Check worktree was created
  [[ -d "../$(basename "$TEST_DIR")--feature-test" ]]

  # Check branch exists
  git branch | grep -q "feature-test"
}

@test "create_worktree adds gitignore entry" {
  create_worktree "feature-test"

  # Check .gitignore in parent has entry
  grep -q "$(basename "$TEST_DIR")--" ../.gitignore
}

@test "is_main_repo returns true in main repo" {
  run is_main_repo
  [ "$status" -eq 0 ]
}

@test "is_main_repo returns false in worktree" {
  create_worktree "feature-test"
  cd "../$(basename "$TEST_DIR")--feature-test"

  run is_main_repo
  [ "$status" -eq 1 ]
}

@test "list_worktrees shows worktrees" {
  create_worktree "feature-test"

  result=$(list_worktrees)
  echo "$result" | grep -q "feature-test"
}

@test "remove_worktree removes worktree and branch" {
  local main_dir="$TEST_DIR"
  create_worktree "feature-test"
  cd "../$(basename "$TEST_DIR")--feature-test"

  remove_worktree

  # Should be back in parent, worktree gone
  cd "$main_dir"
  ! git branch | grep -q "feature-test"
  [[ ! -d "../$(basename "$main_dir")--feature-test" ]]
}

@test "remove_worktree fails in main repo" {
  run remove_worktree
  [ "$status" -eq 1 ]
  echo "$output" | grep -q "Not in a worktree"
}

@test "CLI: create command works" {
  run "$SCRIPT" create "cli-test"
  [ "$status" -eq 0 ]
  [[ -d "../$(basename "$TEST_DIR")--cli-test" ]]
}

@test "CLI: list command works" {
  run "$SCRIPT" list
  [ "$status" -eq 0 ]
}

@test "CLI: is-main command works" {
  run "$SCRIPT" is-main
  [ "$status" -eq 0 ]
  [ "$output" = "true" ]
}

@test "CLI: unknown command shows usage" {
  run "$SCRIPT" unknown
  [ "$status" -eq 1 ]
  echo "$output" | grep -q "Usage"
}
