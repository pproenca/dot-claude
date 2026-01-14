# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Node-API & N-API Fundamentals (napi)

**Impact:** CRITICAL
**Description:** Core N-API patterns for stable ABI, version compatibility, and type-safe JavaScript-C++ interop.

## 2. Memory Management & GC Integration (memory)

**Impact:** CRITICAL
**Description:** Handle scopes, references, external memory tracking, and finalizers for leak-free addons.

## 3. Thread Safety & Async Operations (async)

**Impact:** HIGH
**Description:** AsyncWorker, ThreadSafeFunction, and safe cross-thread communication patterns.

## 4. Error Handling & Exception Management (error)

**Impact:** MEDIUM-HIGH
**Description:** Exception modes, status checking, and consistent error propagation strategies.

## 5. Performance Optimization (perf)

**Impact:** MEDIUM
**Description:** Minimizing marshaling overhead, buffer usage, and batching for optimal throughput.

## 6. Build Systems & Compilation (build)

**Impact:** MEDIUM
**Description:** node-gyp, cmake-js, prebuild, and cross-platform compilation configuration.

## 7. Security & Input Validation (security)

**Impact:** LOW-MEDIUM
**Description:** Buffer validation, bounds checking, and input sanitization for secure addons.

## 8. Common Pitfalls & Anti-Patterns (pitfall)

**Impact:** LOW
**Description:** Avoiding event loop blocking, memory leaks, and thread-safety violations.
