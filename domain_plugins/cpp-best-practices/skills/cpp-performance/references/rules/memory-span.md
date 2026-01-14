---
title: Use span for Non-Owning Array Parameters
impact: HIGH
impactDescription: type-safe, works with any contiguous container
tags: memory, span, arrays, containers, parameters
---

## Use span for Non-Owning Array Parameters

Use `std::span` (C++20) for function parameters that operate on contiguous sequences. It works with vectors, arrays, and raw pointers without copying, while providing bounds information.

**Incorrect (loses size or forces specific type):**

```cpp
// Loses size information
void process(int* data, size_t size) {
    for (size_t i = 0; i < size; ++i) {
        data[i] *= 2;
    }
}

// Forces specific container type
void process(std::vector<int>& data) {
    for (auto& x : data) x *= 2;
}

// Usage is error-prone
int arr[10];
process(arr, 10);  // Easy to get size wrong
process(arr, 100); // Buffer overflow!
```

**Correct (type-safe span):**

```cpp
#include <span>

void process(std::span<int> data) {
    for (auto& x : data) {
        x *= 2;
    }
}

// Usage - works with any contiguous container
std::vector<int> vec = {1, 2, 3};
std::array<int, 5> arr = {1, 2, 3, 4, 5};
int carray[3] = {1, 2, 3};

process(vec);     // Works
process(arr);     // Works
process(carray);  // Works
process({vec.data() + 1, 2});  // Subspan works too
```

**Read-only span:**

```cpp
int sum(std::span<const int> data) {
    return std::accumulate(data.begin(), data.end(), 0);
}
```

**Fixed-size span for compile-time checks:**

```cpp
void process3(std::span<int, 3> exactly3) {
    // Compiler ensures exactly 3 elements
}

std::array<int, 3> arr3 = {1, 2, 3};
process3(arr3);  // OK

std::array<int, 4> arr4 = {1, 2, 3, 4};
// process3(arr4);  // Compile error!
```

**Subspan operations:**

```cpp
void processChunks(std::span<int> data) {
    auto first = data.first(10);    // First 10 elements
    auto last = data.last(10);      // Last 10 elements
    auto mid = data.subspan(5, 20); // 20 elements starting at index 5
}
```

Reference: [C++ Core Guidelines I.13](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#i13-do-not-pass-an-array-as-a-single-pointer)
