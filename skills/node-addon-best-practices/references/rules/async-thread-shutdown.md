---
title: Implement Proper Thread Shutdown with Finalizers
impact: HIGH
impactDescription: Ensures clean process exit and prevents resource leaks on shutdown
tags: async, shutdown, finalizer, cleanup, lifecycle
---

## Implement Proper Thread Shutdown with Finalizers

Background threads must be properly terminated when Node.js shuts down or when the addon is cleaned up. Use `ThreadSafeFunction` finalizers and the `Abort()` method to signal threads to exit, then join them before the finalizer completes.

**Incorrect (orphaned threads and no cleanup):**

```cpp
class BackgroundService {
public:
    BackgroundService(Napi::Env env, Napi::Function callback) {
        tsfn_ = Napi::ThreadSafeFunction::New(env, callback, "service", 0, 1);

        // Thread starts but no shutdown mechanism!
        worker_ = std::thread([this]() {
            while (true) {  // Infinite loop with no exit condition!
                DoWork();
                tsfn_.BlockingCall([](Napi::Env env, Napi::Function cb) {
                    cb.Call({});
                });
            }
        });

        // Thread is detached - can't join or control it!
        worker_.detach();
    }

    // No destructor - threads will crash when Node.js exits!

private:
    Napi::ThreadSafeFunction tsfn_;
    std::thread worker_;
};
```

**Correct (proper shutdown with finalizer):**

```cpp
#include <napi.h>
#include <thread>
#include <atomic>
#include <condition_variable>
#include <mutex>

class BackgroundService {
public:
    BackgroundService(Napi::Env env, Napi::Function callback)
        : running_(true), workerJoined_(false) {
        // Use the destructor callback to clean up threads
        tsfn_ = Napi::ThreadSafeFunction::New(
            env,
            callback,
            "BackgroundService",
            0,  // Unlimited queue
            1,  // Initial thread count
            this,  // Context for invoke
            // Invoke this destructor when reference count reaches 0
            [](Napi::Env env, void* invoke, BackgroundService* self) {
                self->Shutdown();
            },
            static_cast<void*>(nullptr)  // invoke callback (unused)
        );

        worker_ = std::thread([this]() {
            WorkerLoop();
        });
    }

    void Stop() {
        if (!running_.exchange(false)) {
            return;  // Already stopped
        }

        // Wake up any waiting threads
        {
            std::lock_guard<std::mutex> lock(mutex_);
            cv_.notify_all();
        }

        // Abort will cause BlockingCall to return napi_closing
        tsfn_.Abort();
    }

private:
    void WorkerLoop() {
        while (running_) {
            // Interruptible wait
            {
                std::unique_lock<std::mutex> lock(mutex_);
                cv_.wait_for(lock, std::chrono::milliseconds(100), [this]() {
                    return !running_.load();
                });
            }

            if (!running_) break;

            DoWork();

            napi_status status = tsfn_.BlockingCall(
                [](Napi::Env env, Napi::Function callback) {
                    callback.Call({Napi::String::New(env, "tick")});
                }
            );

            if (status == napi_closing) {
                running_ = false;
                break;
            }
        }

        // Thread is done - release our reference
        tsfn_.Release();
    }

    void Shutdown() {
        // Called by TSFN finalizer - must join threads here!
        running_ = false;
        cv_.notify_all();

        if (!workerJoined_.exchange(true)) {
            if (worker_.joinable()) {
                worker_.join();  // Wait for thread to finish
            }
        }
    }

    void DoWork() {
        // Actual work here
    }

    Napi::ThreadSafeFunction tsfn_;
    std::thread worker_;
    std::atomic<bool> running_;
    std::atomic<bool> workerJoined_;
    std::mutex mutex_;
    std::condition_variable cv_;
};

// Wrap in PersistentReference to prevent garbage collection
class ServiceHandle : public Napi::ObjectWrap<ServiceHandle> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "BackgroundService", {
            InstanceMethod("stop", &ServiceHandle::Stop)
        });
        exports.Set("BackgroundService", func);
        return exports;
    }

    ServiceHandle(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<ServiceHandle>(info) {
        Napi::Env env = info.Env();
        Napi::Function callback = info[0].As<Napi::Function>();
        service_ = std::make_unique<BackgroundService>(env, callback);
    }

    ~ServiceHandle() {
        if (service_) {
            service_->Stop();
        }
    }

    Napi::Value Stop(const Napi::CallbackInfo& info) {
        if (service_) {
            service_->Stop();
        }
        return info.Env().Undefined();
    }

private:
    std::unique_ptr<BackgroundService> service_;
};
```

**Pattern: Using AddCleanupHook for process exit:**

```cpp
#include <napi.h>
#include <thread>
#include <vector>
#include <mutex>

// Global registry for cleanup
class ThreadRegistry {
public:
    static ThreadRegistry& Instance() {
        static ThreadRegistry instance;
        return instance;
    }

    void Register(std::thread::id id, std::function<void()> shutdown) {
        std::lock_guard<std::mutex> lock(mutex_);
        shutdownCallbacks_[id] = std::move(shutdown);
    }

    void Unregister(std::thread::id id) {
        std::lock_guard<std::mutex> lock(mutex_);
        shutdownCallbacks_.erase(id);
    }

    void ShutdownAll() {
        std::lock_guard<std::mutex> lock(mutex_);
        for (auto& [id, shutdown] : shutdownCallbacks_) {
            shutdown();
        }
        shutdownCallbacks_.clear();
    }

private:
    std::mutex mutex_;
    std::map<std::thread::id, std::function<void()>> shutdownCallbacks_;
};

// Register cleanup hook when addon loads
Napi::Object Init(Napi::Env env, Napi::Object exports) {
    // This runs when Node.js is about to exit
    napi_add_env_cleanup_hook(
        env,
        [](void* arg) {
            ThreadRegistry::Instance().ShutdownAll();
        },
        nullptr
    );

    return exports;
}
```

Reference: [Environment Cleanup Hooks](https://nodejs.org/api/n-api.html#environment-cleanup-hooks)
