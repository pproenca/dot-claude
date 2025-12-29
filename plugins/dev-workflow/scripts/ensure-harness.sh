#!/usr/bin/env bash
# ensure-harness.sh - Ensure hyh daemon is running
# Returns 0 if daemon is running, 1 if failed to start
# Note: harness was renamed to hyh, accessed via 'uvx hyh'

set -euo pipefail

HARNESS_TIMEOUT="${HARNESS_TIMEOUT:-5}"

# Run hyh command via uvx
run_hyh() {
  uvx hyh "$@"
}

# Installation instructions for hyh
show_install_instructions() {
  cat >&2 << 'EOF'
ERROR: uv/uvx not found (required for hyh)

Install uv first:
  curl -LsSf https://astral.sh/uv/install.sh | sh

Then hyh will be available via:
  uvx hyh <command>

Or install it permanently:
  uv tool install hyh

EOF
}

ensure_harness() {
  # Check if uvx is available
  if ! command -v uvx >/dev/null 2>&1; then
    show_install_instructions
    return 1
  fi

  # Check if daemon responds to ping
  if run_hyh ping >/dev/null 2>&1; then
    return 0
  fi

  # Daemon not running, spawn it (hyh client auto-spawns daemon)
  run_hyh get-state >/dev/null 2>&1 || true

  # Wait for daemon to be ready
  local elapsed=0
  while ! run_hyh ping >/dev/null 2>&1; do
    sleep 0.5
    elapsed=$((elapsed + 1))
    if [[ $elapsed -ge $((HARNESS_TIMEOUT * 2)) ]]; then
      echo "ERROR: hyh daemon failed to start within ${HARNESS_TIMEOUT}s" >&2
      return 1
    fi
  done

  return 0
}

# Allow sourcing without execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  ensure_harness "$@"
fi
