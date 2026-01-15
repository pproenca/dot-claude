---
title: Use ThreadSafeFunction for Callbacks from Threads
impact: CRITICAL
impactDescription: enables safe JS callbacks from any thread
tags: async, thread-safe, tsfn, callbacks
---

## Use ThreadSafeFunction for Callbacks from Threads

Calling JavaScript from non-main threads crashes Node.js. Use `Napi::ThreadSafeFunction` to safely invoke JS callbacks from any thread.

**Incorrect (crashes):**

```cpp
void BackgroundThread(Napi::Function callback, Napi::Env env) {
  std::thread([callback, env]() {
    // CRASH! Calling JS from non-main thread
    callback.Call({Napi::String::New(env, "result")});
  }).detach();
}
```

**Correct (thread-safe function):**

```cpp
class EventEmitter {
 public:
  static Napi::Value Start(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Function callback = info[0].As<Napi::Function>();

    // Create thread-safe function
    tsfn_ = Napi::ThreadSafeFunction::New(
      env,
      callback,
      "EventEmitter",  // Resource name for debugging
      0,               // Max queue size (0 = unlimited)
      1                // Initial thread count
    );

    // Start background thread
    worker_ = std::thread([]() {
      while (running_) {
        // Generate event data
        std::string data = GenerateEvent();

        // Queue call to JS - safe from any thread!
        tsfn_.BlockingCall([data](Napi::Env env, Napi::Function callback) {
          callback.Call({Napi::String::New(env, data)});
        });

        std::this_thread::sleep_for(std::chrono::milliseconds(100));
      }
    });

    return env.Undefined();
  }

  static Napi::Value Stop(const Napi::CallbackInfo& info) {
    running_ = false;
    if (worker_.joinable()) {
      worker_.join();
    }
    tsfn_.Release();
    return info.Env().Undefined();
  }

 private:
  static Napi::ThreadSafeFunction tsfn_;
  static std::thread worker_;
  static std::atomic<bool> running_;
};
```

**With custom data transfer:**

```cpp
struct EventData {
  std::string message;
  int code;
};

void CallJS(Napi::Env env, Napi::Function callback, EventData* data) {
  if (env != nullptr && callback != nullptr) {
    Napi::Object result = Napi::Object::New(env);
    result.Set("message", Napi::String::New(env, data->message));
    result.Set("code", Napi::Number::New(env, data->code));
    callback.Call({result});
  }
  delete data;  // Clean up after use
}

using TSFN = Napi::TypedThreadSafeFunction<void, EventData, CallJS>;

class TypedEmitter {
 public:
  static Napi::Value Start(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    tsfn_ = TSFN::New(
      env,
      info[0].As<Napi::Function>(),
      "TypedEmitter",
      0,
      1
    );

    worker_ = std::thread([]() {
      while (running_) {
        // Create data on heap - will be freed after callback
        EventData* data = new EventData{"event occurred", 42};
        tsfn_.BlockingCall(data);
      }
    });

    return env.Undefined();
  }

 private:
  static TSFN tsfn_;
  static std::thread worker_;
  static std::atomic<bool> running_;
};
```

**Non-blocking variant:**

```cpp
// Use NonBlockingCall when you can't afford to wait
napi_status status = tsfn_.NonBlockingCall(data);
if (status == napi_queue_full) {
  // Queue is full - handle backpressure
  delete data;  // Don't leak
  HandleBackpressure();
}
```

Reference: [ThreadSafeFunction Documentation](https://nodejs.org/api/n-api.html#thread-safe-functions)
