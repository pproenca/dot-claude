---
title: Use ThreadSafeFunction for Callbacks from Worker Threads
impact: HIGH
impactDescription: Enables safe cross-thread JS callbacks - direct calls cause 100% crash rate, TSFN provides 100% safety
tags: async, tsfn, callback, threading, node-addon-api
---

# Use ThreadSafeFunction for Callbacks from Worker Threads

When a background thread needs to call back into JavaScript (for streaming results, events, or progress), use `Napi::ThreadSafeFunction`. This queues calls to be executed on the main thread, ensuring thread safety with V8. Direct JavaScript calls from worker threads cause immediate memory corruption.

## Why This Matters

- **Thread Safety**: TSFN queues calls to the main thread automatically
- **Streaming Data**: Enables sending results back as they become available
- **Event Callbacks**: Essential for native event emitters
- **Progress Updates**: Report progress from long-running operations

## Understanding ThreadSafeFunction

```
Worker Thread                      Main Thread
┌─────────────────┐               ┌─────────────────┐
│ Process data    │               │ Event Loop      │
│       │         │               │       │         │
│       ▼         │               │       │         │
│ tsfn_.Call()────┼──queue───────►│  Check queue    │
│       │         │               │       │         │
│       ▼         │               │       ▼         │
│ Continue work   │               │ Execute callback│
└─────────────────┘               └─────────────────┘
```

## Incorrect: Direct JavaScript Call from Worker Thread

```cpp
// PROBLEM: Calling JS function from non-main thread corrupts V8 heap
// Results in random SIGSEGV crashes - often in unrelated code
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
                // V8 is single-threaded - this corrupts memory
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

## Correct: Using ThreadSafeFunction

```cpp
// SOLUTION: ThreadSafeFunction queues calls to main thread safely
// All JavaScript interaction happens on the event loop
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
                // Invoke finalizer callback when TSFN is released
            }
        );
    }

    void Start() {
        worker_ = std::thread([this]() {
            for (int i = 0; i < 100 && running_; i++) {
                // Safe: Queues call to main thread
                napi_status status = tsfn_.BlockingCall(
                    [i](Napi::Env env, Napi::Function callback) {
                        callback.Call({Napi::Number::New(env, i)});
                    }
                );

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
```

## Alternative: Using NonBlockingCall for High-Throughput

```cpp
// When you can't afford to wait for queue space
void ProcessHighFrequencyEvents() {
    worker_ = std::thread([this]() {
        while (running_) {
            EventData data = GetNextEvent();

            // NonBlockingCall returns immediately if queue is full
            napi_status status = tsfn_.NonBlockingCall(
                [data](Napi::Env env, Napi::Function callback) {
                    Napi::Object event = Napi::Object::New(env);
                    event.Set("type", data.type);
                    event.Set("value", data.value);
                    callback.Call({event});
                }
            );

            if (status == napi_queue_full) {
                // Handle backpressure - drop event or slow down
                dropped_events_++;
            } else if (status == napi_closing) {
                break;
            }
        }
    });
}
```

## Pattern: Multiple Callbacks with Context

```cpp
// Pass custom data to the callback
using ContextType = std::pair<int, std::string>;

auto tsfn = Napi::ThreadSafeFunction::New(
    env, callback, "MultiCallback", 0, 1,
    static_cast<void*>(nullptr),  // No destructor context
    [](Napi::Env, void*, void*) {},  // Destructor
    static_cast<void*>(nullptr)   // No invoke context
);

// Worker thread
worker_ = std::thread([tsfn = std::move(tsfn)]() {
    auto* ctx = new ContextType(42, "data");

    tsfn.BlockingCall(ctx, [](Napi::Env env, Napi::Function fn, ContextType* ctx) {
        fn.Call({
            Napi::Number::New(env, ctx->first),
            Napi::String::New(env, ctx->second)
        });
        delete ctx;  // Clean up context
    });
});
```

**When to use:** Use ThreadSafeFunction whenever you need to call JavaScript from any thread other than the main thread - worker threads, signal handlers, or native callbacks.

**When NOT to use:** For simple request/response patterns, AsyncWorker is simpler. TSFN has ~5-10 microseconds overhead per call due to queue synchronization.

## References

- [ThreadSafeFunction Documentation](https://github.com/nodejs/node-addon-api/blob/main/doc/threadsafe_function.md)
- [N-API Thread-safe Functions](https://nodejs.org/api/n-api.html#asynchronous-thread-safe-function-calls)
