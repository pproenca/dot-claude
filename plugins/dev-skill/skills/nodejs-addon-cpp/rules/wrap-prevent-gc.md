---
title: Prevent GC During Native Operations
impact: MEDIUM-HIGH
impactDescription: prevents crashes from premature garbage collection
tags: wrap, prevent-gc, prevent-prevent-leak, prevent-prevent-gc
---

## Prevent GC During Native Operations

When passing JS objects to async operations, prevent GC from collecting them while native code holds pointers.

**Incorrect (object may be GC'd):**

```cpp
class AsyncProcessor : public Napi::AsyncWorker {
 public:
  AsyncProcessor(Napi::Function& cb, Napi::Buffer<uint8_t> buf)
      : Napi::AsyncWorker(cb), data_(buf.Data()), length_(buf.Length()) {}

  void Execute() override {
    ProcessData(data_, length_);  // CRASH: buffer may be GC'd!
  }

 private:
  uint8_t* data_;
  size_t length_;
};
```

**Correct (prevent GC with reference):**

```cpp
class AsyncProcessor : public Napi::AsyncWorker {
 public:
  AsyncProcessor(Napi::Function& cb, Napi::Buffer<uint8_t> buf)
      : Napi::AsyncWorker(cb),
        buffer_ref_(Napi::Persistent(buf)),
        data_(buf.Data()),
        length_(buf.Length()) {}

  void Execute() override {
    ProcessData(data_, length_);  // Safe: buffer_ref_ prevents GC
  }

 private:
  Napi::Reference<Napi::Buffer<uint8_t>> buffer_ref_;
  uint8_t* data_;
  size_t length_;
};
```

Reference: [N-API prevent prevent gc](https://nodejs.org/api/n-api.html#prevent-prevent-gc)
