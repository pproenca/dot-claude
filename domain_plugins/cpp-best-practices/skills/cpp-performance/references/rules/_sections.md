# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Memory Management (memory)

**Impact:** CRITICAL
**Description:** Proper memory management prevents leaks, reduces fragmentation, and enables efficient resource usage. Smart pointers and RAII patterns eliminate entire classes of bugs while improving performance through deterministic cleanup.

## 2. Compile Time Optimization (compile)

**Impact:** CRITICAL
**Description:** Reducing compile times improves developer productivity. Minimizing binary size improves cache efficiency and deployment. Header organization and template instantiation control are key factors.

## 3. Concurrency Patterns (async)

**Impact:** HIGH
**Description:** Correct concurrent code maximizes hardware utilization. Modern C++ provides high-level abstractions that are both safer and faster than manual thread management. Lock-free patterns eliminate contention bottlenecks.

## 4. Cache Optimization (cache)

**Impact:** MEDIUM-HIGH
**Description:** Memory access patterns dominate performance on modern CPUs. Cache-friendly data layouts and access patterns can improve performance by 10-100x compared to cache-hostile code.

## 5. Algorithm Selection (algo)

**Impact:** MEDIUM
**Description:** Choosing the right algorithm and data structure provides asymptotic improvements. Standard library algorithms are heavily optimized and should be preferred over hand-rolled alternatives.

## 6. I/O Performance (io)

**Impact:** MEDIUM
**Description:** I/O operations are often the slowest part of an application. Buffering, batching, and asynchronous I/O patterns minimize blocking and maximize throughput.

## 7. Code Generation (codegen)

**Impact:** LOW-MEDIUM
**Description:** Compiler hints and code organization can improve generated code quality. Inlining, branch prediction hints, and linkage control enable better optimization.

## 8. Template Metaprogramming (template)

**Impact:** LOW
**Description:** Advanced template techniques enable compile-time computation and zero-overhead abstractions. Use sparingly as they increase compile times and code complexity.
