#!/bin/bash
# PostToolUse hook: Auto-run checks after Write/Edit on Python files

TOOL_INPUT_FILE="$1"

# Extract the file path from tool input if available
# This is a simplified version - actual implementation may need to parse JSON
FILE_PATH=""
if [ -f "$TOOL_INPUT_FILE" ]; then
    FILE_PATH=$(grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' "$TOOL_INPUT_FILE" | head -1 | cut -d'"' -f4)
fi

# Only run checks on Python files
if [[ "$FILE_PATH" == *.py ]]; then
    echo "=== AUTO-CHECK: $FILE_PATH ==="

    # Run ruff check (fast linter)
    if command -v uv &> /dev/null; then
        echo "Running ruff check..."
        uv run ruff check "$FILE_PATH" --fix 2>&1 | head -20
    fi

    # Run type checker
    if command -v ty &> /dev/null; then
        echo "Running type check..."
        ty check "$FILE_PATH" 2>&1 | head -20
    fi

    echo "=== AUTO-CHECK COMPLETE ==="
fi

# Always exit 0 - this is informational, not blocking
exit 0
