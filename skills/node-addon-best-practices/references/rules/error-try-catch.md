---
title: Use try-catch in C++ Callbacks for JS Function Calls
impact: MEDIUM-HIGH
impactDescription: Prevents unhandled exceptions from crashing the Node.js process
tags: error, try-catch, callback, exception-safety
---

## Use try-catch in C++ Callbacks for JS Function Calls

When calling JavaScript functions from C++, the JS code may throw exceptions. These exceptions propagate as `Napi::Error` in C++. Always wrap JS function calls in try-catch to handle errors gracefully and prevent crashes.

**Incorrect (unhandled exceptions from JS callbacks):**

```cpp
#include <napi.h>

class EventProcessor {
public:
    EventProcessor(Napi::Function callback)
        : callback_(Napi::Persistent(callback)) {}

    void ProcessEvent(Napi::Env env, const std::string& data) {
        // DANGEROUS: If JS callback throws, the exception propagates
        // and may crash or leave state inconsistent
        callback_.Value().Call({Napi::String::New(env, data)});

        // This code may never execute if callback throws!
        CleanupAfterEvent();
    }

    void ProcessMultiple(Napi::Env env, const std::vector<std::string>& items) {
        for (const auto& item : items) {
            // If one callback throws, remaining items are skipped!
            callback_.Value().Call({Napi::String::New(env, item)});
        }
    }

private:
    Napi::FunctionReference callback_;
    void CleanupAfterEvent() { /* cleanup */ }
};
```

**Correct (proper exception handling):**

```cpp
#include <napi.h>
#include <vector>

class EventProcessor {
public:
    EventProcessor(Napi::Function callback)
        : callback_(Napi::Persistent(callback)) {}

    bool ProcessEvent(Napi::Env env, const std::string& data) {
        try {
            Napi::Value result = callback_.Value().Call({
                Napi::String::New(env, data)
            });

            // Can check result if needed
            if (result.IsBoolean() && !result.As<Napi::Boolean>().Value()) {
                return false;  // Callback returned false
            }

            return true;
        } catch (const Napi::Error& e) {
            // Log the error but don't crash
            HandleCallbackError(env, e);
            return false;
        }
    }

    struct ProcessResult {
        int successful;
        int failed;
        std::vector<std::string> errors;
    };

    ProcessResult ProcessMultiple(Napi::Env env,
                                   const std::vector<std::string>& items) {
        ProcessResult result{0, 0, {}};

        for (const auto& item : items) {
            try {
                callback_.Value().Call({Napi::String::New(env, item)});
                result.successful++;
            } catch (const Napi::Error& e) {
                result.failed++;
                result.errors.push_back(
                    "Item '" + item + "': " + e.Message());
                // Continue processing remaining items
            }
        }

        return result;
    }

    // Call with error callback pattern
    void ProcessWithErrorCallback(Napi::Env env,
                                   const std::string& data,
                                   Napi::Function errorCallback) {
        try {
            callback_.Value().Call({Napi::String::New(env, data)});
        } catch (const Napi::Error& e) {
            // Forward error to error callback
            try {
                errorCallback.Call({e.Value()});
            } catch (...) {
                // Error callback also threw - log and continue
            }
        }
    }

private:
    Napi::FunctionReference callback_;

    void HandleCallbackError(Napi::Env env, const Napi::Error& e) {
        // Options: log, emit event, store for later retrieval
        std::cerr << "Callback error: " << e.Message() << std::endl;
    }
};

// Pattern for async callbacks with error handling
class SafeAsyncWorker : public Napi::AsyncWorker {
public:
    SafeAsyncWorker(Napi::Function callback)
        : Napi::AsyncWorker(callback) {}

    void Execute() override {
        // Do work...
    }

    void OnOK() override {
        try {
            Callback().Call({
                Env().Null(),  // error
                Napi::String::New(Env(), "result")
            });
        } catch (const Napi::Error& e) {
            // Callback threw - can't do much here except log
            // The exception is swallowed to prevent crashes
            std::cerr << "OnOK callback error: " << e.Message() << std::endl;
        }
    }

    void OnError(const Napi::Error& e) override {
        try {
            Callback().Call({e.Value()});
        } catch (const Napi::Error& callbackError) {
            // Error callback also threw
            std::cerr << "OnError callback error: "
                      << callbackError.Message() << std::endl;
        }
    }
};
```

**Pattern: Safe callback wrapper:**

```cpp
// Reusable wrapper for safe JS function calls
class SafeCallback {
public:
    SafeCallback(Napi::Function fn) : fn_(Napi::Persistent(fn)) {}

    template<typename... Args>
    std::optional<Napi::Value> Call(Napi::Env env, Args&&... args) {
        try {
            std::vector<napi_value> argv = {
                ToNapiValue(env, std::forward<Args>(args))...
            };
            return fn_.Value().Call(argv);
        } catch (const Napi::Error& e) {
            lastError_ = e.Message();
            return std::nullopt;
        }
    }

    const std::string& LastError() const { return lastError_; }
    bool HasError() const { return !lastError_.empty(); }
    void ClearError() { lastError_.clear(); }

private:
    Napi::FunctionReference fn_;
    std::string lastError_;

    template<typename T>
    napi_value ToNapiValue(Napi::Env env, T&& val);
};
```

Reference: [Napi::Error Documentation](https://github.com/nodejs/node-addon-api/blob/main/doc/error.md)
