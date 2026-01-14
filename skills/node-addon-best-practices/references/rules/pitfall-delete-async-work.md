---
title: Don't Forget to Delete Async Work
impact: LOW
impactDescription: Prevents memory leaks in async operations
tags: pitfall, async, memory-leak, cleanup, resources
---

# Don't Forget to Delete Async Work

Call `napi_delete_async_work` in the complete callback. Failing to delete async work structures causes memory leaks that accumulate over time.

## Why This Matters

- Each async operation allocates internal structures
- Structures persist until explicitly deleted
- Long-running servers leak memory over time
- Can lead to out-of-memory crashes

## Incorrect

Leaking async work structure:

```cpp
#include <napi.h>

struct WorkData {
    napi_async_work work;
    napi_deferred deferred;
    int input;
    int result;
};

// BAD: Never deletes async work
void ExecuteWork(napi_env env, void* data) {
    WorkData* workData = static_cast<WorkData*>(data);
    workData->result = workData->input * 2;
}

void CompleteWorkBad(napi_env env, napi_status status, void* data) {
    WorkData* workData = static_cast<WorkData*>(data);

    napi_value result;
    napi_create_int32(env, workData->result, &result);
    napi_resolve_deferred(env, workData->deferred, result);

    // LEAK: Forgot to delete async work
    // LEAK: Forgot to delete WorkData
}

napi_value CreateWorkBad(napi_env env, napi_callback_info info) {
    // ... setup code ...

    WorkData* data = new WorkData();  // Never freed!
    napi_create_async_work(
        env, nullptr, resourceName,
        ExecuteWork, CompleteWorkBad, data,
        &data->work
    );
    napi_queue_async_work(env, data->work);

    // ... return promise ...
}
```

## Correct

Clean up all resources in complete callback:

```cpp
#include <napi.h>
#include <memory>

struct WorkData {
    napi_async_work work;
    napi_deferred deferred;
    int input;
    int result;
};

void ExecuteWork(napi_env env, void* data) {
    WorkData* workData = static_cast<WorkData*>(data);
    workData->result = workData->input * 2;
}

// GOOD: Clean up everything in complete callback
void CompleteWorkGood(napi_env env, napi_status status, void* data) {
    WorkData* workData = static_cast<WorkData*>(data);

    if (status == napi_ok) {
        napi_value result;
        napi_create_int32(env, workData->result, &result);
        napi_resolve_deferred(env, workData->deferred, result);
    } else {
        napi_value error;
        napi_create_string_utf8(env, "Work cancelled", NAPI_AUTO_LENGTH, &error);
        napi_reject_deferred(env, workData->deferred, error);
    }

    // IMPORTANT: Delete the async work structure
    napi_delete_async_work(env, workData->work);

    // IMPORTANT: Free the data structure
    delete workData;
}

napi_value CreateWorkGood(napi_env env, napi_callback_info info) {
    size_t argc = 1;
    napi_value argv[1];
    napi_get_cb_info(env, info, &argc, argv, nullptr, nullptr);

    int32_t input;
    napi_get_value_int32(env, argv[0], &input);

    napi_deferred deferred;
    napi_value promise;
    napi_create_promise(env, &deferred, &promise);

    WorkData* data = new WorkData();
    data->deferred = deferred;
    data->input = input;

    napi_value resourceName;
    napi_create_string_utf8(env, "MyAsyncWork", NAPI_AUTO_LENGTH, &resourceName);

    napi_create_async_work(
        env, nullptr, resourceName,
        ExecuteWork, CompleteWorkGood, data,
        &data->work
    );

    napi_queue_async_work(env, data->work);

    return promise;
}
```

## Using node-addon-api (Recommended)

AsyncWorker handles cleanup automatically:

```cpp
#include <napi.h>

// GOOD: Napi::AsyncWorker handles cleanup automatically
class ComputeWorker : public Napi::AsyncWorker {
public:
    ComputeWorker(const Napi::Env& env,
                  int input,
                  Napi::Promise::Deferred deferred)
        : Napi::AsyncWorker(env),
          input_(input),
          deferred_(deferred) {}

    // Destructor called automatically after OnOK/OnError
    ~ComputeWorker() {
        // Custom cleanup here if needed
    }

    void Execute() override {
        result_ = input_ * 2;
    }

    void OnOK() override {
        deferred_.Resolve(Napi::Number::New(Env(), result_));
        // AsyncWorker cleans itself up after this
    }

    void OnError(const Napi::Error& err) override {
        deferred_.Reject(err.Value());
        // AsyncWorker cleans itself up after this
    }

private:
    int input_;
    int result_;
    Napi::Promise::Deferred deferred_;
};

Napi::Value ComputeAsync(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    int input = info[0].As<Napi::Number>().Int32Value();

    auto deferred = Napi::Promise::Deferred::New(env);

    // Worker is automatically deleted after completion
    auto* worker = new ComputeWorker(env, input, deferred);
    worker->Queue();

    return deferred.Promise();
}
```

## TSFN Cleanup Pattern

```cpp
#include <napi.h>
#include <thread>

// GOOD: Proper TSFN cleanup
class StreamWorker {
public:
    static Napi::Value Start(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        Napi::Function callback = info[0].As<Napi::Function>();

        // Create TSFN with ref count
        auto tsfn = Napi::ThreadSafeFunction::New(
            env,
            callback,
            "StreamCallback",
            0,    // Unlimited queue
            1,    // Initial thread count
            nullptr,
            [](Napi::Env, void*, void*) {
                // Destructor runs when TSFN is released
            },
            nullptr
        );

        std::thread([tsfn]() mutable {
            for (int i = 0; i < 10; i++) {
                auto status = tsfn.BlockingCall(
                    [i](Napi::Env env, Napi::Function cb) {
                        cb.Call({Napi::Number::New(env, i)});
                    }
                );

                if (status != napi_ok) {
                    break;  // TSFN was aborted
                }
            }

            // IMPORTANT: Release TSFN when done
            tsfn.Release();
        }).detach();

        return env.Undefined();
    }
};
```

## Resource Cleanup Checklist

| Resource | Cleanup Method |
|----------|----------------|
| `napi_async_work` | `napi_delete_async_work` |
| `napi_ref` | `napi_delete_reference` |
| `napi_threadsafe_function` | `napi_release_threadsafe_function` |
| Allocated memory | `delete` / `free` |
| `Napi::AsyncWorker` | Automatic (self-delete) |
| `Napi::Reference` | Automatic (destructor) |

## Detecting Leaks

```javascript
// Monitor memory usage
const initialMemory = process.memoryUsage().heapUsed;

// Run many async operations
for (let i = 0; i < 10000; i++) {
    await addon.computeAsync(i);
}

// Force GC if available
if (global.gc) global.gc();

const finalMemory = process.memoryUsage().heapUsed;
const leaked = finalMemory - initialMemory;

if (leaked > 1024 * 1024) {
    console.warn(`Potential leak: ${(leaked / 1024 / 1024).toFixed(2)}MB`);
}
```
