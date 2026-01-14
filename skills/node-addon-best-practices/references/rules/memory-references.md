---
title: Create References for Persistent Values
impact: CRITICAL
impactDescription: Unreferenced values are garbage collected causing use-after-free crashes
tags: memory, references, persistent, gc
---

# Create References for Persistent Values

Use `Napi::Reference` or `napi_ref` for JavaScript values that must outlive a single callback invocation. Without references, values may be garbage collected while your native code still holds pointers to them.

## Why This Matters

- **GC Safety**: References prevent premature garbage collection
- **Async Support**: Required for values used across async boundaries
- **Callback Storage**: Essential for storing JS callbacks
- **Crash Prevention**: Avoids use-after-free bugs

## Understanding References

JavaScript values are normally valid only within a callback. When the callback returns, the GC may collect unreferenced values. References explicitly tell the GC to keep values alive.

```
Without Reference:              With Reference:
Callback starts                 Callback starts
  Create value                    Create value
  Store pointer                   Create reference
Callback returns                Callback returns
  GC runs                         GC runs
  Value collected!                Reference keeps value alive
Later use crashes!              Later use works!
```

## Incorrect: Storing Raw napi_value

```cpp
// BAD: Raw napi_value becomes invalid after callback
class EventEmitter {
public:
    void On(const Napi::CallbackInfo& info) {
        std::string event = info[0].As<Napi::String>().Utf8Value();
        Napi::Function callback = info[1].As<Napi::Function>();

        // DANGEROUS: Storing raw Value - will be garbage collected!
        callbacks_[event] = callback;  // callback is just a handle
    }

    void Emit(const Napi::CallbackInfo& info) {
        std::string event = info[0].As<Napi::String>().Utf8Value();

        auto it = callbacks_.find(event);
        if (it != callbacks_.end()) {
            // CRASH: callback was garbage collected!
            it->second.Call({});  // Use after free!
        }
    }

private:
    // BAD: Map of raw Napi::Function values
    std::map<std::string, Napi::Function> callbacks_;
};
```

## Incorrect: Using Pointer to Stack Value

```cpp
// BAD: Pointer to value that goes out of scope
class AsyncTask {
public:
    void Schedule(const Napi::CallbackInfo& info) {
        Napi::Function callback = info[0].As<Napi::Function>();

        // DANGEROUS: callback is a stack value
        callback_ = &callback;  // Points to stack!

        // Start async work...
    }

    void Complete() {
        // CRASH: callback_ points to invalid stack memory
        (*callback_)->Call({});
    }

private:
    Napi::Function* callback_;  // Points to nothing valid
};
```

## Correct: Using Napi::Reference

```cpp
// GOOD: Use Reference to prevent garbage collection
#include <napi.h>
#include <map>
#include <string>

class EventEmitter : public Napi::ObjectWrap<EventEmitter> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "EventEmitter", {
            InstanceMethod("on", &EventEmitter::On),
            InstanceMethod("off", &EventEmitter::Off),
            InstanceMethod("emit", &EventEmitter::Emit)
        });
        exports.Set("EventEmitter", func);
        return exports;
    }

    EventEmitter(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<EventEmitter>(info) {}

    ~EventEmitter() {
        // References are cleaned up automatically in destructor
        callbacks_.clear();
    }

    void On(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (info.Length() < 2 || !info[0].IsString() || !info[1].IsFunction()) {
            throw Napi::TypeError::New(env, "Expected (string, function)");
        }

        std::string event = info[0].As<Napi::String>().Utf8Value();
        Napi::Function callback = info[1].As<Napi::Function>();

        // CORRECT: Create persistent reference
        // Reference count of 1 prevents garbage collection
        callbacks_[event] = Napi::Persistent(callback);
    }

    void Off(const Napi::CallbackInfo& info) {
        std::string event = info[0].As<Napi::String>().Utf8Value();

        auto it = callbacks_.find(event);
        if (it != callbacks_.end()) {
            // Reset releases the reference
            it->second.Reset();
            callbacks_.erase(it);
        }
    }

    void Emit(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        std::string event = info[0].As<Napi::String>().Utf8Value();

        auto it = callbacks_.find(event);
        if (it != callbacks_.end() && !it->second.IsEmpty()) {
            // Value() returns the referenced function
            Napi::Function callback = it->second.Value();

            // Gather additional arguments
            std::vector<napi_value> args;
            for (size_t i = 1; i < info.Length(); i++) {
                args.push_back(info[i]);
            }

            callback.Call(args);
        }
    }

private:
    // CORRECT: Map of FunctionReference
    std::map<std::string, Napi::FunctionReference> callbacks_;
};
```

## Correct: Reference with Raw N-API

```cpp
// GOOD: Raw N-API reference management
typedef struct {
    napi_env env;
    napi_ref callback_ref;
} AsyncContext;

static void StoreCallback(napi_env env, napi_callback_info info) {
    size_t argc = 1;
    napi_value argv[1];
    void* data;
    napi_get_cb_info(env, info, &argc, argv, NULL, &data);

    AsyncContext* ctx = (AsyncContext*)data;

    // Create reference with ref count 1
    napi_status status = napi_create_reference(env, argv[0], 1, &ctx->callback_ref);
    if (status != napi_ok) {
        napi_throw_error(env, NULL, "Failed to create reference");
        return;
    }

    ctx->env = env;
}

static void InvokeCallback(AsyncContext* ctx, const char* message) {
    napi_value callback;

    // Get the function from reference
    napi_status status = napi_get_reference_value(ctx->env, ctx->callback_ref, &callback);
    if (status != napi_ok) return;

    napi_value global, result, msg_value;
    napi_get_global(ctx->env, &global);
    napi_create_string_utf8(ctx->env, message, NAPI_AUTO_LENGTH, &msg_value);

    napi_call_function(ctx->env, global, callback, 1, &msg_value, &result);
}

static void CleanupCallback(AsyncContext* ctx) {
    // Delete reference to allow GC
    napi_delete_reference(ctx->env, ctx->callback_ref);
    ctx->callback_ref = NULL;
}
```

## Pattern: Weak References for Caches

```cpp
// GOOD: Weak reference for caching without preventing GC
class ObjectCache : public Napi::ObjectWrap<ObjectCache> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "ObjectCache", {
            InstanceMethod("set", &ObjectCache::Set),
            InstanceMethod("get", &ObjectCache::Get),
            InstanceMethod("has", &ObjectCache::Has)
        });
        exports.Set("ObjectCache", func);
        return exports;
    }

    ObjectCache(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<ObjectCache>(info) {}

    void Set(const Napi::CallbackInfo& info) {
        std::string key = info[0].As<Napi::String>().Utf8Value();
        Napi::Object value = info[1].As<Napi::Object>();

        // Weak reference (count 0) - doesn't prevent GC
        cache_[key] = Napi::Weak(value);
    }

    Napi::Value Get(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        std::string key = info[0].As<Napi::String>().Utf8Value();

        auto it = cache_.find(key);
        if (it != cache_.end()) {
            // Check if value still exists
            Napi::Value value = it->second.Value();
            if (!value.IsEmpty()) {
                return value;
            }
            // Value was collected - clean up entry
            cache_.erase(it);
        }

        return env.Undefined();
    }

    Napi::Value Has(const Napi::CallbackInfo& info) {
        std::string key = info[0].As<Napi::String>().Utf8Value();

        auto it = cache_.find(key);
        if (it != cache_.end() && !it->second.IsEmpty()) {
            return Napi::Boolean::New(info.Env(), true);
        }

        return Napi::Boolean::New(info.Env(), false);
    }

private:
    std::map<std::string, Napi::ObjectReference> cache_;
};
```

## Pattern: Multiple Callbacks

```cpp
// GOOD: Store multiple callbacks with proper lifecycle
class MultiEmitter : public Napi::ObjectWrap<MultiEmitter> {
public:
    void AddListener(const Napi::CallbackInfo& info) {
        std::string event = info[0].As<Napi::String>().Utf8Value();
        Napi::Function callback = info[1].As<Napi::Function>();

        // Store in vector of references
        listeners_[event].push_back(Napi::Persistent(callback));
    }

    void RemoveListener(const Napi::CallbackInfo& info) {
        std::string event = info[0].As<Napi::String>().Utf8Value();
        Napi::Function callback = info[1].As<Napi::Function>();

        auto& vec = listeners_[event];
        vec.erase(
            std::remove_if(vec.begin(), vec.end(),
                [&callback](const Napi::FunctionReference& ref) {
                    return ref.Value() == callback;
                }),
            vec.end()
        );
    }

    void Emit(const Napi::CallbackInfo& info) {
        std::string event = info[0].As<Napi::String>().Utf8Value();

        auto it = listeners_.find(event);
        if (it == listeners_.end()) return;

        std::vector<napi_value> args;
        for (size_t i = 1; i < info.Length(); i++) {
            args.push_back(info[i]);
        }

        // Call all listeners
        for (auto& ref : it->second) {
            if (!ref.IsEmpty()) {
                ref.Value().Call(args);
            }
        }
    }

    void RemoveAllListeners(const Napi::CallbackInfo& info) {
        if (info.Length() > 0 && info[0].IsString()) {
            std::string event = info[0].As<Napi::String>().Utf8Value();
            listeners_.erase(event);
        } else {
            listeners_.clear();
        }
    }

private:
    std::map<std::string, std::vector<Napi::FunctionReference>> listeners_;
};
```

## Reference Counting

```cpp
// Managing reference counts manually
void ManageRefCount(napi_env env, napi_ref ref) {
    uint32_t count;

    // Increment reference count (prevent GC)
    napi_reference_ref(env, ref, &count);  // count is now 2

    // Decrement reference count
    napi_reference_unref(env, ref, &count);  // count is now 1

    // When count reaches 0, value can be collected
    // but reference still exists (can check if value is gone)
}
```

## References

- [N-API Reference API](https://nodejs.org/api/n-api.html#references-to-values-with-a-lifespan-longer-than-that-of-the-native-method)
- [node-addon-api Reference](https://github.com/nodejs/node-addon-api/blob/main/doc/reference.md)
