#!/usr/bin/env bash
# Worktree Guard - PreToolUse hook for main branch warning
# Provides informational note when editing on main/master branch

set -euo pipefail

output_decision() {
  local decision="$1"
  local reason="${2:-}"
  if [[ -n "$reason" ]]; then
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "${decision}",
    "permissionDecisionReason": "${reason}"
  }
}
EOF
  else
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "${decision}"
  }
}
EOF
  fi
}

main() {
  local input file_path branch toplevel worktree_main

  input="$(cat)"
  file_path="$(echo "${input}" | jq -r '.tool_input.file_path // .tool_input.path // ""')"

  # If no file path found, allow (safety default)
  if [[ -z "${file_path}" ]]; then
    output_decision "allow"
    exit 0
  fi

  # Skip non-code files (docs, config, scripts, etc.)
  if [[ "${file_path}" =~ \.(md|json|yaml|yml|toml|txt|gitignore|env|lock|log|csv|xml|html|css|scss|less|sh)$ ]]; then
    output_decision "allow"
    exit 0
  fi

  # Skip dotfiles/hidden files
  if [[ "${file_path}" =~ (^|/)\.[^/]+$ ]]; then
    output_decision "allow"
    exit 0
  fi

  # Check if in worktree (different from main worktree)
  toplevel="$(git rev-parse --show-toplevel 2>/dev/null || echo "")"
  worktree_main="$(git worktree list 2>/dev/null | head -1 | awk '{print $1}' || echo "")"

  if [[ -n "$toplevel" && "$toplevel" != "$worktree_main" ]]; then
    # In a worktree, allow silently
    output_decision "allow"
    exit 0
  fi

  # Check if on main/master
  branch="$(git branch --show-current 2>/dev/null || echo "")"
  if [[ "$branch" == "main" || "$branch" == "master" ]]; then
    output_decision "allow" "NOTE: Editing on ${branch} branch. Consider super:using-git-worktrees for isolation."
    exit 0
  fi

  output_decision "allow"
}

main "$@"
