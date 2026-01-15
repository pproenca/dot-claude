---
title: Use Weak References to Prevent Memory Leaks
impact: CRITICAL
impactDescription: eliminates memory leaks in wrapped objects
tags: mem, weak-references, prevent-leaks, prevent-gc
---

## Use Weak References to Prevent Memory Leaks

Memory leaks happen when C++ prevents JavaScript objects from being garbage collected. Use weak references and weak callbacks for proper cleanup.

**Incorrect (memory leak from strong reference):**

```cpp
class DataProcessor : public Napi::ObjectWrap<DataProcessor> {
 public:
  DataProcessor(const Napi::CallbackInfo& info)
      : Napi::ObjectWrap<DataProcessor>(info) {
    // Store strong reference to callback - LEAK!
    callback_ = Napi::Persistent(info[0].As<Napi::Function>());
    // This prevents the callback from ever being GC'd
  }

 private:
  Napi::Reference<Napi::Function> callback_;
};
```

**Correct (weak reference with cleanup):**

```cpp
class DataProcessor : public Napi::ObjectWrap<DataProcessor> {
 public:
  static Napi::Object Init(Napi::Env env, Napi::Object exports) {
    Napi::Function func = DefineClass(env, "DataProcessor", {
      InstanceMethod("dispose", &DataProcessor::Dispose),
    });
    exports.Set("DataProcessor", func);
    return exports;
  }

  DataProcessor(const Napi::CallbackInfo& info)
      : Napi::ObjectWrap<DataProcessor>(info) {
    Napi::Env env = info.Env();

    // Use weak reference - allows callback to be GC'd
    callback_ = Napi::Reference<Napi::Function>::New(
      info[0].As<Napi::Function>(),
      0  // ref count = 0 means weak reference
    );
  }

  void Dispose(const Napi::CallbackInfo& info) {
    // Explicit cleanup
    callback_.Reset();
  }

  ~DataProcessor() {
    // Note: destructor may not run until GC
  }

  bool HasCallback() {
    return !callback_.IsEmpty();
  }

  void InvokeCallback(Napi::Env env, Napi::Value arg) {
    if (!callback_.IsEmpty()) {
      Napi::Function cb = callback_.Value();
      if (!cb.IsUndefined()) {
        cb.Call({arg});
      }
    }
  }

 private:
  Napi::Reference<Napi::Function> callback_;
};
```

**Alternative (weak callback pattern):**

```cpp
class Observer {
 public:
  static void SetCallback(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Function callback = info[0].As<Napi::Function>();

    // Store weak reference with destructor callback
    weak_callback_ = Napi::Weak(callback);
    weak_callback_.SetPointer(new CallbackData{env, callback});

    // Set weak callback to clean up when JS object is GC'd
    weak_callback_.SetPointerGCCallBack([](Napi::Env env, void* data, void*) {
      auto* cb_data = static_cast<CallbackData*>(data);
      delete cb_data;  // Clean up native resources
    });
  }

 private:
  struct CallbackData {
    Napi::Env env;
    Napi::Function callback;
  };
  static Napi::Reference<Napi::Function> weak_callback_;
};
```

**Common memory leak scenarios:**
- Storing event listeners without cleanup
- Circular references between C++ and JS objects
- Global caches holding JS references
- Timer callbacks not cleared on shutdown

Reference: [N-API Reference Handling](https://nodejs.org/api/n-api.html#references)
