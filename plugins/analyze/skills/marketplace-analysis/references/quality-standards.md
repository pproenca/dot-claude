# Anthropic-Level Quality Standards

> **DISCLAIMER**: This document contains **invented proxies and heuristics**, not official Claude Code documentation. These are useful mental models for thinking about quality, but they are NOT documented guidance from Anthropic. Always verify claims against official documentation via `claude-code-guide` before treating them as authoritative.

This reference defines what "Anthropic quality" means for Claude Code plugins.

## Table of Contents

- [The Quality Bar](#the-quality-bar)
- [Quality Dimensions](#quality-dimensions)
  - [Trigger Quality](#1-trigger-quality)
  - [Documentation Quality](#2-documentation-quality)
  - [Architecture Quality](#3-architecture-quality)
  - [Implementation Quality](#4-implementation-quality)
- [Anti-Patterns](#anti-patterns)
- [Quality Checklist](#quality-checklist)

## The Quality Bar

**Definition**: Software that is elegant, efficient, and provides a step-change in developer productivity.

### Elegance

Code and design that feels "right":

- **Minimal**: Nothing to remove, not nothing to add
- **Coherent**: All parts fit together naturally
- **Intuitive**: Users guess correctly how things work
- **Readable**: Future maintainers understand intent

**Test for elegance:**
- Can you explain it in one sentence?
- Would you be proud to show this to a colleague?
- Does it feel inevitable, not arbitrary?

### Efficiency

Maximum value with minimum cost:

- **Token efficient**: Skills/agents load only what's needed
- **Cognitive efficient**: Users don't need to remember complex rules
- **Time efficient**: Common tasks are fast
- **Context efficient**: Progressive disclosure everywhere

**Test for efficiency:**
- Is the common case optimized?
- Are there unnecessary steps?
- Does it scale as usage grows?

### Developer Productivity

Real impact on how people work:

- **Multiplier effect**: One skill enables many workflows
- **Error prevention**: Harder to do wrong than right
- **Flow preservation**: Minimal context switching
- **Learning curve**: Steep improvement, then stable

**Test for productivity:**
- Does this save time on the first use?
- Does it save more time over many uses?
- Does it prevent mistakes?

## Quality Dimensions

### 1. Trigger Quality

**Excellent triggers** (imperative format per official docs):
```yaml
description: Create and configure Claude Code hooks. Validate tool usage,
implement PreToolUse/PostToolUse handlers. Use when working with hook events,
tool validation, or event-driven automation.
```

**Poor triggers:**
```yaml
description: Use for hook development.
```

**Criteria:**
- Action verbs describing capabilities
- Multiple entry points
- Specific trigger terms
- Concrete scenarios

### 2. Documentation Quality

**Excellent docs:**
- Purpose clear in first paragraph
- Working examples that can be copied
- Edge cases addressed
- Progressive disclosure (details in references)

**Poor docs:**
- Vague overview
- Examples that don't run
- Missing edge cases
- Everything in one file

**Criteria:**
- New user productive in 5 minutes
- Copy-paste examples work
- Edge cases documented
- Description under 1024 characters (official limit)

### 3. Architecture Quality

**Excellent architecture:**
- One component, one responsibility
- No duplicated functionality
- Clean interfaces
- Obvious extension points

**Poor architecture:**
- Components doing multiple things
- Same logic in multiple places
- Tangled dependencies
- Unclear boundaries

**Criteria:**
- Can explain each component in one sentence
- No copy-paste between components
- Changes isolated to one component
- New components fit naturally

### 4. Implementation Quality

**Excellent implementation:**
- Simplest code that works
- Named for intent, not implementation
- Handles errors gracefully
- Tested with real usage

**Poor implementation:**
- Over-abstracted
- Cryptic naming
- Silent failures
- Untested assumptions

**Criteria:**
- Would you want to maintain this?
- Are names self-documenting?
- Do errors help users fix issues?
- Has it been used in real scenarios?

## Anti-Patterns

### The Kitchen Sink

Adding features "just in case":
- Configurability for unlikely scenarios
- Abstractions with one implementation
- Options nobody uses

**Fix**: Remove until something breaks

### The Swiss Army Knife

One component doing too many things:
- 500+ line SKILL.md
- Agent with 10+ responsibilities
- Command with 5+ subcommands

**Fix**: Split into focused components

### The Copy-Paste

Duplicated logic across components:
- Same validation in multiple hooks
- Same formatting in multiple agents
- Same patterns reimplemented

**Fix**: Extract shared utility or remove duplication

### The Invisible Feature

Capabilities users don't know about:
- Undocumented trigger phrases
- Hidden command arguments
- Implicit behaviors

**Fix**: Document all entry points with examples

## Quality Checklist

Before declaring something "done":

### Trigger Quality
- [ ] Imperative format with action verbs
- [ ] Specific trigger terms (phrases don't need quotes)
- [ ] Covers different phrasings of same intent
- [ ] "Use when..." clause for context

### Documentation Quality
- [ ] Purpose clear in 2 sentences
- [ ] Working copy-paste examples
- [ ] Edge cases addressed
- [ ] Description under 1024 characters

### Architecture Quality
- [ ] Each component has one job
- [ ] No duplicated functionality
- [ ] Dependencies are obvious
- [ ] Extension points are clear

### Implementation Quality
- [ ] Simplest solution that works
- [ ] Names describe intent
- [ ] Errors are helpful
- [ ] Tested with real usage

### Overall Quality
- [ ] Would you be proud to ship this?
- [ ] Is this better than what exists?
- [ ] Can you prove it's better?
