#!/bin/bash
# Stop hook: Strict completion verification
# Exit 0 = allow completion
# Exit 1 = block completion, continue working

BLOCKED=0
ISSUES=""

echo "=== COMPLETION VERIFICATION ==="

# 1. Check todo.md for incomplete items
if [ -f "todo.md" ]; then
    PENDING=$(grep -c "PENDING" todo.md 2>/dev/null) || PENDING=0
    if [ "$PENDING" -gt 0 ] 2>/dev/null; then
        ISSUES="${ISSUES}\n- todo.md has $PENDING incomplete items:"
        PENDING_ITEMS=$(grep "PENDING" todo.md | head -5)
        ISSUES="${ISSUES}\n  ${PENDING_ITEMS}"
        BLOCKED=1
    fi
else
    echo "Note: No todo.md found (ok if not using orchestrated workflow)"
fi

# 2. Run tests
echo "Running tests..."
if command -v uv &> /dev/null && [ -f "pyproject.toml" ]; then
    if ! uv run pytest --tb=short -q 2>&1; then
        ISSUES="${ISSUES}\n- Tests failing"
        BLOCKED=1
    fi
elif [ -f "package.json" ]; then
    if ! npm test 2>&1; then
        ISSUES="${ISSUES}\n- Tests failing"
        BLOCKED=1
    fi
fi

# 3. Type check
echo "Running type check..."
if command -v ty &> /dev/null && [ -f "pyproject.toml" ]; then
    if ! ty check 2>&1 | head -20; then
        TYPE_ERRORS=$(ty check 2>&1 | grep -c "error" || echo "0")
        if [ "$TYPE_ERRORS" -gt 0 ]; then
            ISSUES="${ISSUES}\n- Type errors: $TYPE_ERRORS"
            BLOCKED=1
        fi
    fi
elif [ -f "tsconfig.json" ]; then
    if ! npm run typecheck 2>&1; then
        ISSUES="${ISSUES}\n- TypeScript errors"
        BLOCKED=1
    fi
fi

# 4. Lint check
echo "Running lint..."
if command -v uv &> /dev/null && [ -f "pyproject.toml" ]; then
    LINT_OUTPUT=$(uv run ruff check . 2>&1)
    LINT_ERRORS=$(echo "$LINT_OUTPUT" | grep -c "error\|warning" || echo "0")
    if [ "$LINT_ERRORS" -gt 0 ]; then
        ISSUES="${ISSUES}\n- Lint issues: $LINT_ERRORS"
        echo "$LINT_OUTPUT" | head -10
        BLOCKED=1
    fi
elif [ -f "package.json" ]; then
    if ! npm run lint 2>&1; then
        ISSUES="${ISSUES}\n- Lint errors"
        BLOCKED=1
    fi
fi

# Report results
if [ "$BLOCKED" -eq 1 ]; then
    echo ""
    echo "=== BLOCKED: VERIFICATION FAILED ==="
    echo -e "$ISSUES"
    echo ""
    echo "Continue working until all issues are resolved."
    echo "Do NOT stop until all checks pass."
    exit 1
else
    echo ""
    echo "=== ALL CHECKS PASSED ==="
    echo "Completion allowed."
    exit 0
fi
