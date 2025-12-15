#!/usr/bin/env bash
# Common functions for marketplace validation scripts
# Source this file at the start of each validation script

# Disable shellcheck warnings for:
# SC2034: Variables appear unused but are used by sourcing scripts
# shellcheck disable=SC2034

set -euo pipefail

# ============================================================================
# Global State
# ============================================================================

ERRORS=0
WARNINGS=0
SCRIPT_NAME="${SCRIPT_NAME:-$(basename "${BASH_SOURCE[1]}" .sh)}"

# ============================================================================
# Output Functions
# ============================================================================

err() {
  echo "[ERR] $1" >&2
  ERRORS=$((ERRORS + 1))
}

ok() {
  echo "[OK] $1"
}

warn() {
  echo "[WARN] $1"
  WARNINGS=$((WARNINGS + 1))
}

info() {
  echo "[INFO] $1"
}

section() {
  echo ""
  echo "--- $1 ---"
}

# ============================================================================
# Exit Functions
# ============================================================================

exit_with_summary() {
  echo ""
  if [[ $ERRORS -eq 0 ]]; then
    echo "=== Result: PASS ==="
  else
    echo "=== Result: FAIL ($ERRORS errors) ==="
  fi
  [[ $WARNINGS -gt 0 ]] && echo "Warnings: $WARNINGS"
  exit $ERRORS
}

# ============================================================================
# Frontmatter Functions
# ============================================================================

# Extract full frontmatter from a markdown file (between --- delimiters)
get_frontmatter() {
  local file="$1"
  sed -n '/^---$/,/^---$/p' "$file" 2>/dev/null | sed '1d;$d'
}

# Get a single frontmatter field value
# Usage: frontmatter_get <file> <key> [default]
# Note: For multi-line YAML values (|), returns "[multiline]" to indicate non-empty
frontmatter_get() {
  local file="$1"
  local key="$2"
  local default="${3:-}"
  local raw_value
  local value

  # Extract the raw line for the key
  raw_value=$(sed -n "/^---$/,/^---$/p" "$file" 2>/dev/null \
    | grep -E "^${key}:" | head -1 \
    | sed "s/^${key}:[[:space:]]*//")

  # Check if it's a multi-line YAML value (starts with |)
  if [[ "$raw_value" =~ ^[|]$ ]] || [[ "$raw_value" =~ ^[|][[:space:]]*$ ]]; then
    echo "[multiline]"
    return
  fi

  # Single-line value: clean up quotes
  value=$(echo "$raw_value" | sed 's/^["'\'']//' | sed 's/["'\'']$//')

  echo "${value:-$default}"
}

# Check if a frontmatter field exists (even if empty)
frontmatter_has() {
  local file="$1"
  local key="$2"
  grep -q "^${key}:" <(get_frontmatter "$file") 2>/dev/null
}

# Get tools list from frontmatter (handles both allowed-tools and tools)
get_tools_list() {
  local file="$1"
  local tools_line

  # Try allowed-tools first, then tools
  tools_line=$(grep -E "^(allowed-tools|tools):" "$file" 2>/dev/null | head -1 | sed 's/^[a-z-]*:[[:space:]]*//')

  if [[ -n "$tools_line" ]]; then
    # Normalize: handle both JSON array ["A", "B"] and comma-separated "A, B" formats
    echo "$tools_line" | sed 's/\[//g; s/\]//g; s/"//g; s/,/ /g'
  fi
}

# ============================================================================
# Tool Validation
# ============================================================================

# Source constants for VALID_BUILTIN_TOOLS
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/constants.sh"

# Check if a tool is valid
# Returns 0 if valid, 1 if invalid
is_valid_tool() {
  local tool="$1"
  tool=$(echo "$tool" | xargs)  # trim whitespace

  [[ -z "$tool" ]] && return 0  # empty is ok (will be caught elsewhere)

  # Check builtin tools
  for valid in "${VALID_BUILTIN_TOOLS[@]}"; do
    [[ "$tool" == "$valid" ]] && return 0
  done

  # Check MCP tools pattern (mcp__server__tool)
  [[ "$tool" =~ ^mcp__ ]] && return 0

  # Check Bash with restrictions pattern (Bash(cmd:*))
  [[ "$tool" =~ ^Bash\( ]] && return 0

  return 1
}

# Validate all tools in a space-separated list
# Returns list of invalid tools (empty if all valid)
validate_tools_list() {
  local tools_str="$1"
  local invalid_tools=""

  for tool in $tools_str; do
    tool=$(echo "$tool" | xargs)
    [[ -z "$tool" ]] && continue
    if ! is_valid_tool "$tool"; then
      invalid_tools+="$tool "
    fi
  done

  echo "$invalid_tools"
}

# ============================================================================
# File/Directory Functions
# ============================================================================

# Get the marketplace root directory (parent of scripts/)
get_marketplace_root() {
  cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd
}

# Check if a file has valid YAML frontmatter
has_valid_frontmatter() {
  local file="$1"
  local frontmatter

  # Must start with ---
  head -1 "$file" | grep -q "^---$" || return 1

  # Must have closing ---
  frontmatter=$(get_frontmatter "$file")
  [[ -n "$frontmatter" ]] || return 1

  return 0
}

# ============================================================================
# JSON Functions
# ============================================================================

# Check if jq is available
has_jq() {
  command -v jq &>/dev/null
}

# Validate JSON file syntax
# Returns 0 if valid or jq not available, 1 if invalid
validate_json() {
  local file="$1"

  if has_jq; then
    jq empty "$file" 2>/dev/null
  else
    return 0  # Can't validate without jq
  fi
}

# Get value from JSON file
# Usage: json_get <file> <jq_query>
json_get() {
  local file="$1"
  local query="$2"

  if has_jq; then
    jq -r "$query" "$file" 2>/dev/null
  else
    echo ""
  fi
}

# ============================================================================
# Plugin Functions
# ============================================================================

# Get list of plugin directories
get_plugin_dirs() {
  local root
  root=$(get_marketplace_root)

  for dir in "$root"/plugins/*/; do
    [[ -d "$dir" ]] && echo "$dir"
  done
}

# Get plugin name from directory path
get_plugin_name() {
  local dir="$1"
  basename "${dir%/}"
}

# Check if plugin has required structure
plugin_has_structure() {
  local plugin_dir="$1"
  [[ -f "$plugin_dir/.claude-plugin/plugin.json" ]]
}
