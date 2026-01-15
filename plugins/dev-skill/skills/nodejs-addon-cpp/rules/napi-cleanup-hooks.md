---
title: Register Cleanup Hooks for Module Unload
impact: MEDIUM
impactDescription: prevents resource leaks on module unload
tags: napi, cleanup, hooks, unload
---

## Register Cleanup Hooks for Module Unload

Register cleanup hooks to release resources when the addon is unloaded or Node.js exits.

**Incorrect (no cleanup):**

```cpp
static Database* global_db = nullptr;

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  global_db = new Database();
  // Memory leak on module unload!
  return exports;
}
```

**Correct (cleanup hook):**

```cpp
static Database* global_db = nullptr;

void Cleanup(void* arg) {
  delete global_db;
  global_db = nullptr;
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  global_db = new Database();

  napi_add_env_cleanup_hook(env, Cleanup, nullptr);

  return exports;
}
```

Reference: [Environment Cleanup Hooks](https://nodejs.org/api/n-api.html#cleanup-on-exit-of-the-current-nodejs-environment)
