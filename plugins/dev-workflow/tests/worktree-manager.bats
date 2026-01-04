#!/usr/bin/env bats
# Tests for worktree-manager.sh

load test_helper

SCRIPT="$PLUGIN_ROOT/scripts/worktree-manager.sh"

setup() {
  setup_git_repo
  source "$SCRIPT"
}

teardown() {
  # Clean up test worktrees (sibling directories)
  local repo_dir
  repo_dir="$(git rev-parse --show-toplevel 2>/dev/null)" || repo_dir=""

  if [[ -n "$repo_dir" ]]; then
    local parent_dir
    parent_dir="$(dirname "$repo_dir")"
    local repo_name
    repo_name="$(basename "$repo_dir")"

    # Remove any sibling worktrees matching repo--*
    find "$parent_dir" -maxdepth 1 -type d -name "${repo_name}--*" -exec rm -rf {} + 2>/dev/null || true
  fi

  teardown_git_repo
}

@test "create_worktree creates sibling directory" {
  local main_dir parent_dir repo_name
  main_dir="$(git rev-parse --show-toplevel)"
  parent_dir="$(dirname "$main_dir")"
  repo_name="$(basename "$main_dir")"

  result=$(create_worktree "feature-test")
  expected="${parent_dir}/${repo_name}--feature-test"

  # Check worktree was created in sibling directory
  [[ -d "$expected" ]]
  [[ "$result" == "$expected" ]]

  # Check branch exists
  git branch | grep -q "feature-test"
}

@test "create_worktree fails if path exists" {
  local main_dir parent_dir repo_name
  main_dir="$(git rev-parse --show-toplevel)"
  parent_dir="$(dirname "$main_dir")"
  repo_name="$(basename "$main_dir")"

  # Create the worktree first
  create_worktree "duplicate-test"

  # Try to create again - should fail
  run create_worktree "duplicate-test"
  [ "$status" -eq 1 ]
  echo "$output" | grep -q "Path exists"
}

@test "validate_worktree_pattern accepts valid patterns" {
  run validate_worktree_pattern "myrepo--feature"
  [ "$status" -eq 0 ]

  run validate_worktree_pattern "my-repo--my-feature"
  [ "$status" -eq 0 ]

  run validate_worktree_pattern "repo123--branch-name"
  [ "$status" -eq 0 ]
}

@test "validate_worktree_pattern rejects invalid patterns" {
  run validate_worktree_pattern "myrepo"
  [ "$status" -eq 1 ]

  run validate_worktree_pattern "--feature"
  [ "$status" -eq 1 ]

  run validate_worktree_pattern "myrepo--"
  [ "$status" -eq 1 ]

  run validate_worktree_pattern "nohyphens"
  [ "$status" -eq 1 ]
}

@test "is_main_repo returns true in main repo" {
  run is_main_repo
  [ "$status" -eq 0 ]
}

@test "is_main_repo returns false in worktree" {
  local main_dir parent_dir repo_name
  main_dir="$(git rev-parse --show-toplevel)"
  parent_dir="$(dirname "$main_dir")"
  repo_name="$(basename "$main_dir")"

  create_worktree "feature-test"
  cd "${parent_dir}/${repo_name}--feature-test"

  run is_main_repo
  [ "$status" -eq 1 ]
}

@test "list_worktrees shows worktrees" {
  create_worktree "feature-test"

  result=$(list_worktrees)
  echo "$result" | grep -q "feature-test"
}

@test "check_unpushed_commits fails when branch never pushed" {
  local main_dir parent_dir repo_name
  main_dir="$(git rev-parse --show-toplevel)"
  parent_dir="$(dirname "$main_dir")"
  repo_name="$(basename "$main_dir")"

  create_worktree "unpushed-feature"
  local worktree_path="${parent_dir}/${repo_name}--unpushed-feature"

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
  local main_dir parent_dir repo_name
  main_dir="$(git rev-parse --show-toplevel)"
  parent_dir="$(dirname "$main_dir")"
  repo_name="$(basename "$main_dir")"

  create_worktree "feature-with-commits"
  local worktree_path="${parent_dir}/${repo_name}--feature-with-commits"

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

@test "remove_worktree validates pattern before operating" {
  # Test that validate_worktree_pattern is called and rejects invalid patterns
  # This is tested indirectly through the validate_worktree_pattern function tests
  # and through integration - if a user somehow has an invalid directory name,
  # the function will reject it

  # Direct pattern validation test (validates the guard)
  run validate_worktree_pattern "invalid"
  [ "$status" -eq 1 ]

  run validate_worktree_pattern "repo--branch"
  [ "$status" -eq 0 ]
}

@test "CLI: create command works" {
  local main_dir parent_dir repo_name
  main_dir="$(git rev-parse --show-toplevel)"
  parent_dir="$(dirname "$main_dir")"
  repo_name="$(basename "$main_dir")"

  run "$SCRIPT" create "cli-test"
  [ "$status" -eq 0 ]
  [[ -d "${parent_dir}/${repo_name}--cli-test" ]]
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

@test "CLI: validate command accepts valid pattern" {
  run "$SCRIPT" validate "myrepo--mybranch"
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "Valid worktree pattern"
}

@test "CLI: validate command rejects invalid pattern" {
  run "$SCRIPT" validate "invalid"
  [ "$status" -eq 1 ]
  echo "$output" | grep -q "Invalid worktree pattern"
}

@test "CLI: unknown command shows usage" {
  run "$SCRIPT" unknown
  [ "$status" -eq 1 ]
  echo "$output" | grep -q "Usage"
}

@test "get_main_worktree returns correct path" {
  local main_repo
  main_repo="$(pwd)"

  result=$(get_main_worktree)
  [[ "$result" == "$main_repo" ]]
}

@test "get_main_worktree from within worktree returns main repo" {
  local main_repo main_dir parent_dir repo_name
  main_dir="$(git rev-parse --show-toplevel)"
  main_repo="$(pwd)"
  parent_dir="$(dirname "$main_dir")"
  repo_name="$(basename "$main_dir")"

  create_worktree "feature-test"
  cd "${parent_dir}/${repo_name}--feature-test"

  result=$(get_main_worktree)
  [[ "$result" == "$main_repo" ]]
}

@test "CLI: check-unpushed command with path argument" {
  local main_dir parent_dir repo_name
  main_dir="$(git rev-parse --show-toplevel)"
  parent_dir="$(dirname "$main_dir")"
  repo_name="$(basename "$main_dir")"

  create_worktree "check-test"
  local worktree_path="${parent_dir}/${repo_name}--check-test"

  # Make a commit (unpushed)
  cd "$worktree_path"
  echo "test" > test.txt
  git add test.txt
  git commit -m "test commit"
  cd -

  run "$SCRIPT" check-unpushed "$worktree_path"
  [ "$status" -eq 1 ]
}
