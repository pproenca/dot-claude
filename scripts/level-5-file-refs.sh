#!/usr/bin/env bash
# Level 5: File References Validation
# Validates @file syntax and ${CLAUDE_PLUGIN_ROOT} references

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

MARKETPLACE_ROOT=$(get_marketplace_root)

echo "=== Level 5: File References Validation ==="

# ============================================================================
# ${CLAUDE_PLUGIN_ROOT} References
# ============================================================================

section "CLAUDE_PLUGIN_ROOT References"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")
  refs_checked=0

  # Find all ${CLAUDE_PLUGIN_ROOT} references in markdown files
  # shellcheck disable=SC2016
  while IFS= read -r line; do
    file=$(echo "$line" | cut -d: -f1)
    relative_file="${file#"$plugin_dir"}"

    # Extract the path after ${CLAUDE_PLUGIN_ROOT}
    # Handle patterns like ${CLAUDE_PLUGIN_ROOT}/references/file.md
    # Note: Exclude quotes, backticks, spaces, and backslashes from path
    # shellcheck disable=SC2016
    ref_path=$(echo "$line" | grep -oE '\$\{CLAUDE_PLUGIN_ROOT\}/[^"'\''` \\]+' | head -1 | sed 's/\${CLAUDE_PLUGIN_ROOT}\///')

    if [[ -n "$ref_path" ]]; then
      # Remove trailing punctuation/escapes that might be captured
      # shellcheck disable=SC2001
      ref_path=$(echo "$ref_path" | sed 's/[)}\]>\\]$//')

      # Resolve to actual path
      resolved_path="$plugin_dir$ref_path"

      if [[ -e "$resolved_path" ]]; then
        refs_checked=$((refs_checked + 1))
      else
        err "$plugin_name/$relative_file: \${CLAUDE_PLUGIN_ROOT}/$ref_path not found"
      fi
    fi
  done < <(grep -rn '\${CLAUDE_PLUGIN_ROOT}' "$plugin_dir" --include="*.md" 2>/dev/null || true)

  if [[ $refs_checked -gt 0 ]]; then
    ok "$plugin_name: $refs_checked CLAUDE_PLUGIN_ROOT references validated"
  else
    info "$plugin_name: no CLAUDE_PLUGIN_ROOT references found"
  fi
done

# ============================================================================
# References Directory Validation
# ============================================================================

section "References Directories"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  # Check top-level references/ directory
  if [[ -d "$plugin_dir/references" ]]; then
    refs_count=$(find "$plugin_dir/references" -name "*.md" -type f 2>/dev/null | wc -l | xargs)
    if [[ "$refs_count" -gt 0 ]]; then
      ok "$plugin_name/references/: $refs_count reference files"
    else
      warn "$plugin_name/references/: directory exists but no .md files"
    fi
  fi

  # Check skill-level references/ directories
  for skill_dir in "$plugin_dir"/skills/*/; do
    [[ -d "$skill_dir" ]] || continue
    skill_name=$(basename "$skill_dir")

    if [[ -d "$skill_dir/references" ]]; then
      refs_count=$(find "$skill_dir/references" -name "*.md" -type f 2>/dev/null | wc -l | xargs)
      if [[ "$refs_count" -gt 0 ]]; then
        ok "$plugin_name/skills/$skill_name/references/: $refs_count files"
      else
        warn "$plugin_name/skills/$skill_name/references/: exists but empty"
      fi
    fi
  done
done

# ============================================================================
# Hook Script References (from hooks.json)
# ============================================================================

section "Hook Script References"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")
  hooks_json="$plugin_dir/hooks/hooks.json"

  [[ -f "$hooks_json" ]] || continue

  if has_jq; then
    # Extract script paths from hooks.json
    # Format: "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/script.sh\""
    while IFS= read -r cmd; do
      [[ -z "$cmd" ]] && continue

      # Extract script path from command
      # shellcheck disable=SC2016
      script_ref=$(echo "$cmd" | grep -oE '\$\{CLAUDE_PLUGIN_ROOT\}/[^"]+' | head -1 | sed 's/\${CLAUDE_PLUGIN_ROOT}\///')

      if [[ -n "$script_ref" ]]; then
        resolved="$plugin_dir$script_ref"
        if [[ -f "$resolved" ]]; then
          if [[ -x "$resolved" ]]; then
            ok "$plugin_name: hooks.json → $script_ref (executable)"
          else
            err "$plugin_name: hooks.json → $script_ref (not executable)"
          fi
        else
          err "$plugin_name: hooks.json references missing script: $script_ref"
        fi
      fi
    done < <(jq -r '.. | .command? // empty' "$hooks_json" 2>/dev/null)
  else
    warn "$plugin_name: skipping hooks.json validation (jq not available)"
  fi
done

# ============================================================================
# @ Syntax File References (if used in commands)
# Note: @ syntax is used for including file content in command prompts
# This section is informational - @ refs typically resolve at runtime
# ============================================================================

section "@ Syntax References"
info "@ syntax validation is informational (refs resolve at Claude Code runtime)"

exit_with_summary
