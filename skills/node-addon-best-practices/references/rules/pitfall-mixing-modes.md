---
title: Don't Mix Exception Modes
impact: LOW
impactDescription: Prevents confusing error handling and missed errors
tags: pitfall, exceptions, errors, consistency, api-design
---

# Don't Mix Exception Modes

Pick one error handling approach and use it consistently throughout your addon. Mixing C++ exceptions with status code checking leads to confusing APIs and missed errors.

## Why This Matters

- Inconsistent error handling confuses users
- Exceptions may propagate unexpectedly
- Status codes may be ignored if exceptions expected
- Makes debugging harder

## Incorrect

Mixing throw with status codes:

```cpp
#include <napi.h>

// BAD: Function throws exception
Napi::Value ProcessWithThrow(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsNumber()) {
        // Throws JavaScript exception
        Napi::TypeError::New(env, "Expected number")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // ...
    return env.Undefined();
}

// BAD: Same API, different function returns status code
Napi::Value ProcessWithStatus(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsNumber()) {
        // Returns error object instead of throwing
        Napi::Object error = Napi::Object::New(env);
        error.Set("error", "Expected number");
        error.Set("code", "INVALID_TYPE");
        return error;
    }

    Napi::Object result = Napi::Object::New(env);
    result.Set("success", true);
    return result;
}

// BAD: C++ exceptions mixed with N-API
void UnsafeCppException() {
    throw std::runtime_error("C++ exception");  // Uncaught!
}

Napi::Value CallUnsafe(const Napi::CallbackInfo& info) {
    UnsafeCppException();  // Will crash Node.js!
    return info.Env().Undefined();
}
```

## Correct

Choose one approach and use it consistently:

### Approach 1: Exceptions (Recommended with node-addon-api)

```cpp
#include <napi.h>

// GOOD: Consistent exception-based error handling
class Calculator {
public:
    static Napi::Value Add(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        ValidateArguments(info, 2, "add");

        double a = info[0].As<Napi::Number>().DoubleValue();
        double b = info[1].As<Napi::Number>().DoubleValue();

        return Napi::Number::New(env, a + b);
    }

    static Napi::Value Divide(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        ValidateArguments(info, 2, "divide");

        double a = info[0].As<Napi::Number>().DoubleValue();
        double b = info[1].As<Napi::Number>().DoubleValue();

        if (b == 0) {
            Napi::RangeError::New(env, "Division by zero")
                .ThrowAsJavaScriptException();
            return env.Undefined();
        }

        return Napi::Number::New(env, a / b);
    }

    static Napi::Value Sqrt(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        ValidateArguments(info, 1, "sqrt");

        double a = info[0].As<Napi::Number>().DoubleValue();

        if (a < 0) {
            Napi::RangeError::New(env, "Cannot compute sqrt of negative number")
                .ThrowAsJavaScriptException();
            return env.Undefined();
        }

        return Napi::Number::New(env, std::sqrt(a));
    }

private:
    // Consistent validation helper
    static void ValidateArguments(const Napi::CallbackInfo& info,
                                   size_t required,
                                   const char* funcName) {
        Napi::Env env = info.Env();

        if (info.Length() < required) {
            std::string msg = std::string(funcName) +
                " requires " + std::to_string(required) + " arguments";
            Napi::TypeError::New(env, msg).ThrowAsJavaScriptException();
            return;
        }

        for (size_t i = 0; i < required; i++) {
            if (!info[i].IsNumber()) {
                std::string msg = std::string(funcName) +
                    ": argument " + std::to_string(i) + " must be a number";
                Napi::TypeError::New(env, msg).ThrowAsJavaScriptException();
                return;
            }
        }
    }
};
```

### Approach 2: Result Objects (Explicit Error Handling)

```cpp
#include <napi.h>
#include <optional>
#include <variant>

// GOOD: Consistent result-object pattern
class ResultApi {
public:
    // All functions return { ok: bool, value?: T, error?: string }
    static Napi::Value Add(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        auto validation = ValidateNumbers(info, 2);
        if (!validation.ok) {
            return CreateError(env, validation.error);
        }

        double a = info[0].As<Napi::Number>().DoubleValue();
        double b = info[1].As<Napi::Number>().DoubleValue();

        return CreateSuccess(env, a + b);
    }

    static Napi::Value Divide(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        auto validation = ValidateNumbers(info, 2);
        if (!validation.ok) {
            return CreateError(env, validation.error);
        }

        double a = info[0].As<Napi::Number>().DoubleValue();
        double b = info[1].As<Napi::Number>().DoubleValue();

        if (b == 0) {
            return CreateError(env, "Division by zero");
        }

        return CreateSuccess(env, a / b);
    }

    static Napi::Value Sqrt(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        auto validation = ValidateNumbers(info, 1);
        if (!validation.ok) {
            return CreateError(env, validation.error);
        }

        double a = info[0].As<Napi::Number>().DoubleValue();

        if (a < 0) {
            return CreateError(env, "Cannot compute sqrt of negative number");
        }

        return CreateSuccess(env, std::sqrt(a));
    }

private:
    struct ValidationResult {
        bool ok;
        std::string error;
    };

    static ValidationResult ValidateNumbers(const Napi::CallbackInfo& info,
                                             size_t count) {
        if (info.Length() < count) {
            return {false, "Not enough arguments"};
        }

        for (size_t i = 0; i < count; i++) {
            if (!info[i].IsNumber()) {
                return {false, "Argument " + std::to_string(i) + " must be a number"};
            }
        }

        return {true, ""};
    }

    static Napi::Object CreateSuccess(Napi::Env env, double value) {
        Napi::Object result = Napi::Object::New(env);
        result.Set("ok", true);
        result.Set("value", value);
        return result;
    }

    static Napi::Object CreateError(Napi::Env env, const std::string& error) {
        Napi::Object result = Napi::Object::New(env);
        result.Set("ok", false);
        result.Set("error", error);
        return result;
    }
};
```

## Catching C++ Exceptions

If using libraries that throw C++ exceptions:

```cpp
#include <napi.h>
#include <stdexcept>

// GOOD: Convert C++ exceptions to JavaScript exceptions
Napi::Value SafeWrapper(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    try {
        // Call code that might throw C++ exceptions
        ExternalLibraryFunction();

        return Napi::String::New(env, "success");
    } catch (const std::invalid_argument& e) {
        Napi::TypeError::New(env, e.what())
            .ThrowAsJavaScriptException();
    } catch (const std::out_of_range& e) {
        Napi::RangeError::New(env, e.what())
            .ThrowAsJavaScriptException();
    } catch (const std::exception& e) {
        Napi::Error::New(env, e.what())
            .ThrowAsJavaScriptException();
    } catch (...) {
        Napi::Error::New(env, "Unknown error")
            .ThrowAsJavaScriptException();
    }

    return env.Undefined();
}
```

## JavaScript Usage Patterns

```javascript
// Exception-based API
try {
    const result = addon.divide(10, 0);
} catch (e) {
    console.error('Error:', e.message);
}

// Result-object API
const result = addon.divide(10, 0);
if (!result.ok) {
    console.error('Error:', result.error);
} else {
    console.log('Result:', result.value);
}
```

## Comparison

| Aspect | Exceptions | Result Objects |
|--------|-----------|----------------|
| Error propagation | Automatic | Manual |
| Code verbosity | Less | More |
| Performance | Slower on error | Consistent |
| TypeScript | Harder to type | Easy to type |
| Stack traces | Yes | No |
