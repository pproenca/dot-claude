#!/usr/bin/env bash
# run-harness.sh - WebCodecs Harness Test Runner
# Usage: curl -fsSL <url> | bash
#    or: ./run-harness.sh [OPTIONS]

set -euo pipefail

VERSION="1.0.0"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]:-run-harness.sh}")"

# Default configuration
IMPLEMENTATION="node-webcodecs"
OUTPUT_DIR="${HOME}/.webcodecs-harness-test"
DRY_RUN=false
VERBOSE=false
QUIET=false
YES=false
NO_COLOR=false
CLEANUP=false
JSON_ONLY=false

# Parse command line arguments
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help)
        show_help
        exit 0
        ;;
      -V|--version)
        echo "$VERSION"
        exit 0
        ;;
      -i|--implementation)
        IMPLEMENTATION="${2:-}"
        shift 2
        ;;
      -o|--output)
        OUTPUT_DIR="${2:-}"
        shift 2
        ;;
      -n|--dry-run)
        DRY_RUN=true
        shift
        ;;
      -v|--verbose)
        VERBOSE=true
        shift
        ;;
      -q|--quiet)
        QUIET=true
        shift
        ;;
      -y|--yes)
        YES=true
        shift
        ;;
      --no-color)
        NO_COLOR=true
        shift
        ;;
      --cleanup)
        CLEANUP=true
        shift
        ;;
      --json-only)
        JSON_ONLY=true
        QUIET=true
        shift
        ;;
      *)
        echo "Unknown option: $1" >&2
        echo "Use --help for usage information" >&2
        exit 1
        ;;
    esac
  done
}

show_help() {
  cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]
       curl -fsSL <url> | bash -s -- [OPTIONS]

Run the WebCodecs test harness against a specified implementation.

Options:
  -h, --help              Show this help message
  -V, --version           Show version information
  -i, --implementation    WebCodecs implementation to test (default: node-webcodecs)
                          Options: node-webcodecs, webcodecs-polyfill, node-libav-webcodecs
  -o, --output DIR        Output directory for results (default: ~/.webcodecs-harness-test)
  -n, --dry-run           Show what would be done without executing
  -v, --verbose           Enable verbose output
  -q, --quiet             Minimal output, only show final results
  -y, --yes               Skip confirmation prompts
  --no-color              Disable colored output
  --cleanup               Remove test directory after completion
  --json-only             Output only JSON (no terminal UI)

Examples:
  # Run with defaults
  $SCRIPT_NAME

  # Test a different implementation
  $SCRIPT_NAME --implementation webcodecs-polyfill

  # Dry run to see what would happen
  $SCRIPT_NAME --dry-run

  # CI mode with JSON output
  $SCRIPT_NAME --json-only --yes
EOF
}

# Main entry point
main() {
  parse_args "$@"

  if [[ "$DRY_RUN" == true ]]; then
    echo "[DRY RUN] Would execute with:"
    echo "  Implementation: $IMPLEMENTATION"
    echo "  Output: $OUTPUT_DIR"
    exit 0
  fi
}

main "$@"
