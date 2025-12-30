#!/usr/bin/env bats
# Tests for worktree-manager.sh

load test_helper

SCRIPT="$PLUGIN_ROOT/scripts/worktree-manager.sh"

setup() {
  setup_git_repo
  source "$SCRIPT"

  # Store original WORKTREE_BASE and override for testing
  ORIGINAL_WORKTREE_BASE="${WORKTREE_BASE:-}"
  export WORKTREE_BASE="${BATS_TEST_TMPDIR}/.dot-claude-worktrees"
  mkdir -p "$WORKTREE_BASE"
}

teardown() {
  # Restore original WORKTREE_BASE
  if [[ -n "$ORIGINAL_WORKTREE_BASE" ]]; then
    export WORKTREE_BASE="$ORIGINAL_WORKTREE_BASE"
  fi

  # Clean up test worktrees
  if [[ -d "${BATS_TEST_TMPDIR}/.dot-claude-worktrees" ]]; then
    rm -rf "${BATS_TEST_TMPDIR}/.dot-claude-worktrees"
  fi

  teardown_git_repo
}

@test "create_worktree creates worktree in centralized location" {
  local repo_name
  repo_name="$(basename "$(git rev-parse --show-toplevel)")"

  result=$(create_worktree "feature-test")

  # Check worktree was created in ~/.dot-claude-worktrees/<repo>/<branch>
  [[ -d "${WORKTREE_BASE}/${repo_name}/feature-test" ]]

  # Check branch exists
  git branch | grep -q "feature-test"
}

@test "create_worktree returns correct path" {
  local repo_name
  repo_name="$(basename "$(git rev-parse --show-toplevel)")"

  result=$(create_worktree "feature-test")

  [[ "$result" == "${WORKTREE_BASE}/${repo_name}/feature-test" ]]
}

@test "get_worktree_path returns correct path" {
  local repo_name
  repo_name="$(basename "$(git rev-parse --show-toplevel)")"

  result=$(get_worktree_path "my-feature")

  [[ "$result" == "${WORKTREE_BASE}/${repo_name}/my-feature" ]]
}

@test "is_main_repo returns true in main repo" {
  run is_main_repo
  [ "$status" -eq 0 ]
}

@test "is_main_repo returns false in worktree" {
  local repo_name
  repo_name="$(basename "$(git rev-parse --show-toplevel)")"

  create_worktree "feature-test"
  cd "${WORKTREE_BASE}/${repo_name}/feature-test"

  run is_main_repo
  [ "$status" -eq 1 ]
}

@test "list_worktrees shows worktrees" {
  create_worktree "feature-test"

  result=$(list_worktrees)
  echo "$result" | grep -q "feature-test"
}

@test "check_unpushed_commits fails when branch never pushed" {
  local repo_name
  repo_name="$(basename "$(git rev-parse --show-toplevel)")"

  create_worktree "unpushed-feature"
  local worktree_path="${WORKTREE_BASE}/${repo_name}/unpushed-feature"

  # Make a commit in the worktree
  cd "$worktree_path"
  echo "test" > test.txt
  git add test.txt
  git commit -m "test commit"
  cd -

  run check_unpushed_commits "$worktree_path"
  [ "$status" -eq 1 ]
  echo "$output" | grep -q "never been pushed"
}

@test "remove_worktree fails in main repo" {
  run remove_worktree
  [ "$status" -eq 1 ]
  echo "$output" | grep -q "Not in a worktree"
}

@test "remove_worktree fails with unpushed commits" {
  local repo_name
  repo_name="$(basename "$(git rev-parse --show-toplevel)")"

  create_worktree "feature-with-commits"
  local worktree_path="${WORKTREE_BASE}/${repo_name}/feature-with-commits"

  # Make a commit in the worktree (unpushed)
  cd "$worktree_path"
  echo "test" > test.txt
  git add test.txt
  git commit -m "test commit"

  # Try to remove - should fail due to unpushed commits
  run remove_worktree
  [ "$status" -eq 1 ]
  echo "$output" | grep -q "unpushed"
}

@test "CLI: create command works" {
  local repo_name
  repo_name="$(basename "$(git rev-parse --show-toplevel)")"

  run "$SCRIPT" create "cli-test"
  [ "$status" -eq 0 ]
  [[ -d "${WORKTREE_BASE}/${repo_name}/cli-test" ]]
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

@test "CLI: get-path command works" {
  local repo_name
  repo_name="$(basename "$(git rev-parse --show-toplevel)")"

  run "$SCRIPT" get-path "my-branch"
  [ "$status" -eq 0 ]
  [[ "$output" == "${WORKTREE_BASE}/${repo_name}/my-branch" ]]
}

@test "CLI: unknown command shows usage" {
  run "$SCRIPT" unknown
  [ "$status" -eq 1 ]
  echo "$output" | grep -q "Usage"
}
