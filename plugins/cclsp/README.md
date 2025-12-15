# cclsp

LSP-based code navigation tools for Claude Code. Provides `find_definition`, `find_references`, `get_diagnostics`, and `rename_symbol` capabilities to any plugin.

## Why This Plugin

Claude Code can search code with Grep, but LSP tools provide:

| Capability | Grep | LSP |
|------------|------|-----|
| Find definition | Pattern matching | Precise, type-aware |
| Find references | Text search | Semantic understanding |
| Type errors | Run compiler manually | Real-time diagnostics |
| Refactoring | Find/replace | Safe, cross-file rename |

This plugin provides cclsp as shared infrastructure. Other plugins (dev-workflow, dev-python, etc.) detect and use these tools when available.

## Installation

```bash
claude plugin add pproenca/cclsp
```

## Setup

After installing the plugin, run the setup command:

```bash
/cclsp:setup
```

This guides you through:
1. Running the cclsp setup wizard
2. Configuring your environment
3. Adding cclsp to Claude Code's MCP settings

## Tools Provided

Once configured, these MCP tools become available:

| Tool | Purpose |
|------|---------|
| `mcp__cclsp__find_definition` | Jump to where a symbol is defined |
| `mcp__cclsp__find_references` | Find all usages across the codebase |
| `mcp__cclsp__get_diagnostics` | Get type errors and warnings |
| `mcp__cclsp__rename_symbol` | Safely rename symbols across files |

## For Plugin Developers

Other plugins should use **feature detection** to gracefully handle cclsp availability:

```markdown
## LSP Tools (Optional Enhancement)

**Feature detection:** Check if cclsp tools are available by attempting
`mcp__cclsp__get_diagnostics` on a file. If available, prefer LSP tools:

| Task | With cclsp | Without cclsp |
|------|------------|---------------|
| Find symbol | `mcp__cclsp__find_definition` | `Grep` + `Read` |
| Find usages | `mcp__cclsp__find_references` | `Grep` pattern matching |
| Type errors | `mcp__cclsp__get_diagnostics` | Manual compiler run |

If cclsp is not available, suggest: "For enhanced navigation, run `/cclsp:setup`."
```

See the `lsp-integration` skill for complete integration patterns.

## Prerequisites

- Node.js (for npx)
- Language servers for your stack (installed during setup)

## Troubleshooting

**"cclsp server failed to start"**
- Run `/cclsp:setup` to configure properly
- Verify `CCLSP_CONFIG_PATH` is set in your shell profile

**"No diagnostics returned"**
- Ensure language servers are installed for your language
- Re-run `npx cclsp@latest setup --user` to configure languages

## License

MIT
