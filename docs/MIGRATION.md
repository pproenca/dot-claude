# Migration Guide: super -> Focused Plugins

This guide helps users transition from the monolithic `super` plugin to the new focused plugin architecture.

## Overview

The `super` plugin (18 skills) has been decomposed into focused, single-purpose plugins:

| New Plugin | Purpose | Skills |
|------------|---------|--------|
| **core** | Essential workflows | using-core, verification, tdd, brainstorming |
| **workflow** | Planning and execution | writing-plans, executing-plans, subagent-dev, git-worktrees, finish-branch, parallel-agents |
| **review** | Code review | code-review (merged from requesting + receiving) |
| **testing** | Test patterns | anti-patterns, condition-wait |
| **meta** | Plugin development | writing-skills, testing-skills |
| **debug** | Debugging (moved from super) | systematic, root-cause, defense-in-depth |

## Skill Name Changes

| Old Name | New Name |
|----------|----------|
| `super:using-superpowers` | `core:using-core` |
| `super:verification-before-completion` | `core:verification` |
| `super:test-driven-development` | `core:tdd` |
| `super:brainstorming` | `core:brainstorming` |
| `super:writing-plans` | `workflow:writing-plans` |
| `super:executing-plans` | `workflow:executing-plans` |
| `super:subagent-driven-development` | `workflow:subagent-dev` |
| `super:using-git-worktrees` | `workflow:git-worktrees` |
| `super:finishing-a-development-branch` | `workflow:finish-branch` |
| `super:dispatching-parallel-agents` | `workflow:parallel-agents` |
| `super:requesting-code-review` | `review:code-review` |
| `super:receiving-code-review` | `review:code-review` |
| `super:systematic-debugging` | `debug:systematic` |
| `super:root-cause-tracing` | `debug:root-cause` |
| `super:defense-in-depth` | `debug:defense-in-depth` |
| `super:testing-anti-patterns` | `testing:anti-patterns` |
| `super:condition-based-waiting` | `testing:condition-wait` |
| `super:writing-skills` | `meta:writing-skills` |
| `super:testing-skills-with-subagents` | `meta:testing-skills` |

## Backward Compatibility

The `super` plugin remains available but is **deprecated**. It now serves as a backward-compatible alias:

- Skills invoked with `super:*` will continue to work through cross-references
- New installations should use the focused plugins directly
- The `super` plugin declares dependencies on `core`, `workflow`, and `review`

## Migration Steps

### For Existing Users

1. **No immediate action required** - existing `super:*` references continue to work
2. **Recommended**: Update skill references to use new plugin names for clarity
3. **Optional**: Remove `super` plugin and install only needed focused plugins

### For New Installations

Install only the plugins you need:

```bash
# Essential - always install
claude plugin install core

# Based on your workflow
claude plugin install workflow   # If using plans, worktrees, subagents
claude plugin install review     # If doing code reviews
claude plugin install debug      # If debugging complex issues
claude plugin install testing    # If writing tests with async patterns
claude plugin install meta       # If creating skills/plugins
```

## Architecture Benefits

The new architecture provides:

1. **Progressive disclosure** - Install only what you need
2. **Smaller context** - Each plugin loads fewer tokens
3. **Clearer ownership** - Skills grouped by domain
4. **Independent versioning** - Plugins can evolve separately
5. **Optional dependencies** - Domain plugins (python, shell, doc) work standalone but enhance with `core`

## Migration Complete

As of v5.0.0, the `super` plugin has been fully removed. All functionality is now in:
- **core** - Essential workflows (TDD, verification, brainstorming)
- **workflow** - Planning, execution, and git workflows
- **review** - Code review
- **testing** - Test patterns
- **meta** - Plugin development
- **debug** - Debugging skills

If you have any references to `super:*` in your own configurations or documentation, update them using the mapping table above.

## Questions?

See `CLAUDE.md` for full architecture documentation or open an issue on GitHub.
