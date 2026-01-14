---
title: Use flat Containers for Small Associative Data
impact: MEDIUM
impactDescription: 2-5x faster for small sizes due to cache locality
tags: algo, flat_map, flat_set, small-containers, cache, c++23
---

## Use flat Containers for Small Associative Data

For small associative containers (< 100-1000 elements), cache-friendly flat containers outperform tree and hash-based alternatives due to memory locality.

**Incorrect (tree overhead for small data):**

```cpp
// Tree overhead not worth it for small maps
std::map<std::string, int> config;  // Few dozen entries
config["timeout"] = 30;
config["retries"] = 3;

// Each node is separate allocation, poor cache locality
for (const auto& [key, value] : config) {
    // Pointer chasing through tree nodes
}
```

**Correct (flat container for small data):**

```cpp
// C++23 flat containers
#include <flat_map>

std::flat_map<std::string, int> config;
config["timeout"] = 30;
config["retries"] = 3;

// Contiguous storage, excellent cache locality
for (const auto& [key, value] : config) {
    // Sequential memory access
}
```

**Pre-C++23 alternative (sorted vector):**

```cpp
// Manual flat map using sorted vector
template<typename K, typename V>
class FlatMap {
    std::vector<std::pair<K, V>> data_;
public:
    V& operator[](const K& key) {
        auto it = std::lower_bound(data_.begin(), data_.end(), key,
            [](const auto& p, const K& k) { return p.first < k; });
        if (it == data_.end() || it->first != key) {
            it = data_.insert(it, {key, V{}});
        }
        return it->second;
    }

    auto find(const K& key) const {
        auto it = std::lower_bound(data_.begin(), data_.end(), key,
            [](const auto& p, const K& k) { return p.first < k; });
        return (it != data_.end() && it->first == key) ? it : data_.end();
    }
};
```

**Boost.Container flat containers:**

```cpp
#include <boost/container/flat_map.hpp>
#include <boost/container/flat_set.hpp>

boost::container::flat_map<int, std::string> flatMap;
boost::container::flat_set<int> flatSet;
```

**Performance characteristics:**

| Container | Lookup | Insert | Memory | Cache |
|-----------|--------|--------|--------|-------|
| map | O(log n) | O(log n) | High | Poor |
| unordered_map | O(1) | O(1) | Medium | Medium |
| flat_map | O(log n) | O(n) | Low | Excellent |

**When to use flat containers:**
- Size < 100-1000 elements
- Read-heavy workloads
- Lookup-dominated (not frequent insertions)
- Memory constrained environments

Reference: [C++23 flat_map](https://en.cppreference.com/w/cpp/container/flat_map)
