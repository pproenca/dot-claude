#!/bin/bash
# Check if worktree directory is configured in additionalDirectories

set -euo pipefail

SETTINGS_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/settings.json"

# Check if worktree directory is already configured
is_configured() {
  if [[ -f "$SETTINGS_FILE" ]]; then
    # Check for the worktree path in additionalDirectories (handles ~ and expanded path)
    if grep -qE '(~|'"$HOME"')/\.dot-claude-worktrees' "$SETTINGS_FILE" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

if ! is_configured; then
  # Output warning as hook context
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<system-reminder>\nWorktree support not configured. Run this command in Claude Code:\n\n/add-dir ~/.dot-claude-worktrees\n\nThis allows Claude to navigate to worktrees. The directory is created automatically when you create your first worktree.\n\nAlternative (for scripting):\nmkdir -p .claude && jq -s '.[0] * .[1]' .claude/settings.json <(echo '{\"permissions\":{\"additionalDirectories\":[\"~/.dot-claude-worktrees\"]}}') > .claude/settings.tmp && mv .claude/settings.tmp .claude/settings.json\n</system-reminder>"
  }
}
EOF
fi

exit 0
