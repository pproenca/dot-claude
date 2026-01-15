---
title: Use Buffer Pools for Repeated Allocations
impact: CRITICAL
impactDescription: 10-50× improvement for high-frequency allocations
tags: mem, buffer-pool, allocation, reuse
---

## Use Buffer Pools for Repeated Allocations

Creating new Buffers or TypedArrays per operation causes allocation pressure. Pool and reuse buffers for repeated operations.

**Incorrect (allocation per call):**

```cpp
Napi::Value ProcessData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  size_t size = info[0].As<Napi::Number>().Uint32Value();

  // New allocation EVERY call
  Napi::Buffer<uint8_t> buffer = Napi::Buffer<uint8_t>::New(env, size);
  uint8_t* data = buffer.Data();

  // Fill buffer with processed data
  ProcessInto(data, size);

  return buffer;
}
```

**Correct (pooled buffers):**

```cpp
#include <queue>
#include <mutex>

class BufferPool {
 public:
  static BufferPool& Instance() {
    static BufferPool instance;
    return instance;
  }

  Napi::Buffer<uint8_t> Acquire(Napi::Env env, size_t size) {
    std::lock_guard<std::mutex> lock(mutex_);

    // Find existing buffer of appropriate size
    for (auto it = pool_.begin(); it != pool_.end(); ++it) {
      if (it->ByteLength() >= size) {
        Napi::Buffer<uint8_t> buffer = std::move(*it);
        pool_.erase(it);
        return buffer;
      }
    }

    // No suitable buffer, create new one
    return Napi::Buffer<uint8_t>::New(env, size);
  }

  void Release(Napi::Buffer<uint8_t>&& buffer) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (pool_.size() < MAX_POOL_SIZE) {
      pool_.push_back(std::move(buffer));
    }
    // If pool is full, buffer is destroyed
  }

 private:
  static constexpr size_t MAX_POOL_SIZE = 32;
  std::vector<Napi::Buffer<uint8_t>> pool_;
  std::mutex mutex_;
};

// Usage with Reference counting
class PooledBuffer {
 public:
  Napi::Buffer<uint8_t> buffer;

  PooledBuffer(Napi::Env env, size_t size)
      : buffer(BufferPool::Instance().Acquire(env, size)) {}

  ~PooledBuffer() {
    BufferPool::Instance().Release(std::move(buffer));
  }
};
```

**Alternative (pre-allocated ring buffer):**

```cpp
class RingBuffer {
 public:
  RingBuffer(Napi::Env env, size_t slot_size, size_t num_slots)
      : slot_size_(slot_size), num_slots_(num_slots), current_(0) {
    for (size_t i = 0; i < num_slots; i++) {
      slots_.push_back(Napi::Buffer<uint8_t>::New(env, slot_size));
    }
  }

  Napi::Buffer<uint8_t> GetNext() {
    Napi::Buffer<uint8_t>& slot = slots_[current_];
    current_ = (current_ + 1) % num_slots_;
    return slot;  // Returns reference, not copy
  }

 private:
  size_t slot_size_;
  size_t num_slots_;
  size_t current_;
  std::vector<Napi::Buffer<uint8_t>> slots_;
};
```

**Benefits:**
- Eliminates allocation overhead in hot paths
- Reduces GC pressure
- More predictable latency

Reference: [Memory Pooling Patterns](https://en.wikipedia.org/wiki/Memory_pool)
