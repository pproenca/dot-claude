# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. JS/C++ Boundary Optimization (boundary)

**Impact:** CRITICAL
**Description:** Every JS↔C++ crossing has significant overhead (~100-1000ns). Minimizing boundary crossings and batching operations yields the largest performance gains.

## 2. Memory Management (mem)

**Impact:** CRITICAL
**Description:** Incorrect memory handling causes V8 heap pressure, native memory leaks, and GC pauses that stall the event loop.

## 3. Thread Safety & Async (async)

**Impact:** CRITICAL
**Description:** Blocking the main thread freezes the event loop. Async workers and thread-safe callbacks enable true parallelism without blocking.

## 4. Data Conversion (conv)

**Impact:** HIGH
**Description:** Converting between JS and C++ types is expensive. Zero-copy techniques and efficient encoding reduce CPU and memory overhead.

## 5. Handle Management (handle)

**Impact:** HIGH
**Description:** V8 handles must be properly scoped and escaped to prevent crashes and memory leaks. HandleScope misuse is a common source of bugs.

## 6. Object Wrapping (wrap)

**Impact:** MEDIUM-HIGH
**Description:** Wrapping C++ objects for JS access requires correct prevent GC handling, weak references, and destructor patterns.

## 7. N-API Best Practices (napi)

**Impact:** MEDIUM
**Description:** N-API provides ABI stability across Node versions. Using it correctly avoids version-specific bugs and simplifies maintenance.

## 8. Build & Module Loading (build)

**Impact:** MEDIUM
**Description:** Optimizing build configuration and module loading reduces binary size, startup time, and cross-platform issues.
