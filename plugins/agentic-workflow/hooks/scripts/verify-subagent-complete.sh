#!/bin/bash
# SubagentStop hook: Verify subagent completion criteria before allowing stop
# Checks that subagent has written required artifact and completed key tasks
#
# Claude Code hook exit codes for SubagentStop hooks:
# Exit 0 = allow subagent to stop
# Exit non-zero = block stop, subagent continues

# Source worktree utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -f "${SCRIPT_DIR}/worktree-utils.sh" ]; then
    # Utils not found - allow stop
    exit 0
fi
source "${SCRIPT_DIR}/worktree-utils.sh"

# Determine state directory based on worktree context
STATE_DIR=$(worktree_state_dir 2>/dev/null || echo ".claude")
WORK_DIR=$(pwd)
ARTIFACTS_DIR="${STATE_DIR}/artifacts"

echo "=== SUBAGENT COMPLETION CHECK ==="
if worktree_is_worktree; then
    echo "Worktree: $(worktree_current)"
fi

BLOCKED=0
ISSUES=""

# Check 1: Artifact directory exists and has files
if [ ! -d "$ARTIFACTS_DIR" ]; then
    ISSUES="${ISSUES}\n- No artifacts directory found at ${ARTIFACTS_DIR}"
    BLOCKED=1
elif [ -z "$(ls -A "$ARTIFACTS_DIR" 2>/dev/null)" ]; then
    ISSUES="${ISSUES}\n- Artifacts directory is empty - write your artifact summary"
    BLOCKED=1
else
    ARTIFACT_COUNT=$(ls -1 "$ARTIFACTS_DIR" | wc -l | tr -d ' ')
    echo "Found $ARTIFACT_COUNT artifact(s) in $ARTIFACTS_DIR"
fi

# Check 2: Look for recent artifact (modified in last 5 minutes)
# This helps ensure the subagent actually wrote something this session
if [ -d "$ARTIFACTS_DIR" ] && [ -n "$(ls -A "$ARTIFACTS_DIR" 2>/dev/null)" ]; then
    RECENT_ARTIFACTS=$(find "$ARTIFACTS_DIR" -type f -mmin -5 2>/dev/null | wc -l | tr -d ' ')
    if [ "$RECENT_ARTIFACTS" -eq 0 ]; then
        echo "Warning: No recently modified artifacts (last 5 min)"
        # Don't block, just warn - artifact might have been written earlier
    fi
fi

# Check 3: If in a worktree, check for uncommitted changes
# Subagents should commit their work before stopping
if worktree_is_worktree; then
    UNCOMMITTED=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    if [ "$UNCOMMITTED" -gt 0 ]; then
        ISSUES="${ISSUES}\n- Uncommitted changes detected ($UNCOMMITTED files) - commit your work first"
        BLOCKED=1
    fi
fi

# Check 4: Quick test check (if test command is configured and tests exist)
# Only run if strict mode is enabled to avoid slowing down every subagent stop
STRICT_MODE=$(read_plugin_config strict_subagent_stop "false")
if [ "$STRICT_MODE" = "true" ]; then
    # Detect test framework and run quick check
    if [ -f "${WORK_DIR}/pyproject.toml" ]; then
        TEST_CMD="uv run pytest --tb=line -q --co -q 2>/dev/null | head -5"
    elif [ -f "${WORK_DIR}/package.json" ]; then
        TEST_CMD="npm test -- --listTests 2>/dev/null | head -5"
    else
        TEST_CMD=""
    fi

    if [ -n "$TEST_CMD" ]; then
        echo "Running quick test check..."
        # Just verify tests can be collected, don't run them fully
        if ! eval "$TEST_CMD" >/dev/null 2>&1; then
            echo "Warning: Test collection failed - tests may have issues"
            # Don't block, just warn
        fi
    fi
fi

# Report
if [ "$BLOCKED" -eq 1 ]; then
    echo -e "\n=== BLOCKED ===$ISSUES"
    echo ""
    echo "Before stopping, ensure you have:"
    echo "1. Written an artifact to ${ARTIFACTS_DIR}/"
    echo "2. Committed all changes (if in worktree)"
    echo "3. Met the success criteria from your task packet"
    exit 1
fi

echo "=== PASSED ==="
exit 0
