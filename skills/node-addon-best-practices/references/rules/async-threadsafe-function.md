---
title: Use ThreadSafeFunction for Callbacks from Worker Threads
impact: HIGH
impactDescription: Enables safe cross-thread JavaScript callbacks without crashes
tags: async, tsfn, callback, threading
---

## Use ThreadSafeFunction for Callbacks from Worker Threads

When a background thread needs to call back into JavaScript (for streaming results, events, or progress), use `Napi::ThreadSafeFunction`. This queues calls to be executed on the main thread, ensuring thread safety with V8.

**Incorrect (calling JavaScript directly from worker thread):**

```cpp
#include <napi.h>
#include <thread>

class StreamProcessor {
public:
    // DANGEROUS: Storing raw callback reference
    StreamProcessor(Napi::Function callback)
        : callback_(Napi::Persistent(callback)) {}

    void Start() {
        worker_ = std::thread([this]() {
            for (int i = 0; i < 100; i++) {
                // CRASH: Calling JS function from non-main thread!
                callback_.Value().Call({Napi::Number::New(callback_.Env(), i)});
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
            }
        });
    }

private:
    Napi::FunctionReference callback_;
    std::thread worker_;
};
```

**Correct (using ThreadSafeFunction):**

```cpp
#include <napi.h>
#include <thread>
#include <atomic>

class StreamProcessor {
public:
    StreamProcessor(const Napi::Env& env, Napi::Function callback)
        : running_(true) {
        // Create ThreadSafeFunction that queues calls to the main thread
        tsfn_ = Napi::ThreadSafeFunction::New(
            env,
            callback,                    // JavaScript function to call
            "StreamProcessor",           // Resource name for diagnostics
            0,                           // Max queue size (0 = unlimited)
            1,                           // Initial thread count
            this,                        // Context passed to invoke
            [](Napi::Env, void*, StreamProcessor* ctx) {
                // Invoke this callback when released
            }
        );
    }

    void Start() {
        worker_ = std::thread([this]() {
            for (int i = 0; i < 100 && running_; i++) {
                // Safe: Queues call to main thread
                napi_status status = tsfn_.BlockingCall([i](Napi::Env env, Napi::Function callback) {
                    callback.Call({Napi::Number::New(env, i)});
                });

                if (status != napi_ok) {
                    break; // TSFN was released or closing
                }

                std::this_thread::sleep_for(std::chrono::milliseconds(100));
            }

            // Signal we're done using the function
            tsfn_.Release();
        });
    }

    void Stop() {
        running_ = false;
        if (worker_.joinable()) {
            worker_.join();
        }
    }

    ~StreamProcessor() {
        Stop();
    }

private:
    Napi::ThreadSafeFunction tsfn_;
    std::thread worker_;
    std::atomic<bool> running_;
};

Napi::Value CreateProcessor(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Function callback = info[0].As<Napi::Function>();

    auto* processor = new StreamProcessor(env, callback);
    processor->Start();

    // Return handle to control the processor
    Napi::Object handle = Napi::Object::New(env);
    handle.Set("stop", Napi::Function::New(env, [processor](const Napi::CallbackInfo&) {
        processor->Stop();
        delete processor;
        return Napi::Value();
    }));

    return handle;
}
```

Reference: [ThreadSafeFunction Documentation](https://github.com/nodejs/node-addon-api/blob/main/doc/threadsafe_function.md)
