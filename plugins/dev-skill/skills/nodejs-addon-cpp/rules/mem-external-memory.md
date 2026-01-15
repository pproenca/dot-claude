---
title: Track External Memory with AdjustExternalMemory
impact: CRITICAL
impactDescription: prevents OOM crashes and improves GC timing
tags: mem, external-memory, gc, v8-heap
---

## Track External Memory with AdjustExternalMemory

V8's garbage collector doesn't see native memory allocations. Use `AdjustExternalMemory` to inform V8 about native allocations so it can trigger GC appropriately.

**Incorrect (V8 unaware of native allocations):**

```cpp
class LargeBuffer : public Napi::ObjectWrap<LargeBuffer> {
 public:
  static Napi::Object Init(Napi::Env env, Napi::Object exports);
  LargeBuffer(const Napi::CallbackInfo& info);

 private:
  std::vector<uint8_t> buffer_;  // V8 doesn't know about this
};

LargeBuffer::LargeBuffer(const Napi::CallbackInfo& info)
    : Napi::ObjectWrap<LargeBuffer>(info) {
  size_t size = info[0].As<Napi::Number>().Uint32Value();
  buffer_.resize(size);  // Allocates native memory - V8 unaware!
  // V8 thinks heap is small, won't GC even as native memory grows
}
```

**Correct (V8 informed of native allocations):**

```cpp
class LargeBuffer : public Napi::ObjectWrap<LargeBuffer> {
 public:
  static Napi::Object Init(Napi::Env env, Napi::Object exports);
  LargeBuffer(const Napi::CallbackInfo& info);
  ~LargeBuffer();

 private:
  std::vector<uint8_t> buffer_;
  int64_t allocated_size_ = 0;
};

LargeBuffer::LargeBuffer(const Napi::CallbackInfo& info)
    : Napi::ObjectWrap<LargeBuffer>(info) {
  Napi::Env env = info.Env();
  size_t size = info[0].As<Napi::Number>().Uint32Value();

  buffer_.resize(size);
  allocated_size_ = static_cast<int64_t>(size);

  // Tell V8 about the native allocation
  Napi::MemoryManagement::AdjustExternalMemory(env, allocated_size_);
}

LargeBuffer::~LargeBuffer() {
  // Tell V8 the memory is freed (negative value)
  // Note: Must be called from correct thread context
}

// Use weak callback for proper cleanup
void LargeBuffer::Destructor(Napi::Env env, LargeBuffer* instance) {
  Napi::MemoryManagement::AdjustExternalMemory(env, -instance->allocated_size_);
  delete instance;
}
```

**Benefits:**
- V8 GC triggers at appropriate times
- Prevents memory bloat from unreferenced native objects
- Application memory usage stays predictable

**When NOT to use this pattern:**
- For small allocations (<1KB) - overhead exceeds benefit
- For memory managed by external libraries with own pooling

Reference: [N-API Memory Management](https://nodejs.org/api/n-api.html#napi_adjust_external_memory)
