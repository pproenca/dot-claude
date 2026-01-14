---
title: Check IsExceptionPending After N-API Calls
impact: MEDIUM-HIGH
impactDescription: Required for non-exception mode to prevent undefined behavior
tags: error, pending, status, exception-mode
---

## Check IsExceptionPending After N-API Calls

When C++ exceptions are disabled (`NAPI_DISABLE_CPP_EXCEPTIONS`), N-API functions set a pending exception instead of throwing. You must check `env.IsExceptionPending()` after operations that can fail, and return early if an exception is pending.

**Incorrect (ignoring pending exceptions):**

```cpp
// With NAPI_DISABLE_CPP_EXCEPTIONS defined
#include <napi.h>

Napi::Value ProcessData(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Type coercion may set pending exception
    Napi::Object obj = info[0].As<Napi::Object>();

    // WRONG: Not checking if As<> set a pending exception!
    Napi::Value name = obj.Get("name");

    // WRONG: Continuing to use potentially invalid values
    std::string nameStr = name.As<Napi::String>().Utf8Value();

    // More operations on potentially invalid state...
    Napi::Value count = obj.Get("count");
    int32_t countVal = count.As<Napi::Number>().Int32Value();

    // At this point we might have multiple pending exceptions
    // and undefined behavior from using invalid values
    return Napi::Number::New(env, countVal);
}
```

**Correct (checking pending exceptions):**

```cpp
// With NAPI_DISABLE_CPP_EXCEPTIONS defined
#include <napi.h>

Napi::Value ProcessData(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Check argument count first
    if (info.Length() < 1) {
        Napi::TypeError::New(env, "Expected 1 argument")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Check type before coercion
    if (!info[0].IsObject()) {
        Napi::TypeError::New(env, "Expected object argument")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Object obj = info[0].As<Napi::Object>();

    // Get property and check for exception
    Napi::Value nameVal = obj.Get("name");
    if (env.IsExceptionPending()) {
        return env.Undefined();
    }

    // Check type before coercion
    if (!nameVal.IsString()) {
        Napi::TypeError::New(env, "name must be a string")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    std::string name = nameVal.As<Napi::String>().Utf8Value();
    if (env.IsExceptionPending()) {
        return env.Undefined();
    }

    // Same pattern for other properties
    Napi::Value countVal = obj.Get("count");
    if (env.IsExceptionPending()) {
        return env.Undefined();
    }

    if (!countVal.IsNumber()) {
        Napi::TypeError::New(env, "count must be a number")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    int32_t count = countVal.As<Napi::Number>().Int32Value();
    if (env.IsExceptionPending()) {
        return env.Undefined();
    }

    // Safe to use values now
    return Napi::String::New(env, name + ": " + std::to_string(count));
}
```

**Pattern: Helper macros for cleaner code:**

```cpp
// Define helpers to reduce boilerplate
#define NAPI_RETURN_IF_PENDING(env) \
    if ((env).IsExceptionPending()) return (env).Undefined()

#define NAPI_RETURN_NULL_IF_PENDING(env) \
    if ((env).IsExceptionPending()) return nullptr

#define NAPI_CHECK_TYPE(env, value, type, message) \
    do { \
        if (!(value).Is##type()) { \
            Napi::TypeError::New((env), (message)) \
                .ThrowAsJavaScriptException(); \
            return (env).Undefined(); \
        } \
    } while (0)

// Usage with macros
Napi::Value ProcessDataClean(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    NAPI_CHECK_TYPE(env, info[0], Object, "Expected object argument");
    Napi::Object obj = info[0].As<Napi::Object>();

    Napi::Value nameVal = obj.Get("name");
    NAPI_RETURN_IF_PENDING(env);
    NAPI_CHECK_TYPE(env, nameVal, String, "name must be string");

    Napi::Value countVal = obj.Get("count");
    NAPI_RETURN_IF_PENDING(env);
    NAPI_CHECK_TYPE(env, countVal, Number, "count must be number");

    std::string name = nameVal.As<Napi::String>().Utf8Value();
    int32_t count = countVal.As<Napi::Number>().Int32Value();

    return Napi::String::New(env, name + ": " + std::to_string(count));
}
```

**Pattern: Wrapper class for automatic checking:**

```cpp
// RAII wrapper that checks exceptions on destruction
class ExceptionGuard {
public:
    ExceptionGuard(Napi::Env env) : env_(env), pending_(false) {}

    ~ExceptionGuard() {
        pending_ = env_.IsExceptionPending();
    }

    bool Check() {
        pending_ = env_.IsExceptionPending();
        return !pending_;
    }

    bool IsPending() const { return pending_; }

    Napi::Value ReturnIfPending() {
        if (env_.IsExceptionPending()) {
            pending_ = true;
            return env_.Undefined();
        }
        return Napi::Value();  // Empty value indicates OK
    }

private:
    Napi::Env env_;
    bool pending_;
};

// Usage
Napi::Value SafeOperation(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    ExceptionGuard guard(env);

    Napi::Object obj = info[0].As<Napi::Object>();
    if (!guard.Check()) return env.Undefined();

    Napi::Value val = obj.Get("key");
    if (!guard.Check()) return env.Undefined();

    return val;
}
```

Reference: [N-API Exception Handling](https://nodejs.org/api/n-api.html#exceptions)
