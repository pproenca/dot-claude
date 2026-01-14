---
title: Use unordered Containers for O(1) Lookups
impact: MEDIUM
impactDescription: O(1) vs O(log n) lookup time
tags: algo, unordered_map, unordered_set, hash, lookup
---

## Use unordered Containers for O(1) Lookups

When you don't need ordered iteration, prefer `unordered_map` and `unordered_set` over `map` and `set`. Hash-based containers provide O(1) average lookup vs O(log n) for tree-based.

**Incorrect (tree-based when order not needed):**

```cpp
// O(log n) operations
std::map<std::string, int> wordCounts;
std::set<int> seenIds;

// Order not needed, but paying for it
for (const auto& word : words) {
    wordCounts[word]++;  // O(log n) per insertion
}

bool exists = seenIds.count(id);  // O(log n)
```

**Correct (hash-based for O(1)):**

```cpp
// O(1) average operations
std::unordered_map<std::string, int> wordCounts;
std::unordered_set<int> seenIds;

for (const auto& word : words) {
    wordCounts[word]++;  // O(1) average
}

bool exists = seenIds.count(id);  // O(1) average
```

**Reserve buckets for known size:**

```cpp
std::unordered_map<int, Data> cache;
cache.reserve(10000);  // Pre-allocate buckets
cache.max_load_factor(0.7);  // Tune for memory/speed tradeoff
```

**Custom hash for complex keys:**

```cpp
struct Point { int x, y; };

struct PointHash {
    size_t operator()(const Point& p) const {
        return std::hash<int>{}(p.x) ^ (std::hash<int>{}(p.y) << 1);
    }
};

std::unordered_set<Point, PointHash> points;
```

**When to prefer ordered containers:**
- Need sorted iteration
- Range queries (`lower_bound`, `upper_bound`)
- Keys don't have good hash function
- Small containers (tree overhead is minimal)

**Comparison:**

| Operation | map/set | unordered_map/set |
|-----------|---------|-------------------|
| Lookup | O(log n) | O(1) average |
| Insert | O(log n) | O(1) average |
| Delete | O(log n) | O(1) average |
| Ordered iter | Yes | No |
| Worst case | O(log n) | O(n) |

**C++20 contains:**

```cpp
// Cleaner existence check
if (seenIds.contains(id)) {  // C++20
    // ...
}
```

Reference: [std::unordered_map](https://en.cppreference.com/w/cpp/container/unordered_map)
