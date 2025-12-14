#!/bin/bash
set -euo pipefail

# PostToolUse hook: Auto-run pytest when test files are modified
# Triggered after Write or Edit operations on Python test files

# Get the file path from the tool input
# The hook receives context via environment variables
FILE_PATH="${TOOL_INPUT_file_path:-}"
TOOL_NAME="${TOOL_NAME:-}"

# Only proceed for Write/Edit operations
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]]; then
    exit 0
fi

# Check if it's a Python file
if [[ ! "$FILE_PATH" =~ \.py$ ]]; then
    exit 0
fi

# Check if it's a test file (test_*.py or *_test.py)
BASENAME=$(basename "$FILE_PATH")
if [[ ! "$BASENAME" =~ ^test_.*\.py$ && ! "$BASENAME" =~ .*_test\.py$ ]]; then
    exit 0
fi

# Verify file exists
if [[ ! -f "$FILE_PATH" ]]; then
    exit 0
fi

# Find project root by looking for pyproject.toml, setup.py, pytest.ini, or setup.cfg
find_project_root() {
    local dir="$1"
    while [[ "$dir" != "/" ]]; do
        if [[ -f "$dir/pyproject.toml" || -f "$dir/setup.py" || \
              -f "$dir/pytest.ini" || -f "$dir/setup.cfg" ]]; then
            echo "$dir"
            return 0
        fi
        dir=$(dirname "$dir")
    done
    return 1
}

# Get directory containing the test file
FILE_DIR=$(dirname "$FILE_PATH")

# Find project root
PROJECT_ROOT=$(find_project_root "$FILE_DIR") || {
    echo "⚠️  Could not find project root for pytest"
    exit 0
}

cd "$PROJECT_ROOT"

# Determine pytest command
get_pytest_cmd() {
    # Prefer uv if pyproject.toml exists and uv is available
    if [[ -f "pyproject.toml" ]] && command -v uv &>/dev/null; then
        echo "uv run pytest"
        return 0
    fi

    # Check for venv pytest
    if [[ -f ".venv/bin/pytest" ]]; then
        echo ".venv/bin/pytest"
        return 0
    fi

    # Check for system pytest
    if command -v pytest &>/dev/null; then
        echo "pytest"
        return 0
    fi

    return 1
}

PYTEST_CMD=$(get_pytest_cmd) || {
    echo "⚠️  pytest not found. Install with: uv add --dev pytest"
    exit 0
}

# Run pytest on the specific test file
echo "🧪 Running tests for: $FILE_PATH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Run pytest with verbose output and short traceback
if $PYTEST_CMD "$FILE_PATH" -v --tb=short; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Tests passed"
else
    EXIT_CODE=$?
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ Tests failed (exit code: $EXIT_CODE)"
fi
