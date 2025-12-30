#!/bin/bash
# SessionStart hook: Check for incomplete work from previous sessions
# Worktree-aware: detects if running in a worktree and shows context

# Source worktree utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/worktree-utils.sh"

# Determine state directory based on worktree context
STATE_DIR=$(worktree_state_dir)
WORK_DIR=$(pwd)

# Show worktree context if in a worktree
if worktree_is_worktree; then
    echo "=== WORKTREE CONTEXT ==="
    echo "Worktree: $(worktree_current)"
    echo "Branch: $(worktree_current_branch)"
    echo "Main repo: $(worktree_main_repo)"
    echo ""
fi

# Check for progress.txt
if [ -f "${WORK_DIR}/progress.txt" ]; then
    echo "=== PREVIOUS SESSION STATE DETECTED ==="
    cat "${WORK_DIR}/progress.txt"
    echo ""
    echo "Consider resuming from the last completed task."
fi

# Check for todo.md with incomplete items
if [ -f "${WORK_DIR}/todo.md" ]; then
    PENDING=$(grep -c "PENDING" "${WORK_DIR}/todo.md" 2>/dev/null || echo "0")
    DONE=$(grep -c "DONE" "${WORK_DIR}/todo.md" 2>/dev/null || echo "0")

    if [ "$PENDING" -gt 0 ]; then
        echo "=== INCOMPLETE TODO ITEMS ==="
        echo "Completed: $DONE | Pending: $PENDING"
        grep "PENDING" "${WORK_DIR}/todo.md"
        echo ""
        echo "Continue with the first PENDING item."
    fi
fi

# Check for artifacts from incomplete work
if [ -d "${STATE_DIR}/artifacts" ]; then
    ARTIFACT_COUNT=$(ls -1 "${STATE_DIR}/artifacts/" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$ARTIFACT_COUNT" -gt 0 ]; then
        echo "=== SUBAGENT ARTIFACTS FOUND ==="
        echo "Found $ARTIFACT_COUNT artifact(s) from previous subagents."
        ls -la "${STATE_DIR}/artifacts/"
    fi
fi

# Show workflow phase if active
if [ -f "${STATE_DIR}/workflow-phase" ]; then
    PHASE=$(cat "${STATE_DIR}/workflow-phase")
    echo "=== WORKFLOW PHASE ==="
    echo "Current: $PHASE"
    if [ -f "${STATE_DIR}/plan-approved" ]; then
        echo "Plan: approved"
    fi
    echo ""
fi

exit 0
