#!/usr/bin/env bash
#
# dot-claude installation helper
# Guides users through Claude Code plugin installation
#

set -euo pipefail

readonly REPO="pproenca/dot-claude"
readonly MARKETPLACE_NAME="dot-claude"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

print_header() {
  echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}  dot-claude Plugin Marketplace Installation Helper${NC}"
  echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
  echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}!${NC} $1"
}

print_error() {
  echo -e "${RED}✗${NC} $1"
}

print_info() {
  echo -e "${BLUE}→${NC} $1"
}

check_claude_code() {
  echo "Checking prerequisites..."
  if command -v claude &> /dev/null; then
    print_success "Claude Code CLI is installed"
    return 0
  else
    print_error "Claude Code CLI not found"
    echo ""
    echo "Please install Claude Code first:"
    echo "  https://github.com/anthropics/claude-code"
    echo ""
    return 1
  fi
}

show_plugins() {
  echo ""
  echo -e "${BLUE}Available Plugins:${NC}"
  echo ""
  echo "  dev-workflow   - TDD, systematic debugging, and code review workflows"
  echo "  dev-python     - Python 3.12+ with uv, ruff, pydantic, FastAPI, Django"
  echo "  dev-ts         - TypeScript/JavaScript with Google Style Guide patterns"
  echo "  dev-cpp        - C++ development with clangd LSP integration"
  echo "  dev-shell      - Shell scripting with Google Style Guide patterns"
  echo ""
}

show_installation_commands() {
  echo -e "${BLUE}Installation Commands:${NC}"
  echo ""
  echo "Run these commands inside Claude Code:"
  echo ""
  echo -e "  ${GREEN}# Step 1: Add the marketplace${NC}"
  echo "  /plugin marketplace add ${REPO}"
  echo ""
  echo -e "  ${GREEN}# Step 2: Install plugins (choose what you need)${NC}"
  echo "  /plugin install dev-workflow@${MARKETPLACE_NAME}"
  echo "  /plugin install dev-python@${MARKETPLACE_NAME}"
  echo "  /plugin install dev-ts@${MARKETPLACE_NAME}"
  echo "  /plugin install dev-cpp@${MARKETPLACE_NAME}"
  echo "  /plugin install dev-shell@${MARKETPLACE_NAME}"
  echo ""
  echo -e "  ${GREEN}# Or install all at once:${NC}"
  echo "  /plugin install dev-workflow@${MARKETPLACE_NAME} dev-python@${MARKETPLACE_NAME} dev-ts@${MARKETPLACE_NAME} dev-cpp@${MARKETPLACE_NAME} dev-shell@${MARKETPLACE_NAME}"
  echo ""
}

show_quick_start() {
  echo -e "${BLUE}Quick Start (copy & paste into Claude Code):${NC}"
  echo ""
  echo "  /plugin marketplace add ${REPO} && /plugin install dev-workflow@${MARKETPLACE_NAME}"
  echo ""
}

show_verification() {
  echo -e "${BLUE}Verify Installation:${NC}"
  echo ""
  echo "  After installing, verify with:"
  echo "  /plugin"
  echo ""
  echo "  You should see your installed plugins in the 'Installed' tab."
  echo ""
}

main() {
  print_header

  if ! check_claude_code; then
    exit 1
  fi

  show_plugins
  show_quick_start
  show_installation_commands
  show_verification

  echo -e "${GREEN}Ready to install!${NC}"
  echo "Open Claude Code and run the commands above."
  echo ""
}

main "$@"
