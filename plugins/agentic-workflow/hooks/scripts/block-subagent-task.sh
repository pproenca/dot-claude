#!/bin/bash
# PreToolUse hook: Block Task tool for task-executor subagents
# Prevents task-executor from spawning sub-subagents
#
# Claude Code hook exit codes:
# Exit 0 = allow tool call
# Exit 2 = block tool call (PreToolUse specific)

# Source worktree utilities for consistent patterns
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -f "${SCRIPT_DIR}/worktree-utils.sh" ]; then
    # Utils not found - allow by default (fail open for safety)
    exit 0
fi
source "${SCRIPT_DIR}/worktree-utils.sh"

# Check if we're in a task-executor context
# Task-executors work in worktrees, so if we're in a worktree and
# the agent is trying to use Task tool, block it

if worktree_is_worktree; then
    # We're in a worktree - this is likely a task-executor
    # Block Task tool to prevent sub-subagent spawning
    echo ""
    echo "=== BLOCKED: TASK TOOL NOT ALLOWED ==="
    echo ""
    echo "Task-executor agents cannot spawn sub-subagents."
    echo "Worktree: $(worktree_current)"
    echo ""
    echo "You must complete this task directly without delegation."
    echo "Focus on your task packet objective and success criteria."
    echo ""
    # Exit 2 = block PreToolUse (Claude Code convention)
    exit 2
fi

# Not in a worktree - allow Task tool (this is likely the lead-orchestrator)
exit 0
