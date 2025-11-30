#!/usr/bin/env bash
# Shell Script Validation - PreToolUse hook
# Validates shell scripts before they're written
# Blocks on syntax errors, warns on style issues

set -euo pipefail

main() {
  local input
  local file_path
  local content
  local temp_file
  local syntax_error=""
  local sc_output=""
  local warnings=()

  input="$(cat)"
  file_path="$(jq -r '.tool_input.file_path // .tool_input.path // ""' \
    <<< "${input}")"
  content="$(jq -r '.tool_input.content // ""' <<< "${input}")"

  # Skip non-shell files
  if [[ ! "${file_path}" =~ \.sh$ ]]; then
    exit 0
  fi

  # Write content to temp file for validation
  temp_file="$(mktemp)"
  trap 'rm -f "${temp_file}"' EXIT
  printf '%s' "${content}" >"${temp_file}"

  # Check for shebang
  if ! head -1 "${temp_file}" | grep -q '^#!'; then
    warnings+=("Missing shebang (add #!/bin/bash or #!/bin/sh)")
  fi

  # Syntax check with bash -n - this is blocking
  if ! bash -n "${temp_file}" 2>/dev/null; then
    syntax_error="$(bash -n "${temp_file}" 2>&1 || true)"
  fi

  # Run shellcheck if available (non-blocking, just warnings)
  if command -v shellcheck &>/dev/null; then
    sc_output="$(shellcheck -f gcc "${temp_file}" 2>&1 || true)"
    if [[ -n "${sc_output}" ]]; then
      warnings+=("shellcheck: ${sc_output}")
    fi
  fi

  # Block on syntax errors
  if [[ -n "${syntax_error}" ]]; then
    cat <<EOF
{
  "decision": "block",
  "reason": "Shell script has syntax error: ${syntax_error//\"/\\\"}. Fix the syntax before writing."
}
EOF
    exit 0
  fi

  # Output warnings if any (non-blocking)
  if [[ ${#warnings[@]} -gt 0 ]]; then
    printf "Shell script warnings for %s:\n" "${file_path}"
    for w in "${warnings[@]}"; do
      printf "  - %s\n" "${w}"
    done
  fi

  exit 0
}

main "$@"
