#!/usr/bin/env bash
# Worktree Guards - PreToolUse hook for git worktree commands
# - Blocks 'git worktree add' if target directory not in .gitignore
# - Blocks 'git worktree remove' if cwd is inside the worktree

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

check_worktree_add() {
  local command="$1"
  local worktree_dir gitignore_path

  # Extract worktree directory from command
  local args
  args="${command#*git worktree add}"
  args="$(echo "$args" | sed 's/^[[:space:]]*//')"

  # Skip -b and --branch flags with their arguments
  while [[ "${args}" =~ ^-[bB][[:space:]] ]] || [[ "${args}" =~ ^--branch[[:space:]] ]]; do
    args="$(echo "$args" | sed 's/^-[bB][[:space:]]*//' | sed 's/^--branch[[:space:]]*//')"
    args="$(echo "$args" | sed 's/^[^[:space:]]*[[:space:]]*//')"
  done

  # Skip other flags
  while [[ "${args}" =~ ^- ]]; do
    args="$(echo "$args" | sed 's/^[^[:space:]]*[[:space:]]*//')"
  done

  worktree_dir="$(echo "$args" | awk '{print $1}')"

  if [[ -z "${worktree_dir}" ]]; then
    output_decision "allow"
    return
  fi

  local dir_name
  dir_name="$(basename "${worktree_dir}")"
  gitignore_path=".gitignore"

  if [[ ! -f "${gitignore_path}" ]]; then
    output_decision "deny" "BLOCKED: No .gitignore found. Add '${dir_name}/' to .gitignore before creating worktree."
    return
  fi

  # Check if worktree is under .worktrees/ or worktrees/
  if [[ "${worktree_dir}" =~ ^\.worktrees/ ]] && grep -qE '^\\.worktrees/?$' "${gitignore_path}" 2>/dev/null; then
    output_decision "allow"
    return
  fi

  if [[ "${worktree_dir}" =~ ^worktrees/ ]] && grep -qE '^worktrees/?$' "${gitignore_path}" 2>/dev/null; then
    output_decision "allow"
    return
  fi

  # Check for exact directory match
  if grep -qE "^${dir_name}/?$|^${worktree_dir}/?$" "${gitignore_path}" 2>/dev/null; then
    output_decision "allow"
    return
  fi

  # Check parent directory
  local parent_dir
  parent_dir="$(dirname "${worktree_dir}")"
  if [[ "${parent_dir}" != "." ]] && grep -qE "^${parent_dir}/?$" "${gitignore_path}" 2>/dev/null; then
    output_decision "allow"
    return
  fi

  output_decision "deny" "BLOCKED: '${worktree_dir}' not in .gitignore. Add '${dir_name}/' first."
}

check_worktree_remove() {
  local command="$1"
  local worktree_path cwd

  # Extract worktree path from command
  local args
  args="${command#*git worktree remove}"
  args="$(echo "$args" | sed 's/^[[:space:]]*//')"

  # Skip flags
  while [[ "${args}" =~ ^- ]]; do
    args="$(echo "$args" | sed 's/^[^[:space:]]*[[:space:]]*//')"
  done

  worktree_path="$(echo "$args" | awk '{print $1}')"

  if [[ -z "${worktree_path}" ]]; then
    output_decision "allow"
    return
  fi

  # Resolve to absolute path
  local resolved_worktree
  if [[ "${worktree_path}" = /* ]]; then
    resolved_worktree="${worktree_path}"
  else
    local main_worktree
    main_worktree="$(git worktree list 2>/dev/null | head -1 | awk '{print $1}' || echo "")"
    if [[ -n "${main_worktree}" ]]; then
      resolved_worktree="${main_worktree}/${worktree_path}"
    else
      resolved_worktree="$(pwd)/${worktree_path}"
    fi
  fi

  resolved_worktree="$(cd "${resolved_worktree}" 2>/dev/null && pwd || echo "${resolved_worktree}")"
  cwd="$(pwd)"

  if [[ "${cwd}" = "${resolved_worktree}" ]] || [[ "${cwd}" = "${resolved_worktree}/"* ]]; then
    local main_worktree
    main_worktree="$(git worktree list 2>/dev/null | head -1 | awk '{print $1}' || echo "main repository")"
    output_decision "deny" "BLOCKED: Cannot remove worktree while inside it. First: cd ${main_worktree}"
    return
  fi

  output_decision "allow"
}

main() {
  local input command

  input="$(cat)"
  command="$(echo "${input}" | jq -r '.tool_input.command // ""')"

  if [[ "${command}" =~ git[[:space:]]+worktree[[:space:]]+add ]]; then
    check_worktree_add "$command"
  elif [[ "${command}" =~ git[[:space:]]+worktree[[:space:]]+remove ]]; then
    check_worktree_remove "$command"
  else
    output_decision "allow"
  fi
}

main "$@"
