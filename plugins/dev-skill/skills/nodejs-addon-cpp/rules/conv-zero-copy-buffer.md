---
title: Use Zero-Copy Buffer Access
impact: HIGH
impactDescription: eliminates buffer copying overhead entirely
tags: conv, zero-copy, buffer, memory
---

## Use Zero-Copy Buffer Access

When receiving Buffer or ArrayBuffer from JS, access the underlying memory directly instead of copying.

**Incorrect (unnecessary copy):**

```cpp
Napi::Value ProcessBuffer(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();

  // Copy into vector - wastes memory and CPU
  std::vector<uint8_t> data(buffer.Data(), buffer.Data() + buffer.Length());

  ProcessData(data.data(), data.size());

  return env.Undefined();
}
```

**Correct (direct access):**

```cpp
Napi::Value ProcessBuffer(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();

  // Direct pointer access - no copy
  uint8_t* data = buffer.Data();
  size_t length = buffer.Length();

  ProcessData(data, length);

  return env.Undefined();
}
```

**For ArrayBuffer:**

```cpp
Napi::Value ProcessArrayBuffer(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::ArrayBuffer ab = info[0].As<Napi::ArrayBuffer>();

  // Direct access to ArrayBuffer data
  void* data = ab.Data();
  size_t length = ab.ByteLength();

  ProcessData(static_cast<uint8_t*>(data), length);

  return env.Undefined();
}
```

**Returning data without copy (External Buffer):**

```cpp
class NativeBuffer {
 public:
  NativeBuffer(size_t size) : data_(size) {
    // Fill with native data
    GenerateData(data_.data(), data_.size());
  }

  uint8_t* Data() { return data_.data(); }
  size_t Size() { return data_.size(); }

 private:
  std::vector<uint8_t> data_;
};

Napi::Value CreateExternalBuffer(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  size_t size = info[0].As<Napi::Number>().Uint32Value();

  // Native buffer with our data
  NativeBuffer* native = new NativeBuffer(size);

  // Create JS Buffer wrapping native memory - NO COPY
  return Napi::Buffer<uint8_t>::New(
    env,
    native->Data(),
    native->Size(),
    // Destructor called when JS Buffer is GC'd
    [](Napi::Env, uint8_t*, NativeBuffer* hint) {
      delete hint;
    },
    native
  );
}
```

**Warning - data lifetime:**

```cpp
// DANGEROUS - data may be GC'd during async operation
Napi::Value DangerousAsync(const Napi::CallbackInfo& info) {
  Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();
  uint8_t* data = buffer.Data();  // Pointer to JS-managed memory

  // BUG: buffer may be GC'd while async work is pending!
  QueueAsyncWork([data]() {
    ProcessData(data, ...);  // CRASH - data might be freed
  });

  return info.Env().Undefined();
}

// SAFE - reference prevents GC
Napi::Value SafeAsync(const Napi::CallbackInfo& info) {
  Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();

  // Store reference to prevent GC
  auto ref = Napi::Persistent(buffer);
  uint8_t* data = buffer.Data();
  size_t length = buffer.Length();

  QueueAsyncWork([data, length, ref = std::move(ref)]() {
    ProcessData(data, length);  // Safe - ref keeps buffer alive
  });

  return info.Env().Undefined();
}
```

Reference: [Node.js Buffer Documentation](https://nodejs.org/api/buffer.html)
