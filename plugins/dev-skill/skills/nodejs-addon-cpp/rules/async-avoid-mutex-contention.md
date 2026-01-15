---
title: Avoid Mutex Contention in Hot Paths
impact: HIGH
impactDescription: 2-10× improvement under concurrent load
tags: async, mutex, lock-free, contention
---

## Avoid Mutex Contention in Hot Paths

Heavy mutex usage in async workers creates contention that serializes parallel work. Use lock-free structures or fine-grained locking.

**Incorrect (global mutex bottleneck):**

```cpp
std::mutex global_cache_mutex;
std::unordered_map<std::string, Result> cache;

class CachingWorker : public Napi::AsyncWorker {
  void Execute() override {
    for (const auto& key : keys_) {
      {
        // All workers contend on this single mutex
        std::lock_guard<std::mutex> lock(global_cache_mutex);
        auto it = cache.find(key);
        if (it != cache.end()) {
          results_.push_back(it->second);
          continue;
        }
      }

      Result result = ComputeExpensive(key);

      {
        std::lock_guard<std::mutex> lock(global_cache_mutex);  // Again!
        cache[key] = result;
      }
      results_.push_back(result);
    }
  }
};
```

**Correct (lock-free read path):**

```cpp
#include <shared_mutex>
#include <atomic>

std::shared_mutex cache_mutex;
std::unordered_map<std::string, Result> cache;

class OptimizedCachingWorker : public Napi::AsyncWorker {
  void Execute() override {
    for (const auto& key : keys_) {
      // Try read with shared lock (multiple readers allowed)
      {
        std::shared_lock<std::shared_mutex> read_lock(cache_mutex);
        auto it = cache.find(key);
        if (it != cache.end()) {
          results_.push_back(it->second);
          continue;
        }
      }

      // Cache miss - compute without holding lock
      Result result = ComputeExpensive(key);

      // Write with exclusive lock
      {
        std::unique_lock<std::shared_mutex> write_lock(cache_mutex);
        // Double-check (another thread may have computed)
        auto it = cache.find(key);
        if (it == cache.end()) {
          cache[key] = result;
        }
      }
      results_.push_back(result);
    }
  }
};
```

**Alternative (thread-local caching):**

```cpp
class ThreadLocalWorker : public Napi::AsyncWorker {
  void Execute() override {
    // Each thread has its own local cache
    thread_local std::unordered_map<std::string, Result> local_cache;

    for (const auto& key : keys_) {
      // Check thread-local cache first (no locking)
      auto it = local_cache.find(key);
      if (it != local_cache.end()) {
        results_.push_back(it->second);
        continue;
      }

      // Then check shared cache
      {
        std::shared_lock<std::shared_mutex> lock(cache_mutex);
        auto shared_it = shared_cache.find(key);
        if (shared_it != shared_cache.end()) {
          local_cache[key] = shared_it->second;  // Promote to local
          results_.push_back(shared_it->second);
          continue;
        }
      }

      Result result = ComputeExpensive(key);
      local_cache[key] = result;

      // Optionally promote to shared cache
      {
        std::unique_lock<std::shared_mutex> lock(cache_mutex);
        shared_cache[key] = result;
      }

      results_.push_back(result);
    }
  }
};
```

**Lock-free approach with atomics:**

```cpp
#include <atomic>

template<typename T>
class LockFreeStack {
  struct Node {
    T data;
    std::atomic<Node*> next;
  };

  std::atomic<Node*> head_{nullptr};

 public:
  void Push(T value) {
    Node* new_node = new Node{std::move(value)};
    new_node->next = head_.load(std::memory_order_relaxed);
    while (!head_.compare_exchange_weak(
      new_node->next, new_node,
      std::memory_order_release,
      std::memory_order_relaxed
    ));
  }
};
```

Reference: [C++ Concurrency in Action](https://www.manning.com/books/c-plus-plus-concurrency-in-action-second-edition)
