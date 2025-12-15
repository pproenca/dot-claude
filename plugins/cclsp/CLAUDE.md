# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Overview

MCP plugin providing LSP-based code navigation tools. When configured, Claude should prefer these tools over text-based search for symbol operations.

## When to Use cclsp Tools

**IMPORTANT:** When `mcp__cclsp__*` tools are available, prefer them for precision:

| Task | Use This | Not This |
|------|----------|----------|
| "Where is X defined?" | `mcp__cclsp__find_definition` | Grep |
| "What calls/uses X?" | `mcp__cclsp__find_references` | Grep |
| "Rename X to Y" | `mcp__cclsp__rename_symbol` | Manual Edit |
| "Any type errors?" | `mcp__cclsp__get_diagnostics` | Run compiler manually |

**Still use Grep/Glob for:**
- Pattern/regex search across files
- Finding text that isn't a symbol (comments, strings)
- Exploring unknown codebases broadly

## Tool Reference

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `find_definition` | Jump to where symbol is defined | `file_path`, `symbol_name`, `symbol_kind` |
| `find_references` | Find all usages across workspace | `file_path`, `symbol_name`, `include_declaration` |
| `rename_symbol` | Safe cross-file rename | `file_path`, `symbol_name`, `new_name`, `dry_run` |
| `get_diagnostics` | Type errors, warnings, hints | `file_path` |
| `restart_server` | Reset LSP if behaving oddly | `extensions` (optional) |

## Best Practices

1. **Check diagnostics after edits** - Run `get_diagnostics` on modified files before committing
2. **Use dry_run for renames** - Preview changes with `dry_run: true` before applying
3. **Prefer find_references before deletion** - Check what depends on a symbol before removing it
4. **Symbol kind helps disambiguation** - Use `symbol_kind` (function, class, method, variable) when symbol names are common

## Setup

If cclsp tools aren't available, users can run `/cclsp:setup` to configure.

## Commands

- `/cclsp:setup` - Interactive setup wizard

## Directory Structure

```text
.claude-plugin/   # Plugin metadata
commands/         # Slash commands
hooks/            # SessionStart reminder
skills/           # LSP integration patterns for other plugins
```
