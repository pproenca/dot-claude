#!/usr/bin/env bash
# PreToolUse hook for commit plugin
# 1. Validates commit messages follow Conventional Commits specification BEFORE execution
# 2. Validates destructive git commands have proper safety measures

set -euo pipefail

# Valid Conventional Commit types (constant)
readonly VALID_TYPES="feat|fix|docs|chore|refactor|perf|test|build|ci"

# Outputs JSON to deny a tool use with a message
output_deny() {
  local message="$1"
  local escaped_msg
  escaped_msg="$(printf '%s' "${message}" \
    | sed 's/\\/\\\\/g' | sed 's/"/\\"/g')"
  cat <<EOF
{
  "hookSpecificOutput": {
    "permissionDecision": "deny"
  },
  "systemMessage": "${escaped_msg}"
}
EOF
}

# Validates commit message follows Conventional Commits format
# Returns non-zero with error message on stdout if invalid
validate_commit_message() {
  local commit_msg="$1"
  local subject
  local description
  local first_word
  local subject_len

  subject="$(head -1 <<< "${commit_msg}")"

  # Check for valid Conventional Commits format: type[!]: description
  if ! grep -qE "^(${VALID_TYPES})(!)?:[[:space:]].+" <<< "${subject}"; then
    if grep -qE "^(${VALID_TYPES})" <<< "${subject}"; then
      if ! grep -qE ":[[:space:]]" <<< "${subject}"; then
        echo "Missing colon and space after type. Format: 'type: description'"
        return 1
      elif ! grep -qE ":[[:space:]].+" <<< "${subject}"; then
        echo "Empty description after type. Format: 'type: description'"
        return 1
      fi
    else
      echo "Missing type prefix. Must start with: feat, fix, docs, chore, refactor, perf, test, build, or ci"
      return 1
    fi
  fi

  # Extract description (part after "type: " or "type!: ")
  description=""
  if grep -qE "^(${VALID_TYPES})(!)?:[[:space:]]" <<< "${subject}"; then
    description="$(sed -E "s/^(${VALID_TYPES})(!)?:[[:space:]]//" <<< "${subject}")"
  fi

  # Check for vague descriptions
  if [[ -n "${description}" ]]; then
    local vague_patterns=(
      "^bug$" "^build$" "^fix$" "^stuff$" "^things$"
      "^update$" "^updates$" "^changes$" "^misc$"
      "^wip$" "^work in progress$" "^done$" "^ready$"
      "^final$" "^initial$" "^first$" "^test$"
    )

    for pattern in "${vague_patterns[@]}"; do
      if grep -qiE "${pattern}" <<< "${description}"; then
        echo "Vague description '${description}' - be specific about WHAT changed"
        return 1
      fi
    done
  fi

  # Check subject length
  subject_len="${#subject}"
  if (( subject_len > 100 )); then
    echo "Subject too long (${subject_len} chars) - max 100"
    return 1
  fi

  # Check imperative mood in description
  if [[ -n "${description}" ]]; then
    first_word="$(awk '{print $1}' <<< "${description}")"
    if grep -qE "^[A-Z]?[a-z]+ing$" <<< "${first_word}"; then
      echo "Use imperative mood: 'add' not 'adding'"
      return 1
    elif grep -qE "^[A-Z]?[a-z]+ed$" <<< "${first_word}"; then
      echo "Use imperative mood: 'add' not 'added'"
      return 1
    elif grep -qE "^[A-Z][a-z]+s$" <<< "${first_word}"; then
      echo "Use imperative mood: 'add' not 'adds'"
      return 1
    fi
  fi

  # Check for period at end
  if [[ "${subject}" =~ \.$ ]]; then
    echo "Subject must not end with period"
    return 1
  fi

  return 0
}

# Checks for destructive git commands without proper safeguards
# Returns non-zero with error message on stdout if blocked
check_destructive_command() {
  local command="$1"
  local current_branch

  # git reset --hard (dangerous without backup)
  if [[ "${command}" =~ git[[:space:]]+reset[[:space:]]+--hard ]]; then
    local backup_exists
    backup_exists="$(git branch --list 'backup/*' 2>/dev/null | head -1)" \
      || backup_exists=""
    if [[ -z "${backup_exists}" ]]; then
      echo "git reset --hard without backup branch"
      return 1
    fi
  fi

  # git push --force or -f (always warn)
  if [[ "${command}" =~ git[[:space:]]+push[[:space:]]+(--force|-f) ]]; then
    echo "git push --force is dangerous"
    return 1
  fi

  # git branch -D (delete branch permanently)
  if [[ "${command}" =~ git[[:space:]]+branch[[:space:]]+-D ]]; then
    current_branch="$(git branch --show-current 2>/dev/null)" || current_branch=""
    if [[ "${command}" =~ ${current_branch} ]]; then
      echo "Cannot delete current branch"
      return 1
    fi
  fi

  # git clean -fd (remove untracked files)
  if [[ "${command}" =~ git[[:space:]]+clean[[:space:]]+-[[:alnum:]]*f ]]; then
    echo "git clean removes untracked files permanently"
    return 1
  fi

  return 0
}

main() {
  local input
  local current_branch
  local command
  local commit_msg
  local commit_issue
  local destructive_issue

  input="$(cat)"

  # Fast-path: exit immediately if input doesn't contain git (avoid jq parsing overhead)
  # Check for both direct git commands ("git ...) and piped commands (| git ...)
  if ! grep -qE '("git |[|] *git )' <<< "${input}"; then
    echo '{}'
    exit 0
  fi

  # Skip validation on WIP/temp branches (subagents need flexible commits)
  current_branch="$(git branch --show-current 2>/dev/null)" || current_branch=""
  if [[ "${current_branch}" =~ ^(wip|temp|backup)/ ]]; then
    echo '{}'
    exit 0
  fi

  # Extract command from tool_input
  command="$(jq -r '.tool_input.command // empty' <<< "${input}")"

  # Quick exit if not a git command (direct or piped)
  if [[ ! "${command}" =~ (^git|[|][[:space:]]*git) ]]; then
    echo '{}'
    exit 0
  fi

  # === COMMIT MESSAGE VALIDATION ===
  if [[ "${command}" =~ git[[:space:]]+commit ]]; then
    # Extract commit message from -m flag
    commit_msg=""
    if [[ "${command}" =~ -m[[:space:]]+[\"\']([^\"\']+)[\"\'] ]]; then
      commit_msg="${BASH_REMATCH[1]}"
    elif [[ "${command}" =~ -m[[:space:]]+\"([^\"]+)\" ]]; then
      commit_msg="${BASH_REMATCH[1]}"
    elif [[ "${command}" =~ -m[[:space:]]+\'([^\']+)\' ]]; then
      commit_msg="${BASH_REMATCH[1]}"
    elif [[ "${command}" =~ -m[[:space:]]+([^[:space:]]+) ]]; then
      commit_msg="${BASH_REMATCH[1]}"
    fi

    # Handle printf pattern: printf '%b' 'message with \n escapes' | git commit -F -
    # Also supports older printf '%s...' patterns
    if [[ -z "${commit_msg}" ]] && [[ "${command}" =~ git[[:space:]]+commit[[:space:]]+-F[[:space:]]+-[[:space:]]*$ ]]; then
      # Match printf '%b' with single-quoted message (preferred pattern)
      if [[ "${command}" =~ printf[[:space:]]+\'%b\'[[:space:]]+\'([^\']+)\' ]]; then
        # Extract message and convert \n escape sequences to actual newlines for validation
        commit_msg="$(printf '%b' "${BASH_REMATCH[1]}")"
      # Match printf '%s...' with single-quoted first message argument (legacy)
      elif [[ "${command}" =~ printf[[:space:]]+\'%s[^\']*\'[[:space:]]+\'([^\']+)\' ]]; then
        commit_msg="${BASH_REMATCH[1]}"
      # Match printf with double-quoted first message argument (legacy)
      elif [[ "${command}" =~ printf[[:space:]]+\"%s[^\"]*\"[[:space:]]+\"([^\"]+)\" ]]; then
        commit_msg="${BASH_REMATCH[1]}"
      fi
    fi

    if [[ -n "${commit_msg}" ]]; then
      if ! commit_issue="$(validate_commit_message "${commit_msg}" 2>&1)"; then
        output_deny "BLOCKED: ${commit_issue}\\n\\nConventional Commits format: "\
"type: description\\nTypes: feat, fix, docs, chore, refactor, perf, test, "\
"build, ci\\nExample: 'feat: add rate limiting to auth endpoint'"
        exit 0
      fi
    fi
  fi

  # === DESTRUCTIVE COMMAND CHECKS ===
  if ! destructive_issue="$(check_destructive_command "${command}" 2>&1)"; then
    output_deny "BLOCKED: ${destructive_issue}. Create a backup branch first: "\
"git branch backup/\$(git branch --show-current)-\$(date +%Y%m%d-%H%M%S)"
    exit 0
  fi

  echo '{}'
  exit 0
}

main "$@"
