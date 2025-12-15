#!/bin/bash
# Check if cclsp is configured and inject appropriate guidance
# This runs at session start

config_exists=false

# Check if config exists
if [ -n "$CCLSP_CONFIG_PATH" ] && [ -f "$CCLSP_CONFIG_PATH" ]; then
  config_exists=true
elif [ -f "$HOME/.config/claude/cclsp.json" ]; then
  config_exists=true
fi

if [ "$config_exists" = true ]; then
  # cclsp IS configured - inject usage guidance
  cat << 'EOF'
<cclsp-guidance>
## LSP Code Navigation (cclsp configured)

**Prefer cclsp tools for symbol operations:**

| Task | Tool | Fallback |
|------|------|----------|
| Find definition | `mcp__cclsp__find_definition` | Grep |
| Find all usages | `mcp__cclsp__find_references` | Grep |
| Rename symbol | `mcp__cclsp__rename_symbol` | Manual Edit |
| Check for errors | `mcp__cclsp__get_diagnostics` | Run compiler |

**When to use which:**
- LSP tools: Known symbol names, precise navigation, refactoring
- Grep/Glob: Pattern search, regex, exploring unknown code, text in strings/comments

**Proactive usage:**
- Run `get_diagnostics` on files after editing (before commit)
- Use `find_references` before deleting/renaming symbols
- Use `rename_symbol` with `dry_run: true` to preview changes
</cclsp-guidance>
EOF
else
  # cclsp NOT configured - remind about setup
  echo "cclsp LSP tools not configured. Run /cclsp:setup for enhanced code navigation."
fi

# Exit successfully regardless - this is just a reminder/guidance, not a blocker
exit 0
