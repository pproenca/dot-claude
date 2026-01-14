---
title: Use Early Exit Algorithms to Avoid Full Scans
impact: MEDIUM
impactDescription: stops at first match instead of processing all
tags: algo, early-exit, short-circuit, any_of, find_if
---

## Use Early Exit Algorithms to Avoid Full Scans

Use algorithms that short-circuit (`any_of`, `none_of`, `find_if`) instead of algorithms that process all elements (`count_if`, `for_each`) when you only need to know if a condition is met.

**Incorrect (processes all elements):**

```cpp
// Counts all matches even though we only need to know if any exist
bool hasNegative(const std::vector<int>& v) {
    return std::count_if(v.begin(), v.end(),
        [](int x) { return x < 0; }) > 0;
}

// Checks every element even after finding match
bool containsValue(const std::vector<int>& v, int target) {
    bool found = false;
    std::for_each(v.begin(), v.end(), [&](int x) {
        if (x == target) found = true;
    });
    return found;
}
```

**Correct (early exit on first match):**

```cpp
// Stops at first negative
bool hasNegative(const std::vector<int>& v) {
    return std::any_of(v.begin(), v.end(),
        [](int x) { return x < 0; });
}

// Stops at first match
bool containsValue(const std::vector<int>& v, int target) {
    return std::find(v.begin(), v.end(), target) != v.end();
}

// Or with C++20 ranges
bool containsValue(const std::vector<int>& v, int target) {
    return std::ranges::contains(v, target);  // C++23
}
```

**Early exit algorithm family:**

```cpp
std::vector<int> data = {1, 2, 3, -4, 5, 6, 7};

// any_of: true if ANY element matches (stops on first true)
bool hasNeg = std::any_of(data.begin(), data.end(),
    [](int x) { return x < 0; });

// none_of: true if NO element matches (stops on first true)
bool allPositive = std::none_of(data.begin(), data.end(),
    [](int x) { return x < 0; });

// all_of: true if ALL elements match (stops on first false)
bool allSmall = std::all_of(data.begin(), data.end(),
    [](int x) { return x < 100; });

// find_if: returns iterator to first match (stops on match)
auto it = std::find_if(data.begin(), data.end(),
    [](int x) { return x < 0; });
```

**Custom early exit loops:**

```cpp
// When algorithm doesn't exist
std::optional<Item> findFirstValid(const std::vector<Item>& items) {
    for (const auto& item : items) {
        if (auto result = validate(item); result.valid) {
            return item;  // Early exit
        }
    }
    return std::nullopt;
}
```

**Impact example:**

```cpp
// Array of 1 million elements, negative at index 10
std::vector<int> data(1000000, 1);
data[10] = -1;

// count_if: processes all 1,000,000 elements
auto count = std::count_if(data.begin(), data.end(),
    [](int x) { return x < 0; });  // ~1ms

// any_of: stops after 11 elements
bool hasNeg = std::any_of(data.begin(), data.end(),
    [](int x) { return x < 0; });  // ~0.00001ms
```

Reference: [std::any_of](https://en.cppreference.com/w/cpp/algorithm/all_any_none_of)
