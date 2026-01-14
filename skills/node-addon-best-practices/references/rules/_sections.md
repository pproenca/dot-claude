# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Node-API & N-API Fundamentals (napi)

**Impact:** CRITICAL
**Description:** V8 API changes break addons on every Node.js major release, requiring rebuild and retest. N-API eliminates this entirely - compile once, run on all supported Node.js versions.

## 2. Memory Management & GC Integration (memory)

**Impact:** CRITICAL
**Description:** Memory errors in native addons cause 70% of addon crashes. Proper handle scopes and reference counting eliminate use-after-free, leaks, and GC-related crashes entirely.

## 3. Thread Safety & Async Operations (async)

**Impact:** HIGH
**Description:** V8 is not thread-safe - calling N-API from worker threads causes immediate crashes. AsyncWorker and ThreadSafeFunction provide safe patterns for 100% of async use cases.

## 4. Error Handling & Exception Management (error)

**Impact:** MEDIUM-HIGH
**Description:** Unchecked napi_status leads to null pointer dereferences and silent failures. Proper error handling catches 100% of N-API failures before they cause crashes.

## 5. Performance Optimization (perf)

**Impact:** MEDIUM
**Description:** JS-native boundary crossing costs ~1-5 microseconds per call. Batching and buffer reuse can reduce overhead by 10-50x for data-intensive operations.

## 6. Build Systems & Compilation (build)

**Impact:** MEDIUM
**Description:** Prebuilt binaries eliminate npm install compilation failures for 95% of users. Proper build configuration reduces installation time from minutes to seconds.

## 7. Security & Input Validation (security)

**Impact:** LOW-MEDIUM
**Description:** Buffer overflows in native code bypass JavaScript safety. Proper bounds checking prevents 100% of buffer overflow vulnerabilities.

## 8. Common Pitfalls & Anti-Patterns (pitfall)

**Impact:** LOW
**Description:** Common mistakes like blocking the event loop or storing env cause subtle bugs. Avoiding these patterns prevents hard-to-debug production issues.
