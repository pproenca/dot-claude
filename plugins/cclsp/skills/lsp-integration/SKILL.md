---
name: lsp-integration
description: |
  Use this skill when developing plugins that should integrate with cclsp LSP tools,
  implementing feature detection for MCP tools, designing graceful degradation patterns,
  or adding code navigation to agents and commands.
allowed-tools: Read, Grep, Glob
---

# LSP Integration Patterns

This skill documents how plugins should integrate with cclsp LSP tools following marketplace best practices.

## Core Principle: Feature Detection

Never assume cclsp is available. Always detect and gracefully degrade.

## Available Tools

When cclsp is configured, these MCP tools are available:

| Tool | Purpose | Use When |
|------|---------|----------|
| `mcp__cclsp__find_definition` | Jump to symbol definition | Need exact location of a function, class, or variable |
| `mcp__cclsp__find_references` | Find all usages | Checking impact of changes, understanding usage patterns |
| `mcp__cclsp__get_diagnostics` | Get type errors/warnings | Validating code before commit, reviewing changes |
| `mcp__cclsp__rename_symbol` | Safe cross-file rename | Refactoring symbols without breaking references |

## Feature Detection Pattern

Add this section to agents that should use LSP tools:

```markdown
## LSP Tools (Optional Enhancement)

**Feature detection:** At the start of analysis, check if cclsp LSP tools
are available by attempting `mcp__cclsp__get_diagnostics` on a known file.
If available, prefer LSP tools:

| Task | With cclsp | Without cclsp |
|------|------------|---------------|
| Find symbol definition | `mcp__cclsp__find_definition` | `Grep` + `Read` |
| Find all usages | `mcp__cclsp__find_references` | `Grep` pattern matching |
| Type errors | `mcp__cclsp__get_diagnostics` | Manual compiler run |
| Safe refactoring | `mcp__cclsp__rename_symbol` | Manual find/replace |

If cclsp is not available, the agent suggests:
"For enhanced code navigation, run `/cclsp:setup`."
```

## Integration Examples

### For Code Exploration Agents

```markdown
## Exploration Methodology

### Phase 2: Pattern Recognition

Use Grep to find similar implementations.

**If cclsp is available** (see feature detection above), prefer LSP tools:

- `mcp__cclsp__find_definition` — Jump to where a symbol is defined
- `mcp__cclsp__find_references` — Find all usages across the codebase
- `mcp__cclsp__get_diagnostics` — Check for type errors that indicate patterns
```

### For Code Review Agents

```markdown
## Review Process

1. Get diff: `git diff BASE_SHA HEAD`
2. Analyze files: Read each changed file
3. Check patterns: Verify consistency
4. **Run LSP diagnostics** (if cclsp available):
   Use `mcp__cclsp__get_diagnostics` on each changed file
5. **Check for broken references** (if cclsp available):
   Use `mcp__cclsp__find_references` on renamed/removed symbols
```

### For Task Execution

```markdown
## LSP Tools (Optional - if cclsp is configured)

Check if `mcp__cclsp__*` tools are available. If so, prefer them:
- `mcp__cclsp__find_definition` - Jump to symbol definitions
- `mcp__cclsp__find_references` - Find all usages before modifying
- `mcp__cclsp__get_diagnostics` - Check for type errors after changes
- `mcp__cclsp__rename_symbol` - Safe refactoring across codebase

If cclsp is available, run `get_diagnostics` on modified files before committing.
If cclsp is not available, proceed without it (use Grep for symbol search).
```

## When to Prefer LSP vs Grep

| Scenario | Prefer |
|----------|--------|
| Known symbol name, need exact definition | LSP `find_definition` |
| Pattern search across files | Grep |
| All usages of a specific function | LSP `find_references` |
| Text search with regex | Grep |
| Type checking before commit | LSP `get_diagnostics` |
| Renaming a symbol safely | LSP `rename_symbol` |

## Graceful Degradation

When cclsp is not available:

1. **Don't fail** - Continue with fallback methods
2. **Suggest setup** - Mention `/cclsp:setup` once
3. **Use Grep** - Pattern matching works for most cases
4. **Skip diagnostics** - No fallback for type checking

## Plugin Dependency

Plugins that integrate cclsp should:

1. NOT bundle `.mcp.json` (causes failures if not configured)
2. Document cclsp as optional enhancement
3. Reference `/cclsp:setup` for installation
4. Use feature detection at runtime

## Best Practices

1. **Check once per session** - Don't check availability on every operation
2. **Prefer LSP for precision** - When you need exact symbol resolution
3. **Fall back gracefully** - Grep works well for most searches
4. **Don't require cclsp** - All core functionality should work without it
5. **Mention setup once** - Don't repeatedly prompt for setup
