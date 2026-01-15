---
title: Avoid Callbacks in Hot Loops
impact: CRITICAL
impactDescription: 50-200× improvement in tight loops
tags: boundary, callbacks, hot-loops, performance
---

## Avoid Callbacks in Hot Loops

Calling JS callbacks from C++ in a tight loop incurs massive overhead. Each callback requires context switching, handle scope creation, and argument marshaling.

**Incorrect (callback per iteration):**

```cpp
Napi::Value ProcessWithCallback(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array data = info[0].As<Napi::Array>();
  Napi::Function callback = info[1].As<Napi::Function>();

  for (uint32_t i = 0; i < data.Length(); i++) {
    Napi::Value item = data[i];
    // Call JS callback for EACH item - extremely slow
    callback.Call({item});  // ~1000ns per call
  }
  return env.Undefined();
}
```

**Correct (batch results, single callback):**

```cpp
Napi::Value ProcessWithCallback(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array data = info[0].As<Napi::Array>();
  Napi::Function callback = info[1].As<Napi::Function>();

  // Process all items natively
  Napi::Array results = Napi::Array::New(env, data.Length());
  for (uint32_t i = 0; i < data.Length(); i++) {
    Napi::Value item = data[i];
    // Process natively
    results[i] = ProcessNatively(env, item);
  }

  // Single callback with all results
  callback.Call({results});
  return env.Undefined();
}
```

**Alternative (streaming with chunks):**

```cpp
// For very large datasets, callback with chunks
const size_t CHUNK_SIZE = 1000;
for (size_t start = 0; start < length; start += CHUNK_SIZE) {
  size_t end = std::min(start + CHUNK_SIZE, length);
  Napi::Array chunk = Napi::Array::New(env, end - start);
  // Fill chunk
  callback.Call({chunk, Napi::Number::New(env, start)});
}
```

**When NOT to use this pattern:**
- When callback performs async I/O that can overlap with native processing
- When immediate streaming feedback is required for UX

Reference: [V8 Embedder's Guide](https://v8.dev/docs/embed)
