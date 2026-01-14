---
title: Never Call N-API Functions in AsyncWorker Execute
impact: HIGH
impactDescription: Prevents 100% of thread-safety crashes - V8 is not thread-safe, Execute() runs on worker thread
tags: async, execute, threading, napi-calls, node-addon-api
---

# Never Call N-API Functions in AsyncWorker::Execute()

The `Execute()` method runs on a libuv worker thread, not the main JavaScript thread. Calling any N-API or node-addon-api functions from this context causes undefined behavior because the V8 engine is not thread-safe. All JavaScript/N-API interaction must happen in `OnOK()` or `OnError()`.

## Why This Matters

- **Thread Safety**: V8 is single-threaded - any N-API call from a worker thread corrupts memory
- **Crash Prevention**: V8 corruption causes random SIGSEGV crashes, often in unrelated code
- **Data Integrity**: Race conditions corrupt JavaScript heap, causing subtle bugs
- **Determinism**: Behavior is undefined - works in testing, crashes in production

## Understanding the Thread Model

```
Main Thread (safe for N-API):      Worker Thread (NO N-API):
┌─────────────────────────────┐    ┌─────────────────────────────┐
│ JavaScript Event Loop       │    │ Execute() runs here         │
│ OnOK() / OnError()          │    │ Only pure C++ operations    │
│ All N-API calls             │    │ No Napi::*, no napi_*       │
└─────────────────────────────┘    └─────────────────────────────┘
```

## Incorrect: Calling N-API in Execute

```cpp
// PROBLEM: Execute() runs on worker thread - V8 is not thread-safe
// This code causes memory corruption and random crashes
class BadWorker : public Napi::AsyncWorker {
public:
    BadWorker(Napi::Function& callback, Napi::Object config)
        : Napi::AsyncWorker(callback),
          config_(Napi::Persistent(config)) {}

    void Execute() override {
        // CRASH: Accessing Napi::Object on worker thread!
        Napi::Value timeout = config_.Value().Get("timeout");

        // CRASH: Creating Napi objects on worker thread!
        Napi::String status = Napi::String::New(Env(), "processing");

        // CRASH: Calling Env() in Execute is undefined behavior!
        if (Env().IsExceptionPending()) {
            return;
        }

        DoWork();
    }

private:
    Napi::ObjectReference config_;
};
```

## Correct: Extract Values Before Execute

```cpp
// SOLUTION: Extract all needed values on main thread in constructor
// Execute() only uses plain C++ types
class GoodWorker : public Napi::AsyncWorker {
public:
    GoodWorker(Napi::Function& callback, Napi::Object config)
        : Napi::AsyncWorker(callback) {
        // Extract all needed values on the main thread BEFORE Execute()
        timeout_ms_ = config.Get("timeout").As<Napi::Number>().Int32Value();
        retries_ = config.Get("retries").As<Napi::Number>().Int32Value();
        endpoint_ = config.Get("endpoint").As<Napi::String>().Utf8Value();
    }

    void Execute() override {
        // Only use plain C++ types here - no N-API calls!
        result_ = DoHttpRequest(endpoint_, timeout_ms_, retries_);

        if (result_.empty()) {
            // SetError() is safe - it stores a std::string, not a Napi object
            SetError("Request failed after " + std::to_string(retries_) + " retries");
        }
    }

    void OnOK() override {
        // NOW it's safe to use N-API - we're back on the main thread
        Napi::Env env = Env();
        Callback().Call({
            env.Null(),
            Napi::String::New(env, result_)
        });
    }

    void OnError(const Napi::Error& e) override {
        Callback().Call({e.Value(), Env().Undefined()});
    }

private:
    // Plain C++ types only!
    int timeout_ms_;
    int retries_;
    std::string endpoint_;
    std::string result_;

    std::string DoHttpRequest(const std::string& url, int timeout, int retries) {
        // Actual HTTP logic here using libcurl or similar
        return "response data";
    }
};
```

## Alternative: Using ThreadSafeFunction for Progress Updates

```cpp
// When you need to call back to JS from Execute(), use ThreadSafeFunction
class ProgressWorker : public Napi::AsyncWorker {
public:
    ProgressWorker(Napi::Function& callback, Napi::Function& progress)
        : Napi::AsyncWorker(callback) {
        // Create TSFN for safe cross-thread callbacks
        tsfn_ = Napi::ThreadSafeFunction::New(
            callback.Env(), progress, "ProgressCallback", 0, 1);
    }

    void Execute() override {
        for (int i = 0; i < 100; i++) {
            // Safe: TSFN queues call to main thread
            tsfn_.BlockingCall([i](Napi::Env env, Napi::Function fn) {
                fn.Call({Napi::Number::New(env, i)});
            });
            DoPartialWork(i);
        }
        tsfn_.Release();
    }

private:
    Napi::ThreadSafeFunction tsfn_;
};
```

**When to use:** Use AsyncWorker for any CPU-intensive operation that would block the event loop (> 10ms). Extract all JavaScript values in the constructor.

**When NOT to use:** For simple async I/O, use libuv directly or Node.js built-in async APIs. AsyncWorker adds overhead (~50-100 microseconds) that isn't worth it for fast operations.

## References

- [Node.js N-API Threading](https://nodejs.org/api/n-api.html#asynchronous-thread-safe-function-calls)
- [node-addon-api AsyncWorker](https://github.com/nodejs/node-addon-api/blob/main/doc/async_worker.md)
- [libuv Thread Pool](https://docs.libuv.org/en/v1.x/threadpool.html)
