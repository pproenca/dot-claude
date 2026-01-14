---
title: Always Acquire and Release ThreadSafeFunction Properly
impact: HIGH
impactDescription: Prevents resource leaks and Node.js process hangs on exit
tags: async, tsfn, acquire, release, lifecycle
---

## Always Acquire and Release ThreadSafeFunction Properly

Each thread using a `ThreadSafeFunction` must call `Acquire()` before use and `Release()` when done. Failure to release keeps the reference count positive, preventing Node.js from exiting cleanly. Always use RAII patterns or ensure release in all code paths including errors.

**Incorrect (missing Release, causing process hang):**

```cpp
class MultiThreadProcessor {
public:
    void StartWorkers(Napi::Env env, Napi::Function callback, int numThreads) {
        tsfn_ = Napi::ThreadSafeFunction::New(
            env, callback, "Processor", 0, 1);

        for (int i = 0; i < numThreads; i++) {
            // WRONG: Not acquiring for additional threads!
            workers_.emplace_back([this, i]() {
                DoWork(i);
                // WRONG: Only some threads might call this
                // If any thread throws, Release is never called
            });
        }
    }

    void DoWork(int threadId) {
        for (int j = 0; j < 10; j++) {
            tsfn_.BlockingCall([=](Napi::Env env, Napi::Function cb) {
                cb.Call({Napi::Number::New(env, threadId * 10 + j)});
            });
        }
        // BUG: If exception thrown above, Release never called!
        tsfn_.Release();
    }

private:
    Napi::ThreadSafeFunction tsfn_;
    std::vector<std::thread> workers_;
};
```

**Correct (proper Acquire/Release with RAII):**

```cpp
#include <napi.h>
#include <thread>
#include <vector>

// RAII wrapper for ThreadSafeFunction acquire/release
class TsfnGuard {
public:
    TsfnGuard(Napi::ThreadSafeFunction& tsfn) : tsfn_(tsfn), acquired_(false) {
        if (tsfn_.Acquire() == napi_ok) {
            acquired_ = true;
        }
    }

    ~TsfnGuard() {
        if (acquired_) {
            tsfn_.Release();
        }
    }

    bool IsAcquired() const { return acquired_; }

    // Prevent copying
    TsfnGuard(const TsfnGuard&) = delete;
    TsfnGuard& operator=(const TsfnGuard&) = delete;

private:
    Napi::ThreadSafeFunction& tsfn_;
    bool acquired_;
};

class MultiThreadProcessor {
public:
    void StartWorkers(Napi::Env env, Napi::Function callback, int numThreads) {
        // Initial thread count matches number of workers
        tsfn_ = Napi::ThreadSafeFunction::New(
            env, callback, "Processor", 0, numThreads);

        for (int i = 0; i < numThreads; i++) {
            workers_.emplace_back([this, i]() {
                DoWork(i);
            });
        }
    }

    void DoWork(int threadId) {
        // No need to Acquire - we set initial count to numThreads
        // But each thread MUST release when done
        try {
            for (int j = 0; j < 10; j++) {
                napi_status status = tsfn_.BlockingCall(
                    [=](Napi::Env env, Napi::Function cb) {
                        cb.Call({Napi::Number::New(env, threadId * 10 + j)});
                    });

                if (status != napi_ok) {
                    break;
                }
            }
        } catch (...) {
            // Ensure release even on exception
            tsfn_.Release();
            throw;
        }
        tsfn_.Release();
    }

    void Join() {
        for (auto& w : workers_) {
            if (w.joinable()) w.join();
        }
    }

private:
    Napi::ThreadSafeFunction tsfn_;
    std::vector<std::thread> workers_;
};

// Alternative: Use initial thread count of 1, acquire for each additional thread
void StartWithAcquire(Napi::Env env, Napi::Function callback, int numThreads) {
    auto tsfn = Napi::ThreadSafeFunction::New(
        env, callback, "Processor", 0, 1);  // Initial count = 1

    for (int i = 0; i < numThreads; i++) {
        if (i > 0) {
            // Acquire for each additional thread beyond the first
            tsfn.Acquire();
        }

        std::thread([tsfn, i]() mutable {
            // Work...
            tsfn.Release();  // Each thread releases
        }).detach();
    }
}
```

Reference: [ThreadSafeFunction Reference Counting](https://github.com/nodejs/node-addon-api/blob/main/doc/threadsafe_function.md#reference-counting)
