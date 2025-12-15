#!/usr/bin/env bash
# Level 7: Integration Testing
# Runs BATS tests and validates cross-plugin integration

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

MARKETPLACE_ROOT=$(get_marketplace_root)

echo "=== Level 7: Integration Testing ==="

# ============================================================================
# BATS Tests
# ============================================================================

section "BATS Tests"

if command -v bats &>/dev/null; then
  # Run marketplace-level tests if they exist
  if [[ -d "$MARKETPLACE_ROOT/tests" ]]; then
    info "Running marketplace tests..."
    if bats "$MARKETPLACE_ROOT/tests/" 2>&1; then
      ok "Marketplace BATS tests passed"
    else
      err "Marketplace BATS tests failed"
    fi
  fi

  # Run per-plugin tests
  for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/; do
    [[ -d "$plugin_dir" ]] || continue
    plugin_name=$(get_plugin_name "$plugin_dir")

    if [[ -d "$plugin_dir/tests" ]]; then
      info "Running $plugin_name tests..."
      if bats "$plugin_dir/tests/" 2>&1; then
        ok "$plugin_name: BATS tests passed"
      else
        err "$plugin_name: BATS tests failed"
      fi
    fi
  done
else
  warn "bats not installed - skipping BATS tests (install with: brew install bats-core)"
fi

# ============================================================================
# Per-Plugin Validation Scripts
# ============================================================================

section "Per-Plugin Validation"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  # Run plugin's own validate.sh if it exists
  if [[ -x "$plugin_dir/scripts/validate.sh" ]]; then
    info "Running $plugin_name/scripts/validate.sh..."
    if "$plugin_dir/scripts/validate.sh" 2>&1; then
      ok "$plugin_name: plugin validation passed"
    else
      err "$plugin_name: plugin validation failed"
    fi
  fi
done

# ============================================================================
# Cross-Plugin Reference Validation
# ============================================================================

section "Cross-Plugin References"

# Check for references between plugins (should be avoided or explicit)
for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  # Get list of other plugin names
  other_plugins=()
  for other_dir in "$MARKETPLACE_ROOT"/plugins/*/; do
    [[ -d "$other_dir" ]] || continue
    other_name=$(get_plugin_name "$other_dir")
    [[ "$other_name" != "$plugin_name" ]] && other_plugins+=("$other_name")
  done

  # Check for cross-plugin skill references
  for other in "${other_plugins[@]}"; do
    cross_refs=$(grep -rn "Skill(\"$other:" "$plugin_dir" --include="*.md" 2>/dev/null | wc -l | xargs)
    if [[ "$cross_refs" -gt 0 ]]; then
      info "$plugin_name references $other skills ($cross_refs refs)"
    fi
  done
done

ok "Cross-plugin reference check complete"

# ============================================================================
# Hook Timeout Validation
# ============================================================================

section "Hook Timeouts"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")
  hooks_json="$plugin_dir/hooks/hooks.json"

  [[ -f "$hooks_json" ]] || continue

  if has_jq; then
    # Check timeout values are reasonable (< 60 seconds)
    while IFS= read -r timeout; do
      [[ -z "$timeout" ]] && continue
      if [[ "$timeout" -gt 60000 ]]; then
        warn "$plugin_name: hook timeout ${timeout}ms exceeds 60 seconds"
      fi
    done < <(jq -r '.. | .timeout? // empty' "$hooks_json" 2>/dev/null)

    ok "$plugin_name: hook timeouts reasonable"
  fi
done

# ============================================================================
# MCP Tool Naming Convention
# ============================================================================

section "MCP Tool References"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  # Find mcp__ references and validate naming convention
  mcp_refs=$(grep -rhoE 'mcp__[a-zA-Z0-9_]+' "$plugin_dir" --include="*.md" 2>/dev/null | sort -u || true)

  if [[ -n "$mcp_refs" ]]; then
    while IFS= read -r ref; do
      # MCP tools should follow pattern: mcp__<server>__<tool>
      if [[ "$ref" =~ ^mcp__[a-zA-Z0-9_]+__[a-zA-Z0-9_]+$ ]]; then
        : # Valid pattern
      elif [[ "$ref" =~ ^mcp__[a-zA-Z0-9_]+$ ]]; then
        warn "$plugin_name: MCP ref '$ref' may be incomplete (expected mcp__<server>__<tool>)"
      fi
    done <<< "$mcp_refs"
    ok "$plugin_name: MCP tool references checked"
  fi
done

exit_with_summary
