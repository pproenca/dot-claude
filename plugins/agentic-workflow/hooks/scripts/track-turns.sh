#!/bin/bash
# PostToolUse hook: Track turns and prompt re-injection of external state
# Increments turn counter after each tool use during execution phases
# Prompts re-injection every REINJECTION_INTERVAL turns (default: 7)
#
# This hook is informational (always exits 0)

# Source worktree utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -f "${SCRIPT_DIR}/worktree-utils.sh" ]; then
    exit 0
fi
source "${SCRIPT_DIR}/worktree-utils.sh"

# Disable strict mode for hook (we want lenient error handling)
set +euo pipefail

# Determine state directory
STATE_DIR=$(worktree_state_dir 2>/dev/null || echo ".claude")
WORK_DIR=$(pwd)
PHASE_FILE="${STATE_DIR}/workflow-phase"
TURN_FILE="${STATE_DIR}/turn-counter"

# Get current phase
CURRENT_PHASE=""
if [ -f "$PHASE_FILE" ]; then
    CURRENT_PHASE=$(cat "$PHASE_FILE" 2>/dev/null || true)
fi

# Only track during execution phases
if [ "$CURRENT_PHASE" != "DELEGATE" ] && [ "$CURRENT_PHASE" != "VERIFY" ]; then
    exit 0
fi

# Get configurable interval (default: 7 turns)
REINJECTION_INTERVAL=$(read_plugin_config reinjection_interval "7")

# Initialize or read current turn count
CURRENT_TURNS=0
if [ -f "$TURN_FILE" ]; then
    CURRENT_TURNS=$(cat "$TURN_FILE" 2>/dev/null || echo "0")
fi

# Increment turn counter
CURRENT_TURNS=$((CURRENT_TURNS + 1))
echo "$CURRENT_TURNS" > "$TURN_FILE"

# Check if we should prompt re-injection
if [ "$CURRENT_TURNS" -ge "$REINJECTION_INTERVAL" ]; then
    # Reset counter
    echo "0" > "$TURN_FILE"

    echo ""
    echo "=== RE-INJECTION REMINDER (Turn $CURRENT_TURNS) ==="
    echo ""
    echo "It's been $CURRENT_TURNS turns. Re-read external state to prevent context drift:"
    echo ""

    # Show todo.md status if exists
    if [ -f "${WORK_DIR}/todo.md" ]; then
        DONE_COUNT=$(grep -c "DONE\|✓\|\[x\]" "${WORK_DIR}/todo.md" 2>/dev/null || echo "0")
        PENDING_COUNT=$(grep -c "PENDING\|☐\|\[ \]" "${WORK_DIR}/todo.md" 2>/dev/null || echo "0")
        echo "todo.md: $DONE_COUNT done, $PENDING_COUNT pending"
        echo ""
        echo "PENDING items:"
        grep -E "PENDING|☐|\[ \]" "${WORK_DIR}/todo.md" 2>/dev/null | head -5
    fi

    echo ""
    echo "Actions to take:"
    echo "1. Read todo.md - identify next incomplete item"
    echo "2. Read progress.txt - check for blockers"
    echo "3. Explicitly state: 'Continuing with: [next item]'"
    echo ""
    echo "=== END REMINDER ==="
fi

exit 0
