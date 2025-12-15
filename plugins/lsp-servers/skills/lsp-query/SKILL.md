---
name: lsp-query
description: Use this skill to query LSP for symbols, definitions, references, hover info. Triggers on "find definition", "go to definition", "find references", "what symbols", "hover", "LSP".
allowed-tools: [Bash, Read]
---

# LSP Query Skill

Query language servers for code intelligence.

## Usage

Run the LSP client directly:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/lsp_client.py" <operation> <file> [--line N] [--character N]
```

## Operations

| Operation | Description | Example |
|-----------|-------------|---------|
| `documentSymbol` | List all symbols in file | `python3 lsp_client.py documentSymbol src/main.py` |
| `goToDefinition` | Find symbol definition | `python3 lsp_client.py goToDefinition src/main.py --line 10 --character 5` |
| `findReferences` | Find all references | `python3 lsp_client.py findReferences src/main.py --line 10 --character 5` |
| `hover` | Get type/doc info | `python3 lsp_client.py hover src/main.py --line 10 --character 5` |
| `goToImplementation` | Find implementations | `python3 lsp_client.py goToImplementation src/main.py --line 10 --character 5` |
| `workspaceSymbol` | Search symbols | `python3 lsp_client.py workspaceSymbol --query "MyClass"` |

## Daemon Mode (Faster)

Start daemon for persistent servers:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/lsp_client.py" daemon start
```

Subsequent queries will be fast (~0.3s vs ~4s cold start).

## Supported Languages

- Python (.py) - requires `pylsp`
- TypeScript/JavaScript (.ts, .tsx, .js, .jsx) - requires `typescript-language-server`

## Example Workflow

1. Find what a function does:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/lsp_client.py" hover /path/to/file.py --line 42 --character 10
   ```

2. Find where it's defined:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/lsp_client.py" goToDefinition /path/to/file.py --line 42 --character 10
   ```

3. Find all usages:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/lsp_client.py" findReferences /path/to/file.py --line 42 --character 10
   ```
