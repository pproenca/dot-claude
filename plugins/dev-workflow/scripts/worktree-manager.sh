#!/usr/bin/env bash
# worktree-manager.sh - Simple git worktree management
# Based on DHH's agent-git-trees pattern
# Naming convention: parentdir--branchname

set -euo pipefail

# Create a new worktree with a branch
# Usage: create_worktree <branch-name>
# Creates worktree at ../<current-dir>--<branch-name>
create_worktree() {
  local branch="${1:?Branch name required}"
  local current_dir
  current_dir="$(basename "$(pwd)")"
  local worktree_path="../${current_dir}--${branch}"

  # Create worktree with new branch
  git worktree add -b "$branch" "$worktree_path"

  # Add to .gitignore if not already there
  local gitignore_entry="/${current_dir}--*"
  if ! grep -qF "$gitignore_entry" ../.gitignore 2>/dev/null; then
    echo "$gitignore_entry" >> ../.gitignore
  fi

  echo "$worktree_path"
}

# Remove current worktree and its branch
# Must be called from within a worktree directory
# Usage: remove_worktree
remove_worktree() {
  local current_dir
  current_dir="$(basename "$(pwd)")"

  # Extract root and branch from pattern: root--branch
  local root="${current_dir%%--*}"
  local branch="${current_dir#*--}"

  # Safety check: ensure we're in a worktree (not main repo)
  if [[ "$root" == "$branch" ]]; then
    echo "ERROR: Not in a worktree directory (expected pattern: name--branch)" >&2
    return 1
  fi

  # Get paths before we leave
  local worktree_path
  worktree_path="$(pwd)"
  local main_repo
  main_repo="$(get_main_worktree)"

  # Move to main repo (not parent directory - parent may not be a git repo)
  cd "$main_repo"

  # Remove worktree forcefully
  git worktree remove --force "$worktree_path"

  # Delete the branch
  git branch -D "$branch" 2>/dev/null || true

  echo "Removed worktree and branch: $branch"
}

# List all worktrees
list_worktrees() {
  git worktree list
}

# Check if currently in main repo (not a worktree)
is_main_repo() {
  local current_dir
  current_dir="$(basename "$(pwd)")"
  local root="${current_dir%%--*}"
  local branch="${current_dir#*--}"

  # If root equals branch, no -- separator found = main repo
  [[ "$root" == "$branch" ]]
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
    *)
      echo "Usage: $0 {create <branch>|remove|list|is-main}"
      exit 1
      ;;
  esac
fi
