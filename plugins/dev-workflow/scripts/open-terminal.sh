#!/usr/bin/env bash
# Opens a new Terminal.app window in the specified directory and runs claude
# Usage: open-terminal.sh <worktree-path> [initial-prompt]

WORKTREE_PATH="$1"
INITIAL_PROMPT="${2:-}"

if [[ -z "$WORKTREE_PATH" ]]; then
  echo "Usage: $0 <worktree-path> [initial-prompt]" >&2
  exit 1
fi

if [[ ! -d "$WORKTREE_PATH" ]]; then
  echo "Error: Directory does not exist: $WORKTREE_PATH" >&2
  exit 1
fi

# Build claude command with optional initial prompt
if [[ -n "$INITIAL_PROMPT" ]]; then
  # Escape single quotes in prompt for AppleScript
  ESCAPED_PROMPT="${INITIAL_PROMPT//\'/\'\\\'\'}"
  CLAUDE_CMD="claude --dangerously-skip-permissions -p '$ESCAPED_PROMPT'"
else
  CLAUDE_CMD="claude --dangerously-skip-permissions"
fi

osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$WORKTREE_PATH' && $CLAUDE_CMD"
end tell
EOF

echo "Launched Terminal.app in: $WORKTREE_PATH"
