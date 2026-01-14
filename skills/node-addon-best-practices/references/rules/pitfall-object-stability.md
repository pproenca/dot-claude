---
title: Don't Assume JavaScript Object Stability
impact: LOW
impactDescription: Prevents use-after-free crashes from garbage-collected objects
tags: pitfall, gc, references, object-lifetime, memory
---

# Don't Assume JavaScript Object Stability

JavaScript objects can be garbage collected at any time if not referenced. Don't store raw `napi_value` handles long-term. Create persistent references for objects that must survive across calls.

## Why This Matters

- V8's garbage collector runs unpredictably
- Unreferenced objects can be collected between calls
- Stale handles cause crashes or data corruption
- References prevent GC of needed objects

## Incorrect

Storing raw napi_value for later use:

```cpp
#include <napi.h>

// BAD: Storing raw handle that may become invalid
class BadCache {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "BadCache", {
            InstanceMethod("store", &BadCache::Store),
            InstanceMethod("retrieve", &BadCache::Retrieve)
        });
        exports.Set("BadCache", func);
        return exports;
    }

    BadCache(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<BadCache>(info) {}

    void Store(const Napi::CallbackInfo& info) {
        // BAD: Storing raw napi_value
        storedValue_ = info[0];

        // After this function returns, the handle scope closes
        // and storedValue_ becomes a dangling reference!
    }

    Napi::Value Retrieve(const Napi::CallbackInfo& info) {
        // BAD: Using potentially garbage-collected value
        // May crash or return corrupted data
        return storedValue_;
    }

private:
    napi_value storedValue_;  // DANGER: Unprotected handle
};

// BAD: Global storage of handles
static napi_value globalCallback;  // Will become invalid after GC

void StoreCallbackBad(const Napi::CallbackInfo& info) {
    globalCallback = info[0];  // Stored but not protected
}

void InvokeCallbackBad(const Napi::CallbackInfo& info) {
    // May crash - callback might have been GC'd
    Napi::Function cb(info.Env(), globalCallback);
    cb.Call({});
}
```

## Correct

Use persistent references for object persistence:

```cpp
#include <napi.h>

// GOOD: Using Napi::Reference for persistent storage
class GoodCache : public Napi::ObjectWrap<GoodCache> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "GoodCache", {
            InstanceMethod("store", &GoodCache::Store),
            InstanceMethod("retrieve", &GoodCache::Retrieve),
            InstanceMethod("clear", &GoodCache::Clear)
        });
        exports.Set("GoodCache", func);
        return exports;
    }

    GoodCache(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<GoodCache>(info) {}

    void Store(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        // GOOD: Create persistent reference
        // Reference count of 1 prevents GC
        storedRef_ = Napi::Persistent(info[0]);
    }

    Napi::Value Retrieve(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (storedRef_.IsEmpty()) {
            return env.Undefined();
        }

        // GOOD: Get value from persistent reference
        return storedRef_.Value();
    }

    void Clear(const Napi::CallbackInfo& info) {
        // GOOD: Reset reference to allow GC
        storedRef_.Reset();
    }

private:
    Napi::Reference<Napi::Value> storedRef_;  // Persistent reference
};

// GOOD: Global callback with reference
class CallbackHolder {
public:
    static void StoreCallback(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (!info[0].IsFunction()) {
            Napi::TypeError::New(env, "Expected function")
                .ThrowAsJavaScriptException();
            return;
        }

        // GOOD: Persistent reference to callback
        callbackRef_ = Napi::Persistent(info[0].As<Napi::Function>());
    }

    static Napi::Value InvokeCallback(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (callbackRef_.IsEmpty()) {
            Napi::Error::New(env, "No callback stored")
                .ThrowAsJavaScriptException();
            return env.Undefined();
        }

        // GOOD: Get function from reference and call
        Napi::Function cb = callbackRef_.Value();
        return cb.Call({});
    }

    static void ClearCallback(const Napi::CallbackInfo& info) {
        callbackRef_.Reset();
    }

private:
    static Napi::FunctionReference callbackRef_;
};

Napi::FunctionReference CallbackHolder::callbackRef_;
```

## Weak References Pattern

For caches where GC is acceptable:

```cpp
#include <napi.h>
#include <unordered_map>
#include <string>

// GOOD: Weak references allow GC but notify when it happens
class WeakCache : public Napi::ObjectWrap<WeakCache> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "WeakCache", {
            InstanceMethod("set", &WeakCache::Set),
            InstanceMethod("get", &WeakCache::Get),
            InstanceMethod("has", &WeakCache::Has)
        });
        exports.Set("WeakCache", func);
        return exports;
    }

    WeakCache(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<WeakCache>(info) {}

    void Set(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        std::string key = info[0].As<Napi::String>().Utf8Value();
        Napi::Object value = info[1].As<Napi::Object>();

        // Create weak reference (ref count 0)
        auto ref = Napi::Reference<Napi::Object>::New(value, 0);

        cache_[key] = std::move(ref);
    }

    Napi::Value Get(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        std::string key = info[0].As<Napi::String>().Utf8Value();

        auto it = cache_.find(key);
        if (it == cache_.end()) {
            return env.Undefined();
        }

        // Check if reference is still valid
        Napi::Object value = it->second.Value();
        if (value.IsEmpty()) {
            // Object was garbage collected
            cache_.erase(it);
            return env.Undefined();
        }

        return value;
    }

    Napi::Value Has(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        std::string key = info[0].As<Napi::String>().Utf8Value();

        auto it = cache_.find(key);
        if (it == cache_.end()) {
            return Napi::Boolean::New(env, false);
        }

        // Check if still alive
        bool valid = !it->second.Value().IsEmpty();
        if (!valid) {
            cache_.erase(it);
        }

        return Napi::Boolean::New(env, valid);
    }

private:
    std::unordered_map<std::string, Napi::Reference<Napi::Object>> cache_;
};
```

## Reference Types

| Reference Type | Prevents GC | Use Case |
|---------------|-------------|----------|
| `Napi::Reference` (refcount=1) | Yes | Long-term storage |
| `Napi::Reference` (refcount=0) | No | Cache with GC allowed |
| `Napi::Persistent` | Yes | Convenience wrapper |
| Raw `napi_value` | No | Within single function |

## JavaScript Test

```javascript
const addon = require('./build/Release/addon');

describe('Object Stability', () => {
    it('survives garbage collection with reference', () => {
        const cache = new addon.GoodCache();
        cache.store({ data: 'test' });

        // Force GC if available
        if (global.gc) global.gc();

        const retrieved = cache.retrieve();
        expect(retrieved.data).toBe('test');
    });

    it('weak reference allows GC', () => {
        const cache = new addon.WeakCache();
        cache.set('key', { data: 'test' });

        // Force GC
        if (global.gc) global.gc();

        // Object might be collected
        // (behavior depends on V8 internals)
    });
});
```
