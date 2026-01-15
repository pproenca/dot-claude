# Node.js Addon C++ Best Practices

Performance optimization guidelines for Node.js native addons using N-API and node-addon-api.

## Overview

This skill contains **38 rules** across **8 categories**, designed to help AI agents and developers write high-performance Node.js native addons in C++.

### Structure

```
nodejs-addon-cpp/
├── SKILL.md           # Quick reference with all rules listed
├── AGENTS.md          # Full compiled guide for AI consumption
├── metadata.json      # Version and reference information
├── README.md          # This file
└── rules/
    ├── _sections.md   # Category definitions
    ├── _template.md   # Rule template
    └── *.md           # Individual rule files (38 rules)
```

## Categories

| # | Category | Impact | Prefix | Rules |
|---|----------|--------|--------|-------|
| 1 | JS/C++ Boundary Optimization | CRITICAL | boundary | 5 |
| 2 | Memory Management | CRITICAL | mem | 5 |
| 3 | Thread Safety & Async | CRITICAL | async | 5 |
| 4 | Data Conversion | HIGH | conv | 5 |
| 5 | Handle Management | HIGH | handle | 5 |
| 6 | Object Wrapping | MEDIUM-HIGH | wrap | 3 |
| 7 | N-API Best Practices | MEDIUM | napi | 5 |
| 8 | Build & Module Loading | MEDIUM | build | 5 |

## Getting Started

### Prerequisites

- Node.js 14+ with N-API support
- C++ compiler (GCC, Clang, or MSVC)
- node-gyp or cmake-js

### Installation

```bash
pnpm install
```

### Building

```bash
pnpm build
```

### Validation

Run the validation script to check all rules meet quality standards:

```bash
pnpm validate
```

## Creating a New Rule

1. Choose the appropriate category from `rules/_sections.md`
2. Create a new file with the naming convention: `{prefix}-{description}.md`
3. Copy the template from `rules/_template.md`
4. Fill in all required fields in the YAML frontmatter
5. Add **Incorrect** and **Correct** code examples with descriptive annotations
6. Run `pnpm validate` to check your rule

### Prefix Reference

| Prefix | Category |
|--------|----------|
| boundary | JS/C++ Boundary Optimization |
| mem | Memory Management |
| async | Thread Safety & Async |
| conv | Data Conversion |
| handle | Handle Management |
| wrap | Object Wrapping |
| napi | N-API Best Practices |
| build | Build & Module Loading |

## Rule File Structure

Each rule file follows this structure:

```markdown
---
title: "Verb Object Context"
impact: "CRITICAL|HIGH|MEDIUM-HIGH|MEDIUM|LOW-MEDIUM|LOW"
impactDescription: "Quantified impact (e.g., 2-10× improvement)"
tags: "prefix, tag2, tag3"
---

## Verb Object Context

Brief explanation of WHY this matters (1-3 sentences).

**Incorrect (describes the problem/cost):**

\`\`\`cpp
// Anti-pattern code
\`\`\`

**Correct (describes the benefit/solution):**

\`\`\`cpp
// Optimized code
\`\`\`

### Additional sections as needed
```

## File Naming Convention

Rule files use the pattern: `{prefix}-{description}.md`

- **prefix**: Category identifier (2-8 lowercase chars) matching `_sections.md`
- **description**: Kebab-case description of the rule

Examples:
- `boundary-batch-calls.md` - Boundary optimization for batching calls
- `mem-buffer-pool.md` - Memory management with buffer pools
- `async-worker-threads.md` - Async pattern for worker threads

## Impact Levels

| Level | Description | When to Use |
|-------|-------------|-------------|
| CRITICAL | 10×+ improvement or prevents crashes | Fundamental patterns, memory safety |
| HIGH | 2-10× improvement | Common optimizations |
| MEDIUM-HIGH | 50-100% improvement | Situational optimizations |
| MEDIUM | 20-50% improvement | Good practices |
| LOW-MEDIUM | 10-20% improvement | Minor optimizations |
| LOW | <10% improvement | Polish and consistency |

## Scripts

| Command | Description |
|---------|-------------|
| `pnpm install` | Install dependencies |
| `pnpm build` | Build AGENTS.md from individual rules |
| `pnpm validate` | Validate all rules against quality guidelines |
| `pnpm validate:strict` | Validate with warnings as errors |

## Contributing

1. **Follow the template** - Use `rules/_template.md` as your starting point
2. **Quantify impact** - Use specific metrics (2-10×, 200ms, O(n) to O(1))
3. **Show both patterns** - Include **Incorrect** and **Correct** examples
4. **Use descriptive annotations** - Explain the problem/benefit in parentheses
5. **Test your examples** - Ensure code compiles and demonstrates the concept
6. **Run validation** - Execute `pnpm validate` before submitting

### Code Style

- Use C++11 or later features where appropriate
- Include comments explaining performance implications
- Keep examples minimal but realistic

## Key Principles

1. **Minimize boundary crossings** - Each JS↔C++ crossing costs ~100-1000ns
2. **Batch operations** - Process arrays in single calls instead of loops
3. **Use TypedArrays** - Direct memory access without per-element conversion
4. **Don't block the event loop** - Use AsyncWorker for CPU-intensive tasks
5. **Manage memory explicitly** - Track external allocations with V8's GC

## References

- [Node-API Documentation](https://nodejs.org/api/n-api.html)
- [node-addon-api](https://github.com/nodejs/node-addon-api)
- [V8 Embedder's Guide](https://v8.dev/docs/embed)
- [libuv Documentation](https://docs.libuv.org/)
