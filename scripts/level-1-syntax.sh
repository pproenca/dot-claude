#!/usr/bin/env bash
# Level 1: Syntax & Structure Validation
# Validates plugin directory structure, file locations, and JSON/YAML syntax

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

MARKETPLACE_ROOT=$(get_marketplace_root)
MARKETPLACE_JSON="$MARKETPLACE_ROOT/.claude-plugin/marketplace.json"

echo "=== Level 1: Syntax & Structure Validation ==="

# ============================================================================
# Marketplace Structure
# ============================================================================

section "Marketplace Structure"

# Check marketplace.json exists
if [[ -f "$MARKETPLACE_JSON" ]]; then
  ok "marketplace.json exists"

  # Validate JSON syntax
  if validate_json "$MARKETPLACE_JSON"; then
    ok "marketplace.json: valid JSON"
  else
    err "marketplace.json: invalid JSON syntax"
  fi
else
  err "marketplace.json not found at $MARKETPLACE_JSON"
fi

# Check plugin directories exist
if [[ -d "$MARKETPLACE_ROOT/plugins" ]]; then
  ok "plugins/ directory exists"
else
  warn "plugins/ directory not found"
fi

if [[ -d "$MARKETPLACE_ROOT/domain_plugins" ]]; then
  ok "domain_plugins/ directory exists"
else
  warn "domain_plugins/ directory not found"
fi

# ============================================================================
# Plugin Directory Structure
# ============================================================================

section "Plugin Structure"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/ "$MARKETPLACE_ROOT"/domain_plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  # Check plugin.json exists
  plugin_json="$plugin_dir/.claude-plugin/plugin.json"
  if [[ -f "$plugin_json" ]]; then
    ok "$plugin_name: plugin.json exists"

    # Validate JSON syntax
    if validate_json "$plugin_json"; then
      ok "$plugin_name: plugin.json valid JSON"
    else
      err "$plugin_name: plugin.json invalid JSON syntax"
    fi
  else
    err "$plugin_name: missing .claude-plugin/plugin.json"
  fi

  # Check hooks.json if hooks directory exists
  if [[ -d "$plugin_dir/hooks" ]]; then
    hooks_json="$plugin_dir/hooks/hooks.json"
    if [[ -f "$hooks_json" ]]; then
      if validate_json "$hooks_json"; then
        ok "$plugin_name: hooks.json valid JSON"
      else
        err "$plugin_name: hooks.json invalid JSON syntax"
      fi
    else
      warn "$plugin_name: hooks/ directory exists but no hooks.json"
    fi
  fi
done

# ============================================================================
# Skills Structure
# ============================================================================

section "Skills Structure"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/ "$MARKETPLACE_ROOT"/domain_plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  # Check skills directory structure
  if [[ -d "$plugin_dir/skills" ]]; then
    for skill_dir in "$plugin_dir"/skills/*/; do
      [[ -d "$skill_dir" ]] || continue
      skill_name=$(basename "$skill_dir")

      # Skills must have SKILL.md
      skill_file="$skill_dir/SKILL.md"
      if [[ -f "$skill_file" ]]; then
        # Check for valid frontmatter
        if has_valid_frontmatter "$skill_file"; then
          ok "$plugin_name/skills/$skill_name: SKILL.md with valid frontmatter"
        else
          err "$plugin_name/skills/$skill_name: SKILL.md missing or invalid frontmatter"
        fi
      else
        err "$plugin_name/skills/$skill_name: missing SKILL.md"
      fi

      # Check naming convention (lowercase with hyphens)
      if [[ "$skill_name" =~ ^[a-z][a-z0-9-]*$ ]]; then
        : # ok, but don't print for every skill
      else
        warn "$plugin_name/skills/$skill_name: name should be lowercase with hyphens"
      fi
    done
  fi
done

# ============================================================================
# Commands Structure
# ============================================================================

section "Commands Structure"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/ "$MARKETPLACE_ROOT"/domain_plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  # Check commands directory structure
  if [[ -d "$plugin_dir/commands" ]]; then
    for cmd_file in "$plugin_dir"/commands/*.md; do
      [[ -f "$cmd_file" ]] || continue
      cmd_name=$(basename "$cmd_file" .md)

      # Check for valid frontmatter
      if has_valid_frontmatter "$cmd_file"; then
        ok "$plugin_name/commands/$cmd_name: valid frontmatter"
      else
        err "$plugin_name/commands/$cmd_name: missing or invalid frontmatter"
      fi

      # Check naming convention (lowercase with hyphens)
      if [[ "$cmd_name" =~ ^[a-z][a-z0-9-]*$ ]]; then
        : # ok
      else
        warn "$plugin_name/commands/$cmd_name: name should be lowercase with hyphens"
      fi
    done
  fi
done

# ============================================================================
# Agents Structure
# ============================================================================

section "Agents Structure"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/ "$MARKETPLACE_ROOT"/domain_plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  # Check agents directory structure
  if [[ -d "$plugin_dir/agents" ]]; then
    for agent_file in "$plugin_dir"/agents/*.md; do
      [[ -f "$agent_file" ]] || continue
      agent_name=$(basename "$agent_file" .md)

      # Check for valid frontmatter
      if has_valid_frontmatter "$agent_file"; then
        ok "$plugin_name/agents/$agent_name: valid frontmatter"
      else
        err "$plugin_name/agents/$agent_name: missing or invalid frontmatter"
      fi

      # Check naming convention (lowercase with hyphens)
      if [[ "$agent_name" =~ ^[a-z][a-z0-9-]*$ ]]; then
        : # ok
      else
        warn "$plugin_name/agents/$agent_name: name should be lowercase with hyphens"
      fi
    done
  fi
done

# ============================================================================
# Script Permissions
# ============================================================================

section "Script Permissions"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/ "$MARKETPLACE_ROOT"/domain_plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  # Check hook scripts are executable
  for script in "$plugin_dir"/hooks/*.sh "$plugin_dir"/scripts/*.sh; do
    [[ -f "$script" ]] || continue
    script_name=$(basename "$script")

    if [[ -x "$script" ]]; then
      ok "$plugin_name: $script_name executable"
    else
      err "$plugin_name: $script_name not executable (run: chmod +x)"
    fi
  done
done

# ============================================================================
# Marketplace Integrity
# ============================================================================

section "Marketplace Integrity"

if has_jq && [[ -f "$MARKETPLACE_JSON" ]]; then
  # Check all plugins in marketplace.json exist (using source paths)
  while IFS= read -r line; do
    plugin_name=$(echo "$line" | cut -d'|' -f1)
    plugin_source=$(echo "$line" | cut -d'|' -f2)
    plugin_path="$MARKETPLACE_ROOT/${plugin_source#./}"

    if [[ -d "$plugin_path" ]]; then
      ok "marketplace: $plugin_name directory exists"
    else
      err "marketplace: $plugin_name listed but directory not found at $plugin_source"
    fi
  done < <(jq -r '.plugins[] | "\(.name)|\(.source)"' "$MARKETPLACE_JSON")

  # Check for plugins not in marketplace
  for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/ "$MARKETPLACE_ROOT"/domain_plugins/*/; do
    [[ -d "$plugin_dir" ]] || continue
    plugin_name=$(get_plugin_name "$plugin_dir")

    if jq -e ".plugins[] | select(.name==\"$plugin_name\")" "$MARKETPLACE_JSON" &>/dev/null; then
      : # ok, in marketplace
    else
      warn "$plugin_name: exists but not listed in marketplace.json"
    fi
  done
else
  warn "Skipping marketplace integrity check (jq not available)"
fi

exit_with_summary
