# C++ Best Practices

**Version 0.2.0**
C++ Core Guidelines & Community Best Practices
January 2026

> **Note:**
> This document is designed for AI agents and LLMs to follow when maintaining,
> generating, or refactoring modern C++ codebases. Guidance is optimized for
> automation and consistency by AI-assisted workflows.

---

## Abstract

Comprehensive performance optimization guide for modern C++ applications (C++17/20/23), designed for AI agents and LLMs. Contains 47 rules across 8 categories, prioritized by impact from critical (memory management, compile-time optimization) to incremental (template metaprogramming). Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct implementations, and specific impact metrics to guide automated refactoring and code generation.

---

## Table of Contents

1. [Memory Management](#1-memory-management) — **CRITICAL**
   - 1.1 [Use Smart Pointers Over Raw Pointers](#11-use-smart-pointers-over-raw-pointers)
   - 1.2 [Prefer make_unique/make_shared Over new](#12-prefer-make_uniquemake_shared-over-new)
   - 1.3 [Use Move Semantics to Avoid Copies](#13-use-move-semantics-to-avoid-copies)
   - 1.4 [Reserve Container Capacity](#14-reserve-container-capacity)
   - 1.5 [Use string_view for Non-Owning String Parameters](#15-use-string_view-for-non-owning-string-parameters)
   - 1.6 [Use span for Non-Owning Array Parameters](#16-use-span-for-non-owning-array-parameters)
2. [Compile Time Optimization](#2-compile-time-optimization) — **CRITICAL**
   - 2.1 [Use Forward Declarations](#21-use-forward-declarations)
   - 2.2 [Use extern template for Common Instantiations](#22-use-extern-template-for-common-instantiations)
   - 2.3 [Use Precompiled Headers](#23-use-precompiled-headers)
   - 2.4 [Use if constexpr Instead of SFINAE](#24-use-if-constexpr-instead-of-sfinae)
   - 2.5 [Use C++20 Modules](#25-use-c20-modules)
3. [Concurrency Patterns](#3-concurrency-patterns) — **HIGH**
   - 3.1 [Use jthread Over thread](#31-use-jthread-over-thread)
   - 3.2 [Prefer atomic Over mutex for Simple Types](#32-prefer-atomic-over-mutex-for-simple-types)
   - 3.3 [Use shared_mutex for Read-Heavy Workloads](#33-use-shared_mutex-for-read-heavy-workloads)
   - 3.4 [Avoid False Sharing](#34-avoid-false-sharing)
   - 3.5 [Use Parallel STL Algorithms](#35-use-parallel-stl-algorithms)
4. [Cache Optimization](#4-cache-optimization) — **MEDIUM-HIGH**
   - 4.1 [Prefer Contiguous Containers](#41-prefer-contiguous-containers)
   - 4.2 [Use Structure of Arrays for Hot Data](#42-use-structure-of-arrays-for-hot-data)
   - 4.3 [Minimize Pointer Chasing](#43-minimize-pointer-chasing)
   - 4.4 [Optimize Memory Access Patterns](#44-optimize-memory-access-patterns)
5. [Algorithm Selection](#5-algorithm-selection) — **MEDIUM**
   - 5.1 [Use std::ranges](#51-use-stdranges)
   - 5.2 [Use unordered Containers for O(1) Lookups](#52-use-unordered-containers-for-o1-lookups)
   - 5.3 [Use flat Containers for Small Data](#53-use-flat-containers-for-small-data)
   - 5.4 [Prefer STL Algorithms Over Hand-Rolled Loops](#54-prefer-stl-algorithms-over-hand-rolled-loops)
   - 5.5 [Use Early Exit Algorithms](#55-use-early-exit-algorithms)
   - 5.6 [Use Small Buffer Optimization](#56-use-small-buffer-optimization)
   - 5.7 [Use Lookup Tables for Repeated Computations](#57-use-lookup-tables-for-repeated-computations)
6. [I/O Performance](#6-io-performance) — **MEDIUM**
   - 6.1 [Use Buffered I/O](#61-use-buffered-io)
   - 6.2 [Use std::format](#62-use-stdformat)
   - 6.3 [Use Asynchronous I/O](#63-use-asynchronous-io)
   - 6.4 [Use Binary I/O for Structured Data](#64-use-binary-io-for-structured-data)
   - 6.5 [Use Memory-Mapped Files for Large File Access](#65-use-memory-mapped-files-for-large-file-access)
   - 6.6 [Preallocate File Space](#66-preallocate-file-space)
   - 6.7 [Use Direct I/O for Large Sequential Transfers](#67-use-direct-io-for-large-sequential-transfers)
7. [Code Generation](#7-code-generation) — **LOW-MEDIUM**
   - 7.1 [Use Inline Hints Appropriately](#71-use-inline-hints-appropriately)
   - 7.2 [Use constexpr](#72-use-constexpr)
   - 7.3 [Use Branch Prediction Hints](#73-use-branch-prediction-hints)
   - 7.4 [Use restrict for Non-Aliasing Pointers](#74-use-restrict-for-non-aliasing-pointers)
   - 7.5 [Enable Link-Time Optimization](#75-enable-link-time-optimization)
   - 7.6 [Use noexcept for Compiler Optimizations](#76-use-noexcept-for-compiler-optimizations)
   - 7.7 [Use Standard Attributes](#77-use-standard-attributes)
   - 7.8 [Structure Code for Auto-Vectorization](#78-structure-code-for-auto-vectorization)
   - 7.9 [Use Branchless Programming for Hot Paths](#79-use-branchless-programming-for-hot-paths)
   - 7.10 [Use Profile-Guided Optimization](#710-use-profile-guided-optimization)
8. [Template Metaprogramming](#8-template-metaprogramming) — **LOW**
   - 8.1 [Use Concepts](#81-use-concepts)
   - 8.2 [Use CRTP for Static Polymorphism](#82-use-crtp-for-static-polymorphism)
   - 8.3 [Use Type Erasure for Runtime Flexibility](#83-use-type-erasure-for-runtime-flexibility)

---

## 1. Memory Management

**Impact: CRITICAL**

Proper memory management prevents leaks, reduces fragmentation, and enables efficient resource usage. Smart pointers and RAII patterns eliminate entire classes of bugs while improving performance through deterministic cleanup.

### 1.1 Use Smart Pointers Over Raw Pointers

Raw pointers require manual memory management and are prone to leaks, double-frees, and dangling pointer bugs. Use `std::unique_ptr` for exclusive ownership and `std::shared_ptr` for shared ownership.

**Incorrect (manual memory management):**

```cpp
class ResourceManager {
    Data* data_;
public:
    ResourceManager() : data_(new Data()) {}
    ~ResourceManager() {
        delete data_;  // Easy to forget, exception-unsafe
    }
    // Missing copy/move operations - rule of 5 violation
};

void processData() {
    Data* data = new Data();
    process(data);
    // If process() throws, memory leaks
    delete data;
}
```

**Correct (RAII with smart pointers):**

```cpp
class ResourceManager {
    std::unique_ptr<Data> data_;
public:
    ResourceManager() : data_(std::make_unique<Data>()) {}
    // Destructor, copy, move automatically handled correctly
};

void processData() {
    auto data = std::make_unique<Data>();
    process(data.get());
}  // Automatically deleted, even if exception thrown
```

**Choosing the right smart pointer:**

```cpp
// Exclusive ownership - use unique_ptr (zero overhead)
auto exclusive = std::make_unique<Widget>();

// Shared ownership - use shared_ptr (reference counting overhead)
auto shared = std::make_shared<Widget>();

// Non-owning reference to shared_ptr - use weak_ptr
std::weak_ptr<Widget> weak = shared;
```

### 1.2 Prefer make_unique/make_shared Over new

The make functions are exception-safe and more efficient. `make_shared` performs a single allocation for both the control block and the object.

**Incorrect (two allocations, exception-unsafe):**

```cpp
auto ptr = std::shared_ptr<Data>(new Data());  // Two allocations
func(std::shared_ptr<A>(new A()), std::shared_ptr<B>(new B()));  // May leak
```

**Correct (single allocation, exception-safe):**

```cpp
auto ptr = std::make_shared<Data>();  // Single allocation

// Exception-safe - no leak possible
func(std::make_shared<A>(), std::make_shared<B>());
```

**Exception safety example:**

```cpp
// Incorrect: If std::make_shared<B>() throws after new A() but before
// shared_ptr constructor, A leaks
void dangerous(std::shared_ptr<A>(new A()), std::shared_ptr<B>(new B()));

// Correct: make_shared is atomic, no interleaving possible
void safe(std::make_shared<A>(), std::make_shared<B>());
```

### 1.3 Use Move Semantics to Avoid Copies

Transfer ownership instead of copying expensive resources. Mark move constructors and assignment operators as noexcept to enable optimizations.

**Incorrect (unnecessary copies):**

```cpp
std::vector<std::string> buildStrings() {
    std::vector<std::string> result;
    std::string temp = "Hello, World!";
    result.push_back(temp);  // Copies temp
    return result;
}

void appendData(std::vector<Data>& dest, std::vector<Data> source) {
    for (auto& item : source) {
        dest.push_back(item);  // Copies each item
    }
}
```

**Correct (move semantics):**

```cpp
std::vector<std::string> buildStrings() {
    std::vector<std::string> result;
    std::string temp = "Hello, World!";
    result.push_back(std::move(temp));  // Moves temp
    return result;  // NRVO or move on return
}

void appendData(std::vector<Data>& dest, std::vector<Data> source) {
    for (auto& item : source) {
        dest.push_back(std::move(item));  // Moves each item
    }
}

// Or use insert with move iterators
void appendDataBetter(std::vector<Data>& dest, std::vector<Data> source) {
    dest.insert(dest.end(),
                std::make_move_iterator(source.begin()),
                std::make_move_iterator(source.end()));
}
```

### 1.4 Reserve Container Capacity

Pre-allocate when size is known to eliminate reallocations. Vector reallocations copy/move all elements and invalidate iterators.

**Incorrect (multiple reallocations):**

```cpp
std::vector<Widget> widgets;
for (int i = 0; i < 10000; ++i) {
    widgets.push_back(Widget(i));  // ~14 reallocations, copies everything
}

std::string buildMessage(const std::vector<std::string>& parts) {
    std::string result;
    for (const auto& part : parts) {
        result += part;  // Multiple reallocations
    }
    return result;
}
```

**Correct (pre-allocation):**

```cpp
std::vector<Widget> widgets;
widgets.reserve(10000);  // Single allocation
for (int i = 0; i < 10000; ++i) {
    widgets.push_back(Widget(i));  // No reallocations
}

std::string buildMessage(const std::vector<std::string>& parts) {
    size_t totalSize = 0;
    for (const auto& part : parts) totalSize += part.size();

    std::string result;
    result.reserve(totalSize);  // Single allocation
    for (const auto& part : parts) {
        result += part;
    }
    return result;
}
```

### 1.5 Use string_view for Non-Owning String Parameters

`std::string_view` provides a non-owning view into string data, avoiding allocations when called with literals or substrings.

**Incorrect (allocates for literals):**

```cpp
void log(const std::string& message);  // Allocates for literals
log("Hello");  // Creates temporary std::string

bool contains(const std::string& haystack, const std::string& needle);
// Substrings require allocation
contains(text, text.substr(0, 5));
```

**Correct (zero-copy with string_view):**

```cpp
void log(std::string_view message);  // No allocation
log("Hello");  // Zero-copy

bool contains(std::string_view haystack, std::string_view needle);
// Substrings are free
contains(text, std::string_view(text).substr(0, 5));

// String concatenation still needs allocation
std::string greeting(std::string_view name) {
    return std::string("Hello, ") + std::string(name);
}
```

### 1.6 Use span for Non-Owning Array Parameters

`std::span` provides a type-safe, non-owning view into contiguous memory. Works with vectors, arrays, and C-style arrays.

**Incorrect (loses size information):**

```cpp
void process(int* data, size_t size);  // Loses size, error-prone
void process(std::vector<int>& data);  // Forces vector usage

int arr[] = {1, 2, 3};
process(arr, 3);  // Manual size tracking
```

**Correct (type-safe with span):**

```cpp
void process(std::span<int> data);  // Size included, type-safe

int arr[] = {1, 2, 3};
process(arr);  // Deduces size automatically

std::vector<int> vec = {1, 2, 3};
process(vec);  // Works with vector

std::array<int, 3> stdArr = {1, 2, 3};
process(stdArr);  // Works with std::array

// Subspans are free
process(std::span(vec).subspan(1, 2));
```

---

## 2. Compile Time Optimization

**Impact: CRITICAL**

Reducing compile times improves developer productivity. Minimizing binary size improves cache efficiency and deployment. Header organization and template instantiation control are key factors.

### 2.1 Use Forward Declarations

Break dependency chains to reduce compile times. Only include headers when the full type definition is needed.

**Incorrect (unnecessary includes):**

```cpp
// widget.h
#include "database.h"    // 500+ lines
#include "network.h"     // 300+ lines
#include "serializer.h"  // 200+ lines

class Widget {
    Database* db_;        // Only needs pointer
    Network* network_;    // Only needs pointer
    Serializer* serial_;  // Only needs pointer
};
```

**Correct (forward declarations):**

```cpp
// widget.h
class Database;   // Forward declaration
class Network;    // Forward declaration
class Serializer; // Forward declaration

class Widget {
    Database* db_;
    Network* network_;
    Serializer* serial_;
};

// widget.cpp - include only where needed
#include "database.h"
#include "network.h"
#include "serializer.h"
```

### 2.2 Use extern template for Common Instantiations

Eliminate redundant template instantiation across translation units. Explicitly instantiate common specializations in one place.

**Incorrect (instantiated in every TU):**

```cpp
// util.h
template<typename T>
T sum(const std::vector<T>& v) {
    return std::accumulate(v.begin(), v.end(), T{});
}
// Instantiated in every .cpp that uses sum<int>
```

**Correct (explicit instantiation):**

```cpp
// util.h
template<typename T>
T sum(const std::vector<T>& v) {
    return std::accumulate(v.begin(), v.end(), T{});
}
extern template int sum(const std::vector<int>&);
extern template double sum(const std::vector<double>&);

// util.cpp
template int sum(const std::vector<int>&);      // Instantiate once
template double sum(const std::vector<double>&); // Instantiate once
```

### 2.3 Use Precompiled Headers

Cache stable dependencies to avoid re-parsing. Include standard library and third-party headers that rarely change.

**CMake setup:**

```cmake
target_precompile_headers(myproject PRIVATE
    <vector>
    <string>
    <memory>
    <unordered_map>
    <algorithm>
    "third_party/json.hpp"
)
```

**Manual pch.h:**

```cpp
// pch.h - precompiled header
#pragma once

// Standard library
#include <vector>
#include <string>
#include <memory>
#include <unordered_map>
#include <algorithm>
#include <functional>

// Stable third-party
#include <fmt/format.h>
#include <nlohmann/json.hpp>

// Don't include frequently changing project headers!
```

### 2.4 Use if constexpr Instead of SFINAE

`if constexpr` provides clearer code and faster compilation than SFINAE-based approaches.

**Incorrect (complex SFINAE):**

```cpp
template<typename T>
typename std::enable_if<std::is_integral<T>::value, T>::type
process(T value) {
    return value * 2;
}

template<typename T>
typename std::enable_if<!std::is_integral<T>::value, T>::type
process(T value) {
    return value;
}
```

**Correct (if constexpr):**

```cpp
template<typename T>
T process(T value) {
    if constexpr (std::is_integral_v<T>) {
        return value * 2;
    } else {
        return value;
    }
}

// More complex example
template<typename Container>
void print(const Container& c) {
    if constexpr (requires { c.size(); }) {
        std::cout << "Size: " << c.size() << "\n";
    }
    for (const auto& item : c) {
        if constexpr (requires { std::cout << item; }) {
            std::cout << item << " ";
        } else {
            std::cout << "[unprintable] ";
        }
    }
}
```

### 2.5 Use C++20 Modules

Modules parse headers once and cache as binary, dramatically reducing compile times for large projects.

**Module definition:**

```cpp
// math_utils.ixx
export module math_utils;

import <vector>;
import <numeric>;

export double average(const std::vector<double>& v) {
    if (v.empty()) return 0.0;
    return std::accumulate(v.begin(), v.end(), 0.0) / v.size();
}

export double standardDeviation(const std::vector<double>& v);
```

**Module usage:**

```cpp
// main.cpp
import math_utils;
import <iostream>;

int main() {
    std::vector<double> data = {1.0, 2.0, 3.0};
    std::cout << average(data) << "\n";
}
```

---

## 3. Concurrency Patterns

**Impact: HIGH**

Correct concurrent code maximizes hardware utilization. Modern C++ provides high-level abstractions that are both safer and faster than manual thread management. Lock-free patterns eliminate contention bottlenecks.

### 3.1 Use jthread Over thread

`std::jthread` provides automatic joining and cooperative cancellation, preventing resource leaks and simplifying thread management.

**Incorrect (manual join, easy to leak):**

```cpp
void worker() {
    std::thread t(task);
    // If exception thrown here, t.join() never called
    // std::terminate() on destruction
    t.join();
}

void cancellableWorker() {
    std::atomic<bool> stop{false};
    std::thread t([&stop] {
        while (!stop) {
            doWork();
        }
    });
    // Manual cancellation coordination
    stop = true;
    t.join();
}
```

**Correct (automatic join and cancellation):**

```cpp
void worker() {
    std::jthread t(task);
    // Automatically joins on destruction, even if exception thrown
}

void cancellableWorker() {
    std::jthread t([](std::stop_token stoken) {
        while (!stoken.stop_requested()) {
            doWork();
        }
    });
    // Automatic cancellation on destruction
    // Or explicit: t.request_stop();
}
```

### 3.2 Prefer atomic Over mutex for Simple Types

For simple shared state (counters, flags, pointers), `std::atomic` provides lock-free synchronization that's 10-100x faster than mutex-based solutions.

**Incorrect (mutex for simple counter):**

```cpp
class Counter {
    int value_ = 0;
    std::mutex mutex_;
public:
    void increment() {
        std::lock_guard<std::mutex> lock(mutex_);
        ++value_;  // Mutex overhead for single instruction
    }
    int get() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return value_;
    }
};
```

**Correct (atomic counter):**

```cpp
class Counter {
    std::atomic<int> value_{0};
public:
    void increment() {
        value_.fetch_add(1, std::memory_order_relaxed);
    }
    int get() const {
        return value_.load(std::memory_order_relaxed);
    }
};

// Memory ordering selection
counter.fetch_add(1, std::memory_order_relaxed);  // Counters, statistics
data.store(value, std::memory_order_release);     // Producer
auto v = data.load(std::memory_order_acquire);    // Consumer
```

### 3.3 Use shared_mutex for Read-Heavy Workloads

Allow multiple concurrent readers while maintaining exclusive write access.

**Incorrect (exclusive lock for reads):**

```cpp
class Cache {
    std::unordered_map<std::string, Data> data_;
    std::mutex mutex_;
public:
    Data get(const std::string& key) const {
        std::lock_guard lock(mutex_);  // Blocks other readers
        return data_.at(key);
    }
};
```

**Correct (shared lock for reads):**

```cpp
class Cache {
    std::unordered_map<std::string, Data> data_;
    mutable std::shared_mutex mutex_;
public:
    Data get(const std::string& key) const {
        std::shared_lock lock(mutex_);  // Multiple readers OK
        return data_.at(key);
    }
    void set(const std::string& key, Data value) {
        std::unique_lock lock(mutex_);  // Exclusive write
        data_[key] = std::move(value);
    }
};
```

### 3.4 Avoid False Sharing

False sharing occurs when threads modify variables on the same cache line, causing unnecessary cache invalidation.

**Incorrect (false sharing):**

```cpp
struct Counters {
    std::atomic<int> counter1{0};  // Same cache line
    std::atomic<int> counter2{0};  // Cache ping-pong
};
```

**Correct (cache line aligned):**

```cpp
struct alignas(64) AlignedCounter {
    std::atomic<int> value{0};
    char padding[64 - sizeof(std::atomic<int>)];
};

struct Counters {
    AlignedCounter counter1;  // Separate cache lines
    AlignedCounter counter2;  // No false sharing
};

// C++17 hardware_destructive_interference_size
struct alignas(std::hardware_destructive_interference_size) Counter {
    std::atomic<int> value{0};
};
```

### 3.5 Use Parallel STL Algorithms

Automatic parallelization for large datasets with execution policies.

**Sequential (single-threaded):**

```cpp
std::sort(data.begin(), data.end());
std::transform(in.begin(), in.end(), out.begin(), func);
auto sum = std::reduce(data.begin(), data.end());
```

**Parallel (multi-threaded):**

```cpp
#include <execution>

std::sort(std::execution::par, data.begin(), data.end());
std::transform(std::execution::par, in.begin(), in.end(), out.begin(), func);
auto sum = std::reduce(std::execution::par, data.begin(), data.end());

// Unsequenced (SIMD + parallel)
std::for_each(std::execution::par_unseq, data.begin(), data.end(), process);
```

---

## 4. Cache Optimization

**Impact: MEDIUM-HIGH**

Memory access patterns dominate performance on modern CPUs. Cache-friendly data layouts and access patterns can improve performance by 10-100x compared to cache-hostile code.

### 4.1 Prefer Contiguous Containers

`std::vector` and `std::array` provide cache-friendly contiguous storage. Avoid `std::list` for iteration-heavy workloads.

**Incorrect (linked list, cache-hostile):**

```cpp
std::list<Widget> widgets;  // Nodes scattered in memory
for (const auto& w : widgets) {
    process(w);  // Cache miss on every node
}
```

**Correct (vector, cache-friendly):**

```cpp
std::vector<Widget> widgets;  // Contiguous memory
for (const auto& w : widgets) {
    process(w);  // Sequential access, prefetching works
}
```

### 4.2 Use Structure of Arrays for Hot Data

When frequently accessing specific fields, Structure of Arrays (SoA) outperforms Array of Structures (AoS).

**Incorrect (AoS - cold data pollutes cache):**

```cpp
struct Particle {
    float x, y, z;           // Hot data (positions)
    int id;                  // Warm data
    std::string name;        // Cold data
    std::vector<int> tags;   // Cold data
};
std::vector<Particle> particles;

// Updating positions loads entire struct into cache
for (auto& p : particles) {
    p.x += velocity;
}
```

**Correct (SoA - hot data together):**

```cpp
struct Particles {
    std::vector<float> x, y, z;  // Hot data together
    std::vector<int> id;
    std::vector<std::string> name;
    std::vector<std::vector<int>> tags;

    void updatePositions(float velocity) {
        for (size_t i = 0; i < x.size(); ++i) {
            x[i] += velocity;  // Only x values in cache
        }
    }
};
```

### 4.3 Minimize Pointer Chasing

Use indices instead of pointers, pool allocation for related objects.

**Incorrect (pointer chasing):**

```cpp
struct Node {
    Node* left;
    Node* right;
    Data data;
};
// Traversal causes random memory access
```

**Correct (index-based):**

```cpp
struct Tree {
    std::vector<Data> data;
    std::vector<int> leftChild;   // Index or -1
    std::vector<int> rightChild;  // Index or -1

    void traverse(int node) {
        if (node < 0) return;
        process(data[node]);
        traverse(leftChild[node]);
        traverse(rightChild[node]);
    }
};
// Data is contiguous, indices are contiguous
```

### 4.4 Optimize Memory Access Patterns

Access memory sequentially when possible. For 2D arrays, match the storage order.

**Incorrect (column-major access of row-major array):**

```cpp
int matrix[N][M];  // Row-major storage
for (int j = 0; j < M; ++j) {
    for (int i = 0; i < N; ++i) {
        sum += matrix[i][j];  // Stride-N access, cache unfriendly
    }
}
```

**Correct (row-major access):**

```cpp
int matrix[N][M];
for (int i = 0; i < N; ++i) {
    for (int j = 0; j < M; ++j) {
        sum += matrix[i][j];  // Sequential access, cache friendly
    }
}
```

---

## 5. Algorithm Selection

**Impact: MEDIUM**

Choosing the right algorithm and data structure provides asymptotic improvements. Standard library algorithms are heavily optimized and should be preferred over hand-rolled alternatives.

### 5.1 Use std::ranges

C++20 ranges provide composable, lazy evaluation with cleaner syntax.

**Incorrect (manual loops):**

```cpp
std::vector<int> result;
for (const auto& x : data) {
    if (x > 0) {
        result.push_back(x * x);
    }
}
```

**Correct (ranges pipeline):**

```cpp
auto result = data
    | std::views::filter([](int x) { return x > 0; })
    | std::views::transform([](int x) { return x * x; })
    | std::ranges::to<std::vector>();

// Lazy evaluation - no intermediate containers
for (auto x : data | std::views::take(10) | std::views::reverse) {
    process(x);
}
```

### 5.2 Use unordered Containers for O(1) Lookups

Hash-based containers provide O(1) average lookup vs O(log n) for tree-based.

**Incorrect (O(log n) when order not needed):**

```cpp
std::map<std::string, Data> cache;
auto it = cache.find(key);  // O(log n)
```

**Correct (O(1) amortized):**

```cpp
std::unordered_map<std::string, Data> cache;
auto it = cache.find(key);  // O(1) average
```

### 5.3 Use flat Containers for Small Data

For small collections (< 100-1000 elements), flat containers outperform node-based ones due to cache efficiency.

**Small map alternatives:**

```cpp
// For small maps, vector of pairs can be faster
std::vector<std::pair<Key, Value>> smallMap;
// Linear search is fast for small N due to cache locality

// C++23 flat_map
std::flat_map<Key, Value> efficientSmallMap;
// Sorted vector, binary search, no node overhead
```

### 5.4 Prefer STL Algorithms Over Hand-Rolled Loops

STL algorithms are optimized, express intent clearly, and enable parallelization.

**Incorrect (manual loop):**

```cpp
bool found = false;
for (const auto& item : data) {
    if (item == target) {
        found = true;
        break;
    }
}
```

**Correct (STL algorithm):**

```cpp
bool found = std::find(data.begin(), data.end(), target) != data.end();
// Or with ranges:
bool found = std::ranges::contains(data, target);
```

### 5.5 Use Early Exit Algorithms

`any_of`, `find_if`, `none_of` stop at first match, avoiding full traversal.

**Incorrect (full traversal):**

```cpp
bool hasNegative = false;
for (const auto& x : data) {
    if (x < 0) hasNegative = true;
}
```

**Correct (early exit):**

```cpp
bool hasNegative = std::any_of(data.begin(), data.end(),
                               [](int x) { return x < 0; });
// Stops at first negative value
```

### 5.6 Use Small Buffer Optimization

Small Buffer Optimization (SBO) stores small collections inline, avoiding heap allocation.

**Incorrect (heap allocation for small vectors):**

```cpp
std::vector<int> items;  // Always heap allocates
items.push_back(1);
items.push_back(2);
// Heap allocation for just 2 integers!
```

**Correct (small vector):**

```cpp
// Boost.Container or LLVM SmallVector
boost::container::small_vector<int, 8> items;  // 8 ints inline
items.push_back(1);
items.push_back(2);
// No heap allocation!
```

### 5.7 Use Lookup Tables for Repeated Computations

Precompute results for known input domains.

**Incorrect (repeated computation):**

```cpp
int popcount(uint8_t byte) {
    int count = 0;
    while (byte) {
        count += byte & 1;
        byte >>= 1;
    }
    return count;
}
```

**Correct (lookup table):**

```cpp
constexpr auto POPCOUNT_TABLE = [] {
    std::array<uint8_t, 256> table{};
    for (int i = 0; i < 256; ++i) {
        table[i] = (i & 1) + table[i / 2];
    }
    return table;
}();

int popcount(uint8_t byte) {
    return POPCOUNT_TABLE[byte];  // Single array lookup
}
```

---

## 6. I/O Performance

**Impact: MEDIUM**

I/O operations are often the slowest part of an application. Buffering, batching, and asynchronous I/O patterns minimize blocking and maximize throughput.

### 6.1 Use Buffered I/O

Batch operations to reduce syscall overhead.

**Incorrect (unbuffered, syscall per byte):**

```cpp
std::ofstream file("output.txt");
for (char c : data) {
    file.put(c);  // Potential syscall per character
}
```

**Correct (buffered writes):**

```cpp
std::ofstream file("output.txt");
file.write(data.data(), data.size());  // Single syscall

// Or explicit buffering
constexpr size_t BUFFER_SIZE = 64 * 1024;
std::vector<char> buffer;
buffer.reserve(BUFFER_SIZE);

for (const auto& item : items) {
    buffer.insert(buffer.end(), item.begin(), item.end());
    if (buffer.size() >= BUFFER_SIZE) {
        file.write(buffer.data(), buffer.size());
        buffer.clear();
    }
}
if (!buffer.empty()) {
    file.write(buffer.data(), buffer.size());
}
```

### 6.2 Use std::format

C++20 `std::format` is faster than iostreams and type-safe unlike printf.

**Incorrect (slow iostreams):**

```cpp
std::stringstream ss;
ss << "User " << name << " has value " << std::fixed
   << std::setprecision(2) << value;
std::string result = ss.str();
```

**Correct (std::format):**

```cpp
std::string result = std::format("User {} has value {:.2f}", name, value);

// Or with fmt library for C++17
std::string result = fmt::format("User {} has value {:.2f}", name, value);
```

### 6.3 Use Asynchronous I/O

Don't block threads waiting for I/O completion.

**Incorrect (blocking I/O):**

```cpp
std::string readFile(const std::string& path) {
    std::ifstream file(path);
    std::stringstream ss;
    ss << file.rdbuf();  // Blocks until complete
    return ss.str();
}
```

**Correct (async I/O):**

```cpp
std::future<std::string> readFileAsync(const std::string& path) {
    return std::async(std::launch::async, [path] {
        std::ifstream file(path);
        std::stringstream ss;
        ss << file.rdbuf();
        return ss.str();
    });
}

// Usage
auto future = readFileAsync("large_file.txt");
doOtherWork();  // Continue while file loads
std::string content = future.get();
```

### 6.4 Use Binary I/O for Structured Data

Binary I/O is 5-10x faster than text parsing for structured data.

**Incorrect (text parsing):**

```cpp
std::ofstream file("data.txt");
for (const auto& record : records) {
    file << record.id << "," << record.value << "\n";
}
// Reading requires parsing each line
```

**Correct (binary I/O):**

```cpp
std::ofstream file("data.bin", std::ios::binary);
file.write(reinterpret_cast<const char*>(records.data()),
           records.size() * sizeof(Record));

// Reading is just a memcpy
std::ifstream in("data.bin", std::ios::binary);
records.resize(fileSize / sizeof(Record));
in.read(reinterpret_cast<char*>(records.data()),
        records.size() * sizeof(Record));
```

### 6.5 Use Memory-Mapped Files for Large File Access

Memory-mapped files allow treating file contents as memory, leveraging the OS page cache.

**Correct (mmap for random access):**

```cpp
#include <sys/mman.h>
#include <fcntl.h>

class MappedFile {
    void* data_ = nullptr;
    size_t size_ = 0;
    int fd_ = -1;
public:
    MappedFile(const char* path) {
        fd_ = open(path, O_RDONLY);
        struct stat st;
        fstat(fd_, &st);
        size_ = st.st_size;
        data_ = mmap(nullptr, size_, PROT_READ, MAP_PRIVATE, fd_, 0);
    }
    ~MappedFile() {
        if (data_ != MAP_FAILED) munmap(data_, size_);
        if (fd_ >= 0) close(fd_);
    }
    char operator[](size_t i) const {
        return static_cast<const char*>(data_)[i];  // O(1) random access
    }
};
```

### 6.6 Preallocate File Space

Preallocating prevents filesystem fragmentation and reduces metadata updates.

```cpp
int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
posix_fallocate(fd, 0, expectedSize);  // Allocates contiguous blocks
write(fd, data, dataSize);
ftruncate(fd, actualSize);  // Trim to actual size
close(fd);
```

### 6.7 Use Direct I/O for Large Sequential Transfers

Direct I/O bypasses the page cache, useful when you manage your own caching.

```cpp
int fd = open(path, O_RDONLY | O_DIRECT);
void* buffer = aligned_alloc(4096, BLOCK_SIZE);  // Must be aligned
read(fd, buffer, BLOCK_SIZE);
free(buffer);
close(fd);
```

---

## 7. Code Generation

**Impact: LOW-MEDIUM**

Compiler hints and code organization can improve generated code quality. Inlining, branch prediction hints, and linkage control enable better optimization.

### 7.1 Use Inline Hints Appropriately

Inline small, frequently called functions. Avoid inlining large functions.

```cpp
// Good candidates for inlining
inline int square(int x) { return x * x; }

class Vector {
    float x, y, z;
public:
    inline float lengthSquared() const { return x*x + y*y + z*z; }
};

// Force inline in hot paths
[[gnu::always_inline]] inline int fastPath(int x) { return x * 2; }
```

### 7.2 Use constexpr

Move computation to compile time when possible.

```cpp
constexpr int factorial(int n) {
    return n <= 1 ? 1 : n * factorial(n - 1);
}

// Compile-time array
constexpr auto FACTORIALS = [] {
    std::array<int, 13> result{};
    for (int i = 0; i < 13; ++i) result[i] = factorial(i);
    return result;
}();

// C++20 constexpr containers
constexpr std::vector<int> getValues() {
    std::vector<int> v;
    v.push_back(1);
    v.push_back(2);
    return v;
}
```

### 7.3 Use Branch Prediction Hints

`[[likely]]` and `[[unlikely]]` (C++20) guide branch prediction.

```cpp
if (error) [[unlikely]] {
    handleError();
} else [[likely]] {
    normalPath();
}

switch (state) {
case State::Running: [[likely]]
    run();
    break;
case State::Error: [[unlikely]]
    handleError();
    break;
}
```

### 7.4 Use restrict for Non-Aliasing Pointers

`__restrict` promises no aliasing, enabling vectorization.

```cpp
void add(float* __restrict a,
         const float* __restrict b,
         const float* __restrict c, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        a[i] = b[i] + c[i];  // Compiler can vectorize safely
    }
}
```

### 7.5 Enable Link-Time Optimization

LTO enables cross-module inlining and dead code elimination.

```cmake
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
```

```bash
g++ -flto -O2 *.cpp -o program
```

### 7.6 Use noexcept for Compiler Optimizations

`noexcept` enables move optimizations in STL containers.

```cpp
class Buffer {
public:
    Buffer(Buffer&& other) noexcept  // Required for vector optimization
        : data_(std::exchange(other.data_, nullptr)) {}
    Buffer& operator=(Buffer&& other) noexcept;
};
```

### 7.7 Use Standard Attributes

Attributes guide the optimizer and catch bugs.

```cpp
[[nodiscard]] ErrorCode initialize();  // Must check return value
[[deprecated("Use newFunc()")]] void oldFunc();
[[maybe_unused]] void* userData;  // Intentionally unused
```

### 7.8 Structure Code for Auto-Vectorization

Enable SIMD by using proper data layout and avoiding aliasing.

```cpp
// Structure for vectorization (SoA)
struct Particles {
    std::vector<float> x, y, z;
    void update(float dt) {
        #pragma omp simd
        for (size_t i = 0; i < x.size(); ++i) {
            x[i] += vx[i] * dt;
        }
    }
};
```

### 7.9 Use Branchless Programming for Hot Paths

Eliminate unpredictable branches with arithmetic or conditional moves.

```cpp
// Branchless clamp
int clamp(int value, int min, int max) {
    return std::min(std::max(value, min), max);
}

// Branchless select
int select(bool cond, int a, int b) {
    return cond ? a : b;  // Often compiles to cmov
}
```

### 7.10 Use Profile-Guided Optimization

PGO uses runtime data to optimize branch prediction and code layout.

```bash
g++ -fprofile-generate -O2 program.cpp -o program
./program < typical_input.txt
g++ -fprofile-use -O2 program.cpp -o program_optimized
```

---

## 8. Template Metaprogramming

**Impact: LOW**

Advanced template techniques enable compile-time computation and zero-overhead abstractions. Use sparingly as they increase compile times and code complexity.

### 8.1 Use Concepts

C++20 concepts provide clear constraints and better error messages.

**Incorrect (SFINAE):**

```cpp
template<typename T, typename = std::enable_if_t<std::is_integral_v<T>>>
T add(T a, T b) { return a + b; }
```

**Correct (concepts):**

```cpp
template<std::integral T>
T add(T a, T b) { return a + b; }

// Custom concept
template<typename T>
concept Addable = requires(T a, T b) {
    { a + b } -> std::convertible_to<T>;
};

template<Addable T>
T add(T a, T b) { return a + b; }
```

### 8.2 Use CRTP for Static Polymorphism

CRTP provides compile-time polymorphism with zero virtual call overhead.

```cpp
template<typename Derived>
class Base {
public:
    void interface() {
        static_cast<Derived*>(this)->implementation();
    }
};

class Derived : public Base<Derived> {
public:
    void implementation() { /* ... */ }
};
```

### 8.3 Use Type Erasure for Runtime Flexibility

Type erasure (like `std::function`, `std::any`) enables heterogeneous containers.

```cpp
// std::function for callable type erasure
std::vector<std::function<int(int)>> operations;
operations.push_back([](int x) { return x * 2; });
operations.push_back([](int x) { return x + 1; });

// Custom type erasure
class Shape {
    struct Concept {
        virtual ~Concept() = default;
        virtual void draw() const = 0;
    };
    template<typename T>
    struct Model : Concept {
        T data;
        void draw() const override { data.draw(); }
    };
    std::unique_ptr<Concept> pimpl_;
public:
    template<typename T>
    Shape(T x) : pimpl_(std::make_unique<Model<T>>(std::move(x))) {}
    void draw() const { pimpl_->draw(); }
};
```

---

## References

1. [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
2. [cppreference.com](https://en.cppreference.com/)
3. [Compiler Explorer](https://godbolt.org/)
4. [What Every Programmer Should Know About Memory](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
5. [Data-Oriented Design](https://www.dataorienteddesign.com/dodbook/)
6. [Algorithmica HPC](https://en.algorithmica.org/hpc/)
7. [CppCon Talks](https://www.youtube.com/user/CppCon)
8. [ISO C++ FAQ](https://isocpp.org/faq)
