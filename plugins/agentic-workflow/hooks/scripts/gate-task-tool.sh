#!/bin/bash
# PreToolUse hook: Gate the Task tool during PLAN_WAITING phase
# Blocks subagent spawning until user approval is recorded
#
# Exit 0 = allow tool call
# Exit 1 = block tool call

PHASE_FILE=".claude/workflow-phase"
APPROVAL_FILE=".claude/plan-approved"

# Get current phase
CURRENT_PHASE="IDLE"
if [ -f "$PHASE_FILE" ]; then
    CURRENT_PHASE=$(cat "$PHASE_FILE")
fi

# Only gate during PLAN_WAITING phase
if [ "$CURRENT_PHASE" != "PLAN_WAITING" ]; then
    exit 0
fi

# Check if approval exists
if [ -f "$APPROVAL_FILE" ]; then
    APPROVAL=$(cat "$APPROVAL_FILE")
    if [ "$APPROVAL" = "approved" ]; then
        echo "Plan approved - allowing Task tool"
        exit 0
    fi
fi

# Block the tool call
echo ""
echo "=== BLOCKED: PLAN APPROVAL REQUIRED ==="
echo ""
echo "Current phase: PLAN_WAITING"
echo ""
echo "You MUST get user approval before spawning subagents."
echo ""
echo "Required actions:"
echo "1. Use AskUserQuestion tool to present the plan"
echo "2. Wait for user to approve"
echo "3. After approval, create .claude/plan-approved with content 'approved'"
echo "4. Then you can proceed with Task tool calls"
echo ""
echo "Example approval flow:"
echo "  AskUserQuestion with options:"
echo "    - 'Approve and proceed'"
echo "    - 'Modify plan'"
echo "    - 'Reject'"
echo ""
echo "After user selects 'Approve and proceed':"
echo "  mkdir -p .claude && echo 'approved' > .claude/plan-approved"
echo "  echo 'DELEGATE' > .claude/workflow-phase"
echo ""
exit 1
