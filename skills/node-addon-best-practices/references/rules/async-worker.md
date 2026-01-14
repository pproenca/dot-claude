---
title: Use AsyncWorker for Background Tasks
impact: HIGH
impactDescription: Blocking main thread freezes event loop and destroys Node.js responsiveness
tags: async, worker, threading, performance
---

# Use AsyncWorker for Background Tasks

Offload CPU-intensive operations to `Napi::AsyncWorker` to keep the JavaScript event loop responsive. Blocking the main thread freezes all JavaScript execution, timers, and I/O.

## Why This Matters

- **Event Loop Health**: JavaScript remains responsive during native work
- **Scalability**: Multiple async operations can proceed in parallel
- **User Experience**: UI/API doesn't hang during heavy computation
- **Server Throughput**: HTTP requests don't timeout waiting for native code

## Understanding AsyncWorker

AsyncWorker runs your code on a libuv thread pool worker thread, separate from the main JavaScript thread. When complete, it schedules callbacks back on the main thread.

```
Main Thread              Worker Thread
    │                        │
    ├─> Create AsyncWorker   │
    │                        │
    ├─> worker.Queue()       │
    │         │              │
    │         └──────────────┼─> Execute() runs here
    │                        │   (can't call N-API)
    │   (JS continues)       │
    │         .              │
    │         .              │
    │         ◄──────────────┼── Execute() completes
    │                        │
    ├─> OnOK()/OnError()     │
    │   (back on main)       │
    │                        │
```

## Incorrect: Blocking Main Thread

```cpp
// BAD: Heavy computation blocks the entire event loop
Napi::Value CalculatePrimes(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    int limit = info[0].As<Napi::Number>().Int32Value();

    // This runs on the main thread - BLOCKS EVERYTHING
    std::vector<int> primes;
    for (int i = 2; i < limit; i++) {
        bool isPrime = true;
        for (int j = 2; j * j <= i; j++) {
            if (i % j == 0) {
                isPrime = false;
                break;
            }
        }
        if (isPrime) primes.push_back(i);
    }
    // While this runs, no other JS can execute
    // HTTP servers won't respond, timers won't fire

    Napi::Array result = Napi::Array::New(env, primes.size());
    for (size_t i = 0; i < primes.size(); i++) {
        result.Set(i, Napi::Number::New(env, primes[i]));
    }
    return result;
}
```

```javascript
// JavaScript is frozen during this call
console.log('Start');
const primes = addon.calculatePrimes(10000000);  // Blocks for seconds
console.log('Done');  // Nothing else runs until this finishes

// All timers, network callbacks, etc. are frozen!
```

## Correct: AsyncWorker for Heavy Computation

```cpp
// GOOD: Use AsyncWorker to run computation in background
#include <napi.h>
#include <vector>

class PrimeWorker : public Napi::AsyncWorker {
public:
    PrimeWorker(Napi::Function& callback, int limit)
        : Napi::AsyncWorker(callback), limit_(limit) {}

    // Runs on worker thread - NO N-API calls allowed here!
    void Execute() override {
        // Heavy computation runs in background
        for (int i = 2; i < limit_; i++) {
            bool isPrime = true;
            for (int j = 2; j * j <= i; j++) {
                if (i % j == 0) {
                    isPrime = false;
                    break;
                }
            }
            if (isPrime) primes_.push_back(i);
        }
        // Main thread continues running JS while this executes
    }

    // Runs on main thread after Execute() completes
    void OnOK() override {
        Napi::Env env = Env();
        Napi::HandleScope scope(env);

        // Now safe to create JS values
        Napi::Array result = Napi::Array::New(env, primes_.size());
        for (size_t i = 0; i < primes_.size(); i++) {
            result.Set(i, Napi::Number::New(env, primes_[i]));
        }

        // Call the JavaScript callback with result
        Callback().Call({env.Null(), result});
    }

    void OnError(const Napi::Error& error) override {
        Callback().Call({error.Value(), Env().Undefined()});
    }

private:
    int limit_;
    std::vector<int> primes_;  // Store results until OnOK
};

Napi::Value CalculatePrimesAsync(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    int limit = info[0].As<Napi::Number>().Int32Value();
    Napi::Function callback = info[1].As<Napi::Function>();

    // Create and queue the worker
    PrimeWorker* worker = new PrimeWorker(callback, limit);
    worker->Queue();

    // Returns immediately - JS continues executing
    return env.Undefined();
}
```

```javascript
// JavaScript remains responsive
console.log('Start');
addon.calculatePrimesAsync(10000000, (err, primes) => {
    if (err) throw err;
    console.log('Found', primes.length, 'primes');
});
console.log('Queued');  // Runs immediately

// Other code, timers, HTTP handlers all continue working
setTimeout(() => console.log('Timer fired'), 100);  // Works!
```

## Correct: AsyncWorker with Promise

```cpp
// GOOD: Promise-based async worker
class PrimeWorkerPromise : public Napi::AsyncWorker {
public:
    PrimeWorkerPromise(Napi::Env env, int limit)
        : Napi::AsyncWorker(env),
          limit_(limit),
          deferred_(Napi::Promise::Deferred::New(env)) {}

    Napi::Promise GetPromise() { return deferred_.Promise(); }

    void Execute() override {
        for (int i = 2; i < limit_; i++) {
            bool isPrime = true;
            for (int j = 2; j * j <= i; j++) {
                if (i % j == 0) { isPrime = false; break; }
            }
            if (isPrime) primes_.push_back(i);
        }
    }

    void OnOK() override {
        Napi::Env env = Env();
        Napi::Array result = Napi::Array::New(env, primes_.size());
        for (size_t i = 0; i < primes_.size(); i++) {
            result.Set(i, Napi::Number::New(env, primes_[i]));
        }
        deferred_.Resolve(result);
    }

    void OnError(const Napi::Error& error) override {
        deferred_.Reject(error.Value());
    }

private:
    int limit_;
    std::vector<int> primes_;
    Napi::Promise::Deferred deferred_;
};

Napi::Value CalculatePrimesPromise(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    int limit = info[0].As<Napi::Number>().Int32Value();

    auto* worker = new PrimeWorkerPromise(env, limit);
    Napi::Promise promise = worker->GetPromise();
    worker->Queue();

    return promise;
}
```

```javascript
// Clean async/await usage
async function main() {
    console.log('Start');
    const primes = await addon.calculatePrimesPromise(10000000);
    console.log('Found', primes.length, 'primes');
}
```

## Pattern: Cancellable Worker

```cpp
// GOOD: Worker that can be cancelled
class CancellableWorker : public Napi::AsyncWorker {
public:
    CancellableWorker(Napi::Env env, int limit)
        : Napi::AsyncWorker(env),
          limit_(limit),
          cancelled_(false),
          deferred_(Napi::Promise::Deferred::New(env)) {}

    void Cancel() { cancelled_ = true; }
    Napi::Promise GetPromise() { return deferred_.Promise(); }

    void Execute() override {
        for (int i = 2; i < limit_ && !cancelled_; i++) {
            // Check cancellation periodically
            bool isPrime = true;
            for (int j = 2; j * j <= i && !cancelled_; j++) {
                if (i % j == 0) { isPrime = false; break; }
            }
            if (isPrime && !cancelled_) primes_.push_back(i);
        }

        if (cancelled_) {
            SetError("Operation cancelled");
        }
    }

    void OnOK() override {
        Napi::Env env = Env();
        Napi::Array result = Napi::Array::New(env, primes_.size());
        for (size_t i = 0; i < primes_.size(); i++) {
            result.Set(i, Napi::Number::New(env, primes_[i]));
        }
        deferred_.Resolve(result);
    }

    void OnError(const Napi::Error& error) override {
        deferred_.Reject(error.Value());
    }

private:
    int limit_;
    std::atomic<bool> cancelled_;
    std::vector<int> primes_;
    Napi::Promise::Deferred deferred_;
};
```

## Pattern: Worker with Input Data Copy

```cpp
// GOOD: Copy input data for thread safety
class DataProcessorWorker : public Napi::AsyncWorker {
public:
    DataProcessorWorker(Napi::Function& callback, Napi::Buffer<uint8_t>& input)
        : Napi::AsyncWorker(callback) {
        // CRITICAL: Copy input data - can't access JS values in Execute()
        inputData_.assign(input.Data(), input.Data() + input.Length());
    }

    void Execute() override {
        // Process the copied data
        outputData_.resize(inputData_.size());
        for (size_t i = 0; i < inputData_.size(); i++) {
            outputData_[i] = ProcessByte(inputData_[i]);
        }
    }

    void OnOK() override {
        Napi::Env env = Env();
        Callback().Call({
            env.Null(),
            Napi::Buffer<uint8_t>::Copy(env, outputData_.data(), outputData_.size())
        });
    }

private:
    std::vector<uint8_t> inputData_;   // Copied input
    std::vector<uint8_t> outputData_;  // Computed output
};
```

## Batch Multiple Operations

```cpp
// GOOD: Process batch in single worker to reduce overhead
class BatchWorker : public Napi::AsyncWorker {
public:
    BatchWorker(Napi::Env env, std::vector<std::string>&& items)
        : Napi::AsyncWorker(env),
          items_(std::move(items)),
          deferred_(Napi::Promise::Deferred::New(env)) {}

    Napi::Promise GetPromise() { return deferred_.Promise(); }

    void Execute() override {
        results_.reserve(items_.size());
        for (const auto& item : items_) {
            results_.push_back(ProcessItem(item));
        }
    }

    void OnOK() override {
        Napi::Env env = Env();
        Napi::Array result = Napi::Array::New(env, results_.size());
        for (size_t i = 0; i < results_.size(); i++) {
            result.Set(i, Napi::String::New(env, results_[i]));
        }
        deferred_.Resolve(result);
    }

private:
    std::vector<std::string> items_;
    std::vector<std::string> results_;
    Napi::Promise::Deferred deferred_;
};
```

## References

- [node-addon-api AsyncWorker](https://github.com/nodejs/node-addon-api/blob/main/doc/async_worker.md)
- [libuv Thread Pool](http://docs.libuv.org/en/v1.x/threadpool.html)
- [N-API Async Operations](https://nodejs.org/api/n-api.html#asynchronous-operations)
