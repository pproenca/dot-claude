---
title: Use Lazy Initialization for Heavy Resources
impact: MEDIUM
impactDescription: faster module load time
tags: build, lazy, initialization, startup
---

## Use Lazy Initialization for Heavy Resources

Defer expensive initialization until first use instead of module load time.

**Incorrect (eager initialization):**

```cpp
static HeavyResource* resource = nullptr;

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  // Blocks require() for seconds!
  resource = new HeavyResource();
  resource->LoadData();

  return exports;
}
```

**Correct (lazy initialization):**

```cpp
static std::once_flag init_flag;
static HeavyResource* resource = nullptr;

HeavyResource* GetResource() {
  std::call_once(init_flag, []() {
    resource = new HeavyResource();
    resource->LoadData();
  });
  return resource;
}

Napi::Value UseResource(const Napi::CallbackInfo& info) {
  // Initialize on first use
  HeavyResource* res = GetResource();
  return res->Process(info);
}
```

Reference: [std::call_once](https://en.cppreference.com/w/cpp/thread/call_once)
