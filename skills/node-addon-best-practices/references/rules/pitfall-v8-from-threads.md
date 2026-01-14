---
title: Don't Access V8 Memory from Worker Threads
impact: LOW
impactDescription: Prevents crashes, data corruption, and undefined behavior
tags: pitfall, threads, v8, memory-safety, async
---

# Don't Access V8 Memory from Worker Threads

Never access JavaScript objects, N-API handles, or V8 heap memory from worker threads. V8 is single-threaded and has no internal synchronization. Use ThreadSafeFunction or copy data before spawning threads.

## Why This Matters

- V8 assumes single-threaded access to all objects
- Concurrent access causes data races and crashes
- No error messages - just random corruption or segfaults
- Hard to debug; may work sometimes and fail randomly

## Incorrect

Accessing JavaScript objects from worker thread:

```cpp
#include <napi.h>
#include <thread>
#include <vector>

// BAD: Accessing Napi::Array from worker thread
class BadAsyncWorker : public Napi::AsyncWorker {
public:
    BadAsyncWorker(Napi::Env env, Napi::Array data,
                   Napi::Promise::Deferred deferred)
        : Napi::AsyncWorker(env),
          data_(data),  // WRONG: Storing N-API handle
          deferred_(deferred) {}

    void Execute() override {
        // DANGER: Accessing data_ from worker thread
        // This accesses V8 heap from non-main thread!
        uint32_t length = data_.Length();  // CRASH or corruption

        for (uint32_t i = 0; i < length; i++) {
            // Each Get() touches V8 memory - UNDEFINED BEHAVIOR
            double val = data_.Get(i).As<Napi::Number>().DoubleValue();
            result_ += val;
        }
    }

    void OnOK() override {
        deferred_.Resolve(Napi::Number::New(Env(), result_));
    }

private:
    Napi::Array data_;  // N-API handle - NOT thread-safe
    Napi::Promise::Deferred deferred_;
    double result_ = 0.0;
};

// BAD: Creating JS objects in worker thread
class BadObjectCreator : public Napi::AsyncWorker {
public:
    BadObjectCreator(Napi::Env env, Napi::Function callback)
        : Napi::AsyncWorker(callback) {}

    void Execute() override {
        // DANGER: Cannot create JS objects here
        // Env() is not valid in worker thread
        result_ = Napi::Object::New(Env());  // CRASH
    }

    void OnOK() override {
        Callback().Call({result_});
    }

private:
    Napi::Object result_;
};

// BAD: Using std::thread without proper data copying
Napi::Value BadThreadUsage(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array arr = info[0].As<Napi::Array>();

    // DANGER: Lambda captures N-API handle
    std::thread worker([arr]() {
        // Accessing arr from another thread - UNDEFINED BEHAVIOR
        uint32_t len = arr.Length();
    });
    worker.detach();

    return env.Undefined();
}
```

## Correct

Copy data to thread-safe containers before processing:

```cpp
#include <napi.h>
#include <vector>
#include <string>

// GOOD: Copy data before worker thread
class SafeAsyncWorker : public Napi::AsyncWorker {
public:
    SafeAsyncWorker(Napi::Env env, std::vector<double> data,
                    Napi::Promise::Deferred deferred)
        : Napi::AsyncWorker(env),
          data_(std::move(data)),  // Thread-safe copy
          deferred_(deferred) {}

    void Execute() override {
        // Safe: data_ is a std::vector, not a V8 object
        for (const double& val : data_) {
            result_ += val;
        }
    }

    void OnOK() override {
        // OnOK runs on main thread - safe to use Napi
        deferred_.Resolve(Napi::Number::New(Env(), result_));
    }

    void OnError(const Napi::Error& error) override {
        deferred_.Reject(error.Value());
    }

private:
    std::vector<double> data_;  // Thread-safe type
    Napi::Promise::Deferred deferred_;
    double result_ = 0.0;
};

Napi::Value ProcessAsync(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Float64Array input = info[0].As<Napi::Float64Array>();

    // Copy data on main thread before creating worker
    std::vector<double> data(input.Data(),
                             input.Data() + input.ElementLength());

    auto deferred = Napi::Promise::Deferred::New(env);
    auto* worker = new SafeAsyncWorker(env, std::move(data), deferred);
    worker->Queue();

    return deferred.Promise();
}
```

## Using ThreadSafeFunction for Callbacks

```cpp
#include <napi.h>
#include <thread>
#include <atomic>

// GOOD: Use ThreadSafeFunction for thread-safe callbacks
class ThreadedProcessor {
public:
    static Napi::Value Start(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        Napi::Float64Array input = info[0].As<Napi::Float64Array>();
        Napi::Function callback = info[1].As<Napi::Function>();

        // Copy data for thread safety
        auto data = std::make_shared<std::vector<double>>(
            input.Data(), input.Data() + input.ElementLength()
        );

        // Create thread-safe function
        auto tsfn = Napi::ThreadSafeFunction::New(
            env,
            callback,
            "ProcessorCallback",
            0,  // Unlimited queue
            1   // 1 thread using it
        );

        // Start worker thread
        std::thread worker([data, tsfn = std::move(tsfn)]() mutable {
            double result = 0.0;

            for (const double& val : *data) {
                result += val;
            }

            // Call JavaScript from worker thread safely
            auto callback = [result](Napi::Env env, Napi::Function jsCallback) {
                jsCallback.Call({Napi::Number::New(env, result)});
            };

            tsfn.BlockingCall(callback);
            tsfn.Release();
        });

        worker.detach();

        return env.Undefined();
    }
};
```

## Thread-Safe String Handling

```cpp
#include <napi.h>
#include <string>
#include <thread>

// GOOD: Copy strings to std::string before worker
class StringProcessor : public Napi::AsyncWorker {
public:
    StringProcessor(Napi::Env env,
                    std::string input,
                    Napi::Promise::Deferred deferred)
        : Napi::AsyncWorker(env),
          input_(std::move(input)),
          deferred_(deferred) {}

    void Execute() override {
        // Safe: working with std::string, not Napi::String
        result_.reserve(input_.size());

        for (char c : input_) {
            result_.push_back(std::toupper(static_cast<unsigned char>(c)));
        }
    }

    void OnOK() override {
        // Convert back to JS string on main thread
        deferred_.Resolve(Napi::String::New(Env(), result_));
    }

private:
    std::string input_;
    std::string result_;
    Napi::Promise::Deferred deferred_;
};

Napi::Value ToUpperAsync(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Copy string data on main thread
    std::string input = info[0].As<Napi::String>().Utf8Value();

    auto deferred = Napi::Promise::Deferred::New(env);
    auto* worker = new StringProcessor(env, std::move(input), deferred);
    worker->Queue();

    return deferred.Promise();
}
```

## Thread-Safe Buffer Access

```cpp
#include <napi.h>
#include <vector>

// GOOD: Copy buffer data before async processing
class BufferProcessor : public Napi::AsyncWorker {
public:
    BufferProcessor(Napi::Env env,
                    std::vector<uint8_t> data,
                    Napi::Promise::Deferred deferred)
        : Napi::AsyncWorker(env),
          data_(std::move(data)),
          deferred_(deferred) {}

    void Execute() override {
        // Process buffer copy
        for (uint8_t& byte : data_) {
            byte ^= 0xFF;  // Example: invert bytes
        }
    }

    void OnOK() override {
        // Create new buffer from result on main thread
        Napi::Buffer<uint8_t> result = Napi::Buffer<uint8_t>::Copy(
            Env(), data_.data(), data_.size()
        );
        deferred_.Resolve(result);
    }

private:
    std::vector<uint8_t> data_;
    Napi::Promise::Deferred deferred_;
};

Napi::Value InvertBufferAsync(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();

    // Copy buffer data before async work
    std::vector<uint8_t> data(buffer.Data(),
                              buffer.Data() + buffer.Length());

    auto deferred = Napi::Promise::Deferred::New(env);
    auto* worker = new BufferProcessor(env, std::move(data), deferred);
    worker->Queue();

    return deferred.Promise();
}
```

## Thread Safety Reference

| Operation | Main Thread | Worker Thread |
|-----------|-------------|---------------|
| Read Napi:: types | Safe | UNSAFE |
| Create Napi:: objects | Safe | UNSAFE |
| Call JavaScript | Safe | Use TSFN |
| Access std:: containers | Safe | Safe (if copied) |
| Use Napi::Env | Safe | UNSAFE |
| Throw exceptions | Safe | SetError() |

Reference: [N-API Thread Safety](https://nodejs.org/api/n-api.html#n_api_asynchronous_thread_safe_function_calls)
