---
name: cpp-best-practices
description: C++ performance optimization guidelines from modern C++ standards (C++17/20/23). This skill should be used when writing, reviewing, or refactoring C++ code to ensure optimal performance patterns. Triggers on tasks involving memory management, concurrency, compile-time optimization, cache efficiency, or performance improvements.
allowed-tools: [Read, Edit, Bash, Glob, Grep, WebSearch, WebFetch, LSP]
---

# C++ Best Practices

## Overview

Comprehensive performance optimization guide for modern C++ applications, containing 47 rules across 8 categories. Rules are prioritized by impact to guide automated refactoring and code generation. Focuses on C++17/20/23 best practices.

## When to Apply

Reference these guidelines when:
- Writing new C++ code or libraries
- Implementing memory management patterns
- Working with concurrent/parallel code
- Reviewing code for performance issues
- Refactoring existing C++ codebases
- Optimizing compile times or binary size

## Priority-Ordered Guidelines

Rules are prioritized by impact:

| Priority | Category | Impact |
|----------|----------|--------|
| 1 | Memory Management | CRITICAL |
| 2 | Compile Time Optimization | CRITICAL |
| 3 | Concurrency Patterns | HIGH |
| 4 | Cache Optimization | MEDIUM-HIGH |
| 5 | Algorithm Selection | MEDIUM |
| 6 | I/O Performance | MEDIUM |
| 7 | Code Generation | LOW-MEDIUM |
| 8 | Template Metaprogramming | LOW |

## Quick Reference

### Critical Patterns (Apply First)

**Memory Management:**
- Use smart pointers over raw pointers
- Prefer `make_unique`/`make_shared` over `new`
- Use RAII for all resource management
- Avoid unnecessary copies with move semantics
- Reserve container capacity when size is known

**Compile Time Optimization:**
- Use forward declarations to reduce includes
- Prefer `extern template` for common instantiations
- Use precompiled headers for large projects
- Minimize template instantiation in headers
- Use `if constexpr` instead of SFINAE when possible

### High-Impact Concurrency Patterns

- Use `std::jthread` over `std::thread` for automatic joining
- Prefer `std::atomic` over mutex for simple types
- Use `std::shared_mutex` for read-heavy workloads
- Avoid false sharing with cache-line alignment
- Use lock-free structures when contention is high

### Medium-Impact Patterns

**Cache Optimization:**
- Prefer contiguous containers (`vector` over `list`)
- Use Structure of Arrays (SoA) for hot data
- Align data to cache line boundaries
- Minimize pointer chasing in hot paths

**Algorithm Selection:**
- Use `std::ranges` algorithms for clarity and performance
- Prefer `std::sort` over hand-rolled sorting
- Use `std::unordered_map` for O(1) lookups
- Consider `flat_map` for small associative containers

## References

Full documentation with code examples is available in:

- `references/cpp-performance-guidelines.md` - Complete guide with all patterns
- `references/rules/` - Individual rule files organized by category

To look up a specific pattern, grep the rules directory:
```
grep -l "smart_ptr" references/rules/
grep -l "atomic" references/rules/
grep -l "cache" references/rules/
```

## Rule Categories in `references/rules/`

- `memory-*` - Memory management and ownership patterns
- `compile-*` - Compile time and binary size optimization
- `async-*` - Concurrency and parallelism patterns
- `cache-*` - Cache-friendly data structures and access patterns
- `algo-*` - Algorithm selection and optimization
- `io-*` - I/O and file system performance
- `codegen-*` - Code generation and inlining hints
- `template-*` - Template metaprogramming patterns
