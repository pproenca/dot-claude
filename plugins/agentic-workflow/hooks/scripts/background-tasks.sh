#!/bin/bash
# Background task registry utilities
# Tracks background Task tool invocations for TaskOutput collection
# Persists task IDs across context compaction
#
# State file: .claude/background-tasks.txt
# Format: task_id|description|status|started_at
#
# Example:
# abc123|Task A: Token service|running|2024-01-15T10:30:00
# def456|Task B: Session service|completed|2024-01-15T10:30:00

# Source worktree utilities if available
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "${SCRIPT_DIR}/worktree-utils.sh" ]; then
    source "${SCRIPT_DIR}/worktree-utils.sh"
    STATE_DIR=$(worktree_state_dir 2>/dev/null || echo ".claude")
else
    STATE_DIR=".claude"
fi

TASKS_FILE="${STATE_DIR}/background-tasks.txt"

# Initialize background task registry
# Usage: bg_init
bg_init() {
    mkdir -p "$STATE_DIR"
    : > "$TASKS_FILE"  # Create or truncate
    echo "Background task registry initialized"
}

# Register a new background task
# Usage: bg_register <task_id> <description>
bg_register() {
    local task_id="$1"
    local description="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S")

    mkdir -p "$STATE_DIR"

    # Check if task already exists
    if [ -f "$TASKS_FILE" ] && grep -q "^${task_id}|" "$TASKS_FILE"; then
        echo "Task $task_id already registered"
        return 1
    fi

    echo "${task_id}|${description}|running|${timestamp}" >> "$TASKS_FILE"
    echo "Registered: $task_id - $description"
}

# Mark a task as completed
# Usage: bg_complete <task_id>
bg_complete() {
    local task_id="$1"

    if [ ! -f "$TASKS_FILE" ]; then
        echo "No tasks registered"
        return 1
    fi

    if ! grep -q "^${task_id}|" "$TASKS_FILE"; then
        echo "Task $task_id not found"
        return 1
    fi

    # Update status to completed
    sed -i.bak "s/^${task_id}|\(.*\)|running|\(.*\)$/${task_id}|\1|completed|\2/" "$TASKS_FILE"
    rm -f "${TASKS_FILE}.bak"
    echo "Completed: $task_id"
}

# Mark a task as failed
# Usage: bg_fail <task_id>
bg_fail() {
    local task_id="$1"

    if [ ! -f "$TASKS_FILE" ]; then
        echo "No tasks registered"
        return 1
    fi

    sed -i.bak "s/^${task_id}|\(.*\)|running|\(.*\)$/${task_id}|\1|failed|\2/" "$TASKS_FILE"
    rm -f "${TASKS_FILE}.bak"
    echo "Failed: $task_id"
}

# Get task info
# Usage: bg_get <task_id>
bg_get() {
    local task_id="$1"

    if [ ! -f "$TASKS_FILE" ]; then
        return 1
    fi

    grep "^${task_id}|" "$TASKS_FILE"
}

# List all tasks
# Usage: bg_list [status]
bg_list() {
    local filter_status="${1:-}"

    if [ ! -f "$TASKS_FILE" ] || [ ! -s "$TASKS_FILE" ]; then
        echo "No background tasks registered"
        return 0
    fi

    echo "=== BACKGROUND TASKS ==="

    if [ -n "$filter_status" ]; then
        echo "Filter: $filter_status"
        echo ""
        grep "|${filter_status}|" "$TASKS_FILE" | while IFS='|' read -r id desc status started; do
            echo "[$status] $id"
            echo "  Description: $desc"
            echo "  Started: $started"
            echo ""
        done
    else
        while IFS='|' read -r id desc status started; do
            echo "[$status] $id"
            echo "  Description: $desc"
            echo "  Started: $started"
            echo ""
        done < "$TASKS_FILE"
    fi
}

# List running tasks (for TaskOutput collection)
# Usage: bg_running
bg_running() {
    if [ ! -f "$TASKS_FILE" ]; then
        return 0
    fi

    echo "=== RUNNING BACKGROUND TASKS ==="
    echo "Use TaskOutput(task_id, block: true) to collect results:"
    echo ""

    local count=0
    grep "|running|" "$TASKS_FILE" | while IFS='|' read -r id desc status started; do
        echo "TaskOutput(task_id: \"$id\", block: true)  # $desc"
        count=$((count + 1))
    done

    if [ "$count" -eq 0 ]; then
        echo "No running tasks"
    fi
}

# Clean up completed/failed tasks
# Usage: bg_cleanup [--all]
bg_cleanup() {
    local clean_all="${1:-}"

    if [ ! -f "$TASKS_FILE" ]; then
        echo "No tasks to clean"
        return 0
    fi

    if [ "$clean_all" = "--all" ]; then
        : > "$TASKS_FILE"
        echo "All tasks cleared"
    else
        # Keep only running tasks
        grep "|running|" "$TASKS_FILE" > "${TASKS_FILE}.tmp" 2>/dev/null || : > "${TASKS_FILE}.tmp"
        mv "${TASKS_FILE}.tmp" "$TASKS_FILE"
        echo "Completed/failed tasks cleaned up"
    fi
}

# Count tasks by status
# Usage: bg_count [status]
bg_count() {
    local filter_status="${1:-}"

    if [ ! -f "$TASKS_FILE" ]; then
        echo "0"
        return
    fi

    if [ -n "$filter_status" ]; then
        grep -c "|${filter_status}|" "$TASKS_FILE" 2>/dev/null || echo "0"
    else
        wc -l < "$TASKS_FILE" | tr -d ' '
    fi
}

# CLI interface
case "${1:-}" in
    init)
        bg_init
        ;;
    register)
        bg_register "$2" "$3"
        ;;
    complete)
        bg_complete "$2"
        ;;
    fail)
        bg_fail "$2"
        ;;
    get)
        bg_get "$2"
        ;;
    list)
        bg_list "$2"
        ;;
    running)
        bg_running
        ;;
    cleanup)
        bg_cleanup "$2"
        ;;
    count)
        bg_count "$2"
        ;;
    *)
        # When sourced, functions are available
        if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
            echo "Usage: background-tasks.sh <command> [args]"
            echo ""
            echo "Commands:"
            echo "  init                    Initialize task registry"
            echo "  register <id> <desc>    Register a new background task"
            echo "  complete <id>           Mark task as completed"
            echo "  fail <id>               Mark task as failed"
            echo "  get <id>                Get task info"
            echo "  list [status]           List all tasks (optionally filter by status)"
            echo "  running                 List running tasks with TaskOutput commands"
            echo "  cleanup [--all]         Remove completed/failed tasks"
            echo "  count [status]          Count tasks"
        fi
        ;;
esac
