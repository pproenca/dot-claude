#!/usr/bin/env bash
# Level 4: Arguments Validation
# Validates command argument definitions and $ARGUMENTS placeholder usage

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

MARKETPLACE_ROOT=$(get_marketplace_root)

echo "=== Level 4: Arguments Validation ==="

# ============================================================================
# Command Arguments
# ============================================================================

section "Command Arguments"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/ "$MARKETPLACE_ROOT"/domain_plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  [[ -d "$plugin_dir/commands" ]] || continue

  for cmd_file in "$plugin_dir"/commands/*.md; do
    [[ -f "$cmd_file" ]] || continue
    cmd_name=$(basename "$cmd_file" .md)

    # Check if command has argument-hint
    has_arg_hint=$(frontmatter_has "$cmd_file" "argument-hint" && echo "yes" || echo "no")

    # Check if command body contains $ARGUMENTS
    has_arguments_var=false
    # shellcheck disable=SC2016
    if grep -q '\$ARGUMENTS' "$cmd_file" 2>/dev/null; then
      has_arguments_var=true
    fi

    # Check if command body contains $1, $2, etc.
    has_positional_args=false
    if grep -qE '\$[1-9]' "$cmd_file" 2>/dev/null; then
      has_positional_args=true
    fi

    # Validation rules:
    # 1. If has argument-hint, should use $ARGUMENTS or positional args
    # 2. If uses $ARGUMENTS without argument-hint, that's a warning

    if [[ "$has_arg_hint" == "yes" ]]; then
      if [[ "$has_arguments_var" == true ]] || [[ "$has_positional_args" == true ]]; then
        ok "$plugin_name/commands/$cmd_name: argument handling consistent"
      else
        warn "$plugin_name/commands/$cmd_name: has argument-hint but doesn't use \$ARGUMENTS or \$1..\$9"
      fi
    else
      if [[ "$has_arguments_var" == true ]] || [[ "$has_positional_args" == true ]]; then
        info "$plugin_name/commands/$cmd_name: uses arguments (consider adding argument-hint)"
      else
        ok "$plugin_name/commands/$cmd_name: no arguments (ok)"
      fi
    fi

    # Check for args: array structure (YAML array in frontmatter)
    if frontmatter_has "$cmd_file" "args"; then
      # Extract args section - this is complex YAML, just check it exists
      ok "$plugin_name/commands/$cmd_name: has args definition"
    fi
  done
done

# ============================================================================
# Agent Arguments (subagent parameters)
# ============================================================================

section "Agent Parameters"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/ "$MARKETPLACE_ROOT"/domain_plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  [[ -d "$plugin_dir/agents" ]] || continue

  for agent_file in "$plugin_dir"/agents/*.md; do
    [[ -f "$agent_file" ]] || continue
    agent_name=$(basename "$agent_file" .md)

    # Agents should have clear descriptions for Task tool dispatch
    desc=$(frontmatter_get "$agent_file" "description")
    if [[ "$desc" == "[multiline]" ]] || [[ ${#desc} -gt 20 ]]; then
      ok "$plugin_name/agents/$agent_name: has dispatch description"
    else
      warn "$plugin_name/agents/$agent_name: description too short for Task tool dispatch"
    fi
  done
done

exit_with_summary
