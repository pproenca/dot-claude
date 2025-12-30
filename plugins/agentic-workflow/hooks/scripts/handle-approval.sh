#!/bin/bash
# PostToolUse hook for AskUserQuestion: Detect plan approval
# Automatically sets approval file when user approves the plan

TOOL_INPUT_FILE="$1"
TOOL_OUTPUT_FILE="$2"

PHASE_FILE=".claude/workflow-phase"
APPROVAL_FILE=".claude/plan-approved"

# Get current phase
CURRENT_PHASE="IDLE"
if [ -f "$PHASE_FILE" ]; then
    CURRENT_PHASE=$(cat "$PHASE_FILE")
fi

# Only handle during PLAN_WAITING phase
if [ "$CURRENT_PHASE" != "PLAN_WAITING" ]; then
    exit 0
fi

# Check if user approved (look for approval-related answers in output)
if [ -f "$TOOL_OUTPUT_FILE" ]; then
    OUTPUT=$(cat "$TOOL_OUTPUT_FILE")

    # Check for approval patterns (case-insensitive)
    if echo "$OUTPUT" | grep -iq "approve\|proceed\|yes\|accept\|go ahead\|looks good\|lgtm"; then
        # Check it's not a rejection
        if ! echo "$OUTPUT" | grep -iq "reject\|cancel\|no\|stop\|don't\|modify"; then
            echo "=== PLAN APPROVED ==="
            mkdir -p .claude
            echo "approved" > "$APPROVAL_FILE"
            echo "DELEGATE" > "$PHASE_FILE"
            echo "Approval recorded. Task tool now unblocked."
            echo "Phase transitioned to: DELEGATE"
            exit 0
        fi
    fi

    # Check for rejection
    if echo "$OUTPUT" | grep -iq "reject\|cancel\|start over"; then
        echo "=== PLAN REJECTED ==="
        echo "EXPLORE" > "$PHASE_FILE"
        rm -f "$APPROVAL_FILE"
        echo "Returning to EXPLORE phase for re-planning."
        exit 0
    fi

    # Check for modification request
    if echo "$OUTPUT" | grep -iq "modify\|change\|adjust\|update"; then
        echo "=== PLAN MODIFICATION REQUESTED ==="
        echo "Please update the plan and ask for approval again."
        exit 0
    fi
fi

# No clear approval detected
echo "Note: User response received during PLAN_WAITING phase."
echo "If this was plan approval, ensure clear approval language was used."
exit 0
