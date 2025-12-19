#!/usr/bin/env bash
# ensure-harness.sh - Ensure harness daemon is running
# Returns 0 if daemon is running, 1 if failed to start

set -euo pipefail

HARNESS_TIMEOUT="${HARNESS_TIMEOUT:-5}"

ensure_harness() {
  # Check if daemon responds to ping
  if harness ping >/dev/null 2>&1; then
    return 0
  fi

  # Daemon not running, spawn it (harness client auto-spawns daemon)
  harness get-state >/dev/null 2>&1 || true

  # Wait for daemon to be ready
  local elapsed=0
  while ! harness ping >/dev/null 2>&1; do
    sleep 0.5
    elapsed=$((elapsed + 1))
    if [[ $elapsed -ge $((HARNESS_TIMEOUT * 2)) ]]; then
      echo "ERROR: harness daemon failed to start within ${HARNESS_TIMEOUT}s" >&2
      return 1
    fi
  done

  return 0
}

# Allow sourcing without execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  ensure_harness "$@"
fi
