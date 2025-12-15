# LSP Servers Plugin

Provides TypeScript and Python language servers for Claude Code's native LSP tool.

## Requirements

- `typescript-language-server` (install via `bun add -g typescript typescript-language-server`)
- `pylsp` (install via `uv tool install "python-lsp-server[all]"`)

## Usage

With `ENABLE_LSP_TOOL=1`, the LSP tool will use these servers for:
- TypeScript/JavaScript files
- Python files
