---
name: nodejs-addon-cpp-best-practices
description: Node.js native addon (C++) performance optimization guidelines. This skill should be used when writing, reviewing, or refactoring native addons to ensure optimal performance patterns. Triggers on tasks involving N-API, node-addon-api, V8 integration, or C++ performance in Node.js.
---

# Node.js Native Addon (C++) Best Practices

Comprehensive performance optimization guide for Node.js native addons written in C++, designed for AI agents and LLMs. Contains 38 rules across 8 categories, prioritized by impact from critical (JS/C++ boundary optimization, memory management) to medium (N-API patterns, build configuration).

## When to Apply

Reference these guidelines when:
- Writing new Node.js native addons in C++
- Optimizing JS/C++ boundary crossings for performance
- Implementing async workers and thread-safe callbacks
- Managing memory between V8 heap and native allocations
- Reviewing native addon code for performance issues

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | JS/C++ Boundary Optimization | CRITICAL | `boundary-` |
| 2 | Memory Management | CRITICAL | `mem-` |
| 3 | Thread Safety & Async | CRITICAL | `async-` |
| 4 | Data Conversion | HIGH | `conv-` |
| 5 | Handle Management | HIGH | `handle-` |
| 6 | Object Wrapping | MEDIUM-HIGH | `wrap-` |
| 7 | N-API Best Practices | MEDIUM | `napi-` |
| 8 | Build & Module Loading | MEDIUM | `build-` |

## Quick Reference

### 1. JS/C++ Boundary Optimization (CRITICAL)

- `boundary-batch-calls` - Batch multiple operations into single native call
- `boundary-avoid-callbacks` - Avoid frequent JS callback invocations from C++
- `boundary-cache-accessors` - Cache property accessors to avoid repeated lookups
- `boundary-typed-arrays` - Use TypedArrays for bulk data transfer
- `boundary-return-primitives` - Return primitives instead of objects when possible

### 2. Memory Management (CRITICAL)

- `mem-external-memory` - Register external memory with V8 for accurate GC
- `mem-buffer-pool` - Use buffer pools to avoid allocation overhead
- `mem-prevent-leaks` - Prevent leaks with correct ref counting
- `mem-avoid-string-copy` - Avoid string copies at boundary
- `mem-arena-allocator` - Use arena allocators for batch allocations

### 3. Thread Safety & Async (CRITICAL)

- `async-worker-threads` - Use AsyncWorker for CPU-intensive tasks
- `async-thread-safe-function` - Use ThreadSafeFunction for cross-thread callbacks
- `async-parallel-workers` - Parallelize independent work across workers
- `async-avoid-mutex-contention` - Minimize mutex contention in hot paths
- `async-libuv-pool-size` - Configure UV_THREADPOOL_SIZE for workload

### 4. Data Conversion (HIGH)

- `conv-zero-copy-buffer` - Use zero-copy Buffer access patterns
- `conv-string-encoding` - Use efficient string encoding methods
- `conv-object-serialization` - Minimize object serialization at boundary
- `conv-number-types` - Use appropriate number types for precision
- `conv-avoid-json` - Avoid JSON serialization for structured data

### 5. Handle Management (HIGH)

- `handle-scope-basics` - Use HandleScope to prevent handle leaks
- `handle-escape-return` - Use EscapableHandleScope for return values
- `handle-persistent-refs` - Use Persistent for long-lived references
- `handle-check-types` - Check types before converting to avoid crashes
- `handle-minimize-creation` - Minimize handle creation in loops

### 6. Object Wrapping (MEDIUM-HIGH)

- `wrap-prevent-gc` - Prevent GC during native operations
- `wrap-weak-pointers` - Use weak pointers for observer patterns
- `wrap-destructor-cleanup` - Implement proper destructor cleanup

### 7. N-API Best Practices (MEDIUM)

- `napi-use-addon-api` - Use node-addon-api over raw N-API
- `napi-error-handling` - Handle errors with exceptions
- `napi-version-compatibility` - Target appropriate N-API version
- `napi-define-class` - Use DefineClass for object-oriented APIs
- `napi-cleanup-hooks` - Register cleanup hooks for module unload

### 8. Build & Module Loading (MEDIUM)

- `build-optimize-flags` - Use optimal compiler flags
- `build-prebuild-binaries` - Distribute prebuilt binaries
- `build-minimize-binary` - Minimize binary size
- `build-context-aware` - Use context-aware addons
- `build-lazy-init` - Use lazy initialization for heavy resources

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/boundary-batch-calls.md
rules/_sections.md
```

Each rule file contains:
- Brief explanation of why it matters
- Incorrect code example with explanation
- Correct code example with explanation
- Additional context and references

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md`
