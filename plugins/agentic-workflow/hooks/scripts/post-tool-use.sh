#!/bin/bash
set -euo pipefail
# PostToolUse hook: Auto-run checks after Write/Edit on code files

# Source worktree utilities for config reading
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/worktree-utils.sh"

TOOL_INPUT_FILE="${1:-}"

# Extract the file path from tool input if available
FILE_PATH=""
if [ -f "$TOOL_INPUT_FILE" ]; then
    FILE_PATH=$(grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' "$TOOL_INPUT_FILE" | head -1 | cut -d'"' -f4)
fi

# Determine file type and get configurable commands
case "$FILE_PATH" in
    *.py)
        # Python: default to ruff + ty
        DEFAULT_LINT="uv run ruff check --fix"
        DEFAULT_TYPECHECK="ty check"
        LINT_CMD=$(read_plugin_config lint_command "$DEFAULT_LINT")
        TYPECHECK_CMD=$(read_plugin_config typecheck_command "$DEFAULT_TYPECHECK")

        echo "=== AUTO-CHECK: $FILE_PATH ==="

        if [ -n "$LINT_CMD" ]; then
            echo "Running lint: $LINT_CMD $FILE_PATH"
            eval "$LINT_CMD" "$FILE_PATH" 2>&1 | head -20 || true
        fi

        if [ -n "$TYPECHECK_CMD" ]; then
            echo "Running typecheck: $TYPECHECK_CMD $FILE_PATH"
            eval "$TYPECHECK_CMD" "$FILE_PATH" 2>&1 | head -20 || true
        fi

        echo "=== AUTO-CHECK COMPLETE ==="
        ;;
    *.ts|*.tsx|*.js|*.jsx)
        # TypeScript/JavaScript: default to eslint if configured
        LINT_CMD=$(read_plugin_config js_lint_command "")
        TYPECHECK_CMD=$(read_plugin_config js_typecheck_command "")

        if [ -n "$LINT_CMD" ] || [ -n "$TYPECHECK_CMD" ]; then
            echo "=== AUTO-CHECK: $FILE_PATH ==="

            if [ -n "$LINT_CMD" ]; then
                echo "Running lint: $LINT_CMD $FILE_PATH"
                eval "$LINT_CMD" "$FILE_PATH" 2>&1 | head -20 || true
            fi

            if [ -n "$TYPECHECK_CMD" ]; then
                echo "Running typecheck: $TYPECHECK_CMD"
                eval "$TYPECHECK_CMD" 2>&1 | head -20 || true
            fi

            echo "=== AUTO-CHECK COMPLETE ==="
        fi
        ;;
esac

# Always exit 0 - this is informational, not blocking
exit 0
