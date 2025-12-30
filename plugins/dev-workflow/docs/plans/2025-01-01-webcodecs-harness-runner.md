# WebCodecs Harness Test Runner Implementation Plan

> **Execution:** Use `/dev-workflow:execute-plan docs/plans/2025-01-01-webcodecs-harness-runner.md` to implement task-by-task.

**Goal:** Create a production-grade, curl|bash installable script that clones vjeux/webcodecs-harness, configures it for node-webcodecs, runs all tests, and reports results in both rich terminal output and JSON format.

**Architecture:** Single self-contained bash script (~500 lines) with modular functions, beautiful terminal UI (colors, spinners, progress bars), comprehensive error handling, cross-platform support (macOS/Linux), and machine-readable JSON output. Follows patterns from industry-standard installers (nvm, Homebrew).

**Tech Stack:** Bash 4+, curl, git, Node.js 18+, npm, ffmpeg, pkg-config, jq (optional), tput for terminal control

---

## Script Design Overview

### Terminal Output Mockup

```
╔══════════════════════════════════════════════════════════════════╗
║   WebCodecs Harness Test Runner v1.0.0                          ║
║   Testing: node-webcodecs against vjeux/webcodecs-harness       ║
╚══════════════════════════════════════════════════════════════════╝

System Information
──────────────────
  OS:           macOS 14.0 (Darwin arm64)
  Node:         v20.10.0
  npm:          10.2.3
  Package Mgr:  Homebrew 4.2.0

Pre-flight Checks
─────────────────
  ✓ git available
  ✓ curl available
  ✓ Node.js >= 18
  ⠋ Checking ffmpeg...

[Step 1/6] Installing Dependencies
──────────────────────────────────
  ✓ ffmpeg 6.1 installed
  ✓ pkg-config 0.29.2 installed

[Step 2/6] Cloning Repository
─────────────────────────────
  ⠸ Cloning vjeux/webcodecs-harness... (1.2 MB)
  ✓ Repository cloned to ~/.webcodecs-harness-test

[Step 3/6] Configuring Polyfill
───────────────────────────────
  ✓ Configured src/polyfill.js for node-webcodecs

[Step 4/6] Installing npm Packages
──────────────────────────────────
  ⠼ Installing 47 packages...
  ✓ npm install completed (23.4s)

[Step 5/6] Running Tests
────────────────────────
  ⠹ Running vitest --run...

  Test Results:
  ┌─────────────────────────────────────┬────────┐
  │ Test Suite                          │ Status │
  ├─────────────────────────────────────┼────────┤
  │ VideoDecoder.test.ts                │ ✓ PASS │
  │ VideoEncoder.test.ts                │ ✓ PASS │
  │ AudioDecoder.test.ts                │ ✓ PASS │
  │ AudioEncoder.test.ts                │ ✓ PASS │
  │ VideoFrame.test.ts                  │ ✗ FAIL │
  └─────────────────────────────────────┴────────┘

[Step 6/6] Generating Report
────────────────────────────
  ✓ JSON report: ~/.webcodecs-harness-test/results.json
  ✓ HTML report: ~/.webcodecs-harness-test/results.html

═══════════════════════════════════════════════════════════════════
                         RESULTS SUMMARY
═══════════════════════════════════════════════════════════════════

  Implementation:    node-webcodecs
  Harness Version:   1.0.0 (commit abc1234)

  Tests Passed:      42/47 (89.4%)
  Tests Failed:      5
  Tests Skipped:     0

  Duration:          34.7s

  Report Location:   ~/.webcodecs-harness-test/results.json

═══════════════════════════════════════════════════════════════════
```

### JSON Output Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "meta": {
      "type": "object",
      "properties": {
        "version": { "type": "string" },
        "timestamp": { "type": "string", "format": "date-time" },
        "implementation": { "type": "string" },
        "harness_version": { "type": "string" },
        "harness_commit": { "type": "string" }
      }
    },
    "environment": {
      "type": "object",
      "properties": {
        "os": { "type": "string" },
        "arch": { "type": "string" },
        "node_version": { "type": "string" },
        "npm_version": { "type": "string" },
        "ffmpeg_version": { "type": "string" }
      }
    },
    "summary": {
      "type": "object",
      "properties": {
        "total": { "type": "integer" },
        "passed": { "type": "integer" },
        "failed": { "type": "integer" },
        "skipped": { "type": "integer" },
        "duration_ms": { "type": "integer" },
        "pass_rate": { "type": "number" }
      }
    },
    "tests": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "file": { "type": "string" },
          "status": { "enum": ["passed", "failed", "skipped"] },
          "duration_ms": { "type": "integer" },
          "error": { "type": ["string", "null"] }
        }
      }
    }
  }
}
```

### Command-Line Interface

```bash
# Standard invocation via curl
curl -fsSL https://raw.githubusercontent.com/user/repo/main/run-harness.sh | bash

# With options
curl -fsSL ... | bash -s -- --implementation node-webcodecs --output ./results

# Direct invocation
./run-harness.sh [OPTIONS]

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
```

---

## Implementation Plan

### Task 1: Create Script Skeleton with CLI Parsing

**Files:**
- Create: `scripts/run-harness.sh`
- Test: `tests/run-harness.bats`

**Step 1: Write the CLI parsing test** (3 min)

```bash
# tests/run-harness.bats

load test_helper

SCRIPT="$PLUGIN_ROOT/scripts/run-harness.sh"

@test "--help shows usage information" {
  run "$SCRIPT" --help
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "Usage:"
  echo "$output" | grep -q -- "--implementation"
  echo "$output" | grep -q -- "--output"
}

@test "--version shows version" {
  run "$SCRIPT" --version
  [ "$status" -eq 0 ]
  echo "$output" | grep -qE "^[0-9]+\.[0-9]+\.[0-9]+$"
}

@test "--dry-run sets DRY_RUN flag" {
  run "$SCRIPT" --dry-run --help
  [ "$status" -eq 0 ]
}

@test "unknown option shows error" {
  run "$SCRIPT" --unknown-option
  [ "$status" -eq 1 ]
  echo "$output" | grep -q "Unknown option"
}
```

**Step 2: Run test to verify failure** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: FAIL (script doesn't exist)

**Step 3: Write script skeleton** (5 min)

```bash
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
```

**Step 4: Make executable and run test** (30 sec)

```bash
chmod +x scripts/run-harness.sh
bats tests/run-harness.bats
```

Expected: PASS (4 passed)

**Step 5: Commit** (30 sec)

```bash
git add scripts/run-harness.sh tests/run-harness.bats
git commit -m "feat(harness): add CLI skeleton with argument parsing"
```

---

### Task 2: Add Terminal UI Functions (Colors, Spinners, Progress)

**Files:**
- Modify: `scripts/run-harness.sh`
- Test: `tests/run-harness.bats`

**Step 1: Write terminal output tests** (3 min)

```bash
# Append to tests/run-harness.bats

@test "output includes colored header when terminal supports it" {
  # Force color mode for testing
  TERM=xterm-256color run "$SCRIPT" --dry-run
  [ "$status" -eq 0 ]
}

@test "--no-color disables colored output" {
  run "$SCRIPT" --no-color --dry-run
  [ "$status" -eq 0 ]
  # Should not contain ANSI escape codes
  ! echo "$output" | grep -q $'\033'
}

@test "--quiet suppresses non-essential output" {
  run "$SCRIPT" --quiet --dry-run
  [ "$status" -eq 0 ]
  # Output should be minimal
  [[ ${#output} -lt 200 ]]
}
```

**Step 2: Run tests to verify failure** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: PASS (existing tests should still pass)

**Step 3: Add terminal UI functions** (5 min)

Add after `set -euo pipefail`:

```bash
# Terminal control
setup_colors() {
  if [[ "$NO_COLOR" == true ]] || [[ ! -t 1 ]] || [[ "${TERM:-}" == "dumb" ]]; then
    RED=""
    GREEN=""
    YELLOW=""
    BLUE=""
    MAGENTA=""
    CYAN=""
    BOLD=""
    DIM=""
    RESET=""
  else
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    MAGENTA='\033[0;35m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    DIM='\033[2m'
    RESET='\033[0m'
  fi
}

# Output functions
print_header() {
  [[ "$QUIET" == true ]] && return
  echo ""
  echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════════╗${RESET}"
  echo -e "${BOLD}${BLUE}║${RESET}   ${BOLD}WebCodecs Harness Test Runner${RESET} v${VERSION}                          ${BOLD}${BLUE}║${RESET}"
  echo -e "${BOLD}${BLUE}║${RESET}   Testing: ${CYAN}${IMPLEMENTATION}${RESET} against vjeux/webcodecs-harness       ${BOLD}${BLUE}║${RESET}"
  echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════════╝${RESET}"
  echo ""
}

print_section() {
  local title="$1"
  [[ "$QUIET" == true ]] && return
  echo ""
  echo -e "${BOLD}${title}${RESET}"
  echo -e "${DIM}$(printf '─%.0s' $(seq 1 ${#title}))${RESET}"
}

print_step() {
  local step="$1"
  local total="$2"
  local desc="$3"
  [[ "$QUIET" == true ]] && return
  echo ""
  echo -e "${BOLD}[Step ${step}/${total}]${RESET} ${desc}"
  echo -e "${DIM}$(printf '─%.0s' $(seq 1 $((${#desc} + 12))))${RESET}"
}

print_ok() {
  local msg="$1"
  [[ "$QUIET" == true ]] && return
  echo -e "  ${GREEN}✓${RESET} ${msg}"
}

print_fail() {
  local msg="$1"
  echo -e "  ${RED}✗${RESET} ${msg}" >&2
}

print_warn() {
  local msg="$1"
  [[ "$QUIET" == true ]] && return
  echo -e "  ${YELLOW}⚠${RESET} ${msg}"
}

print_info() {
  local label="$1"
  local value="$2"
  [[ "$QUIET" == true ]] && return
  printf "  %-14s %s\n" "${label}:" "${value}"
}

# Spinner for long-running operations
SPINNER_PID=""
SPINNER_CHARS="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

start_spinner() {
  local msg="$1"
  [[ "$QUIET" == true ]] && return
  [[ ! -t 1 ]] && return  # No spinner if not terminal

  (
    local i=0
    while true; do
      printf "\r  ${CYAN}${SPINNER_CHARS:i++%${#SPINNER_CHARS}:1}${RESET} %s..." "$msg"
      sleep 0.1
    done
  ) &
  SPINNER_PID=$!
  disown
}

stop_spinner() {
  local success="${1:-true}"
  local msg="${2:-}"

  if [[ -n "$SPINNER_PID" ]]; then
    kill "$SPINNER_PID" 2>/dev/null || true
    wait "$SPINNER_PID" 2>/dev/null || true
    SPINNER_PID=""
    printf "\r"  # Clear spinner line
  fi

  if [[ -n "$msg" ]]; then
    if [[ "$success" == true ]]; then
      print_ok "$msg"
    else
      print_fail "$msg"
    fi
  fi
}
```

**Step 4: Update main() to use UI functions** (2 min)

```bash
main() {
  parse_args "$@"
  setup_colors

  if [[ "$DRY_RUN" == true ]]; then
    print_header
    echo "[DRY RUN] Would execute with:"
    print_info "Implementation" "$IMPLEMENTATION"
    print_info "Output" "$OUTPUT_DIR"
    exit 0
  fi

  print_header
}
```

**Step 5: Run tests** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: PASS

**Step 6: Commit** (30 sec)

```bash
git add scripts/run-harness.sh tests/run-harness.bats
git commit -m "feat(harness): add terminal UI functions (colors, spinners)"
```

---

### Task 3: Add Platform Detection and Dependency Checks

**Files:**
- Modify: `scripts/run-harness.sh`
- Test: `tests/run-harness.bats`

**Step 1: Write platform detection tests** (3 min)

```bash
# Append to tests/run-harness.bats

@test "detects current OS" {
  source "$SCRIPT"
  detect_platform
  [[ -n "$OS" ]]
  [[ "$OS" == "macos" || "$OS" == "linux" ]]
}

@test "detects package manager" {
  source "$SCRIPT"
  detect_platform
  [[ -n "$PKG_MANAGER" ]]
}

@test "checks for required commands" {
  source "$SCRIPT"
  run check_command "bash"
  [ "$status" -eq 0 ]

  run check_command "nonexistent-command-xyz"
  [ "$status" -eq 1 ]
}
```

**Step 2: Run tests to verify failure** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: FAIL (functions don't exist)

**Step 3: Add platform detection** (5 min)

```bash
# Platform detection
detect_platform() {
  case "$(uname -s)" in
    Darwin*)
      OS="macos"
      ARCH="$(uname -m)"
      PKG_MANAGER="brew"
      ;;
    Linux*)
      OS="linux"
      ARCH="$(uname -m)"
      if command -v apt-get &>/dev/null; then
        PKG_MANAGER="apt"
      elif command -v dnf &>/dev/null; then
        PKG_MANAGER="dnf"
      elif command -v yum &>/dev/null; then
        PKG_MANAGER="yum"
      elif command -v pacman &>/dev/null; then
        PKG_MANAGER="pacman"
      else
        PKG_MANAGER="unknown"
      fi
      ;;
    *)
      OS="unknown"
      ARCH="unknown"
      PKG_MANAGER="unknown"
      ;;
  esac

  export OS ARCH PKG_MANAGER
}

# Check if a command exists
check_command() {
  local cmd="$1"
  command -v "$cmd" &>/dev/null
}

# Get version of a command
get_version() {
  local cmd="$1"
  case "$cmd" in
    node)
      node --version 2>/dev/null | sed 's/^v//'
      ;;
    npm)
      npm --version 2>/dev/null
      ;;
    ffmpeg)
      ffmpeg -version 2>/dev/null | head -1 | sed 's/ffmpeg version \([^ ]*\).*/\1/'
      ;;
    git)
      git --version 2>/dev/null | sed 's/git version //'
      ;;
    brew)
      brew --version 2>/dev/null | head -1 | sed 's/Homebrew //'
      ;;
    *)
      echo "unknown"
      ;;
  esac
}

# Print system information
print_system_info() {
  print_section "System Information"

  detect_platform

  local os_pretty
  case "$OS" in
    macos)
      os_pretty="macOS $(sw_vers -productVersion 2>/dev/null || echo 'unknown') (Darwin $ARCH)"
      ;;
    linux)
      if [[ -f /etc/os-release ]]; then
        os_pretty="$(. /etc/os-release && echo "$PRETTY_NAME") ($ARCH)"
      else
        os_pretty="Linux ($ARCH)"
      fi
      ;;
    *)
      os_pretty="Unknown OS"
      ;;
  esac

  print_info "OS" "$os_pretty"

  if check_command node; then
    print_info "Node" "v$(get_version node)"
  else
    print_info "Node" "${RED}not installed${RESET}"
  fi

  if check_command npm; then
    print_info "npm" "$(get_version npm)"
  else
    print_info "npm" "${RED}not installed${RESET}"
  fi

  case "$PKG_MANAGER" in
    brew)
      print_info "Package Mgr" "Homebrew $(get_version brew)"
      ;;
    apt)
      print_info "Package Mgr" "apt (Debian/Ubuntu)"
      ;;
    *)
      print_info "Package Mgr" "$PKG_MANAGER"
      ;;
  esac
}

# Pre-flight checks
preflight_checks() {
  print_section "Pre-flight Checks"

  local failed=0

  # Required commands
  for cmd in git curl; do
    if check_command "$cmd"; then
      print_ok "$cmd available"
    else
      print_fail "$cmd not found - please install it first"
      ((failed++))
    fi
  done

  # Node.js version check
  if check_command node; then
    local node_version
    node_version=$(node --version | sed 's/^v//' | cut -d. -f1)
    if [[ "$node_version" -ge 18 ]]; then
      print_ok "Node.js >= 18 (v$(get_version node))"
    else
      print_fail "Node.js >= 18 required (found v$(get_version node))"
      ((failed++))
    fi
  else
    print_warn "Node.js not installed - will attempt to install"
  fi

  # FFmpeg check
  if check_command ffmpeg; then
    print_ok "ffmpeg $(get_version ffmpeg)"
  else
    print_warn "ffmpeg not installed - will attempt to install"
  fi

  # pkg-config check
  if check_command pkg-config; then
    print_ok "pkg-config available"
  else
    print_warn "pkg-config not installed - will attempt to install"
  fi

  if [[ $failed -gt 0 ]]; then
    echo ""
    print_fail "Pre-flight checks failed. Please install missing dependencies."
    exit 1
  fi
}
```

**Step 4: Run tests** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: PASS

**Step 5: Commit** (30 sec)

```bash
git add scripts/run-harness.sh tests/run-harness.bats
git commit -m "feat(harness): add platform detection and preflight checks"
```

---

### Task 4: Add Dependency Installation

**Files:**
- Modify: `scripts/run-harness.sh`
- Test: `tests/run-harness.bats`

**Step 1: Write dependency installation tests** (3 min)

```bash
# Append to tests/run-harness.bats

@test "install_package function exists" {
  source "$SCRIPT"
  declare -f install_package >/dev/null
}

@test "install_dependencies respects dry-run" {
  DRY_RUN=true
  source "$SCRIPT"
  setup_colors
  detect_platform
  run install_dependencies
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "Would install"
}
```

**Step 2: Run tests to verify failure** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: FAIL

**Step 3: Add installation functions** (5 min)

```bash
# Package installation
install_package() {
  local pkg="$1"
  local name="${2:-$pkg}"

  if [[ "$DRY_RUN" == true ]]; then
    echo "  [DRY RUN] Would install $name via $PKG_MANAGER"
    return 0
  fi

  start_spinner "Installing $name"

  case "$PKG_MANAGER" in
    brew)
      if brew install "$pkg" &>/dev/null; then
        stop_spinner true "$name installed"
      else
        stop_spinner false "Failed to install $name"
        return 1
      fi
      ;;
    apt)
      if sudo apt-get install -y "$pkg" &>/dev/null; then
        stop_spinner true "$name installed"
      else
        stop_spinner false "Failed to install $name"
        return 1
      fi
      ;;
    dnf|yum)
      if sudo "$PKG_MANAGER" install -y "$pkg" &>/dev/null; then
        stop_spinner true "$name installed"
      else
        stop_spinner false "Failed to install $name"
        return 1
      fi
      ;;
    pacman)
      if sudo pacman -S --noconfirm "$pkg" &>/dev/null; then
        stop_spinner true "$name installed"
      else
        stop_spinner false "Failed to install $name"
        return 1
      fi
      ;;
    *)
      stop_spinner false "Unknown package manager: $PKG_MANAGER"
      return 1
      ;;
  esac
}

# Install Node.js if needed
install_nodejs() {
  if check_command node; then
    local node_version
    node_version=$(node --version | sed 's/^v//' | cut -d. -f1)
    if [[ "$node_version" -ge 18 ]]; then
      print_ok "Node.js v$(get_version node) already installed"
      return 0
    fi
  fi

  if [[ "$DRY_RUN" == true ]]; then
    echo "  [DRY RUN] Would install Node.js 20"
    return 0
  fi

  case "$PKG_MANAGER" in
    brew)
      install_package "node@20" "Node.js 20"
      ;;
    apt)
      # Use NodeSource repository for newer Node.js
      start_spinner "Setting up NodeSource repository"
      curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - &>/dev/null
      stop_spinner true "NodeSource repository configured"
      install_package "nodejs" "Node.js 20"
      ;;
    *)
      print_warn "Please install Node.js 18+ manually"
      return 1
      ;;
  esac
}

# Install all dependencies
install_dependencies() {
  print_step 1 6 "Installing Dependencies"

  # FFmpeg
  if ! check_command ffmpeg; then
    install_package "ffmpeg" "ffmpeg"
  else
    print_ok "ffmpeg $(get_version ffmpeg) already installed"
  fi

  # pkg-config
  if ! check_command pkg-config; then
    install_package "pkg-config" "pkg-config"
  else
    print_ok "pkg-config already installed"
  fi

  # Node.js
  install_nodejs
}
```

**Step 4: Run tests** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: PASS

**Step 5: Commit** (30 sec)

```bash
git add scripts/run-harness.sh tests/run-harness.bats
git commit -m "feat(harness): add dependency installation functions"
```

---

### Task 5: Add Repository Cloning and Polyfill Configuration

**Files:**
- Modify: `scripts/run-harness.sh`
- Test: `tests/run-harness.bats`

**Step 1: Write clone and config tests** (3 min)

```bash
# Append to tests/run-harness.bats

@test "clone_harness respects dry-run" {
  DRY_RUN=true
  OUTPUT_DIR="$BATS_TEST_TMPDIR/test-harness"
  source "$SCRIPT"
  setup_colors
  run clone_harness
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "Would clone"
}

@test "configure_polyfill generates valid config" {
  source "$SCRIPT"
  IMPLEMENTATION="node-webcodecs"
  run generate_polyfill_code
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "node-webcodecs"
}
```

**Step 2: Run tests** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: FAIL

**Step 3: Add clone and configuration functions** (5 min)

```bash
HARNESS_REPO="https://github.com/vjeux/webcodecs-harness.git"

# Clone the harness repository
clone_harness() {
  print_step 2 6 "Cloning Repository"

  if [[ "$DRY_RUN" == true ]]; then
    echo "  [DRY RUN] Would clone $HARNESS_REPO to $OUTPUT_DIR"
    return 0
  fi

  if [[ -d "$OUTPUT_DIR/.git" ]]; then
    print_ok "Repository already exists at $OUTPUT_DIR"
    start_spinner "Updating repository"
    (cd "$OUTPUT_DIR" && git pull --quiet) || true
    stop_spinner true "Repository updated"
  else
    start_spinner "Cloning vjeux/webcodecs-harness"

    mkdir -p "$(dirname "$OUTPUT_DIR")"
    if git clone --quiet "$HARNESS_REPO" "$OUTPUT_DIR"; then
      stop_spinner true "Repository cloned to $OUTPUT_DIR"
    else
      stop_spinner false "Failed to clone repository"
      return 1
    fi
  fi

  # Get commit hash for reporting
  HARNESS_COMMIT=$(cd "$OUTPUT_DIR" && git rev-parse --short HEAD)
  export HARNESS_COMMIT
}

# Generate polyfill.js content for the selected implementation
generate_polyfill_code() {
  case "$IMPLEMENTATION" in
    node-webcodecs)
      cat <<'POLYFILL'
// Configured by run-harness.sh for: node-webcodecs
import {
  VideoDecoder,
  AudioDecoder,
  VideoEncoder,
  AudioEncoder,
  VideoFrame,
  AudioData,
  EncodedVideoChunk,
  EncodedAudioChunk,
  VideoColorSpace,
  ImageDecoder
} from 'node-webcodecs';

Object.assign(globalThis, {
  VideoDecoder,
  AudioDecoder,
  VideoEncoder,
  AudioEncoder,
  VideoFrame,
  AudioData,
  EncodedVideoChunk,
  EncodedAudioChunk,
  VideoColorSpace,
  ImageDecoder
});

export function polyfillWebCodecsApi() {}
POLYFILL
      ;;
    webcodecs-polyfill)
      cat <<'POLYFILL'
// Configured by run-harness.sh for: webcodecs-polyfill
import 'webcodecs-polyfill';
export function polyfillWebCodecsApi() {}
POLYFILL
      ;;
    node-libav-webcodecs)
      cat <<'POLYFILL'
// Configured by run-harness.sh for: node-libav-webcodecs
import { init } from 'node-libav-webcodecs/polyfill';
export async function polyfillWebCodecsApi() {
  await init();
}
POLYFILL
      ;;
    webcodecs-node)
      cat <<'POLYFILL'
// Configured by run-harness.sh for: webcodecs-node
import { polyfill } from 'webcodecs-node';
export function polyfillWebCodecsApi() {
  polyfill();
}
POLYFILL
      ;;
    *)
      echo "Unknown implementation: $IMPLEMENTATION" >&2
      return 1
      ;;
  esac
}

# Configure polyfill.js for the selected implementation
configure_polyfill() {
  print_step 3 6 "Configuring Polyfill"

  local polyfill_file="$OUTPUT_DIR/src/polyfill.js"

  if [[ "$DRY_RUN" == true ]]; then
    echo "  [DRY RUN] Would configure $polyfill_file for $IMPLEMENTATION"
    return 0
  fi

  # Backup original
  if [[ ! -f "${polyfill_file}.original" ]]; then
    cp "$polyfill_file" "${polyfill_file}.original"
  fi

  # Generate new polyfill
  generate_polyfill_code > "$polyfill_file"

  print_ok "Configured src/polyfill.js for $IMPLEMENTATION"
}
```

**Step 4: Run tests** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: PASS

**Step 5: Commit** (30 sec)

```bash
git add scripts/run-harness.sh tests/run-harness.bats
git commit -m "feat(harness): add repo cloning and polyfill configuration"
```

---

### Task 6: Add npm Install and Test Execution

**Files:**
- Modify: `scripts/run-harness.sh`
- Test: `tests/run-harness.bats`

**Step 1: Write npm and test execution tests** (3 min)

```bash
# Append to tests/run-harness.bats

@test "npm_install respects dry-run" {
  DRY_RUN=true
  OUTPUT_DIR="$BATS_TEST_TMPDIR/test-harness"
  source "$SCRIPT"
  setup_colors
  run npm_install
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "Would run npm install"
}

@test "run_tests respects dry-run" {
  DRY_RUN=true
  OUTPUT_DIR="$BATS_TEST_TMPDIR/test-harness"
  source "$SCRIPT"
  setup_colors
  run run_tests
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "Would run npm test"
}
```

**Step 2: Run tests** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: FAIL

**Step 3: Add npm and test functions** (5 min)

```bash
# Run npm install
npm_install() {
  print_step 4 6 "Installing npm Packages"

  if [[ "$DRY_RUN" == true ]]; then
    echo "  [DRY RUN] Would run npm install in $OUTPUT_DIR"
    return 0
  fi

  start_spinner "Installing npm packages"

  local npm_output
  local start_time
  start_time=$(date +%s)

  if npm_output=$(cd "$OUTPUT_DIR" && npm install 2>&1); then
    local elapsed=$(($(date +%s) - start_time))
    stop_spinner true "npm install completed (${elapsed}s)"
  else
    stop_spinner false "npm install failed"
    if [[ "$VERBOSE" == true ]]; then
      echo "$npm_output"
    fi
    return 1
  fi
}

# Run the tests
run_tests() {
  print_step 5 6 "Running Tests"

  if [[ "$DRY_RUN" == true ]]; then
    echo "  [DRY RUN] Would run npm test in $OUTPUT_DIR"
    return 0
  fi

  start_spinner "Running vitest"

  local test_output
  local start_time
  local json_output="$OUTPUT_DIR/vitest-results.json"
  start_time=$(date +%s)

  # Run vitest with JSON reporter
  if test_output=$(cd "$OUTPUT_DIR" && npm test -- --reporter=json --outputFile="$json_output" 2>&1); then
    TEST_EXIT_CODE=0
  else
    TEST_EXIT_CODE=$?
  fi

  local elapsed=$(($(date +%s) - start_time))
  TEST_DURATION=$elapsed

  stop_spinner true "Tests completed (${elapsed}s)"

  # Parse results
  if [[ -f "$json_output" ]]; then
    parse_test_results "$json_output"
  else
    # Fallback: parse text output
    parse_text_results "$test_output"
  fi

  # Display results table
  display_test_results

  export TEST_EXIT_CODE TEST_DURATION
}

# Parse JSON test results from vitest
parse_test_results() {
  local json_file="$1"

  if check_command jq; then
    TESTS_TOTAL=$(jq '.numTotalTests // 0' "$json_file")
    TESTS_PASSED=$(jq '.numPassedTests // 0' "$json_file")
    TESTS_FAILED=$(jq '.numFailedTests // 0' "$json_file")
    TESTS_SKIPPED=$(jq '.numPendingTests // 0' "$json_file")
  else
    # Fallback: basic grep parsing
    TESTS_TOTAL=$(grep -o '"numTotalTests":[0-9]*' "$json_file" | cut -d: -f2 || echo 0)
    TESTS_PASSED=$(grep -o '"numPassedTests":[0-9]*' "$json_file" | cut -d: -f2 || echo 0)
    TESTS_FAILED=$(grep -o '"numFailedTests":[0-9]*' "$json_file" | cut -d: -f2 || echo 0)
    TESTS_SKIPPED=$(grep -o '"numPendingTests":[0-9]*' "$json_file" | cut -d: -f2 || echo 0)
  fi

  export TESTS_TOTAL TESTS_PASSED TESTS_FAILED TESTS_SKIPPED
}

# Fallback parser for text output
parse_text_results() {
  local output="$1"

  # Parse vitest output format
  TESTS_PASSED=$(echo "$output" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' || echo 0)
  TESTS_FAILED=$(echo "$output" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' || echo 0)
  TESTS_SKIPPED=$(echo "$output" | grep -oE '[0-9]+ skipped' | grep -oE '[0-9]+' || echo 0)
  TESTS_TOTAL=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))

  export TESTS_TOTAL TESTS_PASSED TESTS_FAILED TESTS_SKIPPED
}

# Display results in a nice table
display_test_results() {
  [[ "$QUIET" == true ]] && return

  echo ""
  echo -e "  ${BOLD}Test Results:${RESET}"
  echo -e "  ┌─────────────────────────────────────┬────────┐"
  echo -e "  │ Metric                              │ Value  │"
  echo -e "  ├─────────────────────────────────────┼────────┤"
  printf "  │ %-35s │ ${GREEN}%6s${RESET} │\n" "Passed" "$TESTS_PASSED"
  printf "  │ %-35s │ ${RED}%6s${RESET} │\n" "Failed" "$TESTS_FAILED"
  printf "  │ %-35s │ ${YELLOW}%6s${RESET} │\n" "Skipped" "$TESTS_SKIPPED"
  printf "  │ %-35s │ %6s │\n" "Total" "$TESTS_TOTAL"
  echo -e "  └─────────────────────────────────────┴────────┘"
}
```

**Step 4: Run tests** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: PASS

**Step 5: Commit** (30 sec)

```bash
git add scripts/run-harness.sh tests/run-harness.bats
git commit -m "feat(harness): add npm install and test execution"
```

---

### Task 7: Add JSON Report Generation

**Files:**
- Modify: `scripts/run-harness.sh`
- Test: `tests/run-harness.bats`

**Step 1: Write JSON generation tests** (3 min)

```bash
# Append to tests/run-harness.bats

@test "generate_json_report produces valid JSON" {
  source "$SCRIPT"
  setup_colors
  detect_platform

  # Set mock values
  IMPLEMENTATION="node-webcodecs"
  HARNESS_COMMIT="abc1234"
  TESTS_TOTAL=10
  TESTS_PASSED=8
  TESTS_FAILED=2
  TESTS_SKIPPED=0
  TEST_DURATION=30

  output=$(generate_json_report)

  # Validate JSON
  echo "$output" | python3 -m json.tool >/dev/null 2>&1 || \
  echo "$output" | jq . >/dev/null 2>&1
}
```

**Step 2: Run tests** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: FAIL

**Step 3: Add JSON generation** (5 min)

```bash
# Generate JSON report
generate_json_report() {
  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  local pass_rate
  if [[ ${TESTS_TOTAL:-0} -gt 0 ]]; then
    pass_rate=$(echo "scale=2; ${TESTS_PASSED:-0} * 100 / ${TESTS_TOTAL}" | bc)
  else
    pass_rate="0.00"
  fi

  cat <<EOF
{
  "meta": {
    "version": "$VERSION",
    "timestamp": "$timestamp",
    "implementation": "$IMPLEMENTATION",
    "harness_version": "1.0.0",
    "harness_commit": "${HARNESS_COMMIT:-unknown}"
  },
  "environment": {
    "os": "$OS",
    "arch": "$ARCH",
    "node_version": "$(get_version node)",
    "npm_version": "$(get_version npm)",
    "ffmpeg_version": "$(get_version ffmpeg)"
  },
  "summary": {
    "total": ${TESTS_TOTAL:-0},
    "passed": ${TESTS_PASSED:-0},
    "failed": ${TESTS_FAILED:-0},
    "skipped": ${TESTS_SKIPPED:-0},
    "duration_ms": $((${TEST_DURATION:-0} * 1000)),
    "pass_rate": $pass_rate
  }
}
EOF
}

# Save reports
save_reports() {
  print_step 6 6 "Generating Report"

  if [[ "$DRY_RUN" == true ]]; then
    echo "  [DRY RUN] Would generate reports in $OUTPUT_DIR"
    return 0
  fi

  local json_report="$OUTPUT_DIR/results.json"

  generate_json_report > "$json_report"
  print_ok "JSON report: $json_report"

  if [[ "$JSON_ONLY" == true ]]; then
    cat "$json_report"
  fi
}

# Print final summary
print_summary() {
  [[ "$JSON_ONLY" == true ]] && return

  local pass_rate
  if [[ ${TESTS_TOTAL:-0} -gt 0 ]]; then
    pass_rate=$(echo "scale=1; ${TESTS_PASSED:-0} * 100 / ${TESTS_TOTAL}" | bc)
  else
    pass_rate="0.0"
  fi

  echo ""
  echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
  echo -e "${BOLD}                         RESULTS SUMMARY${RESET}"
  echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
  echo ""
  print_info "Implementation" "$IMPLEMENTATION"
  print_info "Harness Commit" "${HARNESS_COMMIT:-unknown}"
  echo ""

  if [[ ${TESTS_FAILED:-0} -eq 0 ]]; then
    echo -e "  ${GREEN}${BOLD}Tests Passed:${RESET}      ${TESTS_PASSED:-0}/${TESTS_TOTAL:-0} (${pass_rate}%)"
  else
    echo -e "  ${RED}${BOLD}Tests Passed:${RESET}      ${TESTS_PASSED:-0}/${TESTS_TOTAL:-0} (${pass_rate}%)"
    echo -e "  ${RED}Tests Failed:${RESET}      ${TESTS_FAILED:-0}"
  fi

  if [[ ${TESTS_SKIPPED:-0} -gt 0 ]]; then
    echo -e "  ${YELLOW}Tests Skipped:${RESET}     ${TESTS_SKIPPED}"
  fi

  echo ""
  print_info "Duration" "${TEST_DURATION:-0}s"
  print_info "Report" "$OUTPUT_DIR/results.json"
  echo ""
  echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
  echo ""
}
```

**Step 4: Run tests** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: PASS

**Step 5: Commit** (30 sec)

```bash
git add scripts/run-harness.sh tests/run-harness.bats
git commit -m "feat(harness): add JSON report generation and summary"
```

---

### Task 8: Add Signal Handling and Cleanup

**Files:**
- Modify: `scripts/run-harness.sh`
- Test: `tests/run-harness.bats`

**Step 1: Write signal handling tests** (2 min)

```bash
# Append to tests/run-harness.bats

@test "cleanup function exists" {
  source "$SCRIPT"
  declare -f cleanup >/dev/null
}

@test "trap is set for EXIT" {
  source "$SCRIPT"
  trap -p EXIT | grep -q cleanup
}
```

**Step 2: Run tests** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: FAIL

**Step 3: Add signal handling** (3 min)

Add near the top of the script, after variable declarations:

```bash
# Cleanup function
cleanup() {
  local exit_code=$?

  # Stop any running spinner
  if [[ -n "${SPINNER_PID:-}" ]]; then
    kill "$SPINNER_PID" 2>/dev/null || true
    wait "$SPINNER_PID" 2>/dev/null || true
  fi

  # Cleanup if requested
  if [[ "$CLEANUP" == true ]] && [[ -d "${OUTPUT_DIR:-}" ]]; then
    rm -rf "$OUTPUT_DIR"
  fi

  # Show cursor if it was hidden
  tput cnorm 2>/dev/null || true

  exit $exit_code
}

# Set up signal handlers
trap cleanup EXIT
trap 'echo ""; echo "Interrupted by user"; exit 130' INT TERM
```

**Step 4: Run tests** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: PASS

**Step 5: Commit** (30 sec)

```bash
git add scripts/run-harness.sh tests/run-harness.bats
git commit -m "feat(harness): add signal handling and cleanup"
```

---

### Task 9: Integrate Main Function and User Confirmation

**Files:**
- Modify: `scripts/run-harness.sh`
- Test: `tests/run-harness.bats`

**Step 1: Write integration tests** (3 min)

```bash
# Append to tests/run-harness.bats

@test "main function runs all steps in dry-run" {
  run "$SCRIPT" --dry-run --yes
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "Would"
}

@test "--yes skips confirmation prompt" {
  run timeout 5 "$SCRIPT" --dry-run --yes
  [ "$status" -eq 0 ]
}
```

**Step 2: Run tests** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: May PASS (depends on current main())

**Step 3: Complete the main function** (5 min)

```bash
# User confirmation prompt
confirm_execution() {
  if [[ "$YES" == true ]]; then
    return 0
  fi

  [[ "$QUIET" == true ]] && return 0

  echo ""
  echo -e "${YELLOW}This script will:${RESET}"
  echo "  1. Install ffmpeg and pkg-config if missing"
  echo "  2. Clone vjeux/webcodecs-harness to $OUTPUT_DIR"
  echo "  3. Configure it for $IMPLEMENTATION"
  echo "  4. Run npm install and npm test"
  echo "  5. Generate JSON report"
  echo ""

  read -p "Continue? [Y/n] " -n 1 -r
  echo ""

  if [[ ! $REPLY =~ ^[Yy]?$ ]]; then
    echo "Aborted."
    exit 0
  fi
}

# Main entry point
main() {
  parse_args "$@"
  setup_colors

  # Handle dry-run early display
  if [[ "$DRY_RUN" == true ]]; then
    print_header
    print_system_info
    preflight_checks
    confirm_execution
    install_dependencies
    clone_harness
    configure_polyfill
    npm_install
    run_tests
    save_reports
    print_summary
    exit 0
  fi

  # Normal execution
  print_header
  print_system_info
  preflight_checks
  confirm_execution
  install_dependencies
  clone_harness
  configure_polyfill
  npm_install
  run_tests
  save_reports
  print_summary

  # Exit with test result
  exit "${TEST_EXIT_CODE:-0}"
}

main "$@"
```

**Step 4: Run tests** (30 sec)

```bash
bats tests/run-harness.bats
```

Expected: PASS

**Step 5: Commit** (30 sec)

```bash
git add scripts/run-harness.sh tests/run-harness.bats
git commit -m "feat(harness): complete main function with user confirmation"
```

---

### Task 10: Final Polish and Documentation

**Files:**
- Modify: `scripts/run-harness.sh`
- Create: `docs/run-harness-usage.md`

**Step 1: Add comprehensive header documentation** (3 min)

Add at top of script after shebang:

```bash
#!/usr/bin/env bash
#
# run-harness.sh - WebCodecs Harness Test Runner
#
# Run the vjeux/webcodecs-harness test suite against a WebCodecs implementation.
#
# Usage:
#   curl -fsSL https://example.com/run-harness.sh | bash
#   curl -fsSL ... | bash -s -- --implementation node-webcodecs
#   ./run-harness.sh [OPTIONS]
#
# Options:
#   -h, --help              Show help message
#   -V, --version           Show version
#   -i, --implementation    Implementation to test (default: node-webcodecs)
#   -o, --output DIR        Output directory (default: ~/.webcodecs-harness-test)
#   -n, --dry-run           Show what would be done
#   -v, --verbose           Verbose output
#   -q, --quiet             Minimal output
#   -y, --yes               Skip confirmations
#   --no-color              Disable colors
#   --cleanup               Remove test dir after
#   --json-only             Only output JSON
#
# Supported implementations:
#   - node-webcodecs (default)
#   - webcodecs-polyfill
#   - node-libav-webcodecs
#   - webcodecs-node
#
# Exit codes:
#   0   All tests passed
#   1   Some tests failed or error occurred
#   130 Interrupted by user (Ctrl+C)
#
# Requirements:
#   - bash 4+
#   - curl or wget
#   - git
#   - Node.js 18+ (will attempt to install)
#   - ffmpeg (will attempt to install)
#   - pkg-config (will attempt to install)
#
# For the WebCodecs Node.js 10k Challenge
# https://github.com/nickstenning/webcodecs-nodejs-10k-challenge
#
```

**Step 2: Run full test suite** (30 sec)

```bash
bats tests/run-harness.bats
shellcheck scripts/run-harness.sh
```

Expected: All PASS

**Step 3: Commit final polish** (30 sec)

```bash
git add scripts/run-harness.sh
git commit -m "docs(harness): add comprehensive script documentation"
```

---

### Task 11: Code Review

Run code-reviewer agent to ensure quality.

---

## Parallel Task Groups

| Group | Tasks | Rationale |
|-------|-------|-----------|
| Group 1 | 1, 2 | Core skeleton and UI, no overlap |
| Group 2 | 3, 4 | Platform detection and installation, sequential dependency |
| Group 3 | 5, 6 | Clone/config and test execution, sequential |
| Group 4 | 7, 8 | Reporting and cleanup, independent |
| Group 5 | 9, 10 | Integration and polish |
| Group 6 | 11 | Code review |

---

## Verification Checklist

- [ ] `curl -fsSL <url> | bash` works
- [ ] `--help` shows all options
- [ ] `--dry-run` shows all steps without executing
- [ ] `--yes` skips prompts for CI
- [ ] `--json-only` outputs only JSON
- [ ] macOS with Homebrew works
- [ ] Linux with apt works
- [ ] Ctrl+C cleanly exits
- [ ] JSON report is valid
- [ ] All tests pass with `bats tests/run-harness.bats`
- [ ] shellcheck passes
