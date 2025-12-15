#!/usr/bin/env bash
# Level 6: Bash Syntax Validation
# Validates bash syntax in commands (!` blocks and ```bash fenced blocks)
# Adapted from plugins/dev-workflow/scripts/validate-bash-in-commands.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

MARKETPLACE_ROOT=$(get_marketplace_root)

echo "=== Level 6: Bash Syntax Validation ==="

# ============================================================================
# Bash Blocks in Commands
# ============================================================================

section "Command Bash Blocks"

TOTAL_BLOCKS=0

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  [[ -d "$plugin_dir/commands" ]] || continue

  for cmd_file in "$plugin_dir"/commands/*.md; do
    [[ -f "$cmd_file" ]] || continue
    cmd_name=$(basename "$cmd_file" .md)

    # Create temp file for bash extraction
    tmpfile=$(mktemp)
    # shellcheck disable=SC2064
    trap "rm -f '$tmpfile'" RETURN

    block_count=0
    block_errors=0

    # Extract and validate inline bash blocks (!`...`)
    # shellcheck disable=SC2016
    while IFS= read -r line_content; do
      block_count=$((block_count + 1))
      echo "$line_content" > "$tmpfile"
      if ! bash -n "$tmpfile" 2>/dev/null; then
        err "$plugin_name/commands/$cmd_name: inline bash block #$block_count syntax error"
        echo "    Content: ${line_content:0:60}..."
        block_errors=$((block_errors + 1))
      fi
    done < <(grep -oE '!\`[^\`]+\`' "$cmd_file" 2>/dev/null | sed 's/^!\`//;s/\`$//' || true)

    # Extract and validate ```bash fenced blocks
    in_block=false
    block_content=""
    block_start_line=0
    line_num=0

    while IFS= read -r line; do
      line_num=$((line_num + 1))

      if [[ "$line" =~ ^\`\`\`bash ]]; then
        in_block=true
        block_content=""
        block_start_line=$line_num
        continue
      fi

      if [[ "$line" =~ ^\`\`\` ]] && [[ "$in_block" == true ]]; then
        in_block=false
        block_count=$((block_count + 1))

        # Skip empty blocks
        if [[ -z "${block_content// }" ]]; then
          continue
        fi

        echo "$block_content" > "$tmpfile"
        if ! bash -n "$tmpfile" 2>/dev/null; then
          err "$plugin_name/commands/$cmd_name: bash block at line $block_start_line syntax error"
          first_line=$(echo "$block_content" | head -1)
          echo "    First line: ${first_line:0:60}"
          block_errors=$((block_errors + 1))
        fi
        continue
      fi

      if [[ "$in_block" == true ]]; then
        block_content+="$line"$'\n'
      fi
    done < "$cmd_file"

    TOTAL_BLOCKS=$((TOTAL_BLOCKS + block_count))

    if [[ $block_errors -eq 0 ]]; then
      if [[ $block_count -gt 0 ]]; then
        ok "$plugin_name/commands/$cmd_name: $block_count bash blocks valid"
      fi
    fi

    rm -f "$tmpfile"
  done
done

# ============================================================================
# Shell Scripts Validation
# ============================================================================

section "Shell Scripts"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")

  # Check all .sh files in hooks/ and scripts/
  for script in "$plugin_dir"/hooks/*.sh "$plugin_dir"/scripts/*.sh; do
    [[ -f "$script" ]] || continue
    script_name=$(basename "$script")
    relative_path="${script#"$plugin_dir"}"

    # Bash syntax check
    if bash -n "$script" 2>/dev/null; then
      # Shellcheck if available
      if command -v shellcheck &>/dev/null; then
        if shellcheck -x "$script" >/dev/null 2>&1; then
          ok "$plugin_name/$relative_path: syntax + shellcheck pass"
        else
          warn "$plugin_name/$relative_path: shellcheck warnings (run: shellcheck -x $script)"
        fi
      else
        ok "$plugin_name/$relative_path: syntax valid"
      fi
    else
      err "$plugin_name/$relative_path: bash syntax error"
    fi
  done
done

# ============================================================================
# Hook Script Existence (from hooks.json)
# ============================================================================

section "Hook Script Existence"

for plugin_dir in "$MARKETPLACE_ROOT"/plugins/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name=$(get_plugin_name "$plugin_dir")
  hooks_json="$plugin_dir/hooks/hooks.json"

  [[ -f "$hooks_json" ]] || continue

  if has_jq; then
    # Get all unique script paths referenced
    while IFS= read -r cmd; do
      [[ -z "$cmd" ]] && continue

      # Look for bash script invocations
      if [[ "$cmd" =~ hooks/.*\.sh ]]; then
        script_name=$(echo "$cmd" | grep -oE 'hooks/[a-zA-Z0-9_-]+\.sh' | head -1)
        if [[ -n "$script_name" ]]; then
          resolved="$plugin_dir$script_name"
          if [[ -f "$resolved" ]]; then
            if [[ -x "$resolved" ]]; then
              ok "$plugin_name: $script_name exists and executable"
            else
              err "$plugin_name: $script_name exists but not executable"
            fi
          else
            err "$plugin_name: $script_name referenced in hooks.json but not found"
          fi
        fi
      fi
    done < <(jq -r '.. | .command? // empty' "$hooks_json" 2>/dev/null | sort -u)
  fi
done

info "Total bash blocks checked: $TOTAL_BLOCKS"

exit_with_summary
