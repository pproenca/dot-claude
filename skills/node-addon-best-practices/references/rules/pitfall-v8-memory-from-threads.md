---
title: Don't Access V8 Memory from Threads
impact: LOW
impactDescription: Prevents crashes and data corruption from thread-safety violations
tags: pitfall, threads, v8, thread-safety, tsfn
---

# Don't Access V8 Memory from Threads

Worker threads cannot touch `napi_value` handles or any V8 heap objects. V8 is not thread-safe. Use Thread-Safe Function (TSFN) to communicate results back to the main thread.

## Why This Matters

- V8 heap objects are not thread-safe
- Accessing `napi_value` from wrong thread causes crashes
- Data corruption can occur silently
- Only the main thread can interact with JavaScript

## Incorrect

Using Napi::Value in worker threads:

```cpp
#include <napi.h>
#include <thread>
#include <string>

// BAD: Accessing V8 values from worker thread
Napi::Value ProcessInThreadBad(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Capture napi_value - THIS IS WRONG
    Napi::String input = info[0].As<Napi::String>();
    Napi::Function callback = info[1].As<Napi::Function>();

    std::thread worker([input, callback, env]() {
        // CRASH: Accessing napi_value from worker thread
        std::string str = input.Utf8Value();

        // CRASH: Calling JavaScript from worker thread
        callback.Call({Napi::String::New(env, "result")});
    });

    worker.detach();
    return env.Undefined();
}

// BAD: Storing napi_value for later use in thread
class BadWorker {
public:
    void SetCallback(Napi::Function cb) {
        callback_ = cb;  // Stored reference
    }

    void StartThread() {
        std::thread([this]() {
            // CRASH: Using stored napi_value from thread
            callback_.Call({});
        }).detach();
    }

private:
    Napi::Function callback_;  // Invalid across threads
};
```

## Correct

Copy primitives to thread, use TSFN for results:

```cpp
#include <napi.h>
#include <thread>
#include <string>

// GOOD: Copy data to thread, use TSFN for results
class ThreadSafeWorker {
public:
    static Napi::Value Create(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        // Copy data to C++ types BEFORE starting thread
        std::string inputData = info[0].As<Napi::String>().Utf8Value();
        Napi::Function callback = info[1].As<Napi::Function>();

        // Create Thread-Safe Function
        auto tsfn = Napi::ThreadSafeFunction::New(
            env,
            callback,
            "WorkerCallback",
            0,  // Max queue size (0 = unlimited)
            1   // Initial thread count
        );

        // Start worker thread with copied data
        std::thread worker([inputData, tsfn]() mutable {
            // Process data (all C++ types, no V8 access)
            std::string result = ProcessData(inputData);

            // Use TSFN to call back to main thread
            auto callback = [result](Napi::Env env,
                                      Napi::Function jsCallback) {
                // This runs on main thread - safe to use V8
                jsCallback.Call({Napi::String::New(env, result)});
            };

            tsfn.BlockingCall(callback);
            tsfn.Release();
        });

        worker.detach();
        return env.Undefined();
    }

private:
    static std::string ProcessData(const std::string& input) {
        // Heavy processing here (thread-safe, no V8)
        std::string result = input;
        for (char& c : result) {
            c = std::toupper(static_cast<unsigned char>(c));
        }
        return result;
    }
};

// GOOD: AsyncWorker handles thread safety automatically
class SafeAsyncWorker : public Napi::AsyncWorker {
public:
    SafeAsyncWorker(const Napi::Env& env,
                    const std::string& input,
                    Napi::Promise::Deferred deferred)
        : Napi::AsyncWorker(env),
          input_(input),  // Copy to member
          deferred_(deferred) {}

    void Execute() override {
        // Worker thread - only use C++ data
        // DO NOT access Env() or any Napi types here

        result_ = "";
        for (char c : input_) {
            result_ += std::toupper(static_cast<unsigned char>(c));
        }
    }

    void OnOK() override {
        // Main thread - safe to use Napi types
        deferred_.Resolve(Napi::String::New(Env(), result_));
    }

    void OnError(const Napi::Error& err) override {
        deferred_.Reject(err.Value());
    }

private:
    std::string input_;   // C++ data for thread
    std::string result_;  // C++ result from thread
    Napi::Promise::Deferred deferred_;
};

Napi::Value ProcessAsync(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Copy data from V8 to C++
    std::string input = info[0].As<Napi::String>().Utf8Value();

    auto deferred = Napi::Promise::Deferred::New(env);
    auto* worker = new SafeAsyncWorker(env, input, deferred);
    worker->Queue();

    return deferred.Promise();
}
```

## Progress Reporting with TSFN

```cpp
#include <napi.h>
#include <thread>
#include <atomic>

class ProgressWorker {
public:
    static Napi::Value Start(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        uint64_t total = info[0].As<Napi::Number>().Int64Value();
        Napi::Function progressCb = info[1].As<Napi::Function>();
        Napi::Function completeCb = info[2].As<Napi::Function>();

        // Create TSFN for progress updates
        auto progressTsfn = Napi::ThreadSafeFunction::New(
            env, progressCb, "Progress", 0, 1
        );

        // Create TSFN for completion
        auto completeTsfn = Napi::ThreadSafeFunction::New(
            env, completeCb, "Complete", 0, 1
        );

        std::thread([total, progressTsfn, completeTsfn]() mutable {
            uint64_t result = 0;
            const uint64_t REPORT_INTERVAL = 1000000;

            for (uint64_t i = 0; i < total; i++) {
                result += i;

                // Report progress periodically
                if (i % REPORT_INTERVAL == 0) {
                    double progress = static_cast<double>(i) / total;

                    progressTsfn.BlockingCall(
                        [progress](Napi::Env env, Napi::Function cb) {
                            cb.Call({Napi::Number::New(env, progress)});
                        }
                    );
                }
            }

            // Report completion
            double finalResult = static_cast<double>(result);
            completeTsfn.BlockingCall(
                [finalResult](Napi::Env env, Napi::Function cb) {
                    cb.Call({Napi::Number::New(env, finalResult)});
                }
            );

            progressTsfn.Release();
            completeTsfn.Release();
        }).detach();

        return env.Undefined();
    }
};
```

## JavaScript Usage

```javascript
const addon = require('./build/Release/addon');

// Callback-based
addon.processInThread('hello', (result) => {
    console.log('Result:', result);
});

// Promise-based
const result = await addon.processAsync('hello');

// With progress
addon.startWithProgress(
    1000000000,
    (progress) => console.log(`Progress: ${(progress * 100).toFixed(1)}%`),
    (result) => console.log('Complete:', result)
);
```

## Thread Safety Checklist

| Safe in Worker Thread | Not Safe in Worker Thread |
|-----------------------|---------------------------|
| C++ primitives | `napi_value` |
| `std::string` | `Napi::String` |
| `std::vector` | `Napi::Array` |
| Raw pointers to non-V8 data | `Napi::Object` |
| Mutexes, atomics | `Napi::Function` |
| TSFN calls | Direct V8 calls |
