#!/usr/bin/env bash
# Shell Script Validation - PreToolUse hook
# Validates shell scripts before they're written, warns on issues

set -euo pipefail

main() {
  local input
  local file_path
  local content
  local temp_file
  local error
  local sc_output
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
  echo "${content}" >"${temp_file}"

  # Check for shebang
  if ! head -1 "${temp_file}" | grep -q '^#!'; then
    warnings+=("Missing shebang (add #!/bin/bash or #!/bin/sh)")
  fi

  # Syntax check with bash -n
  if ! bash -n "${temp_file}" 2>/dev/null; then
    error="$(bash -n "${temp_file}" 2>&1 || true)"
    warnings+=("Syntax error: ${error}")
  fi

  # Run shellcheck if available (non-blocking)
  if command -v shellcheck &> /dev/null; then
    sc_output="$(shellcheck -f gcc "${temp_file}" 2>&1 || true)"
    if [[ -n "${sc_output}" ]]; then
      warnings+=("shellcheck: ${sc_output}")
    fi
  fi

  # Output warnings if any
  if [[ ${#warnings[@]} -gt 0 ]]; then
    printf "Shell script warnings for %s:\n" "${file_path}"
    for w in "${warnings[@]}"; do
      printf "  - %s\n" "${w}"
    done
  fi

  exit 0
}

main "$@"
