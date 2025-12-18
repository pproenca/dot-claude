#!/usr/bin/env bash
# Level 2: Frontmatter Fields Validation
# Validates required fields, data types, and values in component frontmatter

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

MARKETPLACE_ROOT=$(get_marketplace_root)

echo "=== Level 2: Frontmatter Fields Validation ==="

# ============================================================================
# Skills Validation
# ============================================================================

section "Skills Frontmatter"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/ "$MARKETPLACE_ROOT"/domain_plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  [[ -d "$plugin_dir/skills" ]] || continue

  for skill_dir in "$plugin_dir"/skills/*/; do
    [[ -d "$skill_dir" ]] || continue
    skill_name=$(basename "$skill_dir")
    skill_file="$skill_dir/SKILL.md"

    [[ -f "$skill_file" ]] || continue

    # Check required fields
    for field in "${SKILL_REQUIRED_FIELDS[@]}"; do
      if frontmatter_has "$skill_file" "$field"; then
        value=$(frontmatter_get "$skill_file" "$field")
        if [[ -n "$value" ]]; then
          : # ok
        else
          err "$plugin_name/skills/$skill_name: '$field' is empty"
        fi
      else
        err "$plugin_name/skills/$skill_name: missing required field '$field'"
      fi
    done

    # Validate allowed-tools
    tools_str=$(get_tools_list "$skill_file")
    if [[ -n "$tools_str" ]]; then
      invalid=$(validate_tools_list "$tools_str")
      if [[ -n "$invalid" ]]; then
        err "$plugin_name/skills/$skill_name: invalid tools: $invalid"
      else
        ok "$plugin_name/skills/$skill_name: valid frontmatter"
      fi
    fi
  done
done

# ============================================================================
# Commands Validation
# ============================================================================

section "Commands Frontmatter"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/ "$MARKETPLACE_ROOT"/domain_plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  [[ -d "$plugin_dir/commands" ]] || continue

  for cmd_file in "$plugin_dir"/commands/*.md; do
    [[ -f "$cmd_file" ]] || continue
    cmd_name=$(basename "$cmd_file" .md)

    # Check required fields
    for field in "${COMMAND_REQUIRED_FIELDS[@]}"; do
      if frontmatter_has "$cmd_file" "$field"; then
        value=$(frontmatter_get "$cmd_file" "$field")
        if [[ -n "$value" ]]; then
          : # ok
        else
          err "$plugin_name/commands/$cmd_name: '$field' is empty"
        fi
      else
        err "$plugin_name/commands/$cmd_name: missing required field '$field'"
      fi
    done

    # Validate allowed-tools
    tools_str=$(get_tools_list "$cmd_file")
    if [[ -n "$tools_str" ]]; then
      invalid=$(validate_tools_list "$tools_str")
      if [[ -n "$invalid" ]]; then
        err "$plugin_name/commands/$cmd_name: invalid tools: $invalid"
      else
        ok "$plugin_name/commands/$cmd_name: valid frontmatter"
      fi
    fi

    # Check description length (warning only)
    desc=$(frontmatter_get "$cmd_file" "description")
    if [[ ${#desc} -gt $MAX_COMMAND_DESC_LENGTH ]]; then
      warn "$plugin_name/commands/$cmd_name: description exceeds $MAX_COMMAND_DESC_LENGTH chars (${#desc})"
    fi
  done
done

# ============================================================================
# Agents Validation
# ============================================================================

section "Agents Frontmatter"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/ "$MARKETPLACE_ROOT"/domain_plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  [[ -d "$plugin_dir/agents" ]] || continue

  for agent_file in "$plugin_dir"/agents/*.md; do
    [[ -f "$agent_file" ]] || continue
    agent_name=$(basename "$agent_file" .md)

    # Check required fields
    for field in "${AGENT_REQUIRED_FIELDS[@]}"; do
      if frontmatter_has "$agent_file" "$field"; then
        value=$(frontmatter_get "$agent_file" "$field")
        if [[ -n "$value" ]]; then
          : # ok
        else
          err "$plugin_name/agents/$agent_name: '$field' is empty"
        fi
      else
        err "$plugin_name/agents/$agent_name: missing required field '$field'"
      fi
    done

    # Check that at least one of tools/allowed-tools is present
    has_tools=false
    for tools_field in "${AGENT_TOOLS_FIELDS[@]}"; do
      if frontmatter_has "$agent_file" "$tools_field"; then
        has_tools=true
        break
      fi
    done

    if [[ "$has_tools" == false ]]; then
      err "$plugin_name/agents/$agent_name: missing 'tools' or 'allowed-tools' field"
    fi

    # Validate tools/allowed-tools
    tools_str=$(get_tools_list "$agent_file")
    if [[ -n "$tools_str" ]]; then
      invalid=$(validate_tools_list "$tools_str")
      if [[ -n "$invalid" ]]; then
        err "$plugin_name/agents/$agent_name: invalid tools: $invalid"
      fi
    fi

    # Validate model if present
    if frontmatter_has "$agent_file" "model"; then
      model=$(frontmatter_get "$agent_file" "model")
      valid_model=false
      for valid in "${VALID_MODELS[@]}"; do
        [[ "$model" == "$valid" ]] && valid_model=true && break
      done

      if [[ "$valid_model" == false ]]; then
        err "$plugin_name/agents/$agent_name: invalid model '$model' (valid: ${VALID_MODELS[*]})"
      fi
    fi

    # Validate color if present
    if frontmatter_has "$agent_file" "color"; then
      color=$(frontmatter_get "$agent_file" "color")
      valid_color=false
      for valid in "${VALID_COLORS[@]}"; do
        [[ "$color" == "$valid" ]] && valid_color=true && break
      done

      if [[ "$valid_color" == false ]]; then
        warn "$plugin_name/agents/$agent_name: unknown color '$color'"
      fi
    fi

    ok "$plugin_name/agents/$agent_name: valid frontmatter"
  done
done

# ============================================================================
# Plugin JSON Validation
# ============================================================================

section "Plugin JSON Fields"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/ "$MARKETPLACE_ROOT"/domain_plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")
  plugin_json="$plugin_dir/.claude-plugin/plugin.json"

  [[ -f "$plugin_json" ]] || continue

  if has_jq; then
    # Check required fields
    for field in "${PLUGIN_JSON_REQUIRED[@]}"; do
      value=$(jq -r ".$field // empty" "$plugin_json" 2>/dev/null)
      if [[ -n "$value" ]]; then
        : # ok
      else
        err "$plugin_name: plugin.json missing or empty '$field'"
      fi
    done

    ok "$plugin_name: plugin.json valid"
  else
    warn "$plugin_name: skipping plugin.json validation (jq not available)"
  fi
done

# ============================================================================
# Note: Plugin prefix validation (Skill() and subagent_type references) is
# handled by per-plugin scripts like validate-prefixes.sh. This avoids
# duplication and keeps Level 2 focused on frontmatter field validation.
# ============================================================================

exit_with_summary
