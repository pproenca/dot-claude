#!/bin/bash
set -euo pipefail
# Workflow phase management
# Tracks: IDLE → EXPLORE → PLAN_WAITING → DELEGATE → VERIFY → COMPLETE

# Source worktree utilities for state directory awareness
SCRIPT_DIR="$(dirname "$0")"
if [ -f "${SCRIPT_DIR}/worktree-utils.sh" ]; then
    source "${SCRIPT_DIR}/worktree-utils.sh"
    STATE_DIR=$(worktree_state_dir 2>/dev/null || echo ".claude")
else
    STATE_DIR=".claude"
fi

PHASE_FILE="${STATE_DIR}/workflow-phase"
LOCK_FILE="${STATE_DIR}/orchestration.lock"

# Acquire orchestration lock (prevents concurrent orchestration)
acquire_lock() {
    mkdir -p "$(dirname "$LOCK_FILE")"
    if [ -f "$LOCK_FILE" ]; then
        local lock_age
        # macOS uses -f %m, Linux uses -c %Y
        if [[ "$OSTYPE" == "darwin"* ]]; then
            lock_age=$(( $(date +%s) - $(stat -f %m "$LOCK_FILE" 2>/dev/null || echo 0) ))
        else
            lock_age=$(( $(date +%s) - $(stat -c %Y "$LOCK_FILE" 2>/dev/null || echo 0) ))
        fi
        if [ "$lock_age" -gt 3600 ]; then
            echo "Stale lock detected (${lock_age}s old), removing..."
            rm -f "$LOCK_FILE"
        else
            echo "Error: Orchestration already in progress"
            echo "Lock file: $LOCK_FILE (age: ${lock_age}s)"
            echo "Wait for it to complete or remove the lock file manually."
            return 1
        fi
    fi
    echo $$ > "$LOCK_FILE"
    echo "Lock acquired: $LOCK_FILE"
}

# Release orchestration lock
release_lock() {
    if [ -f "$LOCK_FILE" ]; then
        rm -f "$LOCK_FILE"
        echo "Lock released: $LOCK_FILE"
    fi
}

# Check if lock is held
is_locked() {
    [ -f "$LOCK_FILE" ]
}

# Get current phase
get_phase() {
    if [ -f "$PHASE_FILE" ]; then
        cat "$PHASE_FILE"
    else
        echo "IDLE"
    fi
}

# Set phase
set_phase() {
    local phase="$1"
    mkdir -p "$STATE_DIR"
    echo "$phase" > "$PHASE_FILE"
    echo "Workflow phase set to: $phase"
}

# Check if in execution phase (where tests should run)
is_execution_phase() {
    local phase=$(get_phase)
    case "$phase" in
        DELEGATE|VERIFY|COMPLETE)
            return 0  # true - tests should run
            ;;
        *)
            return 1  # false - skip tests
            ;;
    esac
}

# Check if waiting for user approval
is_waiting_approval() {
    local phase=$(get_phase)
    [ "$phase" = "PLAN_WAITING" ]
}

# Usage: workflow-phase.sh [get|set|check|waiting|lock|unlock|locked] [phase]
case "${1:-}" in
    get)
        get_phase
        ;;
    set)
        set_phase "${2:-IDLE}"
        ;;
    check)
        if is_execution_phase; then
            echo "true"
            exit 0
        else
            echo "false"
            exit 1
        fi
        ;;
    waiting)
        if is_waiting_approval; then
            echo "true"
            exit 0
        else
            echo "false"
            exit 1
        fi
        ;;
    lock)
        acquire_lock
        ;;
    unlock)
        release_lock
        ;;
    locked)
        if is_locked; then
            echo "true"
            exit 0
        else
            echo "false"
            exit 1
        fi
        ;;
    *)
        echo "Usage: workflow-phase.sh [get|set|check|waiting|lock|unlock|locked] [phase]"
        echo "Phases: IDLE, EXPLORE, PLAN_WAITING, DELEGATE, VERIFY, COMPLETE"
        echo "Lock commands: lock (acquire), unlock (release), locked (check)"
        exit 1
        ;;
esac
