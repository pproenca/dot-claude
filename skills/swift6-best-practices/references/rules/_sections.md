# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Concurrency & Data-Race Safety (concur)

**Impact:** CRITICAL
**Description:** Swift 6 enforces data-race safety at compile time. Proper use of actors, Sendable, and isolation annotations prevents crashes and undefined behavior.

## 2. Memory Management & ARC (memory)

**Impact:** CRITICAL
**Description:** ARC overhead and retain cycles are major performance killers. Proper use of weak/unowned references and value types eliminates memory leaks and reduces reference counting overhead.

## 3. Ownership & Noncopyable Types (owner)

**Impact:** HIGH
**Description:** Swift's ownership system with ~Copyable, borrowing, and consuming enables zero-copy resource management and prevents use-after-free bugs at compile time.

## 4. Value Types & Copy-on-Write (value)

**Impact:** MEDIUM-HIGH
**Description:** Structs with copy-on-write semantics provide value semantics with reference type performance. Proper implementation avoids quadratic copying behavior.

## 5. Collection Performance (collect)

**Impact:** MEDIUM
**Description:** Choosing the right collection type and using lazy sequences can provide 2-10x performance improvements for data-intensive operations.

## 6. Async/Await & Structured Concurrency (async)

**Impact:** MEDIUM
**Description:** Structured concurrency with TaskGroups and async let provides automatic cancellation, proper resource cleanup, and controlled parallelism.

## 7. Compiler Optimization (optim)

**Impact:** LOW-MEDIUM
**Description:** Annotations like @inlinable, final, and @frozen enable aggressive compiler optimizations including devirtualization and cross-module inlining.

## 8. Error Handling & Type Safety (error)

**Impact:** LOW
**Description:** Typed throws in Swift 6 enable exhaustive error handling and eliminate existential boxing overhead for error types.
