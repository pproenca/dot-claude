---
title: Use std::ranges for Cleaner Algorithm Composition
impact: MEDIUM
impactDescription: clearer code, lazy evaluation, better optimization
tags: algo, ranges, views, c++20, algorithms, composition
---

## Use std::ranges for Cleaner Algorithm Composition

C++20 ranges provide composable, lazy-evaluated transformations that are often clearer and more efficient than iterator-based alternatives.

**Incorrect (multiple passes, temporary containers):**

```cpp
std::vector<int> data = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

// Multiple passes, creates temporaries
std::vector<int> filtered;
std::copy_if(data.begin(), data.end(), std::back_inserter(filtered),
    [](int x) { return x % 2 == 0; });

std::vector<int> transformed;
std::transform(filtered.begin(), filtered.end(),
    std::back_inserter(transformed),
    [](int x) { return x * x; });

int sum = std::accumulate(transformed.begin(), transformed.end(), 0);
```

**Correct (single pass, no temporaries):**

```cpp
#include <ranges>

std::vector<int> data = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

// Single pass, lazy evaluation, no temporaries
auto result = data
    | std::views::filter([](int x) { return x % 2 == 0; })
    | std::views::transform([](int x) { return x * x; });

int sum = std::ranges::fold_left(result, 0, std::plus{});  // C++23
// Or in C++20:
int sum = 0;
for (int x : result) sum += x;
```

**Common views:**

```cpp
auto v = data | std::views::take(5);           // First 5 elements
auto v = data | std::views::drop(3);           // Skip first 3
auto v = data | std::views::reverse;           // Reverse view
auto v = data | std::views::filter(pred);      // Filter elements
auto v = data | std::views::transform(func);   // Transform elements

// C++23 additions
auto v = data | std::views::chunk(3);          // Groups of 3
auto v = data | std::views::slide(3);          // Sliding window of 3
auto v = data | std::views::zip(other);        // Pair with other range
```

**Ranges algorithms:**

```cpp
// Cleaner than iterator pairs
std::ranges::sort(data);
std::ranges::reverse(data);
auto it = std::ranges::find(data, 42);
bool found = std::ranges::contains(data, 42);  // C++23

// With projections
std::ranges::sort(people, {}, &Person::name);  // Sort by name
std::ranges::max(people, {}, &Person::age);    // Oldest person
```

**Lazy evaluation benefit:**

```cpp
// Only computes what's needed
auto firstSquareOver100 = data
    | std::views::transform([](int x) { return x * x; })
    | std::views::filter([](int x) { return x > 100; })
    | std::views::take(1);

// Stops processing as soon as first match found
for (int x : firstSquareOver100) {
    std::cout << x << '\n';
}
```

Reference: [C++20 Ranges](https://en.cppreference.com/w/cpp/ranges)
