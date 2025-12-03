#!/usr/bin/env bash
# Plan Validator - PostToolUse hook
# Validates that plan files in docs/plans/ have required structure

set -euo pipefail

main() {
  local input tool_name file_path

  input="$(cat)"
  tool_name="$(echo "${input}" | jq -r '.tool_name // ""')"
  file_path="$(echo "${input}" | jq -r '.tool_input.file_path // .tool_input.path // ""')"

  # Only validate Write operations to docs/plans/*.md
  if [[ "$tool_name" != "Write" ]]; then
    exit 0
  fi

  if [[ ! "$file_path" =~ docs/plans/.*\.md$ ]]; then
    exit 0
  fi

  # Check if file exists
  if [[ ! -f "$file_path" ]]; then
    exit 0
  fi

  # Read file content
  local content
  content="$(cat "$file_path")"

  # Track missing sections
  local missing=""

  # Required sections for a good plan file
  # Check for ## Summary or # Summary (level 1 or 2 heading)
  if ! echo "$content" | grep -qE '^#{1,2}\s+Summary'; then
    missing="${missing:+$missing, }Summary"
  fi

  # Check for Implementation section (Tasks, Steps, or Plan)
  if ! echo "$content" | grep -qiE '^#{1,2}\s+(Implementation|Tasks|Steps|Plan)'; then
    missing="${missing:+$missing, }Implementation/Tasks"
  fi

  # Output warning if sections missing
  if [[ -n "$missing" ]]; then
    echo "Plan validation warning: Missing recommended sections: ${missing}"
    echo "Consider adding these sections to improve plan clarity."
  fi
}

main "$@"
