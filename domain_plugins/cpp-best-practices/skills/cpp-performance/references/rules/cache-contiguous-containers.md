---
title: Prefer Contiguous Containers Over Node-Based
impact: MEDIUM-HIGH
impactDescription: 10-100x faster iteration due to cache locality
tags: cache, vector, list, containers, memory-layout, locality
---

## Prefer Contiguous Containers Over Node-Based

Contiguous containers (`vector`, `array`, `string`) store elements in adjacent memory, enabling CPU prefetching. Node-based containers (`list`, `map`) scatter elements, causing cache misses.

**Incorrect (node-based container):**

```cpp
// std::list: each element is a separate allocation
std::list<int> numbers;
for (int i = 0; i < 10000; ++i) {
    numbers.push_back(i);
}

// Iteration causes cache miss for every element
int sum = 0;
for (int n : numbers) {  // Pointer chase for each element
    sum += n;
}
```

**Correct (contiguous container):**

```cpp
// std::vector: all elements in contiguous memory
std::vector<int> numbers;
numbers.reserve(10000);
for (int i = 0; i < 10000; ++i) {
    numbers.push_back(i);
}

// Iteration is cache-friendly
int sum = 0;
for (int n : numbers) {  // Sequential memory access
    sum += n;
}
```

**Performance comparison (typical):**

| Operation | vector | list |
|-----------|--------|------|
| Sequential iteration | 1x | 10-50x slower |
| Random access | O(1) | O(n) |
| Insert at end | O(1) amortized | O(1) |
| Insert at middle | O(n) | O(1)* |

*Note: list insertion is O(1) only if you have an iterator

**Even middle insertion can be faster with vector:**

```cpp
// For small-medium sizes, vector often wins even for middle insertion
// due to cache effects and move efficiency

std::vector<int> vec = {1, 2, 3, 4, 5};
vec.insert(vec.begin() + 2, 10);  // Often faster than list for < 1000 elements
```

**Use deque for front insertion:**

```cpp
// Need O(1) push_front? Use deque instead of list
std::deque<int> dq;
dq.push_front(1);  // O(1)
dq.push_back(2);   // O(1)
// Still mostly contiguous (chunks of contiguous memory)
```

**When list might be appropriate:**
- Very large elements with frequent middle insertion
- Iterator stability required after insertion
- Splicing between lists

Reference: [C++ Core Guidelines SL.con.2](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#slcon2-prefer-using-stl-vector-by-default-unless-you-have-a-reason-to-use-a-different-container)
