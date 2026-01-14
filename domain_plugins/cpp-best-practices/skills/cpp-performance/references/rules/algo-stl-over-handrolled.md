---
title: Prefer STL Algorithms Over Hand-Rolled Loops
impact: MEDIUM
impactDescription: optimized implementations, clearer intent
tags: algo, stl, algorithms, optimization, readability
---

## Prefer STL Algorithms Over Hand-Rolled Loops

STL algorithms are heavily optimized, express intent clearly, and enable compiler optimizations. Prefer them over manual loops for common operations.

**Incorrect (hand-rolled loops):**

```cpp
// Manual find
int* findValue(int* begin, int* end, int value) {
    while (begin != end) {
        if (*begin == value) return begin;
        ++begin;
    }
    return end;
}

// Manual copy
void copyData(const int* src, int* dst, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        dst[i] = src[i];
    }
}

// Manual accumulate
int sumValues(const std::vector<int>& v) {
    int sum = 0;
    for (int x : v) sum += x;
    return sum;
}
```

**Correct (STL algorithms):**

```cpp
// STL find - optimized, clear intent
auto it = std::find(vec.begin(), vec.end(), value);

// STL copy - may use memcpy for trivial types
std::copy(src.begin(), src.end(), dst.begin());

// STL accumulate
int sum = std::accumulate(vec.begin(), vec.end(), 0);

// Or with ranges (C++20)
int sum = std::ranges::fold_left(vec, 0, std::plus{});
```

**Common algorithm replacements:**

```cpp
// Instead of loop with if
auto it = std::find_if(v.begin(), v.end(), predicate);

// Instead of loop counting
size_t count = std::count_if(v.begin(), v.end(), predicate);

// Instead of loop checking all
bool allPositive = std::all_of(v.begin(), v.end(),
    [](int x) { return x > 0; });

// Instead of loop with max tracking
auto maxIt = std::max_element(v.begin(), v.end());

// Instead of loop filling
std::fill(v.begin(), v.end(), 0);
std::iota(v.begin(), v.end(), 1);  // 1, 2, 3, ...

// Instead of loop removing
v.erase(std::remove_if(v.begin(), v.end(), pred), v.end());
// Or C++20: std::erase_if(v, pred);
```

**Why STL is often faster:**

```cpp
// std::copy can use memcpy for trivial types
std::vector<int> src(10000), dst(10000);
std::copy(src.begin(), src.end(), dst.begin());
// Compiler may generate: memcpy(dst.data(), src.data(), sizeof(int)*10000)

// std::sort uses introsort (quicksort + heapsort + insertion sort)
std::sort(v.begin(), v.end());
// Optimized for different sizes and nearly-sorted data
```

**Expressive algorithms:**

```cpp
// Partition elements
auto pivot = std::partition(v.begin(), v.end(),
    [](int x) { return x < 0; });
// Negatives before pivot, non-negatives after

// Rotate elements
std::rotate(v.begin(), v.begin() + k, v.end());
// First k elements moved to end

// Merge sorted ranges
std::merge(a.begin(), a.end(), b.begin(), b.end(), out.begin());
```

Reference: [C++ Algorithms Library](https://en.cppreference.com/w/cpp/algorithm)
