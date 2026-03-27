#!/usr/bin/env bash
# guardrail.sh — PreToolUse guardrail for composition skills with destructive operations
#
# Called by on-demand hooks to block dangerous commands.
# Input: the tool input JSON (passed as $1)
#
# Exit 0 = allow, exit 2 = block (MITM rejection)

set -euo pipefail

TOOL_INPUT="${1:-}"

if [[ -z "$TOOL_INPUT" ]]; then
  exit 0
fi

# Extract the command from the tool input
# The input is JSON with a "command" field for Bash tool calls
COMMAND=$(echo "$TOOL_INPUT" | grep -oP '"command"\s*:\s*"[^"]*"' | head -1 | sed 's/"command"\s*:\s*"//' | sed 's/"$//' || true)

if [[ -z "$COMMAND" ]]; then
  exit 0
fi

# Patterns to block
BLOCKED_PATTERNS=(
  'rm -rf /'
  'rm -rf ~'
  'rm -rf \.'
  'DROP TABLE'
  'DROP DATABASE'
  'TRUNCATE TABLE'
  'git push --force'
  'git push -f '
  'kubectl delete'
  'docker rm -f'
  'docker system prune'
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qi "$pattern"; then
    echo '{"error": "BLOCKED by guardrail: Command matches destructive pattern \"'"$pattern"'\". Use --dry-run first or get explicit confirmation."}' >&2
    exit 2
  fi
done

# Allow by default
exit 0
