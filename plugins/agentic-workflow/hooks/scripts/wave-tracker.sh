#!/bin/bash
# Wave execution tracking utilities
# Tracks wave-based task scheduling for dependency-aware execution
#
# State file: .claude/wave-state.json (JSON for structured data)
# Format:
# {
#   "current_wave": 1,
#   "total_waves": 3,
#   "waves": {
#     "1": {"status": "complete", "tasks": ["task-a", "task-b"]},
#     "2": {"status": "in_progress", "tasks": ["task-c"]},
#     "3": {"status": "pending", "tasks": ["integration-tests"]}
#   }
# }

# Source worktree utilities if available
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "${SCRIPT_DIR}/worktree-utils.sh" ]; then
    source "${SCRIPT_DIR}/worktree-utils.sh"
    STATE_DIR=$(worktree_state_dir 2>/dev/null || echo ".claude")
else
    STATE_DIR=".claude"
fi

WAVE_FILE="${STATE_DIR}/wave-state.txt"

# Initialize wave tracking
# Usage: wave_init <total_waves>
wave_init() {
    local total_waves="${1:-1}"
    mkdir -p "$STATE_DIR"
    cat > "$WAVE_FILE" << EOF
current_wave=1
total_waves=${total_waves}
wave_1_status=pending
wave_1_tasks=
EOF
    echo "Wave tracking initialized: $total_waves total waves"
}

# Get current wave number
# Usage: wave_current
wave_current() {
    if [ -f "$WAVE_FILE" ]; then
        grep "^current_wave=" "$WAVE_FILE" | cut -d= -f2
    else
        echo "0"
    fi
}

# Get total waves
# Usage: wave_total
wave_total() {
    if [ -f "$WAVE_FILE" ]; then
        grep "^total_waves=" "$WAVE_FILE" | cut -d= -f2
    else
        echo "0"
    fi
}

# Set tasks for a wave
# Usage: wave_set_tasks <wave_num> <task1,task2,task3>
wave_set_tasks() {
    local wave_num="$1"
    local tasks="$2"

    if [ ! -f "$WAVE_FILE" ]; then
        echo "Error: Wave tracking not initialized. Run wave_init first."
        return 1
    fi

    # Update or add wave tasks
    if grep -q "^wave_${wave_num}_tasks=" "$WAVE_FILE"; then
        sed -i.bak "s/^wave_${wave_num}_tasks=.*/wave_${wave_num}_tasks=${tasks}/" "$WAVE_FILE"
        rm -f "${WAVE_FILE}.bak"
    else
        echo "wave_${wave_num}_tasks=${tasks}" >> "$WAVE_FILE"
        echo "wave_${wave_num}_status=pending" >> "$WAVE_FILE"
    fi
    echo "Wave $wave_num tasks set: $tasks"
}

# Start a wave (set status to in_progress)
# Usage: wave_start <wave_num>
wave_start() {
    local wave_num="$1"

    if [ ! -f "$WAVE_FILE" ]; then
        echo "Error: Wave tracking not initialized."
        return 1
    fi

    sed -i.bak "s/^wave_${wave_num}_status=.*/wave_${wave_num}_status=in_progress/" "$WAVE_FILE"
    sed -i.bak "s/^current_wave=.*/current_wave=${wave_num}/" "$WAVE_FILE"
    rm -f "${WAVE_FILE}.bak"
    echo "Wave $wave_num started"
}

# Complete a wave
# Usage: wave_complete <wave_num>
wave_complete() {
    local wave_num="$1"

    if [ ! -f "$WAVE_FILE" ]; then
        echo "Error: Wave tracking not initialized."
        return 1
    fi

    sed -i.bak "s/^wave_${wave_num}_status=.*/wave_${wave_num}_status=complete/" "$WAVE_FILE"
    rm -f "${WAVE_FILE}.bak"
    echo "Wave $wave_num completed"
}

# Get wave status
# Usage: wave_status [wave_num]
wave_status() {
    local wave_num="${1:-}"

    if [ ! -f "$WAVE_FILE" ]; then
        echo "Wave tracking not initialized"
        return 1
    fi

    if [ -n "$wave_num" ]; then
        grep "^wave_${wave_num}_" "$WAVE_FILE"
    else
        echo "=== WAVE STATUS ==="
        local current=$(wave_current)
        local total=$(wave_total)
        echo "Current: Wave $current of $total"
        echo ""
        for i in $(seq 1 "$total"); do
            local status=$(grep "^wave_${i}_status=" "$WAVE_FILE" | cut -d= -f2)
            local tasks=$(grep "^wave_${i}_tasks=" "$WAVE_FILE" | cut -d= -f2)
            echo "Wave $i: $status"
            echo "  Tasks: $tasks"
        done
    fi
}

# Check if all waves are complete
# Usage: wave_all_complete
wave_all_complete() {
    if [ ! -f "$WAVE_FILE" ]; then
        return 1
    fi

    local total=$(wave_total)
    for i in $(seq 1 "$total"); do
        local status=$(grep "^wave_${i}_status=" "$WAVE_FILE" | cut -d= -f2)
        if [ "$status" != "complete" ]; then
            return 1
        fi
    done
    return 0
}

# CLI interface
case "${1:-}" in
    init)
        wave_init "$2"
        ;;
    current)
        wave_current
        ;;
    total)
        wave_total
        ;;
    set-tasks)
        wave_set_tasks "$2" "$3"
        ;;
    start)
        wave_start "$2"
        ;;
    complete)
        wave_complete "$2"
        ;;
    status)
        wave_status "$2"
        ;;
    all-complete)
        if wave_all_complete; then
            echo "true"
            exit 0
        else
            echo "false"
            exit 1
        fi
        ;;
    *)
        # When sourced, functions are available
        # When run directly without args, show usage
        if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
            echo "Usage: wave-tracker.sh <command> [args]"
            echo ""
            echo "Commands:"
            echo "  init <total_waves>     Initialize wave tracking"
            echo "  current                Get current wave number"
            echo "  total                  Get total wave count"
            echo "  set-tasks <n> <tasks>  Set comma-separated tasks for wave n"
            echo "  start <n>              Mark wave n as in_progress"
            echo "  complete <n>           Mark wave n as complete"
            echo "  status [n]             Show wave status (all or specific)"
            echo "  all-complete           Check if all waves complete (exit 0/1)"
        fi
        ;;
esac
