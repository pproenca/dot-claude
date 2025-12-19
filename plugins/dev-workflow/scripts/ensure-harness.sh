#!/usr/bin/env bash
# ensure-harness.sh - Ensure harness daemon is running
# Returns 0 if daemon is running, 1 if failed to start

set -euo pipefail

HARNESS_TIMEOUT="${HARNESS_TIMEOUT:-5}"

# Installation instructions for harness
show_install_instructions() {
  cat >&2 << 'EOF'
ERROR: harness CLI not found

Install harness using one of these methods:

  # Quick install (recommended):
  curl -fsSL https://raw.githubusercontent.com/pproenca/harness/master/install.sh | bash

  # Or with uv directly:
  uv tool install git+https://github.com/pproenca/harness

  # Install specific version:
  uv tool install git+https://github.com/pproenca/harness@v2.0.0

After installation, ensure ~/.local/bin is in your PATH:
  export PATH="$HOME/.local/bin:$PATH"

EOF
}

ensure_harness() {
  # Check if harness CLI is installed
  if ! command -v harness >/dev/null 2>&1; then
    show_install_instructions
    return 1
  fi

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
