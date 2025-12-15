---
description: Configure cclsp LSP server for enhanced code navigation
allowed-tools: Bash, Read, Write, AskUserQuestion
---

# Setup cclsp

Configure [cclsp](https://github.com/ktnyt/cclsp) for LSP-based code navigation in Claude Code.

## What You Get

| Tool | Purpose |
|------|---------|
| `mcp__cclsp__find_definition` | Jump directly to symbol definitions |
| `mcp__cclsp__find_references` | Find all usages across the codebase |
| `mcp__cclsp__get_diagnostics` | Surface type errors and warnings |
| `mcp__cclsp__rename_symbol` | Safely refactor symbols across files |

## Step 1: Check Current Status

Run this to check if cclsp is already configured:

```bash
echo "=== cclsp Status Check ==="
if [ -n "$CCLSP_CONFIG_PATH" ]; then
  echo "CCLSP_CONFIG_PATH: $CCLSP_CONFIG_PATH"
  if [ -f "$CCLSP_CONFIG_PATH" ]; then
    echo "Status: Config file exists"
    echo "Content preview:"
    head -20 "$CCLSP_CONFIG_PATH"
  else
    echo "Status: Config file NOT FOUND at $CCLSP_CONFIG_PATH"
  fi
else
  echo "CCLSP_CONFIG_PATH: (not set)"
  # Check common locations
  for loc in "$HOME/.config/claude/cclsp.json" "$HOME/.cclsp.json"; do
    if [ -f "$loc" ]; then
      echo "Found config at: $loc"
      echo "Set CCLSP_CONFIG_PATH to use it"
    fi
  done
fi
```

**If status shows "Config file exists"**: Skip to Step 4 (Add to Claude Code).

**If status shows config not found**: Continue to Step 2.

## Step 2: Run cclsp Setup Wizard

Run the interactive setup wizard to configure language servers:

```bash
npx cclsp@latest setup --user
```

This wizard will:
- Detect available language servers on your system
- Create config at `~/.config/claude/cclsp.json`
- Configure which languages to support

**Follow the prompts** to select your languages.

## Step 3: Set Environment Variable

Add to your shell profile (`~/.zshrc`, `~/.bashrc`, or `~/.profile`):

```bash
export CCLSP_CONFIG_PATH="$HOME/.config/claude/cclsp.json"
```

Then reload your shell:

```bash
source ~/.zshrc  # or ~/.bashrc
```

## Step 4: Add to Claude Code MCP Settings

Ask the user which method they prefer:

```claude
AskUserQuestion:
  header: "MCP config"
  question: "How should I add cclsp to Claude Code?"
  multiSelect: false
  options:
    - label: "Edit settings.json (Recommended)"
      description: "Add to ~/.claude/settings.json for global availability"
    - label: "Show me the config"
      description: "Display the JSON to add manually"
```

### Option A: Edit settings.json

Read the current settings:

```bash
cat ~/.claude/settings.json 2>/dev/null || echo "{}"
```

Add or merge the cclsp server configuration:

```json
{
  "mcpServers": {
    "cclsp": {
      "command": "npx",
      "args": ["-y", "cclsp@latest"],
      "env": {
        "CCLSP_CONFIG_PATH": "${CCLSP_CONFIG_PATH}"
      }
    }
  }
}
```

Write the updated settings using the Write tool.

### Option B: Show config

Display:

```
Add this to your Claude Code MCP settings (~/.claude/settings.json):

{
  "mcpServers": {
    "cclsp": {
      "command": "npx",
      "args": ["-y", "cclsp@latest"],
      "env": {
        "CCLSP_CONFIG_PATH": "${CCLSP_CONFIG_PATH}"
      }
    }
  }
}
```

## Step 5: Verify Installation

After restarting Claude Code, verify cclsp is working:

1. The user should restart Claude Code
2. Test with: "Use mcp__cclsp__get_diagnostics on any source file"

If it returns diagnostics (or empty list for clean files), cclsp is working.

## Troubleshooting

**Server fails to start:**
- Verify CCLSP_CONFIG_PATH is set: `echo $CCLSP_CONFIG_PATH`
- Verify config file exists: `cat $CCLSP_CONFIG_PATH`
- Try running manually: `CCLSP_CONFIG_PATH=... npx cclsp@latest`

**No language support:**
- Re-run setup: `npx cclsp@latest setup --user`
- Install language servers for your stack (e.g., `typescript-language-server`)

## Success Message

When setup is complete, inform the user:

```
cclsp is configured! After restarting Claude Code, you'll have access to:
- mcp__cclsp__find_definition
- mcp__cclsp__find_references
- mcp__cclsp__get_diagnostics
- mcp__cclsp__rename_symbol

Other plugins (dev-workflow, dev-python) will automatically detect
and use these tools for enhanced code navigation.
```
