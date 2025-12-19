#!/bin/bash
# Session start hook - detects active workflow or loads getting-started skill
# Queries harness daemon for active workflow state

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../scripts/ensure-harness.sh"

# Check for active harness workflow
if ensure_harness 2>/dev/null; then
  # Query harness for active workflow
  STATE=$(harness get-state 2>/dev/null || echo '{}')
  TASK_COUNT=$(echo "$STATE" | jq '.tasks | length' 2>/dev/null || echo "0")

  if [[ "$TASK_COUNT" -gt 0 ]]; then
    COMPLETED=$(echo "$STATE" | jq '[.tasks[] | select(.status == "completed")] | length' 2>/dev/null || echo "0")
    PENDING=$(echo "$STATE" | jq '[.tasks[] | select(.status == "pending")] | length' 2>/dev/null || echo "0")
    RUNNING=$(echo "$STATE" | jq '[.tasks[] | select(.status == "running")] | length' 2>/dev/null || echo "0")

    # Output harness workflow resume context
    cat << EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<system-context>\\n**ACTIVE WORKFLOW DETECTED**\\n\\nProgress: ${COMPLETED}/${TASK_COUNT} tasks completed\\n- Pending: ${PENDING}\\n- Running: ${RUNNING}\\n\\nCommands:\\n- /dev-workflow:resume - Continue execution\\n- /dev-workflow:abandon - Discard workflow state\\n</system-context>"
  }
}
EOF
    exit 0
  fi
fi

# No active workflow - load getting-started skill
SKILL_FILE="${CLAUDE_PLUGIN_ROOT}/skills/getting-started/SKILL.md"

if [[ -f "$SKILL_FILE" ]]; then
  # Check file size (guard against large files)
  FILESIZE=$(wc -c < "$SKILL_FILE" | tr -d '[:space:]')
  if [[ "$FILESIZE" -gt 1048576 ]]; then
    echo '{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "dev-workflow plugin active."}}'
    exit 0
  fi

  # Read and escape content for JSON (awk for BSD/GNU portability)
  CONTENT=$(sed 's/\\/\\\\/g' "$SKILL_FILE" | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}' | sed 's/\\n$//')

  cat << EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<system-context>\\ndev-workflow skills available.\\n\\n**Getting Started:**\\n\\n${CONTENT}\\n</system-context>"
  }
}
EOF
else
  echo '{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "dev-workflow plugin active. Use EnterPlanMode for planning, /dev-workflow:brainstorm for ideation."}}'
fi

exit 0
