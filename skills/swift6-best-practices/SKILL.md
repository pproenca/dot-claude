---
name: swift6-best-practices
description: Swift 6 performance optimization guidelines from Apple Swift Documentation and Swift Evolution. This skill should be used when writing, reviewing, or refactoring Swift code to ensure optimal performance patterns. Triggers on tasks involving Swift concurrency, actor isolation, Sendable conformance, memory management, and performance optimization.
---

# Swift 6 Best Practices

## Overview

Comprehensive performance optimization guide for Swift 6 applications, containing 48 rules across 8 categories. Rules are prioritized by impact to guide automated refactoring and code generation. Focuses on Swift 6's strict concurrency, ownership system, and performance optimizations.

## When to Apply

Reference these guidelines when:
- Writing new Swift classes, structs, or actors
- Implementing async/await and structured concurrency
- Reviewing code for data-race safety issues
- Refactoring existing Swift code for Swift 6 migration
- Optimizing memory usage and execution speed

## Priority-Ordered Guidelines

Rules are prioritized by impact:

| Priority | Category | Impact |
|----------|----------|--------|
| 1 | Concurrency & Data-Race Safety | CRITICAL |
| 2 | Memory Management & ARC | CRITICAL |
| 3 | Ownership & Noncopyable Types | HIGH |
| 4 | Value Types & Copy-on-Write | MEDIUM-HIGH |
| 5 | Collection Performance | MEDIUM |
| 6 | Async/Await & Structured Concurrency | MEDIUM |
| 7 | Compiler Optimization | LOW-MEDIUM |
| 8 | Error Handling & Type Safety | LOW |

## Quick Reference

### Critical Patterns (Apply First)

**Concurrency & Data-Race Safety:**
- Use `@MainActor` for all UI-bound code
- Conform types to `Sendable` when crossing isolation boundaries
- Prefer actors over classes with manual synchronization
- Use `nonisolated` for pure functions without state access
- Handle closure isolation inheritance in async callbacks
- Apply `@preconcurrency` for legacy delegate protocols
- Enable strict concurrency checking incrementally

**Memory Management & ARC:**
- Use `[weak self]` in escaping closures to break retain cycles
- Prefer `unowned` when lifetime is guaranteed (no side table overhead)
- Choose structs over classes to avoid ARC overhead
- Avoid capturing `self` strongly in long-lived closures
- Use `autoreleasepool` for tight loops with Objective-C objects
- Profile with Instruments to identify retain cycles

### High-Impact Patterns

- Use `~Copyable` for unique resource ownership (file handles, connections)
- Apply `consuming` for ownership transfer, `borrowing` for read-only access
- Use `consume` operator to explicitly end variable lifetime
- Implement proper deinit for noncopyable types
- Suppress implicit copying with ownership modifiers

### Medium-Impact Patterns

- Prefer structs with copy-on-write for large value types
- Use `isKnownUniquelyReferenced` for efficient CoW
- Choose `ContiguousArray` for class element types (2x faster)
- Use `Set` for O(1) membership testing
- Apply `lazy` sequences for chained transformations
- Prefer `async let` over TaskGroup for fixed concurrent operations

### Lower-Impact Patterns

- Mark classes `final` for devirtualization
- Use `@inlinable` for cross-module hot paths
- Prefer concrete types over existentials (`any Protocol`)
- Use typed throws for exhaustive error handling in fixed domains

## References

Full documentation with code examples is available in:

- `references/swift-performance-guidelines.md` - Complete guide with all patterns
- `references/rules/` - Individual rule files organized by category

To look up a specific pattern, grep the rules directory:
```
grep -l "Sendable" references/rules/
```

## Rule Categories in `references/rules/`

- `concur-*` - Concurrency & Data-Race Safety patterns
- `memory-*` - Memory Management & ARC optimization
- `owner-*` - Ownership & Noncopyable Types performance
- `value-*` - Value Types & Copy-on-Write patterns
- `collect-*` - Collection Performance optimization
- `async-*` - Async/Await & Structured Concurrency patterns
- `optim-*` - Compiler Optimization techniques
- `error-*` - Error Handling & Type Safety patterns
