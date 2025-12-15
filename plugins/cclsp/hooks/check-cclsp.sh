#!/bin/bash
# Check if cclsp is configured and provide helpful message if not
# This runs at session start to remind users about setup

# Only show message if CCLSP_CONFIG_PATH is not set or config doesn't exist
if [ -z "$CCLSP_CONFIG_PATH" ]; then
  # Check if config exists in default location
  if [ ! -f "$HOME/.config/claude/cclsp.json" ]; then
    echo "cclsp LSP tools not configured. Run /cclsp:setup for enhanced code navigation."
  fi
elif [ ! -f "$CCLSP_CONFIG_PATH" ]; then
  echo "cclsp config not found at $CCLSP_CONFIG_PATH. Run /cclsp:setup to configure."
fi

# Exit successfully regardless - this is just a reminder, not a blocker
exit 0
