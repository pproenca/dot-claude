---
title: Prefer atomic Over mutex for Simple Types
impact: HIGH
impactDescription: 10-100x faster than mutex for simple operations
tags: async, atomic, mutex, lock-free, concurrency
---

## Prefer atomic Over mutex for Simple Types

For simple shared state (counters, flags, pointers), `std::atomic` provides lock-free synchronization that's much faster than mutex-based solutions.

**Incorrect (mutex for simple counter):**

```cpp
class Counter {
    int value_ = 0;
    std::mutex mutex_;
public:
    void increment() {
        std::lock_guard<std::mutex> lock(mutex_);
        ++value_;  // Mutex overhead for single instruction
    }

    int get() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return value_;
    }
};
```

**Correct (atomic counter):**

```cpp
class Counter {
    std::atomic<int> value_{0};
public:
    void increment() {
        value_.fetch_add(1, std::memory_order_relaxed);
    }

    int get() const {
        return value_.load(std::memory_order_relaxed);
    }
};
```

**Atomic flag for simple synchronization:**

```cpp
class SpinLock {
    std::atomic_flag flag_ = ATOMIC_FLAG_INIT;
public:
    void lock() {
        while (flag_.test_and_set(std::memory_order_acquire)) {
            // Spin until lock acquired
        }
    }

    void unlock() {
        flag_.clear(std::memory_order_release);
    }
};
```

**Compare-and-swap for lock-free updates:**

```cpp
template<typename T>
class LockFreeStack {
    struct Node {
        T data;
        Node* next;
    };
    std::atomic<Node*> head_{nullptr};

public:
    void push(T value) {
        Node* newNode = new Node{std::move(value), nullptr};
        newNode->next = head_.load(std::memory_order_relaxed);
        while (!head_.compare_exchange_weak(
            newNode->next, newNode,
            std::memory_order_release,
            std::memory_order_relaxed)) {
            // Retry if another thread modified head
        }
    }
};
```

**Memory order selection:**

```cpp
// Relaxed: No ordering guarantees (counters, statistics)
counter.fetch_add(1, std::memory_order_relaxed);

// Acquire/Release: Synchronize producer-consumer
data.store(value, std::memory_order_release);  // Producer
auto v = data.load(std::memory_order_acquire); // Consumer

// Sequential consistency: Default, strongest guarantee
flag.store(true);  // Implicitly seq_cst
```

**When to use mutex instead:**
- Complex multi-variable updates
- Operations that can't be made atomic
- When contention is low and mutex is simpler

Reference: [std::atomic](https://en.cppreference.com/w/cpp/atomic/atomic)
