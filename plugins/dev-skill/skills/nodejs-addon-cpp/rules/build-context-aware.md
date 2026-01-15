---
title: Use Context-Aware Addons
impact: MEDIUM
impactDescription: enables worker threads and multiple contexts
tags: build, context-aware, workers, isolation
---

## Use Context-Aware Addons

Build context-aware addons to support Worker threads and multiple V8 contexts.

**Incorrect (not context-aware):**

```cpp
// Global state - breaks with workers
static int global_counter = 0;

NODE_MODULE(addon, Init)
```

**Correct (context-aware):**

```cpp
// Per-context state
class AddonData {
 public:
  int counter = 0;
};

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  // Store per-context data
  AddonData* data = new AddonData();
  env.SetInstanceData(data);

  exports.Set("increment", Napi::Function::New(env, [](const Napi::CallbackInfo& info) {
    AddonData* data = info.Env().GetInstanceData<AddonData>();
    return Napi::Number::New(info.Env(), ++data->counter);
  }));

  return exports;
}

NODE_API_MODULE(addon, Init)
```

Reference: [Context-Aware Addons](https://nodejs.org/api/addons.html#context-aware-addons)
