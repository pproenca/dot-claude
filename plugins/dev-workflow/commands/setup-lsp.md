---
name: setup-lsp
description: Configure LSP-based code navigation (cclsp) for enhanced symbol lookup
allowed-tools: Bash, Read, Write, AskUserQuestion
---

# Setup LSP Code Navigation

This command configures [cclsp](https://github.com/ktnyt/cclsp) for LSP-based code navigation.

## What cclsp Provides

| Tool | Purpose |
|------|---------|
| `find_definition` | Jump directly to where a symbol is defined |
| `find_references` | Find all usages of a function, class, or interface |
| `get_diagnostics` | Surface type errors and warnings from the language server |
| `rename_symbol` | Safely refactor symbols across the entire codebase |

These tools enhance code-explorer, code-architect, and code-reviewer agents with precise symbol navigation.

## Setup Instructions

### Step 1: Check Current Status

```bash
# Check if CCLSP_CONFIG_PATH is set
if [ -n "$CCLSP_CONFIG_PATH" ]; then
  echo "CCLSP_CONFIG_PATH is set to: $CCLSP_CONFIG_PATH"
  if [ -f "$CCLSP_CONFIG_PATH" ]; then
    echo "Config file exists. cclsp is configured."
  else
    echo "Config file not found at: $CCLSP_CONFIG_PATH"
  fi
else
  echo "CCLSP_CONFIG_PATH is not set"
  # Check common locations
  if [ -f "$HOME/.config/claude/cclsp.json" ]; then
    echo "Found config at: $HOME/.config/claude/cclsp.json"
    echo "Set CCLSP_CONFIG_PATH to use it"
  fi
fi
```

### Step 2: Run cclsp Setup (if needed)

If no config exists, run the interactive setup wizard:

```bash
npx cclsp@latest setup --user
```

This will:
- Detect available language servers on your system
- Create a config file at `~/.config/claude/cclsp.json`
- Configure which languages to support

### Step 3: Set Environment Variable

Add to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.):

```bash
export CCLSP_CONFIG_PATH="$HOME/.config/claude/cclsp.json"
```

Then reload your shell or run `source ~/.zshrc`.

### Step 4: Add MCP Server to Claude Code

Add cclsp to your Claude Code MCP settings. Create or edit `~/.claude/settings.json`:

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

Or use the Claude Code settings UI to add the MCP server.

### Step 5: Restart Claude Code

Restart Claude Code for the MCP server to start.

## Verification

After setup, verify cclsp is working:

```
Use the mcp__cclsp__get_diagnostics tool on any source file
```

If it returns diagnostics (or an empty list for clean files), cclsp is working.

## Troubleshooting

**Server fails to start:**
- Verify `CCLSP_CONFIG_PATH` is set: `echo $CCLSP_CONFIG_PATH`
- Verify config file exists: `cat $CCLSP_CONFIG_PATH`
- Try running cclsp manually: `CCLSP_CONFIG_PATH=... npx cclsp@latest`

**No language support:**
- Re-run setup: `npx cclsp@latest setup --user`
- Install language servers for your stack (e.g., `typescript-language-server` for TypeScript)

## Without cclsp

The dev-workflow plugin works fully without cclsp. LSP tools are an optional enhancement for:
- Faster symbol lookup (vs grep-based search)
- Type-aware diagnostics
- Safe refactoring

All core functionality (TDD, debugging, planning, code review) works without LSP integration.
