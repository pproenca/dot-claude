#!/usr/bin/env bash
# TDD Guard - PreToolUse hook for Write/Edit enforcement
# Blocks production file edits unless test file edited first

set -euo pipefail

output_decision() {
  local decision="$1"
  local reason="$2"
  cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "${decision}",
    "permissionDecisionReason": "${reason}"
  }
}
EOF
}

main() {
  local input
  local file_path

  input="$(cat)"
  file_path="$(echo "${input}" | jq -r '.tool_input.file_path // .tool_input.path // ""')"

  # If no file path found, allow (safety default)
  if [[ -z "${file_path}" ]]; then
    output_decision "allow" "No file path detected"
    exit 0
  fi

  # Skip non-code files (docs, config, scripts, etc.)
  if [[ "${file_path}" =~ \.(md|json|yaml|yml|toml|txt|gitignore|env|lock|log|csv|xml|html|css|scss|less|sh)$ ]]; then
    output_decision "allow" "Non-code file"
    exit 0
  fi

  # Skip dotfiles/hidden files (Unix convention for config/metadata artifacts)
  # Matches any file starting with . (e.g., .dev-docs-*, .sql-history, .metrics)
  if [[ "${file_path}" =~ (^|/)\.[^/]+$ ]]; then
    output_decision "allow" "Dotfile/hidden artifact"
    exit 0
  fi

  # Check if this is a test file
  if [[ "${file_path}" =~ (test|spec|_test\.|\.test\.|tests/|spec/|__tests__/|\.spec\.) ]]; then
    output_decision "allow" "Test file"
    exit 0
  fi

  # Production file - hard block until test is written first
  output_decision "deny" "TDD VIOLATION: Write a failing test BEFORE editing production code. Create the test file first, run it to see it fail, then retry this edit. (super:test-driven-development)"
}

main "$@"
