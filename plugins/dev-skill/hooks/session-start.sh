#!/bin/bash
# Session start hook - checks dependencies and provides helpful guidance

set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# Check if node is available
if ! command -v node &>/dev/null; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<system-context>\ndev-skill plugin active.\n\n**Warning:** Node.js is not installed. The following scripts will not work:\n- validate-skill.js\n- build-agents-md.js\n\nInstall Node.js 18+ to use all plugin features:\n- macOS: brew install node\n- Linux: sudo apt install nodejs npm\n</system-context>"
  }
}
EOF
  exit 0
fi

# Check if node_modules exists
if [[ ! -d "$PLUGIN_ROOT/node_modules" ]]; then
  cat << EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<system-context>\ndev-skill plugin active.\n\n**Warning:** npm dependencies not installed. Run setup to enable all features:\n\n\\\`\\\`\\\`bash\nbash $PLUGIN_ROOT/scripts/setup.sh\n\\\`\\\`\\\`\n\nOr manually:\n\\\`\\\`\\\`bash\ncd $PLUGIN_ROOT && npm install\n\\\`\\\`\\\`\n</system-context>"
  }
}
EOF
  exit 0
fi

# All dependencies present
cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<system-context>\ndev-skill plugin active. Commands available:\n- /dev-skill:new <technology> - Create best practices skill (40+ rules)\n- /dev-skill:from-codebase <repo> - Extract patterns from reference codebases\n- /dev-skill:migrate <path> - Migrate skill to new structure\n- /dev-skill:shrink <path> - Regenerate AGENTS.md as slim TOC-only doc\n</system-context>"
  }
}
EOF

exit 0
