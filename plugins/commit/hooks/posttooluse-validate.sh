#!/usr/bin/env bash
# PostToolUse hook for commit plugin
# Handles post-commit checks that can't be done before execution:
# - Commit size warnings (requires actual commit stats)
# - Non-trivial commit body requirement (requires file count)
# - Breaking change detection (warns if potential breaking change lacks marker)
# Note: Message format validation is in PreToolUse (blocks before commit)

set -euo pipefail

# Checks for potential breaking changes in the diff
# Outputs indicators if breaking changes detected without proper markers
check_breaking_changes() {
  local subject="$1"
  local commit_msg="$2"
  local diff_content
  local breaking_indicators=""

  # Skip if already marked as breaking
  if grep -qE '^[a-z]+!:' <<< "${subject}"; then
    return 0
  fi
  if grep -qE '^BREAKING[ -]CHANGE:' <<< "${commit_msg}"; then
    return 0
  fi

  diff_content="$(git diff HEAD~1..HEAD 2>/dev/null)" || diff_content=""

  # Check for removed function/method definitions
  if grep -qE '^-[[:space:]]*(def |function |public |export (function|const|class))' \
      <<< "${diff_content}"; then
    breaking_indicators="${breaking_indicators}- Removed function/method definition\n"
  fi

  # Check for removed exports
  if grep -qE '^-[[:space:]]*export ' <<< "${diff_content}"; then
    breaking_indicators="${breaking_indicators}- Removed export\n"
  fi

  # Check for changed function signatures (added required parameter)
  if grep -qE '^-.*\([^)]*\)' <<< "${diff_content}" \
      && grep -qE '^\+.*\([^)]*,[^)]*\)' <<< "${diff_content}"; then
    breaking_indicators="${breaking_indicators}- Modified function signature\n"
  fi

  # Check for removed environment variables or config keys
  if grep -qiE '^-[[:space:]]*(ENV|CONFIG|[A-Z_]+_KEY|[A-Z_]+_URL|[A-Z_]+_SECRET)' \
      <<< "${diff_content}"; then
    breaking_indicators="${breaking_indicators}- Removed environment/config variable\n"
  fi

  if [[ -n "${breaking_indicators}" ]]; then
    echo "${breaking_indicators}"
  fi
}

main() {
  local input
  local current_branch
  local command
  local commit_msg
  local lines_changed
  local subject
  local body
  local warning_issues=""
  local file_count
  local is_trivial
  local breaking_indicators

  input="$(cat)"

  # Skip validation on WIP/temp branches
  current_branch="$(git branch --show-current 2>/dev/null)" || current_branch=""
  if [[ "${current_branch}" =~ ^(wip|temp|backup)/ ]]; then
    echo '{}'
    exit 0
  fi

  command="$(jq -r '.tool_input.command // empty' <<< "${input}")"

  if [[ ! "${command}" =~ ^git[[:space:]]+commit ]]; then
    echo '{}'
    exit 0
  fi

  commit_msg="$(git log -1 --format=%B 2>/dev/null)" || commit_msg=""
  if [[ -z "${commit_msg}" ]]; then
    echo '{}'
    exit 0
  fi

  lines_changed="$(git diff --numstat HEAD~1..HEAD 2>/dev/null \
    | awk '{add+=$1; del+=$2} END {print add+del}')" || lines_changed="0"
  lines_changed="${lines_changed:-0}"

  subject="$(head -1 <<< "${commit_msg}")"
  body="$(tail -n +3 <<< "${commit_msg}")"

  # Check for missing body on non-trivial commits
  file_count="$(git diff --name-only HEAD~1..HEAD 2>/dev/null | wc -l | tr -d ' ')"
  is_trivial=0

  if (( file_count <= 1 && lines_changed < 20 )); then
    is_trivial=1
  fi
  if grep -qiE "(typo|version|bump|import)" <<< "${subject}"; then
    is_trivial=1
  fi

  if (( is_trivial == 0 )) && [[ -z "${body}" ]]; then
    warning_issues="${warning_issues}Non-trivial commits should have a body explaining WHY. Consider: git commit --amend\n"
  fi

  # Commit size warnings
  if (( lines_changed > 1000 )); then
    warning_issues+="VERY LARGE commit (${lines_changed} lines) - strongly consider "
    warning_issues+="splitting. Commits over 1000 lines are difficult to review.\n"
  elif (( lines_changed > 400 )); then
    warning_issues="${warning_issues}Large commit (${lines_changed} lines) - consider splitting into smaller changes\n"
  elif (( lines_changed > 200 )); then
    warning_issues="${warning_issues}Commit is ${lines_changed} lines - review if it could be split\n"
  fi

  # Check for potential breaking changes without marker
  breaking_indicators="$(check_breaking_changes "${subject}" "${commit_msg}")"
  if [[ -n "${breaking_indicators}" ]]; then
    warning_issues+="Potential breaking change detected but no '!' marker or "
    warning_issues+="BREAKING CHANGE footer:\n${breaking_indicators}"
    warning_issues+="If breaking, amend with: feat!: or add BREAKING CHANGE: footer\n"
  fi

  if [[ -n "${warning_issues}" ]]; then
    local escaped_warning
    escaped_warning="$(printf '%s' "${warning_issues}" \
      | sed 's/\\/\\\\/g' | sed 's/"/\\"/g')"
    cat <<EOF
{
  "systemMessage": "Post-commit review:\n${escaped_warning}"
}
EOF
  else
    echo '{}'
  fi

  exit 0
}

main "$@"
