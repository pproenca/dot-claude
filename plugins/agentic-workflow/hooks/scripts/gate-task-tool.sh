#!/bin/bash
set -euo pipefail
# PreToolUse hook: Gate the Task tool during PLAN_WAITING phase
# Blocks subagent spawning until user approval is recorded
# Worktree-aware: uses correct state directory
#
# Exit 0 = allow tool call
# Exit 1 = block tool call

# Source worktree utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/worktree-utils.sh"

# Determine state directory based on worktree context
STATE_DIR=$(worktree_state_dir)
PHASE_FILE="${STATE_DIR}/workflow-phase"
APPROVAL_FILE="${STATE_DIR}/plan-approved"

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
if worktree_is_worktree; then
    echo "Worktree: $(worktree_current)"
fi
echo "Current phase: PLAN_WAITING"
echo "State dir: ${STATE_DIR}"
echo ""
echo "You MUST get user approval before spawning subagents."
echo ""
echo "Required actions:"
echo "1. Use AskUserQuestion tool to present the plan"
echo "2. Wait for user to approve"
echo "3. After approval, create ${STATE_DIR}/plan-approved with content 'approved'"
echo "4. Then you can proceed with Task tool calls"
echo ""
echo "Example approval flow:"
echo "  AskUserQuestion with options:"
echo "    - 'Approve and proceed'"
echo "    - 'Modify plan'"
echo "    - 'Reject'"
echo ""
echo "After user selects 'Approve and proceed':"
echo "  mkdir -p '${STATE_DIR}' && echo 'approved' > '${STATE_DIR}/plan-approved'"
echo "  echo 'DELEGATE' > '${STATE_DIR}/workflow-phase'"
echo ""
exit 1
