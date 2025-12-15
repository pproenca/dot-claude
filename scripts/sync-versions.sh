#!/usr/bin/env bash
# Sync versions between plugin.json and marketplace.json
# Usage: ./sync-versions.sh [--check|--fix]
#   --check: Report mismatches only (default, suitable for pre-commit)
#   --fix:   Update marketplace.json to match plugin.json versions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

MARKETPLACE_ROOT=$(get_marketplace_root)
MARKETPLACE_JSON="$MARKETPLACE_ROOT/.claude-plugin/marketplace.json"
MODE="${1:---check}"

echo "=== Version Sync $([[ "$MODE" == "--fix" ]] && echo "(Fix Mode)" || echo "(Check Mode)") ==="

# Require jq for this script
if ! has_jq; then
  err "jq is required for version sync. Install with: brew install jq"
  exit 1
fi

# Check marketplace.json exists
if [[ ! -f "$MARKETPLACE_JSON" ]]; then
  err "marketplace.json not found at $MARKETPLACE_JSON"
  exit 1
fi

section "Checking Plugin Versions"

# Get plugin names from marketplace.json
mapfile -t marketplace_plugins < <(jq -r '.plugins[].name' "$MARKETPLACE_JSON")

for plugin_name in "${marketplace_plugins[@]}"; do
  plugin_dir="$MARKETPLACE_ROOT/plugins/$plugin_name"
  plugin_json="$plugin_dir/.claude-plugin/plugin.json"

  # Check if plugin directory exists
  if [[ ! -d "$plugin_dir" ]]; then
    if [[ "$MODE" == "--fix" ]]; then
      # Remove orphaned plugin from marketplace.json
      jq --arg name "$plugin_name" 'del(.plugins[] | select(.name==$name))' \
        "$MARKETPLACE_JSON" > "$MARKETPLACE_JSON.tmp" \
        && mv "$MARKETPLACE_JSON.tmp" "$MARKETPLACE_JSON"
      ok "$plugin_name: removed orphaned entry from marketplace.json"
    else
      err "$plugin_name: orphaned in marketplace.json (plugin directory not found)"
    fi
    continue
  fi

  # Check if plugin.json exists
  if [[ ! -f "$plugin_json" ]]; then
    err "$plugin_name: missing .claude-plugin/plugin.json"
    continue
  fi

  # Get versions
  marketplace_version=$(jq -r ".plugins[] | select(.name==\"$plugin_name\") | .version" "$MARKETPLACE_JSON")
  plugin_version=$(jq -r '.version' "$plugin_json")

  if [[ "$marketplace_version" != "$plugin_version" ]]; then
    if [[ "$MODE" == "--fix" ]]; then
      # Update marketplace.json to match plugin.json (source of truth)
      jq --arg name "$plugin_name" --arg ver "$plugin_version" \
        '(.plugins[] | select(.name==$name) | .version) = $ver' \
        "$MARKETPLACE_JSON" > "$MARKETPLACE_JSON.tmp" \
        && mv "$MARKETPLACE_JSON.tmp" "$MARKETPLACE_JSON"
      ok "$plugin_name: synced version $marketplace_version -> $plugin_version"
    else
      err "$plugin_name: version mismatch (plugin.json=$plugin_version, marketplace.json=$marketplace_version)"
    fi
  else
    ok "$plugin_name: versions in sync ($plugin_version)"
  fi
done

section "Checking for Missing Plugins"

# Check if any plugin directories exist that aren't in marketplace.json
for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(basename "$plugin_dir")

  # Skip if plugin doesn't have proper structure
  if [[ ! -f "$plugin_dir/.claude-plugin/plugin.json" ]]; then
    warn "$plugin_name: has no plugin.json, skipping"
    continue
  fi

  # Check if in marketplace.json
  if ! jq -e ".plugins[] | select(.name==\"$plugin_name\")" "$MARKETPLACE_JSON" &>/dev/null; then
    warn "$plugin_name: exists in plugins/ but not in marketplace.json"
  fi
done

exit_with_summary
