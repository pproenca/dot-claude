#!/usr/bin/env bash
#
# Generate .claude-plugin/marketplace.json from plugins/ and domain_plugins/
#
# Usage: ./scripts/generate-marketplace.sh [--dry-run]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
MARKETPLACE_FILE="$ROOT_DIR/.claude-plugin/marketplace.json"

# Configuration (can be overridden via environment)
MARKETPLACE_NAME="${MARKETPLACE_NAME:-dot-claude}"
OWNER_NAME="${OWNER_NAME:-Pedro Proenca}"
OWNER_EMAIL="${OWNER_EMAIL:-pedro@pproenca.dev}"
MARKETPLACE_DESC="${MARKETPLACE_DESC:-Claude Code plugins for productivity workflows - skills, agents, commands, and hooks}"
MARKETPLACE_VERSION="${MARKETPLACE_VERSION:-1.0.0}"
MARKETPLACE_REPO="${MARKETPLACE_REPO:-https://github.com/pproenca/dot-claude}"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

# Collect plugins from a directory
collect_plugins() {
  local base_dir="$1"
  local relative_prefix="$2"
  local first=true

  for plugin_dir in "$ROOT_DIR/$base_dir"/*/; do
    [[ -d "$plugin_dir" ]] || continue

    local plugin_json="$plugin_dir/.claude-plugin/plugin.json"
    [[ -f "$plugin_json" ]] || continue

    local plugin_name
    plugin_name=$(jq -r '.name // empty' "$plugin_json")
    [[ -n "$plugin_name" ]] || continue

    local plugin_desc
    plugin_desc=$(jq -r '.description // empty' "$plugin_json")

    local dir_name
    dir_name=$(basename "$plugin_dir")

    if [[ "$first" != true ]]; then
      echo ","
    fi
    first=false

    # Build plugin entry
    echo -n "    {"
    echo -n "\"name\": \"$plugin_name\""
    echo -n ", \"source\": \"./$relative_prefix/$dir_name\""
    if [[ -n "$plugin_desc" ]]; then
      # Escape quotes in description
      plugin_desc=$(echo "$plugin_desc" | sed 's/"/\\"/g')
      echo -n ", \"description\": \"$plugin_desc\""
    fi
    echo -n "}"
  done
}

# Generate the marketplace JSON
generate_marketplace() {
  cat <<EOF
{
  "name": "$MARKETPLACE_NAME",
  "owner": {
    "name": "$OWNER_NAME",
    "email": "$OWNER_EMAIL"
  },
  "metadata": {
    "description": "$MARKETPLACE_DESC",
    "version": "$MARKETPLACE_VERSION"
  },
  "repository": "$MARKETPLACE_REPO",
  "plugins": [
EOF

  # Collect from plugins/ first, then domain_plugins/
  local has_plugins=false

  if [[ -d "$ROOT_DIR/plugins" ]]; then
    collect_plugins "plugins" "plugins"
    has_plugins=true
  fi

  if [[ -d "$ROOT_DIR/domain_plugins" ]]; then
    # Check if we already output plugins
    local domain_plugins_output
    domain_plugins_output=$(collect_plugins "domain_plugins" "domain_plugins")
    if [[ -n "$domain_plugins_output" ]]; then
      if [[ "$has_plugins" == true ]]; then
        echo ","
      fi
      echo -n "$domain_plugins_output"
    fi
  fi

  echo ""
  echo "  ]"
  echo "}"
}

# Main
main() {
  if ! command -v jq &>/dev/null; then
    echo "Error: jq is required but not installed" >&2
    exit 1
  fi

  local output
  output=$(generate_marketplace)

  # Pretty-print with jq
  output=$(echo "$output" | jq '.')

  if [[ "$DRY_RUN" == true ]]; then
    echo "$output"
  else
    mkdir -p "$(dirname "$MARKETPLACE_FILE")"
    echo "$output" > "$MARKETPLACE_FILE"
    echo "Generated: $MARKETPLACE_FILE"
  fi
}

main
