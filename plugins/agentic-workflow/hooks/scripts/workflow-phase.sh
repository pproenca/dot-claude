#!/bin/bash
# Workflow phase management
# Tracks: IDLE → EXPLORE → PLAN_WAITING → DELEGATE → VERIFY → COMPLETE

PHASE_FILE=".claude/workflow-phase"

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
    mkdir -p .claude
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

# Usage: workflow-phase.sh [get|set|check|waiting] [phase]
case "$1" in
    get)
        get_phase
        ;;
    set)
        set_phase "$2"
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
    *)
        echo "Usage: workflow-phase.sh [get|set|check|waiting] [phase]"
        echo "Phases: IDLE, EXPLORE, PLAN_WAITING, DELEGATE, VERIFY, COMPLETE"
        exit 1
        ;;
esac
