---
title: Validate Input Argument Counts
impact: CRITICAL
impactDescription: Out-of-bounds argv access causes crashes and undefined behavior
tags: napi, validation, arguments, safety
---

# Validate Input Argument Counts

Always check the argument count (`argc` or `info.Length()`) before accessing `argv` elements to prevent out-of-bounds access and crashes.

## Why This Matters

- **Crash Prevention**: Accessing `argv[n]` when `argc < n` is undefined behavior
- **User Experience**: Clear error messages instead of cryptic crashes
- **Security**: Prevents exploitation of argument handling bugs
- **Robustness**: Handles all valid JavaScript calling patterns

## Incorrect: Direct argv Access Without Validation

```cpp
// BAD: No argument count validation
static napi_value Add(napi_env env, napi_callback_info info) {
    size_t argc = 2;
    napi_value argv[2];
    napi_get_cb_info(env, info, &argc, argv, NULL, NULL);

    // DANGEROUS: What if user called add() with no arguments?
    // argv[0] and argv[1] contain garbage or crash
    double a, b;
    napi_get_value_double(env, argv[0], &a);  // Undefined behavior!
    napi_get_value_double(env, argv[1], &b);  // Undefined behavior!

    napi_value result;
    napi_create_double(env, a + b, &result);
    return result;
}
```

**JavaScript that causes crashes:**
```javascript
const addon = require('./addon');

addon.add();           // Crash - no arguments
addon.add(1);          // Crash - only one argument
addon.add(1, 2);       // Works
addon.add(1, 2, 3);    // Works (extra ignored)
```

## Incorrect: Wrong argc Declaration

```cpp
// BAD: argc initialized wrong - N-API updates it to actual count
static napi_value Process(napi_env env, napi_callback_info info) {
    // Declaring argc as the expected count doesn't validate anything!
    size_t argc = 3;  // This will be OVERWRITTEN with actual count
    napi_value argv[3];

    napi_get_cb_info(env, info, &argc, argv, NULL, NULL);
    // argc is now the ACTUAL argument count, not 3

    // Still dangerous - argc might be 0, 1, or 2
    double x = 0, y = 0, z = 0;
    napi_get_value_double(env, argv[0], &x);  // May fail!
    napi_get_value_double(env, argv[1], &y);  // May fail!
    napi_get_value_double(env, argv[2], &z);  // May fail!

    // ...
}
```

## Correct: Validate Argument Count (Raw N-API)

```cpp
// GOOD: Proper argument count validation
static napi_value Add(napi_env env, napi_callback_info info) {
    napi_status status;

    // Get arguments - argc will be updated to actual count
    size_t argc = 2;
    napi_value argv[2];
    status = napi_get_cb_info(env, info, &argc, argv, NULL, NULL);
    if (status != napi_ok) {
        napi_throw_error(env, NULL, "Failed to get callback info");
        return NULL;
    }

    // CRITICAL: Validate argument count
    if (argc < 2) {
        napi_throw_type_error(env, NULL,
            "add() requires 2 arguments: add(a, b)");
        return NULL;
    }

    // Now safe to access argv[0] and argv[1]
    napi_valuetype type0, type1;
    napi_typeof(env, argv[0], &type0);
    napi_typeof(env, argv[1], &type1);

    if (type0 != napi_number || type1 != napi_number) {
        napi_throw_type_error(env, NULL, "Both arguments must be numbers");
        return NULL;
    }

    double a, b;
    napi_get_value_double(env, argv[0], &a);
    napi_get_value_double(env, argv[1], &b);

    napi_value result;
    napi_create_double(env, a + b, &result);
    return result;
}
```

## Correct: Validate with node-addon-api

```cpp
// GOOD: node-addon-api with clear validation
#include <napi.h>

Napi::Value Add(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Check argument count first
    if (info.Length() < 2) {
        throw Napi::TypeError::New(env,
            "add() requires 2 arguments: add(a, b)");
    }

    // Then check types
    if (!info[0].IsNumber() || !info[1].IsNumber()) {
        throw Napi::TypeError::New(env,
            "Both arguments must be numbers");
    }

    // Safe to use
    double a = info[0].As<Napi::Number>().DoubleValue();
    double b = info[1].As<Napi::Number>().DoubleValue();

    return Napi::Number::New(env, a + b);
}
```

## Pattern: Optional Arguments with Defaults

```cpp
// GOOD: Handle optional arguments safely
Napi::Value CreateConfig(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Required argument
    if (info.Length() < 1 || !info[0].IsString()) {
        throw Napi::TypeError::New(env, "First argument (name) is required");
    }
    std::string name = info[0].As<Napi::String>().Utf8Value();

    // Optional argument with default
    int timeout = 30000;  // default
    if (info.Length() >= 2) {
        if (!info[1].IsNumber() && !info[1].IsUndefined()) {
            throw Napi::TypeError::New(env, "Second argument must be a number");
        }
        if (info[1].IsNumber()) {
            timeout = info[1].As<Napi::Number>().Int32Value();
        }
    }

    // Optional argument with default
    bool debug = false;  // default
    if (info.Length() >= 3) {
        if (!info[2].IsBoolean() && !info[2].IsUndefined()) {
            throw Napi::TypeError::New(env, "Third argument must be a boolean");
        }
        if (info[2].IsBoolean()) {
            debug = info[2].As<Napi::Boolean>().Value();
        }
    }

    Napi::Object result = Napi::Object::New(env);
    result.Set("name", name);
    result.Set("timeout", timeout);
    result.Set("debug", debug);
    return result;
}
```

## Pattern: Variadic Arguments

```cpp
// GOOD: Handle variable number of arguments
Napi::Value Sum(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() == 0) {
        return Napi::Number::New(env, 0);
    }

    double total = 0;
    for (size_t i = 0; i < info.Length(); i++) {
        if (!info[i].IsNumber()) {
            throw Napi::TypeError::New(env,
                "Argument " + std::to_string(i) + " must be a number");
        }
        total += info[i].As<Napi::Number>().DoubleValue();
    }

    return Napi::Number::New(env, total);
}
```

## Pattern: Options Object Validation

```cpp
// GOOD: Validate options object with optional properties
Napi::Value Configure(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() < 1 || !info[0].IsObject()) {
        throw Napi::TypeError::New(env, "Expected options object");
    }

    Napi::Object opts = info[0].As<Napi::Object>();

    // Required property
    if (!opts.Has("host") || !opts.Get("host").IsString()) {
        throw Napi::TypeError::New(env, "options.host is required");
    }
    std::string host = opts.Get("host").As<Napi::String>().Utf8Value();

    // Optional property with default
    int port = 8080;
    if (opts.Has("port")) {
        Napi::Value portVal = opts.Get("port");
        if (!portVal.IsNumber()) {
            throw Napi::TypeError::New(env, "options.port must be a number");
        }
        port = portVal.As<Napi::Number>().Int32Value();
    }

    // Optional boolean
    bool secure = false;
    if (opts.Has("secure")) {
        Napi::Value secureVal = opts.Get("secure");
        if (!secureVal.IsBoolean()) {
            throw Napi::TypeError::New(env, "options.secure must be a boolean");
        }
        secure = secureVal.As<Napi::Boolean>().Value();
    }

    return Napi::String::New(env,
        (secure ? "https://" : "http://") + host + ":" + std::to_string(port));
}
```

## Helper: Argument Validator Class

```cpp
// GOOD: Reusable argument validation helper
class ArgValidator {
public:
    ArgValidator(const Napi::CallbackInfo& info) : info_(info), env_(info.Env()) {}

    ArgValidator& RequireArgs(size_t count) {
        if (info_.Length() < count) {
            throw Napi::TypeError::New(env_,
                "Expected at least " + std::to_string(count) + " arguments, got " +
                std::to_string(info_.Length()));
        }
        return *this;
    }

    std::string GetString(size_t index, const char* name) {
        if (index >= info_.Length() || !info_[index].IsString()) {
            throw Napi::TypeError::New(env_,
                std::string(name) + " must be a string");
        }
        return info_[index].As<Napi::String>().Utf8Value();
    }

    double GetNumber(size_t index, const char* name) {
        if (index >= info_.Length() || !info_[index].IsNumber()) {
            throw Napi::TypeError::New(env_,
                std::string(name) + " must be a number");
        }
        return info_[index].As<Napi::Number>().DoubleValue();
    }

    double GetNumberOr(size_t index, double defaultValue) {
        if (index >= info_.Length() || info_[index].IsUndefined()) {
            return defaultValue;
        }
        if (!info_[index].IsNumber()) {
            throw Napi::TypeError::New(env_,
                "Argument " + std::to_string(index) + " must be a number");
        }
        return info_[index].As<Napi::Number>().DoubleValue();
    }

private:
    const Napi::CallbackInfo& info_;
    Napi::Env env_;
};

// Usage
Napi::Value Calculate(const Napi::CallbackInfo& info) {
    ArgValidator args(info);
    args.RequireArgs(2);

    double base = args.GetNumber(0, "base");
    double exponent = args.GetNumber(1, "exponent");
    double precision = args.GetNumberOr(2, 2.0);

    double result = std::pow(base, exponent);
    return Napi::Number::New(info.Env(),
        std::round(result * std::pow(10, precision)) / std::pow(10, precision));
}
```

## References

- [N-API Callback Info](https://nodejs.org/api/n-api.html#napi_get_cb_info)
- [node-addon-api CallbackInfo](https://github.com/nodejs/node-addon-api/blob/main/doc/callbackinfo.md)
