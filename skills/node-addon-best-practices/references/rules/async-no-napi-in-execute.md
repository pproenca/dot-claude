---
title: Never Call N-API Functions in AsyncWorker Execute
impact: HIGH
impactDescription: Prevents undefined behavior and crashes from thread-safety violations
tags: async, execute, threading, napi-calls
---

## Never Call N-API Functions in AsyncWorker::Execute()

The `Execute()` method runs on a libuv worker thread, not the main JavaScript thread. Calling any N-API or node-addon-api functions from this context causes undefined behavior because the V8 engine is not thread-safe. All JavaScript/N-API interaction must happen in `OnOK()` or `OnError()`.

**Incorrect (calling N-API in Execute):**

```cpp
class BadWorker : public Napi::AsyncWorker {
public:
    BadWorker(Napi::Function& callback, Napi::Object config)
        : Napi::AsyncWorker(callback),
          config_(Napi::Persistent(config)) {}

    void Execute() override {
        // WRONG: Accessing Napi::Object on worker thread!
        Napi::Value timeout = config_.Value().Get("timeout");

        // WRONG: Creating Napi objects on worker thread!
        Napi::String status = Napi::String::New(Env(), "processing");

        // WRONG: Calling Env() and using it in Execute!
        if (Env().IsExceptionPending()) {
            return;
        }

        DoWork();
    }

private:
    Napi::ObjectReference config_;
};
```

**Correct (extract values before Execute, use only in OnOK/OnError):**

```cpp
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
        // Actual HTTP logic here
        return "response data";
    }
};
```

Reference: [Node.js N-API Threading](https://nodejs.org/api/n-api.html#asynchronous-thread-safe-function-calls)
