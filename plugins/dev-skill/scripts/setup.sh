#!/usr/bin/env bash
# One-click contributor setup for dev-skill plugin
# Usage: ./scripts/setup.sh

set -euo pipefail

SCRIPT_DIR="$(command cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(command cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Setting up dev-skill for contributors ==="
echo ""

# Check Node.js
if ! command -v node &>/dev/null; then
  echo "Error: Node.js is required but not installed."
  echo ""
  echo "Install Node.js 18+ from: https://nodejs.org/"
  echo "  macOS: brew install node"
  echo "  Linux: sudo apt install nodejs npm"
  exit 1
fi

# Check Node.js version (18+)
NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
if [[ "$NODE_VERSION" -lt 18 ]]; then
  echo "Error: Node.js 18+ required (current: v$NODE_VERSION)"
  echo ""
  echo "Upgrade Node.js from: https://nodejs.org/"
  exit 1
else
  echo "✓ Node.js v$(node -v | sed 's/v//') installed"
fi

# Check npm
if ! command -v npm &>/dev/null; then
  echo "Error: npm is required but not installed."
  exit 1
else
  echo "✓ npm v$(npm -v) installed"
fi

# Check git
if ! command -v git &>/dev/null; then
  echo "Warning: git is not installed. clone-repos.sh will not work."
else
  echo "✓ git installed"
fi

# Install npm dependencies
echo ""
echo "Installing npm dependencies..."
cd "$PLUGIN_ROOT"
npm install

# Verify
echo ""
echo "Running dependency check..."
"$SCRIPT_DIR/check-dependencies.sh"

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Available commands:"
echo "  /dev-skill:new <tech>          # Create new best practices skill"
echo "  /dev-skill:from-codebase <repo># Extract patterns from codebases"
echo "  /dev-skill:migrate <path>      # Migrate skill to new structure"
echo ""
echo "Validation:"
echo "  node scripts/validate-skill.js <skill-dir>  # Validate a skill"
echo "  node scripts/build-agents-md.js <skill-dir> # Build AGENTS.md"
