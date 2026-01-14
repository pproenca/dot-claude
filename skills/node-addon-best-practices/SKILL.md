---
name: node-addon-best-practices
description: Node.js native addon C++ best practices from Node-API and node-addon-api documentation. This skill should be used when writing, reviewing, or refactoring native Node.js addons in C++. Triggers on tasks involving N-API, node-addon-api, native modules, C++ bindings, AsyncWorker, ThreadSafeFunction, or memory management in native addons.
allowed-tools: [Read, Edit, Bash, Glob, Grep, WebSearch, WebFetch]
---

# Node.js Native Addon Best Practices

## Overview

Comprehensive best practices guide for building native Node.js addons in C++ using Node-API (N-API) and node-addon-api. Contains 46 rules across 8 categories, prioritized by impact to guide automated refactoring and code generation. Focuses on stable ABI, memory safety, thread safety, and performance.

## When to Apply

Reference these guidelines when:
- Writing new native Node.js addons in C++
- Implementing memory management with handle scopes and references
- Working with async operations (AsyncWorker, ThreadSafeFunction)
- Reviewing code for memory leaks or thread safety issues
- Refactoring existing native modules for N-API compatibility
- Optimizing data marshaling between JavaScript and C++

## Priority-Ordered Guidelines

Rules are prioritized by impact:

| Priority | Category | Impact |
|----------|----------|--------|
| 1 | Node-API & N-API Fundamentals | CRITICAL |
| 2 | Memory Management & GC Integration | CRITICAL |
| 3 | Thread Safety & Async Operations | HIGH |
| 4 | Error Handling & Exception Management | MEDIUM-HIGH |
| 5 | Performance Optimization | MEDIUM |
| 6 | Build Systems & Compilation | MEDIUM |
| 7 | Security & Input Validation | LOW-MEDIUM |
| 8 | Common Pitfalls & Anti-Patterns | LOW |

## Quick Reference

### Critical Patterns (Apply First)

**Node-API & N-API Fundamentals:**
- Always use N-API over V8 for stable ABI across Node.js versions
- Define NAPI_VERSION before includes to enable specific features
- Check all napi_status return codes before using results
- Use node-addon-api C++ wrapper for type safety and exception handling
- Use type-tagged objects for safe native object casting

**Memory Management & GC Integration:**
- Use handle scopes in loops to prevent memory buildup
- Create references for JavaScript objects that persist beyond callbacks
- Track external memory allocations with AdjustExternalMemory
- Register finalizers for cleanup when JavaScript objects are GC'd
- Prefer buffers for large data to avoid V8 heap pressure

### High-Impact Thread Safety Patterns

- Use AsyncWorker for CPU-intensive background tasks
- Never call N-API functions in AsyncWorker::Execute()
- Use ThreadSafeFunction for callbacks from worker threads
- Always Acquire/Release ThreadSafeFunction properly
- Use AsyncProgressWorker for progress updates

### Medium-Impact Patterns

**Error Handling:**
- Enable C++ exceptions for cleaner error handling
- Check env.IsExceptionPending() after N-API calls
- Return immediately after throwing exceptions

**Performance:**
- Minimize data marshaling overhead between JS and C++
- Use buffers to bypass V8 heap copying
- Batch small operations to reduce per-call overhead

### Lower-Impact Patterns

**Build Systems:**
- Use node-gyp for standard setup, cmake-js for CMake projects
- Provide prebuilt binaries with prebuild/prebuildify

**Security:**
- Validate buffer sizes before use
- Bounds-check array access
- Sanitize external input

## References

Full documentation with code examples is available in:

- `references/node-addon-guidelines.md` - Complete guide with all patterns
- `references/rules/` - Individual rule files organized by category

To look up a specific pattern, grep the rules directory:
```
grep -l "AsyncWorker" references/rules/
grep -l "memory" references/rules/
grep -l "ThreadSafe" references/rules/
```

## Rule Categories in `references/rules/`

- `napi-*` - Node-API fundamentals and version compatibility
- `memory-*` - Memory management, handle scopes, and GC integration
- `async-*` - Thread safety and async operation patterns
- `error-*` - Exception handling and error propagation
- `perf-*` - Performance optimization and data marshaling
- `build-*` - Build systems and compilation configuration
- `security-*` - Input validation and buffer safety
- `pitfall-*` - Common mistakes and anti-patterns to avoid
