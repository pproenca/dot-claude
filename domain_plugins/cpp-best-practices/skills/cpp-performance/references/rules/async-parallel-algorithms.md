---
title: Use Parallel STL Algorithms for Data Parallelism
impact: HIGH
impactDescription: automatic parallelization, near-linear speedup
tags: async, parallel, algorithms, execution-policy, stl, c++17
---

## Use Parallel STL Algorithms for Data Parallelism

C++17 execution policies enable automatic parallelization of STL algorithms. Use `std::execution::par` for parallel execution on large datasets.

**Incorrect (sequential processing):**

```cpp
std::vector<int> data(10'000'000);
std::iota(data.begin(), data.end(), 0);

// Sequential - uses single core
std::transform(data.begin(), data.end(), data.begin(),
    [](int x) { return x * x; });

long long sum = std::accumulate(data.begin(), data.end(), 0LL);
```

**Correct (parallel execution):**

```cpp
#include <execution>

std::vector<int> data(10'000'000);
std::iota(data.begin(), data.end(), 0);

// Parallel - uses all cores
std::transform(std::execution::par, data.begin(), data.end(), data.begin(),
    [](int x) { return x * x; });

long long sum = std::reduce(std::execution::par, data.begin(), data.end(), 0LL);
```

**Execution policies:**

```cpp
// Sequential (default)
std::sort(std::execution::seq, v.begin(), v.end());

// Parallel
std::sort(std::execution::par, v.begin(), v.end());

// Parallel + vectorized (SIMD)
std::sort(std::execution::par_unseq, v.begin(), v.end());

// Vectorized only (C++20)
std::sort(std::execution::unseq, v.begin(), v.end());
```

**Common parallel operations:**

```cpp
// Parallel sort
std::sort(std::execution::par, data.begin(), data.end());

// Parallel transform
std::transform(std::execution::par, in.begin(), in.end(),
    out.begin(), [](auto x) { return process(x); });

// Parallel find
auto it = std::find_if(std::execution::par, data.begin(), data.end(),
    [](int x) { return x > threshold; });

// Parallel for_each
std::for_each(std::execution::par, items.begin(), items.end(),
    [](auto& item) { item.process(); });

// Parallel reduce (note: reduce, not accumulate)
auto sum = std::reduce(std::execution::par, data.begin(), data.end());
```

**When to use parallel:**

```cpp
// Use parallel for large datasets
if (data.size() > 10000) {
    std::sort(std::execution::par, data.begin(), data.end());
} else {
    std::sort(data.begin(), data.end());  // Sequential faster for small data
}
```

**Thread-safe lambdas required:**

```cpp
// Incorrect - data race
int count = 0;
std::for_each(std::execution::par, v.begin(), v.end(),
    [&count](int x) { if (x > 0) ++count; });  // Race condition!

// Correct - use atomic or reduce
std::atomic<int> count{0};
std::for_each(std::execution::par, v.begin(), v.end(),
    [&count](int x) { if (x > 0) count.fetch_add(1); });

// Better - use count_if
auto count = std::count_if(std::execution::par, v.begin(), v.end(),
    [](int x) { return x > 0; });
```

Reference: [C++17 Parallel Algorithms](https://en.cppreference.com/w/cpp/algorithm#Execution_policies)
