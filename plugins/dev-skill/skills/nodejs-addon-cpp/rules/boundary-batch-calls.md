---
title: Batch Multiple Operations in Single Call
impact: CRITICAL
impactDescription: 10-100× improvement for repeated operations
tags: boundary, batching, performance, call-overhead
---

## Batch Multiple Operations in Single Call

Each JS→C++ boundary crossing costs ~100-1000ns. When performing many similar operations, batch them into a single native call that processes an array.

**Incorrect (N boundary crossings):**

```javascript
// JavaScript - calling native function in loop
const addon = require('./build/Release/addon');

const results = [];
for (let i = 0; i < 10000; i++) {
  results.push(addon.processItem(items[i]));  // 10,000 boundary crossings
}
```

```cpp
// C++ - processes one item per call
Napi::Value ProcessItem(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  auto item = info[0].As<Napi::Object>();
  // Process single item
  return Napi::Number::New(env, result);
}
```

**Correct (1 boundary crossing):**

```javascript
// JavaScript - single call with array
const addon = require('./build/Release/addon');

const results = addon.processItems(items);  // 1 boundary crossing
```

```cpp
// C++ - processes entire array
Napi::Value ProcessItems(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array items = info[0].As<Napi::Array>();
  uint32_t length = items.Length();

  Napi::Array results = Napi::Array::New(env, length);
  for (uint32_t i = 0; i < length; i++) {
    Napi::Value item = items[i];
    // Process item
    results[i] = Napi::Number::New(env, result);
  }
  return results;
}
```

**Benefits:**
- Eliminates N-1 boundary crossings
- Better CPU cache utilization
- Allows native-side vectorization

Reference: [Node-API Documentation](https://nodejs.org/api/n-api.html)
