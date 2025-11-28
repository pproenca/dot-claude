#!/usr/bin/env bash
# PostToolUse hook for commit-organizer
# Handles post-commit checks that can't be done before execution:
# - Commit size warnings (requires actual commit stats)
# - Non-trivial commit body requirement (requires file count)
# Note: Message format validation is in PreToolUse (blocks before commit)

set -euo pipefail

input="$(cat)"

# Skip validation on WIP/temp branches
current_branch=$(git branch --show-current 2>/dev/null || echo "")
if [[ "$current_branch" =~ ^(wip|temp|backup)/ ]]; then
    echo '{}'
    exit 0
fi

command="$(echo "${input}" | jq -r '.tool_input.command // empty')"

if [[ ! "${command}" =~ ^git[[:space:]]+commit ]]; then
    echo '{}'
    exit 0
fi

commit_msg="$(git log -1 --format=%B 2>/dev/null || echo "")"
if [[ -z "${commit_msg}" ]]; then
    echo '{}'
    exit 0
fi

lines_changed="$(git diff --numstat HEAD~1..HEAD 2>/dev/null | awk '{add+=$1; del+=$2} END {print add+del}' || echo "0")"
lines_changed="${lines_changed:-0}"

subject="$(echo "${commit_msg}" | head -1)"
body="$(echo "${commit_msg}" | tail -n +3)"

warning_issues=""

# Check for missing body on non-trivial commits
file_count="$(git diff --name-only HEAD~1..HEAD 2>/dev/null | wc -l | tr -d ' ')"
is_trivial=false

if (( file_count <= 1 && lines_changed < 20 )); then
    is_trivial=true
fi
if echo "${subject}" | grep -qiE "(typo|version|bump|import)"; then
    is_trivial=true
fi

if [[ "${is_trivial}" == "false" && -z "${body}" ]]; then
    warning_issues="${warning_issues}Non-trivial commits should have a body explaining WHY. Consider: git commit --amend\n"
fi

# Commit size warnings
if (( lines_changed > 400 )); then
    warning_issues="${warning_issues}Large commit (${lines_changed} lines) - consider splitting into smaller changes\n"
elif (( lines_changed > 200 )); then
    warning_issues="${warning_issues}Commit is ${lines_changed} lines - review if it could be split\n"
fi

if [[ -n "${warning_issues}" ]]; then
    escaped_warning="$(printf '%s' "${warning_issues}" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g')"
    cat <<EOF
{
  "systemMessage": "Post-commit review:\n${escaped_warning}"
}
EOF
else
    echo '{}'
fi

exit 0
