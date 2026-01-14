---
title: Create References for Persistent JavaScript Objects
impact: CRITICAL
impactDescription: Prevents use-after-free and premature GC of JS objects
tags: memory, references, gc, persistence
---

# Create References for Persistent JavaScript Objects

When native code needs to hold onto a JavaScript object beyond the current callback scope (e.g., storing a callback for later invocation), you must create a reference. Without a reference, the garbage collector may free the object, causing crashes when you try to use it later.

## Why This Matters

- **Use-After-Free**: Accessing GC'd objects causes crashes or corruption
- **Callback Storage**: Async operations need to store callbacks safely
- **Event Emitters**: Persistent listeners require references
- **Caching**: Any JS object cache needs reference management

## How References Work

```
Without Reference:
┌──────────────────────────────────────────────┐
│ JavaScript                                    │
│   callback function ────────────────────┐    │
└────────────────────────────────────────│────┘
                                         │
┌────────────────────────────────────────│────┐
│ Native Code                            │    │
│   napi_value callback ──────────────────    │
│   (only valid during current callback!)     │
└─────────────────────────────────────────────┘

After callback returns, GC runs:
┌──────────────────────────────────────────────┐
│ JavaScript                                    │
│   callback function 💀 (garbage collected)   │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Native Code                                   │
│   napi_value callback → DANGLING POINTER     │
│   Later access = CRASH                        │
└──────────────────────────────────────────────┘

With Reference:
┌──────────────────────────────────────────────┐
│ JavaScript                                    │
│   callback function ◄───────────────────┐    │
│   (ref count > 0, won't be GC'd)       │    │
└────────────────────────────────────────│────┘
                                         │
┌────────────────────────────────────────│────┐
│ Native Code                            │    │
│   napi_ref reference ──────────────────┘    │
│   (prevents GC, safe to use later)          │
└─────────────────────────────────────────────┘
```

## Incorrect: Storing napi_value Directly

```cpp
// BAD: Storing napi_value for later use - WILL CRASH
#define NAPI_VERSION 8
#include <napi.h>

class BadEventEmitter {
public:
    void SetCallback(napi_value callback) {
        // BAD: napi_value is only valid during current callback!
        stored_callback_ = callback;  // Dangling after scope ends
    }

    void EmitEvent(napi_env env) {
        // CRASH: stored_callback_ points to freed memory
        napi_call_function(env, /* ... */, stored_callback_, /* ... */);
    }

private:
    napi_value stored_callback_;  // DANGER: Will become invalid
};
```

## Correct: Using Napi::Reference (node-addon-api)

```cpp
// GOOD: Napi::Reference keeps object alive
#define NAPI_VERSION 8
#include <napi.h>

class EventEmitter : public Napi::ObjectWrap<EventEmitter> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "EventEmitter", {
            InstanceMethod("on", &EventEmitter::On),
            InstanceMethod("emit", &EventEmitter::Emit),
            InstanceMethod("removeListener", &EventEmitter::RemoveListener)
        });

        exports.Set("EventEmitter", func);
        return exports;
    }

    EventEmitter(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<EventEmitter>(info) {}

    ~EventEmitter() {
        // References are automatically cleaned up
        callbacks_.clear();
    }

private:
    Napi::Value On(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (info.Length() < 2 || !info[0].IsString() || !info[1].IsFunction()) {
            Napi::TypeError::New(env, "Expected (event, callback)").ThrowAsJavaScriptException();
            return env.Undefined();
        }

        std::string event = info[0].As<Napi::String>().Utf8Value();
        Napi::Function callback = info[1].As<Napi::Function>();

        // Create a persistent reference to the callback
        // Reference count of 1 prevents GC
        Napi::FunctionReference ref = Napi::Persistent(callback);
        ref.SuppressDestruct();  // Don't release in destructor

        callbacks_[event].push_back(std::move(ref));

        return info.This();
    }

    Napi::Value Emit(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (info.Length() < 1 || !info[0].IsString()) {
            Napi::TypeError::New(env, "Expected event name").ThrowAsJavaScriptException();
            return env.Undefined();
        }

        std::string event = info[0].As<Napi::String>().Utf8Value();

        auto it = callbacks_.find(event);
        if (it == callbacks_.end()) {
            return Napi::Boolean::New(env, false);
        }

        // Collect additional arguments
        std::vector<napi_value> args;
        for (size_t i = 1; i < info.Length(); i++) {
            args.push_back(info[i]);
        }

        // Call all registered callbacks
        for (auto& ref : it->second) {
            // Get the function from the reference
            Napi::Function callback = ref.Value();
            callback.Call(info.This(), args);
        }

        return Napi::Boolean::New(env, true);
    }

    Napi::Value RemoveListener(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (info.Length() < 2 || !info[0].IsString() || !info[1].IsFunction()) {
            Napi::TypeError::New(env, "Expected (event, callback)").ThrowAsJavaScriptException();
            return env.Undefined();
        }

        std::string event = info[0].As<Napi::String>().Utf8Value();
        Napi::Function callback = info[1].As<Napi::Function>();

        auto it = callbacks_.find(event);
        if (it != callbacks_.end()) {
            auto& vec = it->second;
            vec.erase(
                std::remove_if(vec.begin(), vec.end(),
                    [&callback](const Napi::FunctionReference& ref) {
                        return ref.Value().StrictEquals(callback);
                    }),
                vec.end()
            );
        }

        return info.This();
    }

    std::unordered_map<std::string, std::vector<Napi::FunctionReference>> callbacks_;
};
```

## Correct: Async Callback Storage

```cpp
// GOOD: Storing callback for async completion
#define NAPI_VERSION 8
#include <napi.h>
#include <thread>

class AsyncTask {
public:
    AsyncTask(Napi::Env env, Napi::Function callback)
        : env_(env),
          callback_(Napi::Persistent(callback)),
          completed_(false) {
        callback_.SuppressDestruct();
    }

    void Execute() {
        // Simulate async work on background thread
        std::thread([this]() {
            // Do heavy computation
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
            result_ = 42;
            completed_ = true;

            // Call back to main thread (in real code, use uv_async or TSFN)
        }).detach();
    }

    void Complete() {
        if (completed_ && !callback_.IsEmpty()) {
            Napi::HandleScope scope(env_);

            // Retrieve function from reference
            Napi::Function cb = callback_.Value();
            cb.Call(env_.Global(), {
                env_.Null(),
                Napi::Number::New(env_, result_)
            });

            // Release the reference
            callback_.Reset();
        }
    }

private:
    Napi::Env env_;
    Napi::FunctionReference callback_;
    bool completed_;
    int result_;
};
```

## Correct: Raw N-API References

```cpp
// GOOD: Raw N-API reference management
typedef struct {
    napi_env env;
    napi_ref callback_ref;
    int result;
} AsyncData;

void StoreCallback(napi_env env, napi_value callback, AsyncData* data) {
    data->env = env;

    // Create reference with refcount 1 (prevents GC)
    napi_status status = napi_create_reference(env, callback, 1, &data->callback_ref);
    if (status != napi_ok) {
        napi_throw_error(env, NULL, "Failed to create reference");
    }
}

void InvokeStoredCallback(AsyncData* data) {
    napi_env env = data->env;

    // Retrieve the callback from reference
    napi_value callback;
    napi_status status = napi_get_reference_value(env, data->callback_ref, &callback);
    if (status != napi_ok || callback == NULL) {
        return;  // Reference was cleared or object was GC'd
    }

    // Call the callback
    napi_value global;
    napi_get_global(env, &global);

    napi_value argv[2];
    napi_get_null(env, &argv[0]);
    napi_create_int32(env, data->result, &argv[1]);

    napi_value result;
    napi_call_function(env, global, callback, 2, argv, &result);

    // Delete the reference when done
    napi_delete_reference(env, data->callback_ref);
    data->callback_ref = NULL;
}

void CleanupAsyncData(AsyncData* data) {
    if (data->callback_ref != NULL) {
        napi_delete_reference(data->env, data->callback_ref);
        data->callback_ref = NULL;
    }
    free(data);
}
```

## Correct: Weak References for Caching

```cpp
// GOOD: Weak references for cache that allows GC
#define NAPI_VERSION 8
#include <napi.h>

class ObjectCache {
public:
    void Store(const std::string& key, Napi::Object obj) {
        // Weak reference (refcount 0) - allows object to be GC'd
        Napi::ObjectReference ref = Napi::Weak(obj);
        cache_[key] = std::move(ref);
    }

    Napi::Value Get(Napi::Env env, const std::string& key) {
        auto it = cache_.find(key);
        if (it == cache_.end()) {
            return env.Undefined();
        }

        Napi::Value value = it->second.Value();

        // Check if object was garbage collected
        if (value.IsEmpty() || value.IsUndefined()) {
            cache_.erase(it);
            return env.Undefined();
        }

        return value;
    }

private:
    std::unordered_map<std::string, Napi::ObjectReference> cache_;
};
```

## Reference Lifecycle Checklist

1. **Create**: `napi_create_reference` or `Napi::Persistent/Weak`
2. **Use**: `napi_get_reference_value` or `ref.Value()`
3. **Update refcount**: `napi_reference_ref/unref` if needed
4. **Delete**: `napi_delete_reference` or `ref.Reset()` when done
5. **Check validity**: Always check if value is empty/undefined after getting
