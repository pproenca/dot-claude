#!/bin/bash
# Stop hook: Phase-aware completion verification
# Only runs during DELEGATE/VERIFY phases of orchestrated workflow

PHASE_FILE=".claude/workflow-phase"

# Get current phase
CURRENT_PHASE=""
if [ -f "$PHASE_FILE" ]; then
    CURRENT_PHASE=$(cat "$PHASE_FILE")
fi

echo "=== COMPLETION VERIFICATION ==="
echo "Phase: ${CURRENT_PHASE:-none}"

# Only run verification during execution phases
if [ "$CURRENT_PHASE" != "DELEGATE" ] && [ "$CURRENT_PHASE" != "VERIFY" ]; then
    echo "Skipping verification (not in execution phase)"
    exit 0
fi

# In execution phase - run checks
BLOCKED=0
ISSUES=""

# Check todo.md
if [ -f "todo.md" ]; then
    PENDING=$(grep -c "PENDING" todo.md 2>/dev/null) || PENDING=0
    if [ "$PENDING" -gt 0 ]; then
        ISSUES="${ISSUES}\n- todo.md has $PENDING incomplete items"
        BLOCKED=1
    fi
fi

# Run tests (let them fail naturally if not configured)
echo "Running tests..."
if [ -f "pyproject.toml" ]; then
    uv run pytest --tb=short -q 2>&1 || { ISSUES="${ISSUES}\n- Tests failing"; BLOCKED=1; }
elif [ -f "package.json" ]; then
    npm test 2>&1 || { ISSUES="${ISSUES}\n- Tests failing"; BLOCKED=1; }
fi

# Report
if [ "$BLOCKED" -eq 1 ]; then
    echo -e "\n=== BLOCKED ===$ISSUES"
    exit 1
fi

echo "=== PASSED ==="
exit 0
