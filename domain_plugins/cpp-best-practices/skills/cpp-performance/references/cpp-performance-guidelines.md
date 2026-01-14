# C++ Best Practices

**Version 0.1.0**
January 2026

> **Note:**
> This document is designed for AI agents and LLMs to follow when maintaining,
> generating, or refactoring modern C++ codebases. Guidance is optimized for
> automation and consistency by AI-assisted workflows.

---

## Abstract

Comprehensive performance optimization guide for modern C++ applications (C++17/20/23), designed for AI agents and LLMs. Contains 37+ rules across 8 categories, prioritized by impact from critical (memory management, compile-time optimization) to incremental (template metaprogramming). Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct implementations, and specific impact metrics.

---

## Table of Contents

1. [Memory Management](#1-memory-management) — **CRITICAL**
2. [Compile Time Optimization](#2-compile-time-optimization) — **CRITICAL**
3. [Concurrency Patterns](#3-concurrency-patterns) — **HIGH**
4. [Cache Optimization](#4-cache-optimization) — **MEDIUM-HIGH**
5. [Algorithm Selection](#5-algorithm-selection) — **MEDIUM**
6. [I/O Performance](#6-io-performance) — **MEDIUM**
7. [Code Generation](#7-code-generation) — **LOW-MEDIUM**
8. [Template Metaprogramming](#8-template-metaprogramming) — **LOW**

---

## 1. Memory Management

**Impact: CRITICAL**

Proper memory management prevents leaks, reduces fragmentation, and enables efficient resource usage. Smart pointers and RAII patterns eliminate entire classes of bugs.

### 1.1 Use Smart Pointers Over Raw Pointers

Use `std::unique_ptr` for exclusive ownership and `std::shared_ptr` for shared ownership.

**Incorrect:**
```cpp
Data* data = new Data();
process(data);
delete data;  // Easy to forget, exception-unsafe
```

**Correct:**
```cpp
auto data = std::make_unique<Data>();
process(data.get());
// Automatically deleted
```

### 1.2 Prefer make_unique/make_shared Over new

Exception-safe and more efficient (single allocation for shared_ptr).

**Incorrect:**
```cpp
auto ptr = std::shared_ptr<Data>(new Data());  // Two allocations
```

**Correct:**
```cpp
auto ptr = std::make_shared<Data>();  // Single allocation
```

### 1.3 Use Move Semantics to Avoid Copies

Transfer ownership instead of copying expensive resources.

**Incorrect:**
```cpp
result.push_back(temp);  // Copies temp
```

**Correct:**
```cpp
result.push_back(std::move(temp));  // Moves temp
```

### 1.4 Reserve Container Capacity

Pre-allocate when size is known to eliminate reallocations.

**Incorrect:**
```cpp
std::vector<Widget> widgets;
for (int i = 0; i < 10000; ++i) {
    widgets.push_back(Widget(i));  // ~14 reallocations
}
```

**Correct:**
```cpp
std::vector<Widget> widgets;
widgets.reserve(10000);  // Single allocation
for (int i = 0; i < 10000; ++i) {
    widgets.push_back(Widget(i));
}
```

### 1.5 Use string_view for Non-Owning String Parameters

Avoids allocations when called with literals or substrings.

**Incorrect:**
```cpp
void log(const std::string& message);  // Allocates for literals
log("Hello");  // Creates temporary string
```

**Correct:**
```cpp
void log(std::string_view message);  // No allocation
log("Hello");  // Zero-copy
```

### 1.6 Use span for Non-Owning Array Parameters

Type-safe, works with any contiguous container.

**Incorrect:**
```cpp
void process(int* data, size_t size);  // Loses size, error-prone
```

**Correct:**
```cpp
void process(std::span<int> data);  // Size included, type-safe
```

---

## 2. Compile Time Optimization

**Impact: CRITICAL**

Reducing compile times improves developer productivity. Header organization and template control are key.

### 2.1 Use Forward Declarations

Break dependency chains to reduce compile times.

**Incorrect:**
```cpp
#include "database.h"  // 500+ lines
class Widget { Database* db_; };
```

**Correct:**
```cpp
class Database;  // Forward declaration
class Widget { Database* db_; };
```

### 2.2 Use extern template for Common Instantiations

Eliminate redundant template instantiation across translation units.

**Header:**
```cpp
extern template int sum(const std::vector<int>&);
```

**Implementation:**
```cpp
template int sum(const std::vector<int>&);  // Instantiate once
```

### 2.3 Use Precompiled Headers

Cache stable dependencies to avoid re-parsing.

```cpp
// pch.h
#include <vector>
#include <string>
#include <memory>
// Parsed once, reused everywhere
```

### 2.4 Use if constexpr Instead of SFINAE

Clearer code, faster compilation.

**Incorrect:**
```cpp
template<typename T>
typename std::enable_if<std::is_integral<T>::value, T>::type
process(T value);
```

**Correct:**
```cpp
template<typename T>
T process(T value) {
    if constexpr (std::is_integral_v<T>) {
        return value * 2;
    }
}
```

### 2.5 Use C++20 Modules

Parse headers once, cache as binary.

```cpp
export module math_utils;
export double average(const std::vector<double>& v);
```

---

## 3. Concurrency Patterns

**Impact: HIGH**

Modern C++ provides safe, efficient threading abstractions.

### 3.1 Use jthread Over thread

Automatic joining, cooperative cancellation.

**Incorrect:**
```cpp
std::thread worker(task);
worker.join();  // Easy to forget
```

**Correct:**
```cpp
std::jthread worker(task);  // Auto-joins on destruction
```

### 3.2 Prefer atomic Over mutex for Simple Types

Lock-free, 10-100x faster for simple operations.

**Incorrect:**
```cpp
std::mutex mutex_;
void increment() {
    std::lock_guard lock(mutex_);
    ++value_;
}
```

**Correct:**
```cpp
std::atomic<int> value_;
void increment() {
    value_.fetch_add(1, std::memory_order_relaxed);
}
```

### 3.3 Use shared_mutex for Read-Heavy Workloads

Allow concurrent readers.

```cpp
mutable std::shared_mutex mutex_;
std::string get(const std::string& key) const {
    std::shared_lock lock(mutex_);  // Multiple readers OK
    return data_[key];
}
```

### 3.4 Avoid False Sharing

Align to cache line boundaries.

```cpp
struct alignas(64) AlignedCounter {
    std::atomic<int> value{0};
};
```

### 3.5 Use Parallel STL Algorithms

Automatic parallelization for large datasets.

```cpp
std::sort(std::execution::par, data.begin(), data.end());
```

---

## 4. Cache Optimization

**Impact: MEDIUM-HIGH**

Memory access patterns dominate modern CPU performance.

### 4.1 Prefer Contiguous Containers

Cache-friendly `vector` over cache-hostile `list`.

### 4.2 Use Structure of Arrays for Hot Data

Keep frequently accessed fields together.

**Incorrect (AoS):**
```cpp
struct Particle { float x, y, z; int id; std::string name; };
std::vector<Particle> particles;
```

**Correct (SoA):**
```cpp
struct Particles {
    std::vector<float> x, y, z;  // Hot data together
    std::vector<int> id;          // Cold data separate
};
```

### 4.3 Minimize Pointer Chasing

Use indices instead of pointers, pool allocation.

### 4.4 Optimize Memory Access Patterns

Row-major iteration for C++ arrays.

**Incorrect:**
```cpp
for (int j = 0; j < N; ++j)
    for (int i = 0; i < N; ++i)
        sum += matrix[i][j];  // Column-major, cache unfriendly
```

**Correct:**
```cpp
for (int i = 0; i < N; ++i)
    for (int j = 0; j < N; ++j)
        sum += matrix[i][j];  // Row-major, cache friendly
```

---

## 5. Algorithm Selection

**Impact: MEDIUM**

Right algorithms provide asymptotic improvements.

### 5.1 Use std::ranges

Composable, lazy evaluation.

```cpp
auto result = data
    | std::views::filter([](int x) { return x > 0; })
    | std::views::transform([](int x) { return x * x; });
```

### 5.2 Use unordered Containers for O(1) Lookups

Hash-based vs tree-based when order not needed.

### 5.3 Use flat Containers for Small Data

Cache-friendly for < 100-1000 elements.

### 5.4 Prefer STL Algorithms Over Hand-Rolled Loops

Optimized, clear intent.

### 5.5 Use Early Exit Algorithms

`any_of`, `find_if` stop at first match.

---

## 6. I/O Performance

**Impact: MEDIUM**

Minimize syscall overhead, maximize throughput.

### 6.1 Use Buffered I/O

Batch operations to reduce syscalls.

### 6.2 Use std::format

Faster than iostreams, type-safe.

```cpp
std::format("User {} has value {:.2f}", name, value);
```

### 6.3 Use Asynchronous I/O

Don't block threads waiting for I/O.

### 6.4 Use Binary I/O for Structured Data

5-10x faster than text parsing.

---

## 7. Code Generation

**Impact: LOW-MEDIUM**

Help the compiler generate better code.

### 7.1 Use Inline Hints Appropriately

Small functions, hot paths.

### 7.2 Use constexpr

Move computation to compile time.

```cpp
constexpr int factorial(int n) {
    return n <= 1 ? 1 : n * factorial(n - 1);
}
```

### 7.3 Use Branch Prediction Hints

`[[likely]]` and `[[unlikely]]` for expected branches.

### 7.4 Use restrict for Non-Aliasing Pointers

Enable vectorization.

---

## 8. Template Metaprogramming

**Impact: LOW**

Advanced patterns for specific use cases.

### 8.1 Use Concepts

Clear constraints, better errors.

```cpp
template<std::integral T>
T add(T a, T b) { return a + b; }
```

### 8.2 Use CRTP for Static Polymorphism

Zero-overhead polymorphism.

### 8.3 Use Type Erasure for Runtime Flexibility

`std::function`, `std::any` for heterogeneous containers.

---

## References

1. [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
2. [cppreference.com](https://en.cppreference.com/)
3. [Compiler Explorer](https://godbolt.org/)
4. [What Every Programmer Should Know About Memory](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
5. [Data-Oriented Design](https://www.dataorienteddesign.com/dodbook/)
