#!/bin/bash
set -euo pipefail
# Stop hook: Phase-aware completion verification
# Only runs during DELEGATE/VERIFY phases of orchestrated workflow
# Worktree-aware: uses correct state directory

# Source worktree utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/worktree-utils.sh"

# Determine state directory based on worktree context
STATE_DIR=$(worktree_state_dir)
WORK_DIR=$(pwd)
PHASE_FILE="${STATE_DIR}/workflow-phase"

# Get current phase
CURRENT_PHASE=""
if [ -f "$PHASE_FILE" ]; then
    CURRENT_PHASE=$(cat "$PHASE_FILE")
fi

echo "=== COMPLETION VERIFICATION ==="
if worktree_is_worktree; then
    echo "Worktree: $(worktree_current)"
fi
echo "Phase: ${CURRENT_PHASE:-none}"

# Only run verification during execution phases
if [ "$CURRENT_PHASE" != "DELEGATE" ] && [ "$CURRENT_PHASE" != "VERIFY" ]; then
    echo "Skipping verification (not in execution phase)"
    exit 0
fi

# In execution phase - run checks
BLOCKED=0
ISSUES=""

# Check todo.md in work directory
if [ -f "${WORK_DIR}/todo.md" ]; then
    PENDING=$(grep -c "PENDING" "${WORK_DIR}/todo.md" 2>/dev/null) || PENDING=0
    if [ "$PENDING" -gt 0 ]; then
        ISSUES="${ISSUES}\n- todo.md has $PENDING incomplete items"
        BLOCKED=1
    fi
fi

# Get configurable commands (with smart defaults based on project type)
if [ -f "${WORK_DIR}/pyproject.toml" ]; then
    DEFAULT_TEST="uv run pytest --tb=short -q"
    DEFAULT_BUILD=""
elif [ -f "${WORK_DIR}/package.json" ]; then
    DEFAULT_TEST="npm test"
    DEFAULT_BUILD="npm run build --if-present"
else
    DEFAULT_TEST=""
    DEFAULT_BUILD=""
fi

TEST_CMD=$(read_plugin_config test_command "$DEFAULT_TEST")
BUILD_CMD=$(read_plugin_config build_command "$DEFAULT_BUILD")

# Run tests
if [ -n "$TEST_CMD" ]; then
    echo "Running tests: $TEST_CMD"
    cd "${WORK_DIR}" && eval "$TEST_CMD" 2>&1 || { ISSUES="${ISSUES}\n- Tests failing"; BLOCKED=1; }
else
    echo "No test command configured, skipping tests"
fi

# Run build if configured
if [ -n "$BUILD_CMD" ]; then
    echo "Running build: $BUILD_CMD"
    cd "${WORK_DIR}" && eval "$BUILD_CMD" 2>&1 || { ISSUES="${ISSUES}\n- Build failing"; BLOCKED=1; }
fi

# Report
if [ "$BLOCKED" -eq 1 ]; then
    echo -e "\n=== BLOCKED ===$ISSUES"
    exit 1
fi

echo "=== PASSED ==="
exit 0
