---
title: Reserve Container Capacity When Size is Known
impact: HIGH
impactDescription: eliminates reallocations, 2-10x faster insertion
tags: memory, vector, reserve, capacity, reallocation
---

## Reserve Container Capacity When Size is Known

When you know the final size of a container (or a reasonable upper bound), call `reserve()` before inserting elements. This eliminates expensive reallocations and copies during growth.

**Incorrect (repeated reallocations):**

```cpp
std::vector<Widget> widgets;
for (int i = 0; i < 10000; ++i) {
    widgets.push_back(Widget(i));
    // Vector reallocates ~14 times, copying all elements each time
}

std::vector<std::string> processLines(const std::vector<std::string>& input) {
    std::vector<std::string> result;
    for (const auto& line : input) {
        if (isValid(line)) {
            result.push_back(transform(line));
        }
    }
    return result;
}
```

**Correct (pre-allocated):**

```cpp
std::vector<Widget> widgets;
widgets.reserve(10000);  // Single allocation
for (int i = 0; i < 10000; ++i) {
    widgets.push_back(Widget(i));  // No reallocations
}

std::vector<std::string> processLines(const std::vector<std::string>& input) {
    std::vector<std::string> result;
    result.reserve(input.size());  // Upper bound
    for (const auto& line : input) {
        if (isValid(line)) {
            result.push_back(transform(line));
        }
    }
    return result;
}
```

**Use emplace_back for in-place construction:**

```cpp
std::vector<std::pair<int, std::string>> pairs;
pairs.reserve(1000);

// Incorrect: creates temporary, then moves
pairs.push_back(std::make_pair(1, "one"));

// Correct: constructs in place
pairs.emplace_back(1, "one");
```

**Shrink to fit after bulk operations:**

```cpp
std::vector<int> data;
data.reserve(10000);
// ... fill with 500 elements ...
data.shrink_to_fit();  // Release unused capacity
```

Reference: [C++ Core Guidelines SL.con.2](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#slcon2-prefer-using-stl-vector-by-default-unless-you-have-a-reason-to-use-a-different-container)
