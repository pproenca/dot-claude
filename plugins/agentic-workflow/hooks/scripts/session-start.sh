#!/bin/bash
# SessionStart hook: Check for incomplete work from previous sessions
# Worktree-aware: detects if running in a worktree and shows context
#
# Claude Code hook exit codes:
# Exit 0 = success (always for SessionStart)

# Source worktree utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -f "${SCRIPT_DIR}/worktree-utils.sh" ]; then
    # Utils not found - exit silently
    exit 0
fi
source "${SCRIPT_DIR}/worktree-utils.sh"

# Determine state directory based on worktree context
STATE_DIR=$(worktree_state_dir 2>/dev/null || echo ".claude")
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

# Show wave status if tracking active
if [ -f "${STATE_DIR}/wave-state.txt" ]; then
    echo "=== WAVE STATUS ==="
    CURRENT_WAVE=$(grep "^current_wave=" "${STATE_DIR}/wave-state.txt" | cut -d= -f2)
    TOTAL_WAVES=$(grep "^total_waves=" "${STATE_DIR}/wave-state.txt" | cut -d= -f2)
    echo "Current: Wave $CURRENT_WAVE of $TOTAL_WAVES"

    # Show status of each wave
    for i in $(seq 1 "$TOTAL_WAVES"); do
        STATUS=$(grep "^wave_${i}_status=" "${STATE_DIR}/wave-state.txt" 2>/dev/null | cut -d= -f2)
        TASKS=$(grep "^wave_${i}_tasks=" "${STATE_DIR}/wave-state.txt" 2>/dev/null | cut -d= -f2)
        echo "  Wave $i: ${STATUS:-pending} - ${TASKS:-no tasks}"
    done
    echo ""
fi

# Show background tasks if any are running
if [ -f "${STATE_DIR}/background-tasks.txt" ] && [ -s "${STATE_DIR}/background-tasks.txt" ]; then
    RUNNING_COUNT=$(grep -c "|running|" "${STATE_DIR}/background-tasks.txt" 2>/dev/null || echo "0")
    if [ "$RUNNING_COUNT" -gt 0 ]; then
        echo "=== BACKGROUND TASKS RUNNING ==="
        echo "$RUNNING_COUNT task(s) running. Collect results with TaskOutput:"
        echo ""
        grep "|running|" "${STATE_DIR}/background-tasks.txt" | while IFS='|' read -r id desc status started; do
            echo "  TaskOutput(task_id: \"$id\", block: true)"
            echo "    Description: $desc"
        done
        echo ""
    fi
fi

# Show turn counter if active
if [ -f "${STATE_DIR}/turn-counter" ]; then
    TURNS=$(cat "${STATE_DIR}/turn-counter")
    if [ "$TURNS" -gt 0 ]; then
        echo "=== TURN COUNTER ==="
        echo "Turns since last re-injection: $TURNS"
        echo ""
    fi
fi

exit 0
