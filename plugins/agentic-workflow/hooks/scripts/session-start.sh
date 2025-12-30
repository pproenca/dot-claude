#!/bin/bash
# SessionStart hook: Check for incomplete work from previous sessions

# Check for progress.txt
if [ -f "progress.txt" ]; then
    echo "=== PREVIOUS SESSION STATE DETECTED ==="
    cat progress.txt
    echo ""
    echo "Consider resuming from the last completed task."
fi

# Check for todo.md with incomplete items
if [ -f "todo.md" ]; then
    PENDING=$(grep -c "PENDING" todo.md 2>/dev/null || echo "0")
    DONE=$(grep -c "DONE" todo.md 2>/dev/null || echo "0")

    if [ "$PENDING" -gt 0 ]; then
        echo "=== INCOMPLETE TODO ITEMS ==="
        echo "Completed: $DONE | Pending: $PENDING"
        grep "PENDING" todo.md
        echo ""
        echo "Continue with the first PENDING item."
    fi
fi

# Check for artifacts from incomplete work
if [ -d ".claude/artifacts" ]; then
    ARTIFACT_COUNT=$(ls -1 .claude/artifacts/ 2>/dev/null | wc -l | tr -d ' ')
    if [ "$ARTIFACT_COUNT" -gt 0 ]; then
        echo "=== SUBAGENT ARTIFACTS FOUND ==="
        echo "Found $ARTIFACT_COUNT artifact(s) from previous subagents."
        ls -la .claude/artifacts/
    fi
fi

exit 0
