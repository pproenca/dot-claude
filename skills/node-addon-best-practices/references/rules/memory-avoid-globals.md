---
title: Avoid Global Object References
impact: CRITICAL
impactDescription: Global references prevent GC and cause memory leaks across module reloads
tags: memory, globals, lifecycle, references
---

# Avoid Global Object References

Never store persistent references to JavaScript objects in global or static variables without proper lifecycle management. Global references prevent garbage collection and leak memory across module reloads.

## Why This Matters

- **Memory Leaks**: Global refs prevent GC indefinitely
- **Module Reload Issues**: References survive module unload
- **Worker Thread Problems**: Globals are per-isolate
- **Testing Difficulty**: State persists between tests

## Understanding the Problem

Global C++ variables persist for the process lifetime, but JavaScript values should be collected when unreachable. Storing JS references globally creates a mismatch.

```
Process Start
  │
  ├─> Module Load #1
  │     └─> Store globalRef = someJSObject
  │
  ├─> Module Unload (require.cache cleared)
  │     └─> globalRef still holds reference!
  │         └─> someJSObject cannot be GC'd
  │
  ├─> Module Load #2
  │     └─> Store globalRef = newJSObject
  │         └─> Old object STILL not GC'd (leaked!)
  │
  └─> Repeat = unbounded memory growth
```

## Incorrect: Static Reference

```cpp
// BAD: Static reference never released
#include <napi.h>

// Global/static reference - DANGEROUS
static Napi::FunctionReference globalCallback;

Napi::Value SetCallback(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Store in static - never properly cleaned up
    globalCallback = Napi::Persistent(info[0].As<Napi::Function>());

    return env.Undefined();
}

Napi::Value InvokeCallback(const Napi::CallbackInfo& info) {
    if (!globalCallback.IsEmpty()) {
        globalCallback.Call({});
    }
    return info.Env().Undefined();
}

// Problems:
// 1. Callback function can never be garbage collected
// 2. If module is reloaded, old callback leaks
// 3. Worker threads have separate globalCallback (undefined behavior)
```

## Incorrect: Global Instance Data

```cpp
// BAD: Raw global pointer to instance
class DatabasePool {
public:
    static DatabasePool* instance;  // Global raw pointer

    static void SetInstance(DatabasePool* pool) {
        instance = pool;  // No cleanup of previous
    }
};

DatabasePool* DatabasePool::instance = nullptr;

Napi::Value CreatePool(const Napi::CallbackInfo& info) {
    // Leaks previous instance!
    DatabasePool::SetInstance(new DatabasePool());
    return info.Env().Undefined();
}
```

## Correct: Instance Data Per Environment

```cpp
// GOOD: Use per-environment instance data
#include <napi.h>

class AddonData {
public:
    Napi::FunctionReference callback;
    Napi::ObjectReference config;

    // Constructor/destructor handle cleanup
    AddonData() {}
    ~AddonData() {
        callback.Reset();
        config.Reset();
    }
};

Napi::Value SetCallback(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Get per-environment data
    AddonData* data = env.GetInstanceData<AddonData>();

    // Properly release previous callback
    data->callback.Reset();

    // Store new callback
    data->callback = Napi::Persistent(info[0].As<Napi::Function>());

    return env.Undefined();
}

Napi::Value InvokeCallback(const Napi::CallbackInfo& info) {
    AddonData* data = info.Env().GetInstanceData<AddonData>();

    if (data && !data->callback.IsEmpty()) {
        data->callback.Call({});
    }

    return info.Env().Undefined();
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    // Create per-environment data with destructor
    AddonData* data = new AddonData();
    env.SetInstanceData<AddonData>(data);

    exports.Set("setCallback", Napi::Function::New(env, SetCallback));
    exports.Set("invokeCallback", Napi::Function::New(env, InvokeCallback));

    return exports;
}

NODE_API_MODULE(addon, Init)
```

## Correct: Raw N-API Instance Data

```cpp
// GOOD: Raw N-API with proper cleanup
#define NAPI_VERSION 8
#include <node_api.h>

typedef struct {
    napi_ref callback_ref;
    napi_ref config_ref;
} AddonData;

static void AddonDataCleanup(napi_env env, void* data, void* hint) {
    AddonData* addon_data = (AddonData*)data;

    // Clean up references
    if (addon_data->callback_ref) {
        napi_delete_reference(env, addon_data->callback_ref);
    }
    if (addon_data->config_ref) {
        napi_delete_reference(env, addon_data->config_ref);
    }

    free(addon_data);
}

static napi_value Init(napi_env env, napi_value exports) {
    // Allocate per-environment data
    AddonData* data = (AddonData*)calloc(1, sizeof(AddonData));

    // Set with cleanup callback
    napi_set_instance_data(env, data, AddonDataCleanup, NULL);

    // ... register functions ...

    return exports;
}

static napi_value SetCallback(napi_env env, napi_callback_info info) {
    size_t argc = 1;
    napi_value argv[1];
    napi_get_cb_info(env, info, &argc, argv, NULL, NULL);

    // Get per-environment data
    AddonData* data;
    napi_get_instance_data(env, (void**)&data);

    // Clean up previous reference
    if (data->callback_ref) {
        napi_delete_reference(env, data->callback_ref);
    }

    // Create new reference
    napi_create_reference(env, argv[0], 1, &data->callback_ref);

    return NULL;
}
```

## Pattern: ObjectWrap with Instance Data

```cpp
// GOOD: Combine ObjectWrap with environment instance data
class ServiceManager : public Napi::ObjectWrap<ServiceManager> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "ServiceManager", {
            InstanceMethod("register", &ServiceManager::Register),
            InstanceMethod("invoke", &ServiceManager::Invoke),
            StaticMethod("getInstance", &ServiceManager::GetInstance)
        });

        // Store constructor in instance data for later access
        Napi::FunctionReference* constructor = new Napi::FunctionReference();
        *constructor = Napi::Persistent(func);
        env.SetInstanceData(constructor);

        exports.Set("ServiceManager", func);
        return exports;
    }

    static Napi::Value GetInstance(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        Napi::FunctionReference* constructor = env.GetInstanceData<Napi::FunctionReference>();

        // Create singleton per environment
        if (!singletonRef_.IsEmpty()) {
            return singletonRef_.Value();
        }

        Napi::Object instance = constructor->New({});
        singletonRef_ = Napi::Persistent(instance);
        return instance;
    }

private:
    // Per-instance reference, not global
    static Napi::ObjectReference singletonRef_;
};

// This is still a static, but managed per-environment through instance data
Napi::ObjectReference ServiceManager::singletonRef_;
```

## Pattern: Weak Reference for Caching

```cpp
// GOOD: Weak references for caches that don't prevent GC
class ObjectCache : public Napi::ObjectWrap<ObjectCache> {
public:
    void Store(const Napi::CallbackInfo& info) {
        std::string key = info[0].As<Napi::String>().Utf8Value();
        Napi::Object value = info[1].As<Napi::Object>();

        // Weak reference - doesn't prevent GC
        cache_[key] = Napi::Reference<Napi::Object>::New(value, 0);
    }

    Napi::Value Retrieve(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        std::string key = info[0].As<Napi::String>().Utf8Value();

        auto it = cache_.find(key);
        if (it != cache_.end()) {
            Napi::Value value = it->second.Value();
            if (!value.IsEmpty()) {
                return value;
            }
            // Value was collected - remove from cache
            cache_.erase(it);
        }

        return env.Undefined();
    }

private:
    // Weak references allow GC to collect cached objects
    std::map<std::string, Napi::Reference<Napi::Object>> cache_;
};
```

## Anti-Pattern: Global Singleton

```cpp
// BAD: Global singleton pattern
class BadSingleton {
public:
    static BadSingleton& getInstance() {
        static BadSingleton instance;  // Global static
        return instance;
    }

    Napi::FunctionReference callback;  // Never cleaned up!
};

// GOOD: Per-environment singleton
class GoodSingleton {
public:
    static GoodSingleton* getInstance(Napi::Env env) {
        return env.GetInstanceData<GoodSingleton>();
    }

    Napi::FunctionReference callback;

    ~GoodSingleton() {
        callback.Reset();  // Proper cleanup
    }
};
```

## Testing Instance Data Cleanup

```javascript
// test/lifecycle.test.js
const assert = require('assert');

describe('Module lifecycle', () => {
    it('should not leak on reload', () => {
        // Load module
        const addon = require('./build/Release/addon');
        addon.setCallback(() => console.log('callback 1'));

        // Clear cache and reload
        delete require.cache[require.resolve('./build/Release/addon')];
        const addon2 = require('./build/Release/addon');

        // New callback should work, old should be cleaned up
        addon2.setCallback(() => console.log('callback 2'));

        // Force GC if available
        if (global.gc) global.gc();

        // Memory should not grow unboundedly
    });
});
```

## References

- [N-API Instance Data](https://nodejs.org/api/n-api.html#napi_set_instance_data)
- [Node.js Worker Threads](https://nodejs.org/api/worker_threads.html)
- [Module Lifecycle](https://nodejs.org/api/modules.html#modules_caching)
