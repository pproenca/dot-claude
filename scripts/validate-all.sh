#!/usr/bin/env bash
# Master orchestrator for marketplace validation
# Usage: ./validate-all.sh [options]
#
# Options:
#   --quick       Run only levels 1-2 (fast, good for pre-commit)
#   --level=N     Run specific level (1-7)
#   --skip-bats   Skip BATS tests in level 7
#   --help        Show this help

set -euo pipefail

# Get script directory BEFORE sourcing common.sh
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck disable=SC1091
source "$SCRIPTS_DIR/lib/common.sh"

# ============================================================================
# Options
# ============================================================================

QUICK_MODE=false
SPECIFIC_LEVEL=""
SKIP_BATS=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quick)
      QUICK_MODE=true
      shift
      ;;
    --level=*)
      SPECIFIC_LEVEL="${1#*=}"
      shift
      ;;
    --skip-bats)
      SKIP_BATS=true
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  --quick       Run only levels 1-2 (fast, good for pre-commit)"
      echo "  --level=N     Run specific level (1-7)"
      echo "  --skip-bats   Skip BATS tests in level 7"
      echo "  --help        Show this help"
      echo ""
      echo "Validation Levels:"
      echo "  1: Syntax & Structure"
      echo "  2: Frontmatter Fields"
      echo "  4: Arguments"
      echo "  5: File References"
      echo "  6: Bash Syntax"
      echo "  7: Integration Tests (BATS)"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# ============================================================================
# Validation Functions
# ============================================================================

run_level() {
  local level="$1"
  local script=""

  case "$level" in
    1) script="level-1-syntax.sh" ;;
    2) script="level-2-frontmatter.sh" ;;
    4) script="level-4-arguments.sh" ;;
    5) script="level-5-file-refs.sh" ;;
    6) script="level-6-bash.sh" ;;
    7) script="level-7-integration.sh" ;;
    *)
      echo "Unknown level: $level"
      return 1
      ;;
  esac

  if [[ -x "$SCRIPTS_DIR/$script" ]]; then
    echo ""
    echo "========================================"
    echo "Running Level $level: $script"
    echo "========================================"
    if [[ "$level" == "7" && "$SKIP_BATS" == true ]]; then
      # Run level 7 but skip the BATS section
      echo "[INFO] Skipping BATS tests (--skip-bats)"
      # For now, just run the script normally; a more sophisticated
      # approach would pass an env var to level-7 to skip BATS
    fi
    if "$SCRIPTS_DIR/$script"; then
      return 0
    else
      return 1
    fi
  else
    echo "Script not found: $SCRIPTS_DIR/$script"
    return 1
  fi
}

# ============================================================================
# Main
# ============================================================================

echo "========================================"
echo "Claude Code Plugin Marketplace Validator"
echo "========================================"

TOTAL_ERRORS=0

# Determine which levels to run
if [[ -n "$SPECIFIC_LEVEL" ]]; then
  # Run specific level only
  LEVELS=("$SPECIFIC_LEVEL")
elif [[ "$QUICK_MODE" == true ]]; then
  # Quick mode: levels 1-2 only
  LEVELS=(1 2)
else
  # Default: levels 1-6 (skip 7 which is slow BATS/integration)
  LEVELS=(1 2 4 5 6)
fi

# Run each level
for level in "${LEVELS[@]}"; do
  if ! run_level "$level"; then
    TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
  fi
done

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "========================================"
echo "VALIDATION SUMMARY"
echo "========================================"

if [[ $TOTAL_ERRORS -eq 0 ]]; then
  echo "All validation levels PASSED"
  exit 0
else
  echo "FAILED: $TOTAL_ERRORS level(s) had errors"
  exit 1
fi
