---
title: Don't Mix Exception Handling Modes
impact: LOW
impactDescription: Prevents confusing error behavior and missed exceptions
tags: pitfall, exceptions, error-handling, consistency
---

# Don't Mix Exception Handling Modes

Choose one error handling strategy and use it consistently: either C++ exceptions (with node-addon-api exception support) or manual status checking. Mixing modes leads to missed errors and inconsistent behavior.

## Why This Matters

- C++ exceptions bypass N-API error checking
- Uncaught exceptions cause process crashes
- Mixed modes make error origin unclear
- Code becomes harder to maintain and debug

## Incorrect

Mixing C++ exceptions with N-API status checks:

```cpp
#include <napi.h>
#include <stdexcept>

// BAD: Throwing C++ exception without proper handling
Napi::Value MixedErrorHandling(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Sometimes use N-API exceptions
    if (!info[0].IsNumber()) {
        Napi::TypeError::New(env, "Expected number")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    double value = info[0].As<Napi::Number>().DoubleValue();

    // Sometimes throw C++ exceptions (inconsistent!)
    if (value < 0) {
        throw std::runtime_error("Value must be non-negative");
        // This will crash Node.js if not caught!
    }

    // Sometimes check status manually
    napi_value result;
    napi_status status = napi_create_double(env, value * 2, &result);
    if (status != napi_ok) {
        // Now we're checking status...inconsistent
        return env.Undefined();
    }

    return Napi::Value(env, result);
}

// BAD: Forgetting to check for pending exception
Napi::Value ForgotExceptionCheck(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array arr = info[0].As<Napi::Array>();

    double sum = 0;
    for (uint32_t i = 0; i < arr.Length(); i++) {
        // This Get() might throw (e.g., if getter throws)
        Napi::Value elem = arr.Get(i);

        // MISSING: Check if exception is pending
        // if (env.IsExceptionPending()) return env.Undefined();

        sum += elem.As<Napi::Number>().DoubleValue();
    }

    return Napi::Number::New(env, sum);
}

// BAD: Library code throws, wrapper doesn't catch
double InternalCompute(double x) {
    if (x < 0) {
        throw std::domain_error("Negative input");
    }
    return std::sqrt(x);
}

Napi::Value WrapperWithoutCatch(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    double x = info[0].As<Napi::Number>().DoubleValue();

    // If InternalCompute throws, Node.js crashes
    double result = InternalCompute(x);

    return Napi::Number::New(env, result);
}
```

## Correct

Consistent exception mode with proper handling:

```cpp
#include <napi.h>
#include <cmath>

// GOOD: Consistent N-API exception mode
// Build with NAPI_CPP_EXCEPTIONS defined

Napi::Value ConsistentNapiExceptions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // All error paths use Napi exceptions
    if (!info[0].IsNumber()) {
        Napi::TypeError::New(env, "Expected number")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    double value = info[0].As<Napi::Number>().DoubleValue();

    if (value < 0) {
        Napi::RangeError::New(env, "Value must be non-negative")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    if (std::isnan(value)) {
        Napi::RangeError::New(env, "Value cannot be NaN")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    return Napi::Number::New(env, std::sqrt(value));
}

// GOOD: Check for pending exceptions after operations that might throw
Napi::Value SafeArrayIteration(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsArray()) {
        Napi::TypeError::New(env, "Expected array")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Array arr = info[0].As<Napi::Array>();
    double sum = 0;

    for (uint32_t i = 0; i < arr.Length(); i++) {
        Napi::Value elem = arr.Get(i);

        // IMPORTANT: Check for pending exception
        if (env.IsExceptionPending()) {
            return env.Undefined();
        }

        if (!elem.IsNumber()) {
            continue;  // Skip non-numbers
        }

        sum += elem.As<Napi::Number>().DoubleValue();
    }

    return Napi::Number::New(env, sum);
}
```

## Wrapping C++ Libraries with Exception Translation

```cpp
#include <napi.h>
#include <stdexcept>
#include <cmath>

// C++ library that throws exceptions
namespace lib {
    double compute(double x) {
        if (x < 0) {
            throw std::domain_error("Negative input not allowed");
        }
        if (std::isnan(x)) {
            throw std::invalid_argument("NaN input not allowed");
        }
        return std::sqrt(x);
    }

    void process(const std::string& data) {
        if (data.empty()) {
            throw std::runtime_error("Empty data");
        }
        // ...
    }
}

// GOOD: Translate C++ exceptions to JavaScript exceptions
Napi::Value SafeCompute(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsNumber()) {
        Napi::TypeError::New(env, "Expected number")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    double x = info[0].As<Napi::Number>().DoubleValue();

    try {
        double result = lib::compute(x);
        return Napi::Number::New(env, result);
    } catch (const std::domain_error& e) {
        Napi::RangeError::New(env, e.what())
            .ThrowAsJavaScriptException();
        return env.Undefined();
    } catch (const std::invalid_argument& e) {
        Napi::TypeError::New(env, e.what())
            .ThrowAsJavaScriptException();
        return env.Undefined();
    } catch (const std::exception& e) {
        Napi::Error::New(env, e.what())
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }
}

// GOOD: Helper macro for exception translation
#define NAPI_TRY_CATCH(env, expr)                                    \
    try {                                                            \
        return expr;                                                 \
    } catch (const std::domain_error& e) {                          \
        Napi::RangeError::New(env, e.what())                        \
            .ThrowAsJavaScriptException();                          \
        return env.Undefined();                                     \
    } catch (const std::invalid_argument& e) {                      \
        Napi::TypeError::New(env, e.what())                         \
            .ThrowAsJavaScriptException();                          \
        return env.Undefined();                                     \
    } catch (const std::exception& e) {                             \
        Napi::Error::New(env, e.what())                             \
            .ThrowAsJavaScriptException();                          \
        return env.Undefined();                                     \
    }

Napi::Value SafeProcess(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    std::string data = info[0].As<Napi::String>().Utf8Value();

    NAPI_TRY_CATCH(env, {
        lib::process(data);
        return env.Undefined();
    });
}
```

## Consistent Error Handling in AsyncWorker

```cpp
#include <napi.h>
#include <stdexcept>

// GOOD: Consistent exception handling in async context
class ConsistentAsyncWorker : public Napi::AsyncWorker {
public:
    ConsistentAsyncWorker(Napi::Env env, Napi::Promise::Deferred deferred,
                          double input)
        : Napi::AsyncWorker(env),
          deferred_(deferred),
          input_(input),
          result_(0.0) {}

    void Execute() override {
        // In Execute, use SetError for errors (not exceptions)
        if (input_ < 0) {
            SetError("Input must be non-negative");
            return;
        }

        try {
            // C++ exceptions here are caught by AsyncWorker
            result_ = lib::compute(input_);
        } catch (const std::exception& e) {
            // Translate to SetError
            SetError(e.what());
        }
    }

    void OnOK() override {
        // Runs on main thread - can use Napi exceptions
        deferred_.Resolve(Napi::Number::New(Env(), result_));
    }

    void OnError(const Napi::Error& error) override {
        // Error from SetError is passed here
        deferred_.Reject(error.Value());
    }

private:
    Napi::Promise::Deferred deferred_;
    double input_;
    double result_;
};
```

## Build Configuration for Exception Mode

```python
# binding.gyp - Enable C++ exceptions for node-addon-api

{
  "targets": [{
    "target_name": "addon",
    "sources": ["src/addon.cpp"],
    "include_dirs": [
      "<!@(node -p \"require('node-addon-api').include\")"
    ],
    "defines": [
      "NAPI_VERSION=8",
      "NAPI_CPP_EXCEPTIONS"  # Enable C++ exception support
    ],
    "cflags!": ["-fno-exceptions"],
    "cflags_cc!": ["-fno-exceptions"],
    "xcode_settings": {
      "GCC_ENABLE_CPP_EXCEPTIONS": "YES"
    },
    "msvs_settings": {
      "VCCLCompilerTool": {
        "ExceptionHandling": 1
      }
    }
  }]
}
```

## Exception Mode Reference

| Mode | Define | Behavior |
|------|--------|----------|
| C++ exceptions | `NAPI_CPP_EXCEPTIONS` | Napi methods throw C++ exceptions |
| No exceptions | `NAPI_DISABLE_CPP_EXCEPTIONS` | Must check `env.IsExceptionPending()` |
| Default | Neither | Same as C++ exceptions if enabled |

Reference: [node-addon-api Error Handling](https://github.com/nodejs/node-addon-api/blob/main/doc/error_handling.md)
