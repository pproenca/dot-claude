#!/usr/bin/env bash
# Dependency checker for dev-skill plugin
# Validates required tools and node_modules installation

set -euo pipefail

SCRIPT_DIR="$(command cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(command cd "$SCRIPT_DIR/.." && pwd)"

MISSING=()
OPTIONAL_MISSING=()

# Core requirements
command -v node &> /dev/null || MISSING+=("node")
command -v npm &> /dev/null || MISSING+=("npm")
command -v git &> /dev/null || MISSING+=("git")

# Check node_modules exists
if [[ ! -d "$PLUGIN_ROOT/node_modules" ]]; then
  MISSING+=("node_modules (run: npm install)")
fi

# Check Node.js version (18+)
NODE_VERSION_OK=false
if command -v node &> /dev/null; then
  NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
  if [[ "$NODE_VERSION" -ge 18 ]]; then
    NODE_VERSION_OK=true
  else
    OPTIONAL_MISSING+=("Node.js 18+ (current: v$NODE_VERSION)")
  fi
fi

# Performance tools (recommended but optional)
command -v rg &> /dev/null || OPTIONAL_MISSING+=("rg (ripgrep) - faster grep")
command -v fd &> /dev/null || OPTIONAL_MISSING+=("fd (fd-find) - faster find")

# Report
echo "=== dev-skill Dependencies ==="
echo ""

echo "Required:"
if command -v node &> /dev/null; then
  if [[ "$NODE_VERSION_OK" == "true" ]]; then
    echo "  ✓ node (v$(node -v | sed 's/v//'))"
  else
    echo "  ✗ node (v$(node -v | sed 's/v//') - requires 18+)"
  fi
else
  echo "  ✗ node (MISSING - required)"
fi

if command -v npm &> /dev/null; then
  echo "  ✓ npm (v$(npm -v))"
else
  echo "  ✗ npm (MISSING - required)"
fi

if command -v git &> /dev/null; then
  echo "  ✓ git"
else
  echo "  ✗ git (MISSING - required for clone-repos.sh)"
fi

if [[ -d "$PLUGIN_ROOT/node_modules" ]]; then
  echo "  ✓ node_modules"
else
  echo "  ✗ node_modules (MISSING - run: npm install)"
fi

echo ""
echo "Optional (recommended):"
command -v rg &> /dev/null && echo "  ✓ rg (ripgrep)" || echo "  - rg (ripgrep) - faster searches"
command -v fd &> /dev/null && echo "  ✓ fd (fd-find)" || echo "  - fd (fd-find) - faster file finding"

echo ""

if [ ${#MISSING[@]} -eq 0 ]; then
  echo "Status: OK - all required dependencies present"
  exit 0
else
  echo "Status: MISSING required dependencies: ${MISSING[*]}"
  echo ""
  echo "To install:"
  echo "  bash $PLUGIN_ROOT/scripts/setup.sh"
  exit 1
fi
