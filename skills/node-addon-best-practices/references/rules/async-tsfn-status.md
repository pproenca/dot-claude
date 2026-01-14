---
title: Check ThreadSafeFunction Status Codes
impact: HIGH
impactDescription: Ignoring status causes data loss, infinite loops, and deadlocks
tags: async, tsfn, status, error-handling
---

# Check ThreadSafeFunction Status Codes

Always check return status from `BlockingCall()` and `NonBlockingCall()`. Status codes like `napi_closing` and `napi_queue_full` indicate important conditions that require different handling.

## Why This Matters

- **Graceful Shutdown**: Detect when TSFN is closing
- **Backpressure Handling**: Respond to queue limits
- **Data Integrity**: Prevent data loss from ignored errors
- **Resource Cleanup**: Properly release resources on failure

## TSFN Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| `napi_ok` | Success | Continue |
| `napi_closing` | TSFN is shutting down | Stop calling, release |
| `napi_queue_full` | Queue at capacity | Wait and retry, or drop |
| `napi_invalid_arg` | Invalid TSFN handle | Bug - fix code |
| `napi_generic_failure` | Other failure | Log and handle |

## Incorrect: Ignoring Status

```cpp
// BAD: Status completely ignored
void BrokenWorker(Napi::ThreadSafeFunction& tsfn) {
    while (running_) {
        int* data = new int(counter_++);

        // BAD: Status ignored!
        tsfn.NonBlockingCall(data, Callback);
        // What if TSFN is closing? We leak data and keep looping
        // What if queue is full? We lose data silently

        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}
```

## Incorrect: Only Checking for napi_ok

```cpp
// BAD: Treating all non-ok as fatal
void PartiallyBrokenWorker(Napi::ThreadSafeFunction& tsfn) {
    while (running_) {
        int* data = new int(counter_++);
        napi_status status = tsfn.NonBlockingCall(data, Callback);

        if (status != napi_ok) {
            // BAD: Assumes all errors are fatal
            // napi_queue_full is recoverable!
            delete data;
            break;
        }
    }
}
```

## Correct: Comprehensive Status Handling

```cpp
// GOOD: Handle all status codes appropriately
#include <napi.h>
#include <thread>
#include <chrono>

class StatusAwareWorker {
public:
    void Run(Napi::ThreadSafeFunction& tsfn) {
        while (running_) {
            int* data = new int(counter_++);

            napi_status status = tsfn.NonBlockingCall(data, Callback);

            switch (status) {
                case napi_ok:
                    // Success - continue normally
                    break;

                case napi_closing:
                    // TSFN is being destroyed
                    // Clean up and exit gracefully
                    delete data;
                    LogInfo("TSFN closing, worker shutting down");
                    tsfn.Release();
                    return;

                case napi_queue_full:
                    // Queue is at capacity
                    // Options: wait, drop, or apply backpressure
                    delete data;
                    HandleQueueFull();
                    continue;

                case napi_invalid_arg:
                    // Invalid TSFN - programming error
                    delete data;
                    LogError("Invalid TSFN - bug in code");
                    return;

                default:
                    // Unexpected error
                    delete data;
                    LogError("Unexpected TSFN error: " + std::to_string(status));
                    tsfn.Release();
                    return;
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }

        tsfn.Release();
    }

private:
    void HandleQueueFull() {
        queueFullCount_++;

        if (queueFullCount_ > 10) {
            // Apply backpressure - slow down producer
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
            queueFullCount_ = 0;
        } else {
            // Brief pause before retry
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }

    std::atomic<bool> running_{true};
    std::atomic<int> counter_{0};
    int queueFullCount_ = 0;
};
```

## Pattern: Blocking vs NonBlocking Choice

```cpp
// GOOD: Choose call type based on requirements
class SmartWorker {
public:
    void ProducerThread(Napi::ThreadSafeFunction& tsfn) {
        while (running_) {
            auto* data = ProduceData();

            if (canDropData_) {
                // Non-critical data - use NonBlocking
                napi_status status = tsfn.NonBlockingCall(data, Callback);
                if (status == napi_queue_full) {
                    delete data;  // OK to drop
                    droppedCount_++;
                } else if (status == napi_closing) {
                    delete data;
                    break;
                }
            } else {
                // Critical data - use Blocking (waits for queue space)
                napi_status status = tsfn.BlockingCall(data, Callback);
                if (status != napi_ok) {
                    delete data;
                    if (status == napi_closing) break;
                }
            }
        }
        tsfn.Release();
    }
};
```

## Pattern: Retry with Exponential Backoff

```cpp
// GOOD: Sophisticated retry logic for queue_full
bool SendWithRetry(Napi::ThreadSafeFunction& tsfn, void* data,
                   int maxRetries = 5) {
    int retryDelay = 10;  // Start at 10ms

    for (int attempt = 0; attempt < maxRetries; attempt++) {
        napi_status status = tsfn.NonBlockingCall(data, Callback);

        switch (status) {
            case napi_ok:
                return true;

            case napi_queue_full:
                // Exponential backoff
                std::this_thread::sleep_for(
                    std::chrono::milliseconds(retryDelay));
                retryDelay = std::min(retryDelay * 2, 1000);  // Max 1s
                continue;

            case napi_closing:
                return false;  // TSFN shutting down

            default:
                return false;  // Other error
        }
    }

    return false;  // Max retries exceeded
}
```

## Pattern: Status-Based State Machine

```cpp
// GOOD: State machine for complex status handling
enum class WorkerState {
    Running,
    Backpressure,
    Draining,
    Stopped
};

class StateMachineWorker {
public:
    void Run(Napi::ThreadSafeFunction& tsfn) {
        state_ = WorkerState::Running;

        while (state_ != WorkerState::Stopped) {
            switch (state_) {
                case WorkerState::Running:
                    HandleRunningState(tsfn);
                    break;

                case WorkerState::Backpressure:
                    HandleBackpressureState(tsfn);
                    break;

                case WorkerState::Draining:
                    HandleDrainingState(tsfn);
                    break;

                default:
                    break;
            }
        }

        tsfn.Release();
    }

private:
    void HandleRunningState(Napi::ThreadSafeFunction& tsfn) {
        auto* data = ProduceData();
        napi_status status = tsfn.NonBlockingCall(data, Callback);

        switch (status) {
            case napi_ok:
                // Stay in Running
                break;

            case napi_queue_full:
                delete data;
                state_ = WorkerState::Backpressure;
                backpressureStart_ = std::chrono::steady_clock::now();
                break;

            case napi_closing:
                delete data;
                state_ = WorkerState::Draining;
                break;

            default:
                delete data;
                state_ = WorkerState::Stopped;
                break;
        }
    }

    void HandleBackpressureState(Napi::ThreadSafeFunction& tsfn) {
        // Wait before trying again
        std::this_thread::sleep_for(std::chrono::milliseconds(50));

        // Check if we've been in backpressure too long
        auto now = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::seconds>(
            now - backpressureStart_);

        if (duration.count() > 30) {
            LogWarning("Backpressure timeout - stopping");
            state_ = WorkerState::Stopped;
            return;
        }

        // Try to resume
        auto* data = ProduceData();
        napi_status status = tsfn.NonBlockingCall(data, Callback);

        if (status == napi_ok) {
            state_ = WorkerState::Running;
        } else if (status == napi_queue_full) {
            delete data;
            // Stay in Backpressure
        } else {
            delete data;
            state_ = WorkerState::Stopped;
        }
    }

    void HandleDrainingState(Napi::ThreadSafeFunction& tsfn) {
        // TSFN is closing - finish up
        state_ = WorkerState::Stopped;
    }

    WorkerState state_;
    std::chrono::steady_clock::time_point backpressureStart_;
};
```

## Quick Reference

```cpp
// Status handling cheat sheet
napi_status status = tsfn.NonBlockingCall(data, callback);

if (status == napi_ok) {
    // Data was queued successfully
}
else if (status == napi_closing) {
    // TSFN is shutting down
    // - Don't call again
    // - Clean up data
    // - Call Release()
    delete data;
    tsfn.Release();
}
else if (status == napi_queue_full) {
    // Queue is full (only if maxQueueSize > 0)
    // - Retry after delay, OR
    // - Drop data (if acceptable), OR
    // - Use BlockingCall instead
    delete data;  // or retry
}
else {
    // Other error - treat as fatal
    delete data;
    tsfn.Release();
}
```

## References

- [N-API TSFN Call](https://nodejs.org/api/n-api.html#napi_call_threadsafe_function)
- [napi_threadsafe_function_call_mode](https://nodejs.org/api/n-api.html#napi_threadsafe_function_call_mode)
