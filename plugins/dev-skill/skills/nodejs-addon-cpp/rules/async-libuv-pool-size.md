---
title: Configure UV_THREADPOOL_SIZE for Workload
impact: HIGH
impactDescription: 2-4× throughput for I/O-bound addons
tags: async, libuv, threadpool, configuration
---

## Configure UV_THREADPOOL_SIZE for Workload

The libuv thread pool defaults to 4 threads. For addons with heavy async operations, increase this to match your workload.

**Incorrect (default pool size):**

```javascript
// No configuration - uses default 4 threads
const addon = require('./build/Release/addon');

// With 100 concurrent async operations, only 4 run in parallel
// 96 operations wait in queue
for (let i = 0; i < 100; i++) {
  addon.asyncOperation(data[i], callback);
}
```

**Correct (sized pool):**

```javascript
// Set BEFORE requiring any native modules
process.env.UV_THREADPOOL_SIZE = '16';  // Must be string

// Or set in environment before starting Node
// UV_THREADPOOL_SIZE=16 node app.js

const addon = require('./build/Release/addon');

// Now 16 operations can run in parallel
for (let i = 0; i < 100; i++) {
  addon.asyncOperation(data[i], callback);
}
```

**Programmatic check and documentation:**

```cpp
// In addon init, document thread pool usage
Napi::Object Init(Napi::Env env, Napi::Object exports) {
  // Check current pool size
  const char* pool_size = std::getenv("UV_THREADPOOL_SIZE");
  int size = pool_size ? std::atoi(pool_size) : 4;

  // Warn if pool might be undersized
  if (size < 8) {
    Napi::Error::New(env,
      "Warning: UV_THREADPOOL_SIZE is " + std::to_string(size) +
      ". Increase to 8+ for better async performance."
    ).ThrowAsJavaScriptException();
  }

  // Export pool info
  exports.Set("threadPoolSize", Napi::Number::New(env, size));

  return exports;
}
```

**Guidelines for sizing:**
- CPU-bound tasks: `UV_THREADPOOL_SIZE` = number of CPU cores
- I/O-bound tasks: `UV_THREADPOOL_SIZE` = 2-4× number of CPU cores
- Mixed workloads: Profile to find optimal value
- Maximum: 1024 (hard limit in libuv)

**Self-sizing addon:**

```cpp
#include <thread>

int RecommendPoolSize(bool io_bound) {
  int cores = std::thread::hardware_concurrency();
  if (io_bound) {
    return std::min(cores * 4, 128);
  }
  return cores;
}

Napi::Value GetRecommendedPoolSize(const Napi::CallbackInfo& info) {
  bool io_bound = info[0].As<Napi::Boolean>().Value();
  return Napi::Number::New(info.Env(), RecommendPoolSize(io_bound));
}
```

```javascript
// Application startup
const addon = require('./build/Release/addon');
const recommended = addon.getRecommendedPoolSize(true);

if (!process.env.UV_THREADPOOL_SIZE) {
  console.warn(`Set UV_THREADPOOL_SIZE=${recommended} for optimal performance`);
}
```

**When NOT to increase pool size:**
- Memory-constrained environments (each thread uses stack space)
- Mostly synchronous operations
- When using custom thread pools instead of libuv's

Reference: [libuv Threadpool Documentation](https://docs.libuv.org/en/v1.x/threadpool.html)
