---
title: Use shared_mutex for Read-Heavy Workloads
impact: HIGH
impactDescription: allows concurrent reads, 5-10x throughput improvement
tags: async, shared_mutex, reader-writer, concurrency, locks
---

## Use shared_mutex for Read-Heavy Workloads

When data is read frequently but written rarely, use `std::shared_mutex` to allow multiple concurrent readers while ensuring exclusive write access.

**Incorrect (exclusive lock for all operations):**

```cpp
class ConfigStore {
    std::map<std::string, std::string> config_;
    std::mutex mutex_;
public:
    std::string get(const std::string& key) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = config_.find(key);
        return it != config_.end() ? it->second : "";
    }

    void set(const std::string& key, const std::string& value) {
        std::lock_guard<std::mutex> lock(mutex_);
        config_[key] = value;
    }
    // All reads are serialized even though they don't conflict!
};
```

**Correct (shared lock for reads):**

```cpp
class ConfigStore {
    std::map<std::string, std::string> config_;
    mutable std::shared_mutex mutex_;
public:
    std::string get(const std::string& key) const {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        auto it = config_.find(key);
        return it != config_.end() ? it->second : "";
    }

    void set(const std::string& key, const std::string& value) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        config_[key] = value;
    }
    // Multiple threads can read concurrently
};
```

**Read-write lock pattern:**

```cpp
class Cache {
    std::unordered_map<int, Data> cache_;
    mutable std::shared_mutex mutex_;

public:
    std::optional<Data> get(int key) const {
        std::shared_lock lock(mutex_);  // C++17 CTAD
        if (auto it = cache_.find(key); it != cache_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    void put(int key, Data value) {
        std::unique_lock lock(mutex_);
        cache_[key] = std::move(value);
    }

    void clear() {
        std::unique_lock lock(mutex_);
        cache_.clear();
    }
};
```

**Upgrading from shared to unique:**

```cpp
Data getOrCompute(int key) {
    // First try with shared lock
    {
        std::shared_lock lock(mutex_);
        if (auto it = cache_.find(key); it != cache_.end()) {
            return it->second;
        }
    }
    // Upgrade to unique lock for write
    std::unique_lock lock(mutex_);
    // Double-check after acquiring unique lock
    if (auto it = cache_.find(key); it != cache_.end()) {
        return it->second;
    }
    auto data = computeExpensive(key);
    cache_[key] = data;
    return data;
}
```

**When to prefer regular mutex:**
- Write-heavy workloads (shared_mutex has higher overhead)
- Very short critical sections
- Single-threaded access patterns

Reference: [std::shared_mutex](https://en.cppreference.com/w/cpp/thread/shared_mutex)
