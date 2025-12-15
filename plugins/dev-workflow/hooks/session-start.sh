#!/bin/bash
# Session start hook - detects active workflow or loads getting-started skill
# No external dependencies required

set -euo pipefail

# Try to source hook-helpers.sh if available (for state file detection)
HELPERS="${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
if [[ -f "$HELPERS" ]]; then
  # shellcheck disable=SC1090,SC1091
  source "$HELPERS"

  # Check for active workflow FIRST (resume capability)
  STATE_FILE="$(get_state_file 2>/dev/null)" || STATE_FILE=""

  if [[ -n "$STATE_FILE" ]] && [[ -f "$STATE_FILE" ]]; then
    PLAN=$(frontmatter_get "$STATE_FILE" "plan" "")
    CURRENT=$(frontmatter_get "$STATE_FILE" "current_task" "0")
    TOTAL=$(frontmatter_get "$STATE_FILE" "total_tasks" "0")

    # Output resume context instead of getting-started skill
    cat << EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<system-context>\\n**ACTIVE WORKFLOW DETECTED**\\n\\nPlan: ${PLAN}\\nProgress: ${CURRENT}/${TOTAL} tasks\\n\\nCommands:\\n- /dev-workflow:resume - Continue execution\\n- /dev-workflow:abandon - Discard workflow state\\n</system-context>"
  }
}
EOF
    exit 0
  fi
fi

# No active workflow - load getting-started skill
SKILL_FILE="${CLAUDE_PLUGIN_ROOT}/skills/getting-started/SKILL.md"

# Check for Serena project configuration
SERENA_CONTEXT=""
if [[ -f ".serena/project.yml" ]]; then
  # Extract project name from .serena/project.yml
  SERENA_PROJECT=$(grep -E "^name:" .serena/project.yml 2>/dev/null | sed 's/name:[[:space:]]*//' | tr -d '"' || echo "")
  if [[ -n "$SERENA_PROJECT" ]]; then
    SERENA_CONTEXT="\\n\\n**Serena MCP Integration:**\\nIf Serena MCP tools are available (mcp__plugin_serena_serena__*), activate the project first:\\n- Call mcp__plugin_serena_serena__activate_project with project: \\\"${SERENA_PROJECT}\\\"\\n- Use Serena symbolic tools (find_symbol, get_symbols_overview, find_referencing_symbols) for code navigation"
  fi
fi

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
    "additionalContext": "<system-context>\\ndev-workflow skills available.\\n\\n**Getting Started:**\\n\\n${CONTENT}${SERENA_CONTEXT}\\n</system-context>"
  }
}
EOF
else
  echo '{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "dev-workflow plugin active. Use EnterPlanMode for planning, /dev-workflow:brainstorm for ideation."}}'
fi

exit 0
