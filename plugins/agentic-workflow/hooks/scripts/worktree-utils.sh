#!/bin/bash
set -euo pipefail
# Worktree utilities for agentic-workflow plugin
# Provides functions to create, manage, and clean up git worktrees
# Worktrees are stored at ~/.dot-claude-worktrees/<project>--<branch>

# Configuration
WORKTREE_BASE="${DOT_CLAUDE_WORKTREES:-$HOME/.dot-claude-worktrees}"

# Get the project name from current git repo
worktree_project_name() {
    local repo_root
    repo_root=$(git rev-parse --show-toplevel 2>/dev/null)
    if [ -z "$repo_root" ]; then
        echo ""
        return 1
    fi
    basename "$repo_root"
}

# Get the main repo root (works from within a worktree too)
worktree_main_repo() {
    local common_dir
    common_dir=$(git rev-parse --git-common-dir 2>/dev/null)
    if [ -z "$common_dir" ]; then
        echo ""
        return 1
    fi
    # The common dir is the .git directory of the main repo
    dirname "$common_dir"
}

# Check if we're currently in a worktree (not the main repo)
worktree_is_worktree() {
    local git_dir common_dir
    git_dir=$(git rev-parse --git-dir 2>/dev/null)
    common_dir=$(git rev-parse --git-common-dir 2>/dev/null)

    if [ -z "$git_dir" ] || [ -z "$common_dir" ]; then
        return 1
    fi

    # If git-dir and git-common-dir differ, we're in a worktree
    [ "$git_dir" != "$common_dir" ]
}

# Get current worktree name (project--branch format)
worktree_current() {
    if ! worktree_is_worktree; then
        echo ""
        return 1
    fi

    local cwd
    cwd=$(pwd)
    basename "$cwd"
}

# Get current worktree branch name
worktree_current_branch() {
    if ! worktree_is_worktree; then
        echo ""
        return 1
    fi

    local worktree_name
    worktree_name=$(worktree_current)
    # Extract branch name (everything after first --)
    echo "${worktree_name#*--}"
}

# Generate worktree path for a branch
worktree_path() {
    local branch="$1"
    local project
    project=$(worktree_project_name)

    if [ -z "$project" ] || [ -z "$branch" ]; then
        echo ""
        return 1
    fi

    echo "${WORKTREE_BASE}/${project}--${branch}"
}

# Check if a worktree exists for a branch
worktree_exists() {
    local branch="$1"
    local wt_path
    wt_path=$(worktree_path "$branch")

    [ -d "$wt_path" ]
}

# Create a new worktree
# Usage: worktree_create <branch-name> [base-branch]
worktree_create() {
    local branch="$1"
    local base="${2:-HEAD}"

    if [ -z "$branch" ]; then
        echo "Usage: worktree_create <branch-name> [base-branch]"
        return 1
    fi

    local project wt_path
    project=$(worktree_project_name)
    wt_path=$(worktree_path "$branch")

    if [ -z "$project" ]; then
        echo "Error: Not in a git repository"
        return 1
    fi

    # Ensure base directory exists
    mkdir -p "$WORKTREE_BASE"

    # Check if worktree already exists
    if [ -d "$wt_path" ]; then
        echo "Worktree already exists: $wt_path"
        echo "$wt_path"
        return 0
    fi

    # Create the worktree with a new branch
    echo "Creating worktree: $wt_path"
    if git worktree add -b "$branch" "$wt_path" "$base" 2>/dev/null; then
        # Create .claude directory in the new worktree
        mkdir -p "${wt_path}/.claude/artifacts"
        echo "$wt_path"
        return 0
    else
        # Branch might already exist, try without -b
        if git worktree add "$wt_path" "$branch" 2>/dev/null; then
            mkdir -p "${wt_path}/.claude/artifacts"
            echo "$wt_path"
            return 0
        else
            echo "Error: Failed to create worktree"
            return 1
        fi
    fi
}

# Remove a worktree
# Usage: worktree_remove <branch-name> [--delete-branch]
worktree_remove() {
    local branch="$1"
    local delete_branch="${2:-}"

    if [ -z "$branch" ]; then
        echo "Usage: worktree_remove <branch-name> [--delete-branch]"
        return 1
    fi

    local wt_path
    wt_path=$(worktree_path "$branch")

    if [ ! -d "$wt_path" ]; then
        echo "Worktree does not exist: $wt_path"
        return 1
    fi

    # Remove the worktree
    echo "Removing worktree: $wt_path"
    git worktree remove "$wt_path" --force

    # Optionally delete the branch
    if [ "$delete_branch" = "--delete-branch" ]; then
        echo "Deleting branch: $branch"
        git branch -D "$branch" 2>/dev/null || true
    fi
}

# List all worktrees for current project
worktree_list() {
    local project
    project=$(worktree_project_name)

    if [ -z "$project" ]; then
        echo "Error: Not in a git repository"
        return 1
    fi

    echo "Worktrees for project: $project"
    echo "Location: $WORKTREE_BASE"
    echo ""

    # Use git worktree list for accurate info
    git worktree list | while read -r line; do
        echo "$line"
    done
}

# Clean up stale worktrees
worktree_cleanup() {
    local project
    project=$(worktree_project_name)

    if [ -z "$project" ]; then
        echo "Error: Not in a git repository"
        return 1
    fi

    echo "Pruning stale worktrees..."
    git worktree prune

    # List remaining worktrees in our base directory
    if [ -d "$WORKTREE_BASE" ]; then
        echo ""
        echo "Remaining worktrees in $WORKTREE_BASE:"
        ls -la "$WORKTREE_BASE" 2>/dev/null | grep "^d" | grep -v "^\.\.$" | grep -v "^\.$" || echo "(none)"
    fi
}

# Get state directory for current context (worktree or main repo)
worktree_state_dir() {
    if worktree_is_worktree; then
        echo "$(pwd)/.claude"
    else
        echo "$(git rev-parse --show-toplevel 2>/dev/null)/.claude"
    fi
}

# Read a configuration value from agentic-workflow.local.md YAML frontmatter
# Usage: read_plugin_config <key> [default_value]
# Example: read_plugin_config test_command "uv run pytest"
read_plugin_config() {
    local key="$1"
    local default="${2:-}"
    local config_file
    config_file="$(worktree_state_dir)/agentic-workflow.local.md"

    if [[ ! -f "$config_file" ]]; then
        echo "$default"
        return 0
    fi

    # Extract YAML frontmatter value (between --- markers)
    local value
    value=$(sed -n '/^---$/,/^---$/{ /^---$/d; /^'"$key"':/{ s/^'"$key"': *//; s/^ *//; s/ *$//; p; } }' "$config_file" 2>/dev/null | head -1)

    if [[ -n "$value" ]]; then
        # Remove surrounding quotes if present
        value="${value#\"}"
        value="${value%\"}"
        value="${value#\'}"
        value="${value%\'}"
        echo "$value"
    else
        echo "$default"
    fi
}

# Merge worktree branch back to target branch
# Usage: worktree_merge <worktree-branch> [target-branch]
worktree_merge() {
    local wt_branch="$1"
    local target="${2:-main}"

    if [ -z "$wt_branch" ]; then
        echo "Usage: worktree_merge <worktree-branch> [target-branch]"
        return 1
    fi

    local main_repo
    main_repo=$(worktree_main_repo)

    if [ -z "$main_repo" ]; then
        echo "Error: Cannot find main repository"
        return 1
    fi

    # Switch to main repo
    cd "$main_repo" || return 1

    # Checkout target and merge
    git checkout "$target"
    git merge "$wt_branch" --no-edit
}

# Export functions for use by other scripts
export -f worktree_project_name
export -f worktree_main_repo
export -f worktree_is_worktree
export -f worktree_current
export -f worktree_current_branch
export -f worktree_path
export -f worktree_exists
export -f worktree_create
export -f worktree_remove
export -f worktree_list
export -f worktree_cleanup
export -f worktree_state_dir
export -f worktree_merge
export -f read_plugin_config
export WORKTREE_BASE
