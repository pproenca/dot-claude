#!/usr/bin/env bash
# worktree-manager.sh - Simple git worktree management
# Worktrees stored in ~/.dot-claude-worktrees/<repo>/<branch>

set -euo pipefail

# Worktree base directory
WORKTREE_BASE="${HOME}/.dot-claude-worktrees"

# Create a new worktree with a branch
# Usage: create_worktree <branch-name>
# Creates worktree at ~/.dot-claude-worktrees/<repo>/<branch>
create_worktree() {
  local branch="${1:?Branch name required}"
  local repo_name
  repo_name="$(basename "$(git rev-parse --show-toplevel)")"
  local worktree_dir="${WORKTREE_BASE}/${repo_name}"
  mkdir -p "$worktree_dir"
  local worktree_path="${worktree_dir}/${branch}"

  # Create worktree with new branch
  git worktree add -b "$branch" "$worktree_path"

  echo "$worktree_path"
}

# Check if a branch has unpushed commits
# Usage: check_unpushed_commits <worktree_path>
# Returns 0 if safe (no unpushed commits), 1 if unsafe
check_unpushed_commits() {
  local worktree_path="${1:?Worktree path required}"
  local branch
  branch=$(git -C "$worktree_path" branch --show-current)

  # Check if branch exists on remote
  if ! git ls-remote --heads origin "$branch" 2>/dev/null | grep -q .; then
    echo "ERROR: Branch '$branch' has never been pushed to remote!" >&2
    echo "Push your changes first: git push -u origin $branch" >&2
    return 1
  fi

  # Check for unpushed commits
  local unpushed
  unpushed=$(git -C "$worktree_path" log "origin/$branch..$branch" --oneline 2>/dev/null)
  if [[ -n "$unpushed" ]]; then
    echo "ERROR: Branch '$branch' has unpushed commits:" >&2
    echo "$unpushed" >&2
    echo "Push your changes first: git push origin $branch" >&2
    return 1
  fi

  return 0
}

# Get worktree path for a branch
# Usage: get_worktree_path <branch>
get_worktree_path() {
  local branch="${1:?Branch name required}"
  local repo_name
  repo_name="$(basename "$(git rev-parse --show-toplevel)")"
  echo "${WORKTREE_BASE}/${repo_name}/${branch}"
}

# Remove current worktree and its branch
# Must be called from within a worktree directory
# Usage: remove_worktree
remove_worktree() {
  # Safety check: ensure we're in a worktree (not main repo)
  if is_main_repo; then
    echo "ERROR: Not in a worktree directory (currently in main repo)" >&2
    return 1
  fi

  # Get branch name from current branch
  local branch
  branch="$(git branch --show-current)"

  # Get paths before we leave
  local worktree_path
  worktree_path="$(pwd)"
  local main_repo
  main_repo="$(get_main_worktree)"

  # SAFETY: Check for unpushed commits before removal
  if ! check_unpushed_commits "$worktree_path"; then
    echo "Refusing to delete worktree with unpushed work." >&2
    return 1
  fi

  # Move to main repo
  cd "$main_repo"

  # Remove worktree (no --force - let it fail if there are changes)
  git worktree remove "$worktree_path"

  # Delete the branch (use -d not -D - fails if unmerged)
  git branch -d "$branch"

  echo "Removed worktree and branch: $branch"
}

# List all worktrees
list_worktrees() {
  git worktree list
}

# Check if currently in main repo (not a linked worktree)
is_main_repo() {
  # Use git's built-in worktree detection
  # Returns true if this is the main worktree, false if it's a linked worktree
  local git_common_dir git_dir
  git_dir="$(git rev-parse --git-dir 2>/dev/null)" || return 1
  git_common_dir="$(git rev-parse --git-common-dir 2>/dev/null)" || return 1

  # In main repo: .git dir equals .git common dir
  # In linked worktree: .git dir is different from .git common dir
  [[ "$git_dir" == "$git_common_dir" ]]
}

# Get path to main worktree
get_main_worktree() {
  git worktree list --porcelain | grep "^worktree " | head -1 | cut -d' ' -f2
}

# CLI interface
if [[ "${BASH_SOURCE[0]:-}" == "${0}" ]]; then
  case "${1:-help}" in
    create)
      create_worktree "${2:?Branch name required}"
      ;;
    remove)
      remove_worktree
      ;;
    list)
      list_worktrees
      ;;
    is-main)
      if is_main_repo; then
        echo "true"
      else
        echo "false"
        exit 1
      fi
      ;;
    check-unpushed)
      check_unpushed_commits "${2:-.}"
      ;;
    get-path)
      get_worktree_path "${2:?Branch name required}"
      ;;
    *)
      echo "Usage: $0 {create <branch>|remove|list|is-main|check-unpushed [path]|get-path <branch>}"
      exit 1
      ;;
  esac
fi
